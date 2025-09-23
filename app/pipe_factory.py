import shlex

from typing import Optional
from types import SimpleNamespace

from twisted.internet import (
  defer,
  interfaces,
  protocol,
  reactor
)

from twisted.logger import LogLevel

from callbacks import (
  cb_exit,
  cb_log_result,
  eb_crash
)

from context_logger import ContextLogger

#
# PipeProtocol class
#
class PipeProtocol(protocol.ProcessProtocol):
  logger = ContextLogger()
  transport : Optional[interfaces.IProcessTransport]

  def __init__(self, pipe):
    super().__init__()
    self.pipe   = pipe
    self.next : Optional["PipeProtocol"] = None
    self.ready  = defer.Deferred()
    self.result = b''

  def set_next(self, proto: "PipeProtocol"):
    self.next = proto
  
  def connectionMade(self):
    self.ready.callback(self)

  def outReceived(self, data):
    if self.next:
      self.next.ready.addCallbacks(PipeProtocol.forward, eb_crash, (data,))
    else:
      self.result = self.result + data
 
  def outConnectionLost(self):
    if self.next:
      self.next.ready.addCallbacks(PipeProtocol.closeStdin, eb_crash)
    else:
      self.pipe.finished.callback(self.result)

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

  @property
  def procs(self):
    return self.factory.cache[self].procs

  @property
  def finished(self):
    return self.factory.cache[self].finished

  def run(self, data : bytes = None) -> defer.Deferred:
    for cmd in self.factory.cmds:
      args = shlex.split(cmd)
      pipe_protocol = PipeProtocol(self)
      proc = reactor.spawnProcess(pipe_protocol, args[0], args)
      self.procs.append(proc)

    n = len(self.factory.cmds)
    for i,j in zip(range(0,n-1), range(1,n)):
      proto_i = self.procs[i].proto
      proto_j = self.procs[j].proto
      proto_i.set_next(proto_j)

    init : defer.Deferred = self.procs[0].proto.ready
    if data:
      init.addCallbacks(PipeProtocol.forward, eb_crash, (data,))
    init.addCallbacks(PipeProtocol.closeStdin, eb_crash)

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
    pipe = Pipe(self)

    self.cache[pipe] = SimpleNamespace(
      procs = [],
      finished = defer.Deferred()
    )

    finished = pipe.run(data)
    finished.addCallbacks(self.finalize, eb_crash, (pipe,))

    return finished
  
  def finalize(self, result, pipe):
    del self.cache[pipe]
    return result

#
# main
#
if __name__ == '__main__':

  from iso.context_logger import initialize_logging
  observer = initialize_logging(LogLevel.debug, {})

  logger = ContextLogger()
  logger.observer = observer

  # Pipe.logger.observer = observer

  cmds = [
    """ /usr/bin/find ./vmfs -type f -not -path "*/__pycache__/*" -print """,
    """ /usr/bin/xargs -I% /usr/bin/md5sum %""",
    """ /usr/bin/sort """,
    """ /usr/bin/md5sum """
  ]

  data = "\n".join([
    "./vmfs/etc/systemd/resolved.conf.d/10-mdns.conf",
    "./vmfs/etc/issue",
    "./vmfs/run/scripts/netplan-override.sh"
  ]).encode('utf8')

  d1 = PipeFactory(cmds[1:]).run(data)
  d1.addCallback(cb_log_result, format = "with data: {result}")
  d1.addErrback(eb_crash)

  d2 = PipeFactory(cmds).run()
  d2.addCallback(cb_log_result, format = "without data: {result}")
  d2.addErrback(eb_crash)

  dl = defer.DeferredList([d1, d2])
  dl.addCallbacks(cb_exit, eb_crash)

  reactor.run()
