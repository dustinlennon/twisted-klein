import jinja2
import os

from twisted.internet import defer, reactor
from twisted.logger import LogLevel

from tkap.pipe_factory import PipeFactory

class SelfExtractor(object):
  cmds = [
    """ /usr/bin/tar -C {basedir} --sort=name --owner=0 --group=0 --mtime='1970-01-01' -cz . """,
    """ /usr/bin/base64 - """
  ]

  def __init__(self, template):
    self.template = template

  @classmethod
  def from_raw(cls, template):
    return cls(jinja2.Template(template))

  @classmethod
  def from_filesystem(cls, template_directory, template_name):
    env = jinja2.Environment(
      loader = jinja2.FileSystemLoader(template_directory)
    )
    template = env.get_template(template_name)
    return cls(template)
  
  @classmethod
  def from_package(cls, template_name):
    env = jinja2.Environment(
      loader = jinja2.PackageLoader("tkap", "resources/templates")
    )  
    template = env.get_template(template_name)
    return cls(template)

  def generate(self, basedir) -> defer.Deferred:
    if os.path.isdir(basedir) == False:
      raise FileNotFoundError(f"'{basedir}' is not a directory.")
    
    kw = dict(basedir = basedir)
    cmds = [ cmd.format(**kw) for cmd in self.cmds ]

    d = PipeFactory(cmds).run()
    d.addCallback(self.render)
    return d
  
  def render(self, b64encoded_tarball):
    script = self.template.render(
      b64encoded_tarball = b64encoded_tarball.decode()
    )
    return script.encode('utf8')


#
# main
#
if __name__ == '__main__':
  import jinja2
  from tkap.callbacks import (
    cb_log_result,
    cb_exit
  )
  from tkap.context_logger import initialize_logging, ContextLogger

  initialize_logging(LogLevel.debug, {})
  logger = ContextLogger()

  self_extractor = SelfExtractor.from_raw( "{{ b64encoded_tarball }}" )
  d1 = self_extractor.generate("./tests/data/foo")

  d1.addCallback(cb_log_result, "{result}")
  d1.addBoth(cb_exit)

  reactor.run()
