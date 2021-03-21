import functools as ft


id = lambda x: x
empty = lambda *a, **kw: None
true = lambda *a, **kw: True
false = lambda *a, **kw: False


def compose(*fs):
  def _compose2(f, g):
    return lambda arg: f(g(arg))
  return ft.reduce(_compose2, fs)


