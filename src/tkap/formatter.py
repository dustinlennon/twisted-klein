from constantly import NamedConstant

import re
import inspect
import traceback

from typing import cast, Optional
from types import FrameType

from twisted.logger import LogEvent

from twisted.logger._format import(
  _formatEvent,
  _formatTraceback,
  formatTime
)

#
# Enable custom formatting
#

def eventAsText(
    event: LogEvent,
  ) -> str:
    eventText = _formatEvent(event)
    if "log_failure" in event:      
      f   = event["log_failure"]
      tbstr  = _formatTraceback(f)
      eventText = "\n".join((eventText, tbstr))

    if not eventText:      
      return eventText

    timeStamp = "".join([formatTime(cast(float, event.get("log_time", None))), " "])
    
    namespace = event.get("log_namespace")
    level     = cast(Optional[NamedConstant], event.get("log_level", None))
    context   = namespace

    frame : FrameType = event.get('log_frame')
    if frame:
      try:
        argobj    = inspect.getargvalues(frame)
        arglist   = [ ", ".join(l) for l in argobj[:3] if l is not None ]
        signature = ", ".join(arglist)
        
        qualname  = frame.f_code.co_qualname
        lineno    = frame.f_lineno

        cwd       = event.get('log_cwd')
        filename  = re.sub(cwd, ".", frame.f_code.co_filename)
        context = f"\n# {qualname}({signature}) [{filename}:{lineno}]\n"

      except Exception as e:
        print(">>>", traceback.format_exc())

    logmsg = "{timeStamp} | {level:<6} | {eventText} | {context}".format(
      timeStamp = timeStamp,
      level = level.name,
      eventText = eventText,
      context = context
    )


    return logmsg

def formatEvent(event : LogEvent):
  eventText = eventAsText(event)
  if not eventText:
      return None
  eventText = eventText.replace("\n", "\n\t")
  return eventText + "\n"

