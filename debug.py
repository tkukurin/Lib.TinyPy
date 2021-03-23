import sys
import logging
import reprlib

from functools import wraps


# Improved version of
# https://wiki.python.org/moin/PythonDecoratorLibrary#Controllable_DIY_debug
class debug:
  '''Decorator to debug on a per-function basis.
  ex:
  @debug('core')
  def func(): pass
  debug.enable('core')

  @debug.byname
  def func(): pass
  debug.enable('func')
  '''

  ENABLE = set(['core',])
  REPR = reprlib.repr
  L = logging.getLogger(__name__)

  @classmethod
  def _debug_fn(cls, f, args, kwargs):
    args_str, kwds_str = map(debug.REPR, (args, kwargs))
    cls.L.debug('[CALL:%s] (%s, %s)', f.__name__, args_str, kwds_str)
    result = f(*args, **kwargs)
    cls.L.debug('[RET:%s] %s', f.__name__, debug.REPR(result))
    return result

  @classmethod
  def byname(cls, f):
    '''Use name of `f` as aspect.
    @debug.byname
    def mymethod: pass
    '''
    dbg = cls(f.__name__)
    return wraps(f)(dbg(f))

  @classmethod
  def enable(cls, *what):
    cls.ENABLE = set(what)
    return cls.ENABLE

  def __init__(self, *aspects):
    self.aspects = set(aspects)

  def __call__(self, f):
    @wraps(f)
    def newf(*args, **kwargs):
      if not (self.aspects & self.ENABLE or f.__name__ in self.ENABLE):
        return f(*args, **kwargs)
      return self._debug_fn(f, args=args, kwargs=kwargs)
    return newf


enable = debug.enable
byname = debug.byname

