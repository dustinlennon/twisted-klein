
from functools import wraps
import inspect
from typing import Callable, Optional

from twisted.logger import LogLevel
from iso.context_logger import ContextLogger

def getargs(f : Callable) -> str:
  sig     = inspect.signature(f)
  params  = [ p.replace(annotation = inspect._empty) for p in sig.parameters.values() ]
  free_sig = sig.replace(parameters = params, return_annotation = inspect._empty)
  return str(free_sig)

#
# settrace helper function
#
def settrace(cls : type, key : str, func : Callable):
  name    = f"{cls.__name__}.{key}"
  depth   = 3
  fargs   = getargs(func)

  @wraps(func)
  def wrapper(*args, **kw):
    cls.logger.debug("<BEGIN: {name}{fargs}>", _depth = depth, name = name, fargs = fargs)
    v = func(*args, **kw)
    cls.logger.debug("<END: {name}>", _depth = depth, name = name)
    return v
  return wrapper

#
# Tracer
#   - injects a ContextLogger into a class hierarchy
#   - verbosity is inherited from nearest ancestor that specified a non-null value
#
class Tracer(object):
  verb_state = dict()

  def __init_subclass__(cls, verbose : Optional[bool] = None, **kwargs):
    super().__init_subclass__(**kwargs)
    
    cls.logger  = ContextLogger(namespace = cls.__qualname__)

    if verbose is not None:
      Tracer.verb_state.setdefault(cls.__qualname__, verbose)

    for T in cls.__mro__:
      if T.__qualname__ in Tracer.verb_state:
        verbose = Tracer.verb_state[T.__qualname__]
        break
    
    if verbose:
      for key in cls.__dict__.keys():
        attr = getattr(cls, key)

        if callable(attr):
          setattr(cls, key, settrace(cls, key, attr))

#
#  Some sandbox testing
#
if __name__ == '__main__':

  from iso.context_logger import initialize_logging

  initialize_logging(LogLevel.debug, {})

  class D1(Tracer):
    def im(self):
      pass

    @classmethod
    def cm(self):
      pass
  
  class D2(D1, verbose = True):
    def im(self, i):
      pass

  class D3(D2):
    def im(self, i : int):
      pass

  D1.cm()
  D1().im()  
  
  D2().im(2)
  D3().im(3)
