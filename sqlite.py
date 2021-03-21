'''Simple query from Sqlite3 databases.

Usage:
  with Fetcher('db.sqlite') as f:
    table = f.for_('table')
    single_row = table.qone('id', 'name')

Usage:
  fetcher = Fetcher('db.sqlite')
  with fetcher.for_('table') as table:
    single_row = table.qone('id', 'name')
'''

import sqlite3
import re
import functools
import contextlib
import typing as T
import logging

from dataclasses import dataclass, field
from types import SimpleNamespace as ns
from typing import Union
from collections import namedtuple
from pathlib import Path


L = logging.getLogger(__name__)


def _sql_cleanup(sql: str):
  def _structure(line):
    name, type_, *meta = re.split('\\s+', line.strip(' ,'))

    if type_ == 'integer': type_ = int
    elif type_ == 'real': type_ = float
    elif type_ == 'text': type_ = str
    elif type_ == 'blob': type_ = bytes
    else: type_ = None

    return ns(
      name=name, type=type_, meta=' '.join(meta))

  # 1st and last lines are not named columns (`create ...` and `)`)
  # TODO(tk) check if true for every db?
  return [_structure(line) for line in sql.split('\n')[1:-1]]


class Fetcher:
  def __init__(self, database):
    self.database = database
    self.conn = None

  @dataclass
  class TableInfo:
    name: str
    def __init__(self, name: str, sql: str):
      self.name = name
      self.sql = _sql_cleanup(sql)

  @property
  def tables(self):
    tables = self.qall(
      '''SELECT tbl_name, sql FROM sqlite_master WHERE type='table' ''')
    return [self.TableInfo(*t) for t in tables]

  def __enter__(self):
    if not self.conn:
      self.conn = sqlite3.connect(self.database)
      self.conn.row_factory = sqlite3.Row
    return self

  def __exit__(self, exc_type, exc_value, exc_tb):
    if self.conn:
      if exc_type is None:
        self.conn.commit()
      else:
        L.exception('Rolling back transaction')
        self.conn.rollback()
      self.conn.close()
    self.conn = None

  def for_(self, table: T.Union[str, TableInfo]):
    if isinstance(table, self.TableInfo):
      table = table.name
    return TableFetcher(self, table)

  exe = lambda self, *a: self.conn.execute(' '.join(a))
  qone = lambda self, *a: self.exe(*a).fetchone()
  qall = lambda self, *a: self.exe(*a).fetchall()


@dataclass
class TableFetcher:
  '''Can be used either as a context mgr or within fetcher's context mgr.
  '''
  fetcher: Fetcher
  table: str

  @functools.cached_property
  def columns(self):
    sql = self.fetcher.qone(
      f'SELECT sql FROM sqlite_master WHERE name=\'{self.table}\'')[0]
    return _sql_cleanup(sql)

  def __enter__(self):
    self.fetcher.__enter__()
    return self

  def __exit__(self, *a):
    self.fetcher.__exit__(*a)

  def qone(self, *sel, **kw):
    return ns(**self.qd(*sel, **kw).fetchone())

  def qgen(self, *sel, **kw):
    return map(lambda row: ns(**row), self.qd(*sel, **kw))

  def qall(self, *sel, **kw):
    return list(self.qgen(*sel, **kw))

  def qd(self, *sel, **kw):
    '''Ex: qd('title', WHERE='title <> "abc"', LIMIT=5)
    '''
    query_params = ' '.join(f'{k} {v}' for k, v in kw.items())
    return self.qq(','.join(sel), query_params)

  qq = lambda self, sel, *a: self.fetcher.exe(
    f'SELECT {sel} FROM {self.table} ' + ' '.join(a))

