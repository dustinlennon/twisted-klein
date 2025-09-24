import os

from twisted.internet import defer, reactor
from twisted.logger import LogLevel

from tk.callbacks import (
  cb_exit,
  cb_log_result,
  eb_crash
)

from tk.pipe_factory import PipeFactory

class DirectoryHash(object):
  cmds = [
    """ /usr/bin/find {basedir} -type f -print0 """,
    """ /usr/bin/xargs -0 -I% {hasher} %""",
    """ awk '{{ print $1 }}' """,
    """ /usr/bin/sort """,
    """ {hasher} """
  ]

  @classmethod
  def md5(cls, basedir) -> defer.Deferred:
    return cls.hash(basedir, "/usr/bin/md5sum")

  @classmethod
  def sha256(cls, basedir) -> defer.Deferred:
    return cls.hash(basedir, "/usr/bin/sha256sum")

  @classmethod
  def hash(cls, basedir, hasher) -> defer.Deferred:
    if os.path.isdir(basedir) == False:
      raise FileNotFoundError(f"'{basedir}' is not a directory.")
    
    kw = dict(basedir = basedir, hasher = hasher )
    cmds = [ cmd.format(**kw) for cmd in cls.cmds ]    

    d = PipeFactory(cmds).run()
    d.addCallbacks(lambda r: r.strip(), eb_crash)
    return d

#
# main
#
if __name__ == '__main__':
  from context_logger import initialize_logging, ContextLogger

  initialize_logging(LogLevel.debug, {})
  logger = ContextLogger()

  d3 = DirectoryHash.md5('./vmfs')
  d3.addCallback(cb_log_result, "directory hash (md5): {result}")
  d3.addErrback(eb_crash)

  d4 = DirectoryHash.sha256('./vmfs')
  d4.addCallback(cb_log_result, "directory hash (sha256): {result}")
  d4.addErrback(eb_crash)

  dl = defer.DeferredList([d3, d4])
  dl.addCallbacks(cb_exit, eb_crash)

  reactor.run()
