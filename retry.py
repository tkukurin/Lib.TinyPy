import sys
import funct as f
from time import sleep


def retry(max_tries, delay=1, backoff=2, exceptions=(Exception,), hook=f.empty):
  """
  delay: Sleep this many seconds * backoff * try number after failure
  backoff: Multiply delay by this factor after each failure
  exceptions: A tuple of exception classes; default (Exception,)
  hook: Optional; called prior to retry. Mainly for logging failures.
  """
  def dec(func):
    def f2(*args, **kwargs):
      mydelay = delay
      for tries_remaining in reversed(range(max_tries)):
        try:
          return func(*args, **kwargs)
        except exceptions as e:
          if tries_remaining <= 0: raise
          if hook is not None:
            hook(tries_remaining, e, mydelay)
          sleep(mydelay)
          mydelay = mydelay * backoff
    return f2
  return dec

