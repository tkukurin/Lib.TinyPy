
import sys
import logging
import threading
import funct as f


def backoff(max_tries, delay=1, backoff=2, exceptions=(Exception,), hook=f.true):
  """
  delay: Sleep this many seconds * backoff * try number after failure
  backoff: Multiply delay by this factor after each failure
  exceptions: A tuple of exception classes; default (Exception,)
  hook: Optional; called prior to retry. Mainly for logging failures.
    Return False to early exit from retrying.
  """
  def dec(func):
    def f2(*args, tries_remaining=max_tries, cur_delay=delay, **kwargs):
      try:
        return func(*args, **kwargs)
      except exceptions as e:
        if not hook(e, tries_remaining, cur_delay) or tries_remaining <= 0: raise
        kwargs['tries_remaining'] = tries_remaining - 1
        kwargs['cur_delay'] = cur_delay * backoff
        threading.Timer(
          cur_delay, f2, args=args, kwargs=kwargs).start()
    return f2
  return dec

