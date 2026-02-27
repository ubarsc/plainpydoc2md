# MyModule

    Module docstring (short description)

    Long description of the module. This can have multiple paragraphs, and the layout of
    the string will be preserved. No further formatting is added within the docstring, but
    to be honest, our docstrings are usually sufficiently readable anyway that nothing
    further is required

    This would be the second paragraph of the module docstring

## Classes
### class myclass
      Class docstring (short description)

      As before, this can be multiple paragraphs, and the layout is not touched

#### &nbsp;&nbsp;&nbsp;&nbsp; myclass.\__init__(self, arg1, arg2)
        Docstring for __init__

        This is also passed through unaltered and unformatted
        
#### &nbsp;&nbsp;&nbsp;&nbsp; myclass.method(self, arg1, arg2)
        The method docstring (short description)

        The longer description would go here. In principle it could be several
        paragraphs, so I am just going to go on and on for a bit to make this long enough.

        Another paragraph here, this would be the second paragraph of the docstring.

        Parameters
        ----------
          arg1 : str
            Description of the parameter. This can, of course,
            have multiple lines.
          arg2 : int
            Description of the second parameter

## Functions

### def myfunc(arg1, arg2)
      Function docstring (short description)

      Long description. This to can have multiple paragraphs. The formatting is exactly
      as written into the Python code. This means that parameter blocks, etc., are
      preserved as written

      Parameters
      ----------
        arg1 : numpy.ndarray
          Description of arg1
        arg2 : float
          Description of arg2. Because the layout is not touched, this
          can spread across as many lines as you like.

## Values
    SOMEDEFINITION = 100
    SOMETHINGELSE = "hello"