import functools as ft

# cf. https://wiki.python.org/moin/PythonDecoratorLibrary#Pseudo-currying
class curried(object):
  '''Decorator. Returns functions until all arguments are supplied.'''
  def __init__(self, func, *a):
    self.func = func
    self.args = a

  def __call__(self, *a):
    args = self.args + a
    if len(args) < self.func.func_code.co_argcount:
      # TODO check if update wrapper necessary
      return ft.update_wrapper(curried(self.func, *args), self.func)
    else:
      return self.func(*args)


def singleton(cls):
  '''Designates the decorated class as singleton.
  `@singleton class Foo` => `Foo()` will always be the same instance.'''

  cls.__new_original__ = cls.__new__

  @functools.wraps(cls.__new__)
  def singleton_new(cls, *args, **kw):
    it = cls.__dict__.get('__it__')
    if it is not None:
      return it

    cls.__it__ = it = cls.__new_original__(cls, *args, **kw)
    it.__init_original__(*args, **kw)
    return it

  cls.__new__ = singleton_new
  cls.__init_original__ = cls.__init__
  cls.__init__ = object.__init__

  return cls
