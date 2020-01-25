import logging

from functools import wraps


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
    finally:
      sys.stdout = stdold
  return pwrapper

