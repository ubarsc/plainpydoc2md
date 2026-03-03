#!/usr/bin/env python
"""
Convert plain Python docstrings into Markdown files

This is intended for simple projects, where things like Sphinx and ReadTheDocs
are more complex than desired. The main value in writing Markdown is that
Github will render it directly in a web browser.

This script reads one or more Python modules and generates corresponding
Markdown (.md) files with the docstrings layed out in a simple but readable
fashion. The main point is that the docstrings are not parsed for further
formatting, but rather they are just copied over as plain text. In most cases,
programmers make their docstrings readable in a text editor anyway, so this is
usually sufficient, even if not very fancy.

"""
import sys
import os
import argparse
import inspect
import pkgutil
import importlib
import glob


__version__ = '1.0.1'

# Markdown indent for pre-formatted text
INDENT_BASE = 4

# Other indent amounts are added to the base amount
INDENT_MODULE = INDENT_BASE
INDENT_CLASS = INDENT_BASE + 2
INDENT_FUNCTION = INDENT_BASE + 4
INDENT_METHODHDR = INDENT_BASE + 2
INDENT_METHOD = INDENT_METHODHDR + 4


def getCmdargs():
    "Get command line arguments"
    p = argparse.ArgumentParser(description="""
        Convert plain Python docstrings into Markdown files. The main value
        of writing Markdown is that it will be rendered directly in a web
        browser when viewed on Github
        """)
    p.add_argument("-i", "--input", help=("Input specification. Can be " +
        "the name of a package or module (i.e. something one might import), " +
        "or a path to either a python file, the top directory of a package, " +
        "or a non-package directory of .py files"))
    p.add_argument("-o", "--outdir",
        help="Output directory to write Markdown files")
    p.add_argument("--noflatten", default=False, action="store_true",
        help=("For package input, write output Markdown files into a " +
              "corresponding directory structure. Default will flatten " +
              "the structure into a single output directory"))
    p.add_argument("--includeprivate", default=False, action="store_true",
        help=("Include private objects (i.e. those whose names begin with " +
              "an underscore). Default will leave these hidden."))
    cmdargs = p.parse_args()

    return cmdargs


def mainCmd():
    "Main routine"
    cmdargs = getCmdargs()

    modulelist = findAllModules(cmdargs)
    for mod in modulelist:
        processModule(mod, cmdargs)


def findAllModules(cmdargs):
    """
    Find all the modules to be processed. Return a list of the imported
    module objects
    """
    modulelist = []
    if os.path.isfile(cmdargs.input):
        (moddir, modname) = os.path.split(cmdargs.input)
        if modname.endswith('.py'):
            modname = modname[:-3]
        if moddir not in sys.path:
            sys.path.append(moddir)
        modObj = doImport(modname)
        if modObj is not None:
            modulelist = [modObj]
    elif (os.path.isdir(cmdargs.input) and
            not os.path.exists(os.path.join(cmdargs.input, "__init__.py"))):
        # Plain directory containing .py files
        filelist = glob.glob(os.path.join(cmdargs.input, "*.py"))
        if cmdargs.input not in sys.path:
            sys.path.append(cmdargs.input)
        modulelist = []
        for filename in filelist:
            modname = os.path.basename(filename)[:-3]
            modObj = doImport(modname)
            if modObj is not None:
                modulelist.append(modObj)
    else:
        # Assume we have a name to import, either as path to package top dir
        # or simple package/module name
        inputStr = cmdargs.input
        if inputStr.endswith('/'):
            inputStr = inputStr[:-1]
        (pkgdir, pkgname) = os.path.split(inputStr)
        if pkgdir not in sys.path:
            sys.path.append(pkgdir)
        pkg = doImport(pkgname)
        if pkg is None:
            raise FileNotFoundError(f"Unable to import '{cmdargs.input}'")
        modulelist = [pkg]
        if hasattr(pkg, '__path__'):
            # This is genuinely a package, so we search recursively for
            # modules and sub-packages
            if pkgdir == '':
                pkgdirlist = pkg.__path__
            else:
                pkgdirlist = [inputStr]
            modulelist = [pkg]
            for modinfo in pkgutil.walk_packages(pkgdirlist, pkgname + '.'):
                modObj = doImport(modinfo.name)
                if modObj is not None:
                    modulelist.append(modObj)

    return modulelist


def doImport(modname):
    """
    Import the given module or package. Return the imported object

    Any exceptions are catch and printed to stderr, and the return value
    will be None
    """
    try:
        modObj = importlib.import_module(modname)
    except Exception as e:
        print(f'Exception "{e}" while importing "{modname}"', file=sys.stderr)
        modObj = None

    return modObj


