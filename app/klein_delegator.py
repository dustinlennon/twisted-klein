from zope.interface import implementer
from twisted.web import resource, server
from klein import Klein

import klein_mixins as mixins

#
# KleinDelegator
#   - delegate Resource methods to klein instance
#
@implementer(resource.IResource)
class KleinDelegator(mixins.KBase):
  app : Klein

  def getChildWithDefault(self, name, request):
    return self.app.resource().getChildWithDefault(name, request)

  def putChild(self, path: bytes, child: "resource.IResource") -> None:
    self.app.resource().putChild(path, child)

  def render(self, request : server.Request):
    self.logger.info("{request}", request = request)
    return self.app.resource().render(request)

