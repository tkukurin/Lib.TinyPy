import typing as T

import logging
import sys
import io

from pathlib import Path
from functools import wraps


def cfg(name=None, level=logging.DEBUG):
  logging.basicConfig(**_getcfg(level=level))
  return logging.getLogger(name)


def _getcfg(level=logging.DEBUG):
  return dict(
      format='[%(levelname)s|%(module)s:%(lineno)s|%(asctime)s] %(message)s',
    datefmt='%y-%m-%d %X',
    level=level)


def get_strlog(name, stream=None, fmt=None, datefmt=None):
  '''Log to stream. Creates StringIO if none provided.'''
  stream = stream or io.StringIO()
  logger = logging.getLogger(name)
  logger.propagate = False
  logger.addHandler(_streamhandler(stream, logging.Formatter(fmt, datefmt)))
  return logger, stream


class LogPrinter:
  def __init__(self, log=None):
    self.log = log or logging.getLogger(__name__)
    self.log.setLevel(logging.DEBUG)

  def write(self, text):
    if text.strip():
      self.log.debug(text)


def printlog(func):
  '''Treat print as log within some function. Assumes single-thread execution.
  '''
  @wraps(func)
  def pwrapper(*arg, **kwargs):
    stdold = sys.stdout
    try:
      sys.stdout = LogPrinter()
      return func(*arg, **kwargs)
    finally: sys.stdout = stdold
  return pwrapper


def to(stream_or_fname: T.Union[io.IOBase, str, Path]):
  '''Temp redirect log. Assumes single-thread execution.
  If stream_or_fname is path, will open/close file as appropriate.
  '''
  logger = logging.getLogger()
  is_fname = isinstance(stream_or_fname, (str, Path))

  def _inner(func):
    @wraps(func)
    def _innerinner(*a, **kw):
      hs_old = logger.handlers
      stream = open(stream_or_fname, 'a') if is_fname else stream_or_fname
      try:
        formatter = hs_old[-1].formatter if hs_old else logging.Formatter()
        logger.handlers = [_streamhandler(stream, formatter)]
        return func(*a, **kw)
      finally:
        logger.handlers = hs_old
        if is_fname: stream.close()
    return _innerinner
  return _inner


def _streamhandler(stream, formatter):
  sh = logging.StreamHandler(stream)
  sh.formatter = formatter
  return sh

