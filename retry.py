
import sys
import logging
import threading
import funct as f
import functools

from time import sleep


def _timer(f, amount, args, kwargs):
  timer = threading.Timer(amount, f, args=args, kwargs=kwargs)
  timer.start()
  return timer


def _sleep(f, amount, args, kwargs):
  if kwargs.get('_tries_remaining', 1) < 0: raise
  sleep(amount)
  return f(*args, **kwargs)


def backoff_async(
    max_tries, delay=1, backoff=2, exceptions=(Exception,), hook=f.true):
  return _backoff(
    max_tries, delay=delay, backoff=backoff, exceptions=(Exception,), hook=hook,
    retry=_timer,)


def backoff_hook(delay=1, backoff=2, hook=f.true):
  return _backoff(
    float('inf'), delay=delay, backoff=backoff, exceptions=(Exception,),
    hook=hook, retry=_timer)


def backoff(
    max_tries, delay=1, backoff=2, exceptions=(Exception,), hook=f.true):
  return _backoff(
    max_tries, delay=delay, backoff=backoff, exceptions=(Exception,), hook=hook,
    retry=_sleep)


def _backoff(
    max_tries, delay=1, backoff=2, exceptions=(Exception,),
    hook=f.true, retry=_timer):
  '''
  delay: Sleep this many seconds * backoff * try number after failure
  backoff: Multiply delay by this factor after each failure
  exceptions: A tuple of exception classes to catch.
  hook: Optional; called prior to retry. Mainly for logging failures.
    Return False to early exit from retrying.
  retry: retry method
  '''
  def dec(func):
    @functools.wraps(func)
    def f2(*args, _tries_remaining=max_tries, _cur_delay=delay, **kwargs):
      try:
        return func(*args, **kwargs)
      except exceptions as e:
        if hook(e, _tries_remaining, _cur_delay) and _tries_remaining > 0:
          kwargs['_tries_remaining'] = _tries_remaining - 1
          kwargs['_cur_delay'] = _cur_delay * backoff
          retry(f2, _cur_delay, args, kwargs)
    return lambda *args, **kwargs: retry(f2, 0, args, kwargs)
  return dec
