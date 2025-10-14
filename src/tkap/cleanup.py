from zope.interface import implementer, Interface

#
# ICleaner
#
class ICleanup(Interface):
  def cleanup(self):
    pass  

#
# ICleanupContext
#
class ICleanupContext(Interface):
  def __enter__(self):
    pass

  def __exit__(self, exc_type, exc_value, tb):
    pass


#
# Adapter from ICleanup 
#           to ICleanupContext
#
@implementer(ICleanupContext)
class CleanupContextFromCleaner(object):
  def __init__(self, cleaner : ICleanup):
    self.cleaner = cleaner

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, tb):
    self.cleaner.cleanup()
