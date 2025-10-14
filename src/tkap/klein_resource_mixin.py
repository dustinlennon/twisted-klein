from zope.interface import implementer
from twisted.web import resource, server
from klein import Klein

#
# KleinResourceMixin
#
@implementer(resource.IResource)
class KleinResourceMixin(object):
  app : Klein

  def getChildWithDefault(self, name, request):
    return self.app.resource().getChildWithDefault(name, request)

  def putChild(self, path: bytes, child: "resource.IResource") -> None:
    self.app.resource().putChild(path, child)

  def render(self, request : server.Request):
    return self.app.resource().render(request)

