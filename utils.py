
import functools as ft
import itertools as it
import operator
import typing
import types

from typing import (
  Union, List, Callable, Iterable, Iterator,)

import funct


idx = operator.itemgetter
partial = ft.partial
nt = typing.NamedTuple
const = types.SimpleNamespace

# Take a look at an element from iterable
peek = funct.compose(next, iter)


class ModLoad:
  ''' Helper to load from another Python project.
  Really shouldn't be used, but sometimes useful for Jupyter prototyping.

  ex: ModLoad('/home/toni/PythonProj')
  '''

  def __init__(self, where):
    from pathlib import Path
    self.where = Path(
      where.where if isinstance(where, ModLoad)
      else where)

  def __call__(self, modname):
    '''Load module `modname` from `self.where/modname.py`'''
    import importlib.util
    modname = modname.strip('.py')
    spec = importlib.util.spec_from_file_location(
      modname, self.where / f'{modname}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

  def make(pathobj: const):
    for name, val in pathobj.__dict__.items():
      if name != 'base':
        setattr(pathobj, name, ModLoad(val))
    return pathobj


def flatmap(func: Callable, iterable: Iterable):
  return it.chain.from_iterable(map(func, *iterable))


def zip2lst(list_of_zips: Union[List, Iterator]):
  if not isinstance(list_of_zips, list):
    list_of_zips = list(list_of_zips)
  def accumulate(result, ziprow):
    for lst, el in zip(result, ziprow):
      lst.append(el)
    return result
  return ft.reduce(accumulate, list_of_zips, tuple([] for _ in list_of_zips))


def fuzzymatch(search_term_cased):
  '''Ignore-case simple fuzzy matching.'''
  search_term = search_term_cased.lower()
  def fuzzy_inner(test_against):
    test_against = test_against.lower()
    iterm = 0
    for letter in test_against:
      iterm += (letter == search_term[iterm])
      if iterm == len(search_term):
        return True
    return False
  return fuzzy_inner

