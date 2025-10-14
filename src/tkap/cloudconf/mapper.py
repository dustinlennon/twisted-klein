import os
from pathlib import Path
from pwd import getpwnam, struct_passwd
import shutil
from typing import Optional

from twisted.internet import defer

from tkap.context_logger import ContextLogger
from tkap.errors import UnknownFsidError


#
# KeyMapper
#   - fsid is keyed to a user specified path
#
class KeyMapper(object):
  logger = ContextLogger()

  def __init__(self, fsmap : Optional[dict] = None):
    super().__init__()
    self.fsmap = fsmap

  def map(self, fsid) -> defer.Deferred:
    try:
      dirname = self.fsmap[fsid]

    except TypeError:
      d = defer.succeed(fsid)

    except KeyError as e:
      exc = UnknownFsidError(fsid)
      exc.__cause__ = e
      self.logger.error("UtilityService.map: {e}", e = repr(exc))
      raise exc

    else:
      d = defer.succeed(dirname)

    return d

#
# RelocatedMixin
#
class RelocatedMixin(object):
  logger : ContextLogger

  def relocate(self, fsmap):
    new_root = Path("/run/tkap")

    if fsmap is None:
      return None

    elif not isinstance(fsmap, dict):
      raise ValueError("if specified, fsmap must be a dict")
    
    for k, d in fsmap.items():
      p = Path(d).resolve()
      if not p.is_dir():
        raise ValueError(f"'{d}' is not a valid directory path")
      
    pw = getpwnam("tkap")
    uid = pw.pw_uid
    gid = pw.pw_gid

    new_fsmap = dict()
    for k, d in fsmap.items():
      src = Path(d).resolve()
      dst = new_root / src.stem
      new_location = self._install(src, dst, uid, gid)
      new_fsmap[k] = new_location

    return new_fsmap

  def _install(self, src : Path, dst : Path, uid, gid):
    self.logger.info("installing {src} to {dst}", src = src, dst = dst)
    new_location = shutil.copytree(src, dst)

    os.chown(dst, uid, gid)
    for root, dirs, files in dst.walk():
      for d in dirs:
        os.chown(root / Path(d), uid, gid)

      for f in files:
        os.chown(root / Path(f), uid, gid)

    return new_location
   