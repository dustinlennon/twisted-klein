import traceback

from twisted.internet import interfaces, reactor
from twisted.logger import Logger, LogLevel
from twisted.python.failure import Failure

logger = Logger()

#
# callback, errback functions
#
def eb_crash(f : Failure):
  tb = f.getTracebackObject()
  if tb:
    traceback.print_tb(tb)
  else:
    print(f">>> unknown failure mode: {f}")
  f.raiseException()

def cb_exit(success_value_list):
  interfaces.IReactorTime(reactor).callLater(0, reactor.stop)

def cb_log_result(result, format, transform = str, level = LogLevel.info, **kw):
  getattr(logger, level.name)(
    format = format, result = transform(result), **kw
  )

def cb_debug(result, *args, **kw):
  logger.debug("{result}", result = result)
  for a in args:
    logger.debug("{a}", a = a)
  for k,v in kw.items():
    logger.debug("{k} : {v}", k = k, v = v)
  return result

def to_utf(b : bytes):
  return b.decode().strip()
