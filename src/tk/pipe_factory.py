import shlex

from typing import Optional
from types import SimpleNamespace

from twisted.internet import (
  defer,
  error,
  interfaces,
  protocol,
  reactor
)

from twisted.internet.interfaces import IReactorProcess

from twisted.logger import LogLevel
from twisted.python import failure

from tk.callbacks import (
  cb_exit,
  cb_log_result
)

from tk.context_logger import ContextLogger
from tk.errors import ProcessError

#
# PipeProtocol class
#
class PipeProtocol(protocol.ProcessProtocol):
  logger = ContextLogger()
  transport : Optional[interfaces.IProcessTransport]

  def __init__(self, pipe):
    super().__init__()
    self.pipe     = pipe
    self.next : Optional["PipeProtocol"] = None
    
    # ready for stdin
    self.ready    = defer.Deferred()  
    
    self.stdout   = b''
    self.stderr   = b''
    
    self._exiting = False

  def set_next(self, proto: "PipeProtocol"):
    self.next = proto
  
  def connectionMade(self):
    self.ready.callback(self)

  def outReceived(self, data):
    if self.next:
      self.next.ready.addCallback(PipeProtocol.forward, data)
    else:
      self.stdout = self.stdout + data

  def errReceived(self, data):
    self.stderr = self.stderr + data

  def processExited(self, reason : failure.Failure):
    if isinstance(reason.value, error.ProcessTerminated):
      proc = self.next
      while proc is not None:
        if proc._exiting == False:
          proc.transport.signalProcess("TERM")
          proc._exiting = True
        proc = proc.next
   
      if self.pipe.finished is not None:
        exc = ProcessError(self.stderr)
        self.logger.error("{e}", e = repr(exc))
        self.pipe.finished.errback(exc)
        self.pipe.finished = None
              
    elif isinstance(reason.value, error.ProcessDone):
      if self.next is None:
        self.pipe.finished.callback(self.stdout)


  def outConnectionLost(self):     
    if self.next:
      self.next.ready.addCallback(PipeProtocol.closeStdin)
     
  def forward(self, data):
    self.transport.write(data)
    return self
  
  def closeStdin(self):
    self.transport.closeStdin()
    return self


#
# Pipe class
# 
class Pipe(object):
  logger = ContextLogger()

  def __init__(self, factory):
    self.factory  = factory
    self.finished = defer.Deferred()

  @property
  def procs(self):
    return self.factory.cache[self].procs

  def run(self, data : bytes = None) -> defer.Deferred:
    for cmd in self.factory.cmds:
      args = shlex.split(cmd)
      pipe_protocol     = PipeProtocol(self)
      pipe_protocol.cmd = cmd

      proc = IReactorProcess(reactor).spawnProcess(pipe_protocol, args[0], args)
      self.procs.append(proc)

    n = len(self.factory.cmds)
    for i,j in zip(range(0,n-1), range(1,n)):
      proto_i = self.procs[i].proto
      proto_j = self.procs[j].proto
      proto_i.set_next(proto_j)

    init : defer.Deferred = self.procs[0].proto.ready
    if data:
      init.addCallback(PipeProtocol.forward, data)
    init.addCallback(PipeProtocol.closeStdin)

    return self.finished

#
# PipeFactory class
#
class PipeFactory(object):
  logger  = ContextLogger()
  cache   = dict()

  def __init__(self, cmds):
    self.cmds     = cmds

  def run(self, data = None) -> defer.Deferred:
    pipe        = Pipe(self)

    initialized = defer.maybeDeferred(lambda d: d, data)

    self.cache[pipe] = SimpleNamespace(
      procs = []
    )

    initialized.addCallback(pipe.run)
    initialized.addBoth(self.finalize, pipe)

    return initialized
  
  def finalize(self, result, pipe: Pipe):
    del self.cache[pipe]
    return result 

#
# main
#
if __name__ == '__main__':

  from context_logger import initialize_logging
  observer = initialize_logging(LogLevel.debug, {})

  logger = ContextLogger()
  logger.observer = observer

  # Pipe.logger.observer = observer

  cmds = [
    """ /usr/bin/find ./tests/data/foo -type f -not -path "*/__pycache__/*" -print """,
    """ /usr/bin/xargs -I% /usr/bin/md5sum %""",
    """ /usr/bin/sort """,
    """ /usr/bin/md5sum """
  ]

  data = "\n".join([
    "./tests/data/foo/message_one",
    "./tests/data/foo/message_two",
  ]).encode('utf8')

  d1 = PipeFactory(cmds[1:]).run( data )
  d1.addCallback(cb_log_result, format = "with data    : {result}")

  d2 = PipeFactory(cmds).run()
  d2.addCallback(cb_log_result, format = "without data : {result}")

  dl = defer.DeferredList([d1, d2])
  dl.addBoth(cb_exit)

  reactor.run()
