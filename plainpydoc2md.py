#!/usr/bin/env python
"""
Convert plain Python docstrings into Markdown files

This is intended for simple projects, where things like Sphinx and ReadTheDocs
are more complex than desired.

This scripts reads one or more Python modules and generates corresponding
Markdown (.md) files with the docstrings layed out in a simple but readable
fashion. The main point is that the docstrings are not parsed for further
formatting, but rather they are just copied over as plain text. In most cases,
programmers make their docstrings readable in a text editor anyway, so this is
usually sufficient, even if not very fancy.

We make heavy use of the inspect module to understand each object and find
its docstring.

"""
import sys
import os
import argparse
import inspect
import pkgutil
import importlib
import glob


def getCmdargs():
    "Get command line arguments"
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", help=("Input specification. Can be " +
        "either a Python filename, a directory containing .py files, " +
        "a Python package name, or the top directory of a Python package"))
    p.add_argument("-o", "--outdir",
        help="Output directory to write Markdown files")
    p.add_argument("--flatten", default=False, action="store_true",
        help=("Flatten any directory structure and place all output files " +
              "in one directory (default places output files in " +
              "corresponding directory structure)"))
    cmdargs = p.parse_args()
    return cmdargs


def mainCmd():
    "Main command"
    cmdargs = getCmdargs()

    modulelist = findAllModules(cmdargs)
    for mod in modulelist:
        processModule(mod, cmdargs)


def findAllModules(cmdargs):
    """
    Find all the modules to be processed. Return a list of the imported
    module objects
    """
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
        # Assume we have a package, either as path to top dir or simple
        # package name
        (pkgdir, pkgname) = os.path.split(cmdargs.input)
        if pkgdir not in sys.path:
            sys.path.append(pkgdir)
        pkg = doImport(pkgname)
        if pkgdir == '':
            pkgdirlist = pkg.__path__
        else:
            pkgdirlist = [pkgdir]
        modulelist = []
        for modinfo in pkgutil.walk_packages(pkgdirlist, pkgname + '.'):
            if not modinfo.ispkg:
                modObj = doImport(modinfo.name)
                if modObj is not None:
                    modulelist.append(modObj)
            # Not yet sure what to do with package docstrings, so ignoring them

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
    filename = os.path.join(cmdargs.outdir, f"{modName}.md")
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

    f = openOutfile(modObj, cmdargs)
    writeDocstring(f, modDoc, indent=4)

    classList = []
    funcList = []
    valueList = []

    for (name, obj) in members:
        if inspect.isclass(obj) and not importedVal(modFile, obj):
            classList.append(obj)
        elif inspect.isfunction(obj) and not importedVal(modFile, obj):
            funcList.append(obj)
        elif inspect.ismodule(obj):
            pass
        elif (not importedVal(modFile, obj) and
                not (name.startswith('__') or name.endswith('__'))):
            valueList.append((name, obj))

    if len(classList) > 0:
        print("## Classes", file=f)
        for obj in classList:
            processClass(obj, f)
    if len(funcList) > 0:
        print("## Functions", file=f)
        for obj in funcList:
            processFunction(obj, f)
    if len(valueList) > 0:
        print("## Values", file=f)
        for (name, val) in valueList:
            print(f"    {name} = {val}", file=f)


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


def writeDocstring(f, docString, indent):
    """
    Copy the given docstring into the output file, with suitable indentation
    """
    indentStr = indent * ' '
    lines = []
    if docString is not None:
        lines = docString.split('\n')

    for line in lines:
        print(indentStr, end='', file=f)
        print(line, file=f)
    print(file=f)


def processClass(obj, f):
    """
    Output Markdown for the given class object
    """
    classname = obj.__name__
    print("### class", classname, file=f)
    docstr = inspect.getdoc(obj)
    writeDocstring(f, docstr, indent=6)

    members = inspect.getmembers(obj)
    for (objname, subobj) in members:
        if inspect.ismethod(subobj) or inspect.isfunction(subobj):
            processMethod(subobj, classname, f)


def processFunction(obj, f):
    """
    Output Markdown for the given function object
    """
    name = obj.__name__
    sigStr = str(inspect.signature(obj))
    print("### def", name + sigStr, file=f)
    docstr = inspect.getdoc(obj)
    writeDocstring(f, docstr, indent=8)


def processMethod(obj, classname, f):
    """
    Output Markdown for the given method of the given class
    """
    methname = obj.__name__
    # Hide all special methods except __init__, which is escaped with '\'
    if methname.startswith("__") and methname.endswith("__"):
        if methname == "__init__":
            methname = f"\\{methname}"
        else:
            methname = None

    if methname is not None:
        sigStr = str(inspect.signature(obj))
        fullMethodStr = f"{classname}.{methname}{sigStr}"
        print("#### &nbsp;&nbsp;&nbsp;&nbsp;", fullMethodStr, file=f)
        docstr = inspect.getdoc(obj)
        writeDocstring(f, docstr, indent=8)


if __name__ == "__main__":
    mainCmd()
