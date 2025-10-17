import argparse
from importlib import resources
import os
from pwd import getpwuid
import shlex
import subprocess
import sys

#
# parser
#
parser = argparse.ArgumentParser()
parser.add_argument("--install", action="store_true")
parser.add_argument("--uninstall", action="store_true")

#
# Installer
#
class Installer(object):

  @property
  def path(self):
    return resources.files("tkap")

  def install(self):
    self._validate_user()
    self._add_user()
    self._install_dirs()

  def uninstall(self):
    self._validate_user()
    self._del_user()
    self._rm_resources()

  def _validate_user(self):
    pw_caller = getpwuid( os.getuid() )
    if pw_caller.pw_name != "root":
      raise RuntimeError("Installer must run as 'root'.")

  def _add_user(self,):
    cmd = shlex.split("/usr/sbin/adduser --quiet --system --group tkap")
    subprocess.run(cmd, check = True)

  def _del_user(self,):
    cmd = shlex.split("/usr/sbin/deluser --quiet --system tkap")
    subprocess.run(cmd, check = True)

  def _install_dirs(self,):
    cmd = shlex.split("/usr/bin/install --owner=tkap --group=tkap -d /var/lib/tkap /run/tkap")
    subprocess.run(cmd, check = True)

  def _rm_resources(self):
    cmd = shlex.split("rm -rf /var/lib/tkap /run/tkap")
    subprocess.run(cmd, check = True)


#
# cli
#
def cli():
  installer = Installer()
  args = parser.parse_args()

  if args.install:
    installer.install()

  elif args.uninstall:
    installer.uninstall()

  else:
    print(installer.path)


if __name__ == "__main__":
  sys.exit(cli())
