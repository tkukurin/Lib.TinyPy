'''Simple query from Sqlite3 databases.
'''

import sqlite3

from dataclasses import dataclass
from types import SimpleNamespace as ns
from typing import Union
from pathlib import Path


@dataclass
class Fetcher:
  def __init__(self, database: Union[str, Path]):
    self.conn = sqlite3.connect(database)

  qq = lambda self, *a, **kw: self.conn.execute(' '.join(a), **kw)
  ql = lambda self, *a, **kw: self.qq(*a, **kw).fetchall()
  __call__ = lambda self, *a, **kw: self.ql(*a, **kw)

  for_ = lambda self, table: TableFetcher(self, table)

  # Longform
  query = qq
  query_ = ql

  @property
  def tables(self):
    return self.ql('''SELECT * FROM sqlite_master WHERE type='table' ''')



@dataclass
class TableFetcher:
  fetcher: Fetcher
  table: str

  qq = lambda self, sel, *a, **kw: self.fetcher.qq(
    f'SELECT {sel} FROM {self.table} ' + ' '.join(a), **kw)
  ql = lambda self, *a, **kw: self.qq(*a, **kw).fetchall()
  qns = lambda self, selects, *a, **kw: map(
    lambda row: ns(**dict(zip(selects, row))),
    self.qq(','.join(selects), *a, **kw))

  def qd(self, *sel, **kw):
    '''Convenience? use **kw to specify SELECT params.
    Example:
      qd('title', WHERE='title <> "abc"', LIMIT=5, kw={})
    '''
    kw_for_query = kw.pop('kw', {})
    query_params = ' '.join(f'{k} {v}' for k, v in kw.items())
    return self.qq(','.join(sel), query_params, **kw_for_query).fetchall()

  # Longform
  query = qq
  query_ = ql
  query_namespace = qns
  query_dict = qd

  __call__ = lambda self, *a, **kw: self.ql(*a, **kw)

