"""
Module docstring

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit
anim id est laborum.

"""
import os
import tempfile


class MySuperClass:
    def baseFunc(self):
        """
        This method is on the super class
        """


class MyClass(MySuperClass):
    """
    Class docstring

    Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus
    ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus
    duis convallis.

    Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus
    fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada
    lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti
    sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
    """
    def __init__(self, arg1):
        """
        Docstring for constructor

        Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque
        faucibus ex sapien vitae pellentesque sem placerat. In id cursus
        mi pretium tellus duis convallis.

        Parameters
        ----------
          arg1 : str
            Some description of arg1
        
        """

    def doSomething(self, arg1, arg2):
        """
        Docstring for simple method

        This method does something of great value, using just two arguments. I have
        no idea what it does, but here is a verbose description of it.

        Parameters
        ----------
          arg1 : int
            The first argument is pretty important
          arg2 : float
            The second argument is also important. Infact, it is so important
            that its description runs over two lines

        Returns
        -------
          retVal : str
            Some sort of string is returned
        """

    def _weakPrivate(self):
        """
        This method is weakly private, because it starts with a single underscore
        """

    def __strongPrivate(self):
        """
        This method is strongly private, as it starts with double underscore
        """


def someFunc(arg1, arg2, arg3):
    """
    Simple function docstring

    Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque
    faucibus ex sapien vitae pellentesque sem placerat. In id cursus
    mi pretium tellus duis convallis.

    Parameters
    ----------
      arg1 : str
        Some description of arg1
      arg2 : str
        Some description of arg2
      arg3 : str
        Some description of arg3
    """


def _weakPriv():
    """
    A weakly private function
    """


def __strongPriv():
    """
    A strongly private function
    """


SOME_VALUE = 100
OTHER_VALUE = "A string"
