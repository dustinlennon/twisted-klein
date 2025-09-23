import os
import jinja2

from twisted.internet import defer, reactor
from twisted.logger import LogLevel

from callbacks import (
  cb_exit,
  cb_log_result,
  eb_crash
)

from pipe_factory import PipeFactory

class SelfExtractor(object):
  cmds = [
    """ /usr/bin/tar -C {basedir} -cz . """,
    """ /usr/bin/base64 - """
  ]

  def __init__(self, template_dir, template):
    self.env = jinja2.Environment(
      loader = jinja2.FileSystemLoader( template_dir )
    )
    self.template = template

  def generate(self, basedir) -> defer.Deferred:
    if os.path.isdir(basedir) == False:
      raise FileNotFoundError(f"'{basedir}' is not a directory.")
    
    kw = dict(basedir = basedir )
    cmds = [ cmd.format(**kw) for cmd in self.cmds ]

    d = PipeFactory(cmds).run()
    d.addCallbacks(self.render, eb_crash)
    return d
  
  def render(self, b64encoded_tarball):
    template = self.env.get_template( self.template )
    script = template.render(
      b64encoded_tarball = b64encoded_tarball.decode()
    )
    return script.encode('utf8')


#
# main
#
if __name__ == '__main__':
  from context_logger import initialize_logging, ContextLogger

  initialize_logging(LogLevel.debug, {})
  logger = ContextLogger()

  self_extractor = SelfExtractor("./templates", "install.sh.j2")

  d3 = self_extractor.generate('./vmfs')

  def cb_print(result):
    print( result.decode() )

  d3.addCallbacks(cb_print, eb_crash)
  d3.addCallback(cb_exit)

  reactor.run()