def openOutfile(modObj, cmdargs):
    """
    Open the output Markdown file for the given module
    """
    modName = modObj.__name__
    outdir = cmdargs.outdir
    if cmdargs.noflatten:
        subpkglist = modName.split('.')
        if len(subpkglist) > 1:
            subdirs = os.path.join(*subpkglist[:-1])
            outdir = os.path.join(cmdargs.outdir, subdirs)
        filename = os.path.join(outdir, f"{subpkglist[-1]}.md")
    else:
        filename = os.path.join(outdir, f"{modName}.md")

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    f = open(filename, 'w')
    print(f"# {modName}", file=f)
    return f


def processModule(modObj, cmdargs):
    """
    Process a single module into its Markdown file
    """
    modFile = modObj.__file__
    modDoc = inspect.getdoc(modObj)
    members = inspect.getmembers(modObj)

    classList = []
    funcList = []
    valueList = []
    hidePrivate = not cmdargs.includeprivate

    for (name, obj) in members:
        if (inspect.isclass(obj) and not importedVal(modFile, obj) and
                not (hidePrivate and isPrivate(name))):
            classList.append(obj)
        elif ((inspect.isfunction(obj) or isNumbaFunc(obj)) and
                not importedVal(modFile, obj) and
                not (hidePrivate and isPrivate(name))):
            funcList.append(obj)
        elif inspect.ismodule(obj):
            pass
        elif (not importedVal(modFile, obj) and not inspect.isbuiltin(obj) and
                not (hidePrivate and isPrivate(name))):
            valueList.append((name, obj))

    emptyModule = (modDoc is None and len(classList) == 0 and
                   len(funcList) == 0 and len(valueList) == 0)

    if not emptyModule:
        f = openOutfile(modObj, cmdargs)
        writeDocstring(f, modDoc, indent=INDENT_MODULE)

    if len(classList) > 0:
        print("## Classes", file=f)
        for obj in classList:
            processClass(obj, f, hidePrivate)
    if len(funcList) > 0:
        print("## Functions", file=f)
        for obj in funcList:
            processFunction(obj, f)
    if len(valueList) > 0:
        print("## Values", file=f)
        for (name, val) in valueList:
            print(f"    {name} = {repr(val)}", file=f)


def isNumbaFunc(obj):
    """
    Checks if the object is a jit-ed numba function
    """
    return (type(obj).__name__ == "CPUDispatcher")


def importedVal(modFile, obj):
    """
    Check if obj is imported from another file, returns True if so.

    This is used to exclude things which have been imported into this module
    """
    try:
        objFile = inspect.getsourcefile(obj)
    except TypeError:
        objFile = None
    return (objFile is not None and objFile != modFile)


def isPrivate(name):
    """
    Return True if name is private by convention
    """
    return (name.startswith('_'))


def writeDocstring(f, docString, indent):
    """
    Copy the given docstring into the output file, with suitable indentation
    """
    indentStr = indent * ' '
    lines = []
    if docString is not None:
        lines = docString.split('\n')

    for line in lines:
        if len(line.rstrip()) > 0:
            print(indentStr, end='', file=f)
        print(line.rstrip(), file=f)
    print(file=f)


def processClass(obj, f, hidePrivate):
    """
    Output Markdown for the given class object
    """
    classname = obj.__name__
    baseclassNames = [c.__name__ for c in obj.__bases__
                      if c.__name__ != "object"]
    fullClassname = classname
    if len(baseclassNames) > 0:
        fullClassname = f"{classname}({'.'.join(baseclassNames)})"
    print("### class", fullClassname, file=f)
    docstr = inspect.getdoc(obj)
    writeDocstring(f, docstr, indent=INDENT_CLASS)

    members = inspect.getmembers(obj)
    for (objname, subobj) in members:
        if inspect.ismethod(subobj) or inspect.isfunction(subobj):
            processMethod(subobj, classname, hidePrivate, f)


def processFunction(obj, f):
    """
    Output Markdown for the given function object
    """
    name = obj.__name__
    sigStr = str(inspect.signature(obj))
    print("### def", name + sigStr, file=f)
    docstr = inspect.getdoc(obj)
    writeDocstring(f, docstr, indent=INDENT_FUNCTION)


def processMethod(obj, classname, hidePrivate, f):
    """
    Output Markdown for the given method of the given class
    """
    qualnameFields = obj.__qualname__.split('.')
    methname = qualnameFields[-1]
    methClassName = '.'.join(qualnameFields[:-1])

    # Hide all special methods except __init__, which is escaped with '\'
    if methname == "__init__":
        methname = "\\_\\_init\\_\\_"
    elif hidePrivate and isPrivate(methname):
        methname = None
    elif methClassName != classname:
        # Hide inherited methods
        methname = None

    if methname is not None:
        sigStr = str(inspect.signature(obj))
        fullMethodStr = f"{classname}.{methname}{sigStr}"
        nbsp = INDENT_METHODHDR * '&nbsp;'
        print("####", nbsp, fullMethodStr, file=f)
        docstr = inspect.getdoc(obj)
        writeDocstring(f, docstr, indent=INDENT_METHOD)


if __name__ == "__main__":
    mainCmd()
