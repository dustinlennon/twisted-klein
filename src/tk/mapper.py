import os
from pathlib import Path
import shutil
from typing import Optional

from twisted.internet import defer

from tk.context_logger import ContextLogger
from tk.errors import UnknownFsidError


#
# BaseMapper
#
class BaseMapper(object):
  def mapper(self) -> defer.Deferred:
    raise NotImplementedError("implement 'mapper' method in subclass")

#
# KeyMapper
#   - fsid is keyed to a user specified path
#
class KeyMapper(BaseMapper):
  logger = ContextLogger()

  def __init__(self, fsmap : Optional[dict] = None):
    self.fsmap = fsmap

  def mapper(self, fsid) -> defer.Deferred:
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

  def validate_args(self, fsmap, root):
    new_root = Path(root).resolve()
    new_root.mkdir(parents = True, exist_ok=True)
    new_root.chmod(0o777)

    if fsmap is None:
      self.fsmap = None
      return

    elif not isinstance(fsmap, dict):
      raise ValueError("if specified, fsmap must be a dict")
    
    for k, d in fsmap.items():
      p = Path(d).resolve()
      if not p.is_dir():
        raise ValueError(f"'{d}' is not a valid directory path")
      
    new_fsmap = dict()
    for k, d in fsmap.items():
      src = Path(d).resolve()
      dst = new_root / src.stem
      new_location = self._install(src, dst)
      new_fsmap[k] = new_location

    self.fsmap  = new_fsmap
    self.root   = new_root

  def _install(self, src : Path, dst : Path):
    self.logger.info("installing {src} to {dst}", src = src, dst = dst)
    new_location = shutil.copytree(src, dst)

    dst.chmod(0o777)
    for root, dirs, files in dst.walk():
      for d in dirs:
        (root / Path(d)).chmod(0o777)
      for f in files:
        (root / Path(f)).chmod(0o777)

    return new_location
   
  def cleanup(self):
    for pth in self.fsmap.values():
      self.logger.info("removing {pth}", pth = pth)
      shutil.rmtree(pth)
