# plainpydoc2md
Convert plain Python docstrings into Markdown files

This is intended for simple projects, where things like Sphinx and ReadTheDocs are more complex
than desired. The main value of writing Markdown is that this can be stored directly into
a Git repository and will be rendered directly in a web browser when viewed on Github. This
makes for very direct availablity of the Python documentation.

This script reads one or more Python modules and generates corresponding Markdown (.md) files
with the docstrings layed out in a simple but readable fashion. The main point is that the
docstrings are not parsed for further formatting, but rather they are just copied over as
plain text. In most cases, programmers make their docstrings readable in a text editor anyway,
so this is usually sufficient, even if not very fancy.


## Installation
The script can be installed from the repository using pip, e.g.

    git clone https://github.com/ubarsc/plainpydoc2md.git
    cd plainpydoc2md
    pip install .

or directly from the provided `.tar.gz` file of a specific release, e.g.

    pip install https://github.com/ubarsc/plainpydoc2md/releases/download/1.0.0/plainpydoc2md-1.0.0.tar.gz

Check if it is installed by requesting the command line help

    plainpydoc2md -h

## Usage
There are some example files provided in the testInputs subdirectory. For example

    plainpydoc2md -i testInputs/testfile.py -o ~/tmp

will write the output Markdown file as `/tmp/testfile.md`. Use your favourite Markdown
viewing tool (e.g. `retext`) to view it. This example deomonstrates most of the main
features.

There is also an example of a package directory structure, demonstrating how different
package components are handled.

The input can be specified as either a specific file, a specific directory of `*.py` files,
or a package or module name (assuming they are installed and importable).

## Requirements
This package uses only Python standard library tools. However, it is important to be
aware that any requirements of the code being documented should be available. The module
files being processed are imported during processing, and while the code itself does not
necessarily have to be installed (if filenames are specified explicitly), their dependent
imports must be installed and importable. If this is not true, warning messages will be
printed to stderr indicating which files were not imported.
