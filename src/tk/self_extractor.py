import os
import jinja2

from twisted.internet import defer, reactor
from twisted.logger import LogLevel

from tk.callbacks import (
  cb_exit,
  cb_log_result,
  eb_crash
)

from tk.pipe_factory import PipeFactory

class SelfExtractor(object):
  cmds = [
    """ /usr/bin/tar -C {basedir} --sort=name --owner=0 --group=0 --mtime='1970-01-01' -cz . """,
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
  import argparse
  import sys
  
  parser = argparse.ArgumentParser()
  parser.add_argument("script_id", type=int)
  args = parser.parse_args()

  if args.script_id == 0:
    path = "./tests/data/foo"
  elif args.script_id == 1:
    path = "/tmp/pytest-of-dnlennon/pytest-93/test_elsewhere0"
  else:
    print(args.script_id)
    sys.exit(1)

  self_extractor = SelfExtractor("./tests/templates", "encoded_tarball.j2")
  d1 = self_extractor.generate(path)

  def cb_print(result):
    sys.stdout.write( result.decode() )

  d1.addCallbacks(cb_print, eb_crash)
  d1.addCallback(cb_exit)

  reactor.run()
