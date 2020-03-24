import logging
import sys
import io

from functools import wraps


cfg = lambda: logging.basicConfig(**_getcfg())


def _getcfg():
  return dict(
    format='[%(levelname)s] %(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M',
    level=logging.DEBUG)


def _streamhandler(stream, formatter):
  sh = logging.StreamHandler(stream)
  sh.formatter = formatter
  return sh


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
    self.log.debug(text)


def printlog(func):
  @wraps(func)
  def pwrapper(*arg, **kwargs):
    stdold = sys.stdout
    try:
      sys.stdout = LogPrinter()
      return func(*arg, **kwargs)
    finally: sys.stdout = stdold
  return pwrapper

def logto(stream, formatter=None):
  logger = logging.getLogger()
  def _inner(func):
    @wraps(func)
    def _innerinner(*a, **kw):
      hs_old = logger.handlers
      try:
        formatter = (formatter or (
          hs_old[-1].formatter if hs_old else logging.Formatter()))
        logger.handlers = [_streamhandler(stream, formatter)]
        return func(*a, **kw)
      finally: logger.handlers = hs_old
    return _innerinner
  return _inner



