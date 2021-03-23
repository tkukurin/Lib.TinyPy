
import sys
import log
import retry
import debug


L = log.cfg()


def test_backoff():
  def hook(e, remain, delay):
    L.exception('remain=%s, delay=%s', remain, delay)
    return True
  @retry.backoff(max_tries=2, delay=1, hook=hook)
  def x():
    raise Exception('failed')
  x()


def test_debug():
  @debug.debug('core')
  def mymethod(x, y):
    print('mymethod', x, y)
    return x+y

  debug.debug.enable('core')
  mymethod(1,2)


def test_logto():
  @log.to('test.txt')
  def a():
    print('asdf')
    L.info('asdfg')
    return 1
  a()

def test_printlog():
  @log.printlog
  def a():
    print('asdf')
    return 1
  a()

for method in (
    test_printlog,
  ):
  method()
  print('--')


