import sys
import logging
import reprlib

from functools import wraps


# Improved version of
# https://wiki.python.org/moin/PythonDecoratorLibrary#Controllable_DIY_debug
class debug:
  '''Decorator to debug on a per-function basis.'''

  REPR = reprlib.repr
  ENABLE = set(['core',])
  L = logging.getLogger(__name__)

  @classmethod
  def enable(cls, *what):
    debug.ENABLE = set(what)
    return debug.ENABLE

  def __init__(self, *aspects):
    self.aspects = set(aspects)

  def __call__(self, f):
    if self.aspects & debug.ENABLE:
      @wraps(f)
      def newf(*args, **kwds):
        args_str, kwds_str = map(debug.REPR, (args, kwds))
        debug.L.debug('[CALL:%s] (%s, %s)', f.__name__, args_str, kwds_str)
        result = f(*args, **kwds)
        debug.L.debug('[RET:%s] %s', f.__name__, debug.REPR(result))
        return result
      return newf
    return f

