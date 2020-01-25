import functools as ft


id = lambda x: x
empty = lambda *args, **kwargs: None


def _compose2(f, g):
    return lambda arg: f(g(arg))


def compose(*fs):
    return ft.reduce(_compose2, fs)


