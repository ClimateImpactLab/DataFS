'''
Utilities for assisting examples
'''


import tempfile
import shutil
import sys
from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO



@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield (sys.stdout, sys.stderr)
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def using_tmp_dir(func):
    '''
    Decorator providing a temporary directory as an argument
    '''

    def inner():
        '''
        Create a temporary directory and make sure to clean it up
        '''

        tmp_dir = tempfile.mkdtemp()
        
        try:
            func(tmp_dir)

        finally:
            shutil.rmtree(tmp_dir)

    return inner


class expect(object):

    @classmethod
    def stdout(cls, expected_output=None, test=None):
        '''
        Testing decorator asserting that stderr is Null and stdout passes test

        Parameters
        ~~~~~~~~~~
        expected_output : str
            Assert stdout == expected_output if provided
        
        test : func
            Assert func(stdout) == True if provided

        '''

        def decorator(func):
            def inner(*args, **kwargs):
                with captured_output() as conn:
                    out, err = conn
                    retval = func(*args, **kwargs)

                assert err is None or len(err.getvalue()) == 0

                outstr = out.getvalue().strip()

                if test:
                    assert test(outstr.strip())
                
                if expected_output:
                    assert outstr == expected_output

                print(outstr)

            return inner

        return decorator


    @classmethod
    def stderr(cls, expected_output=None, test=None):
        '''
        Testing decorator asserting that stdout is Null and stderr passes test

        Parameters
        ~~~~~~~~~~
        expected_output : str
            Assert stderr == expected_output if provided
        
        test : func
            Assert func(stderr) == True if provided

        '''

        def decorator(func):
            def inner(*args, **kwargs):
                with captured_output() as conn:
                    out, err = conn
                    retval = func(*args, **kwargs)

                assert err is None or len(err.getvalue()) == 0

                outstr = out.getvalue().strip()

                if test:
                    assert test(outstr.strip())
                
                if expected_output:
                    assert outstr == expected_output

                print(outstr)

            return inner

        return decorator

