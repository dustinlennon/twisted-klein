import sys
import os

from typing import Optional, Any

from twisted.logger import (
  FileLogObserver,
  FilteringLogObserver,
  globalLogBeginner,
  globalLogPublisher,
  ILogObserver,
  Logger,
  LogLevelFilterPredicate,
  LogLevel
)

from twisted.python.compat import currentframe

from tkap.formatter import formatEvent

#
# Initialize logging
#

def initialize_logging(
    default_loglevel : LogLevel,
    ns_map : dict,
    running_as_script = False
  ) -> ILogObserver:

  filter = LogLevelFilterPredicate(default_loglevel)
  for ns,level in ns_map.items():
    filter.setLogLevelForNamespace(ns, level)
  
  observer = FilteringLogObserver(
    FileLogObserver(sys.stdout, formatEvent),
    [ filter ]
  )
  
  if running_as_script:
    globalLogBeginner.beginLoggingTo([], redirectStandardIO = False)
  
  globalLogPublisher.addObserver(observer)

  return observer


#
# ContextLogger
#

class ContextLogger(Logger):

  def debug(self, format: Optional[str] = None, _depth = 2, **kwargs: object) -> None:
    self.emit(LogLevel.debug, format, _depth = _depth, **kwargs)

  def info(self, format: Optional[str] = None, _depth = 2, **kwargs: object) -> None:
    self.emit(LogLevel.info, format, _depth = _depth, **kwargs)

  def warn(self, format: Optional[str] = None, _depth = 2, **kwargs: object) -> None:
    self.emit(LogLevel.warn, format, _depth = _depth, **kwargs)

  def error(self, format: Optional[str] = None, _depth = 2, **kwargs: object) -> None:
    self.emit(LogLevel.error, format, _depth = _depth, **kwargs)

  def critical(self, format: Optional[str] = None, _depth = 2, **kwargs: object) -> None:
    self.emit(LogLevel.critical, format, _depth = _depth, **kwargs)


  def emit(
    self, level: LogLevel, format: Optional[str] = None, *, _depth, **kwargs: object
  ) -> None:
    if level < LogLevel.info:
      kwargs['log_frame'] = currentframe(_depth)
      kwargs['log_cwd']   = os.getcwd()

    try:
      super().emit(level, format, **kwargs)
    finally:
      kwargs.pop('log_frame', None)
