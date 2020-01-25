
import functools as ft
import itertools as it
import operator

from typing import (
  Union, List, Callable, Iterable)

import funct


idx = operator.itemgetter
partial = ft.partial

# Take a look at an element from iterable
peek = funct.compose(next, iter)


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


