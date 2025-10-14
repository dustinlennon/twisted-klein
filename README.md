# twisted-klein-and-pipes


Quick start: Hello World
----

Start with an interface,

```python
class IHello(Interface):
  def hello(self) -> str:
    pass
```

and a concrete implementation:

```python
@implementer(IHello)
class ConcreteHello(object):
  def __init__(self, whoami):
    self.whoami = whoami

  def hello(self, to_whom):
    if to_whom is None:
      msg = f"Hello, I'm {self.whoami}.\n"

    elif to_whom == self.whoami:
      msg = "Thanks!\n"

    else:
      msg = f"I'm not {to_whom}.\n"

    return msg
```

Next, we'll create an adapter.  `twisted-klein-and-pipes` provides two base classes to facilitate this, a "netcat" adapter and a Klein HTTP adapter.

### netcat adapter

The "netcat" adapter creates an `IProtocolFactory` from an `IHello` interface using the `NetcatRequestFactory` base class.  In our example, this takes the form:

```python
@implementer(IProtocolFactory)
class NetcatFactoryFromIHello(NetcatRequestFactory):
  def __init__(self, obj : IHello):
    self.obj = obj

  def cmd_hello(self, to_whom = None) -> defer.Deferred:
    response = self.obj.hello(to_whom)
    return defer.succeed( response.encode("utf8") )
```

A client API might take the form `echo "hello world" | nc -C localhost 8120`, and this would map to the `cmd_hello` function with `to_whom` populated by "world".

### Klein HTTP adapter

The Klein HTTP adapter creates an `IResource` from an `IHello` interface using the `KleinDelegator` base class.  In our example this takes the form:

```python
@implementer(IResource)
class ResourceFromIHello(KleinResourceMixin):
  app     = Klein()
  isLeaf  = True

  def __init__(self, delegate : IHello):
    self.delegate = delegate

  @app.route("/hello/<to_whom>")
  def hello(self, request: server.Request, to_whom):
    return self.delegate.hello(to_whom)

  @app.route("/hello/")
  def hello_unknown(self, request: server.Request):
    return self.hello(request, None)
```

A client API might take the form `curl -L -s http://localhost:8122/hello` or `curl -L -s http://localhost:8122/hello/world`.  The former redirects into `hello_unknown`; the latter, without redirection, into `hello`.

### register adapters

The component model requires adapters to be registered.  This happens as:

```python
components.registerAdapter(NetcatFactoryFromIHello, IHello, IProtocolFactory)
components.registerAdapter(ResourceFromIHello, IHello, IResource)
```


### `main`

A `main` code need only do a few things.  For example, the below code initializes twisted logging; creates an object that implements the IHello interfaces; starts a netcat endpoint; starts an HTTP endpoint; and runs the reactor:

```python
def main():
  # initialize logging
  observers = [ 
    FileLogObserver(sys.stdout, formatEventAsClassicLogText)
  ]
  globalLogBeginner.beginLoggingTo( observers )

  # Create an object that implements the IHello interface
  hello = ConcreteHello("world")

  # a "netcat" endpoint
  endpoint = endpoints.serverFromString(reactor, "tcp:8120")
  endpoint.listen( IProtocolFactory(hello) )

  # an HTTP endpoint
  site = server.Site( IResource(hello) )
  endpoint = endpoints.serverFromString(reactor, "tcp:8122")
  endpoint.listen( site )
  
  reactor.run()


if __name__ == '__main__':
  main()
```

From the components perspective, the interesting bit is the implicit casting:

```python
endpoint.listen( IProtocolFactory(hello) )
```

and 

```python
site = server.Site( IResource(hello) )
```

See [src/tkap/resources/examples/hello_world.py](src/tkap/resources/examples/hello_world.py) for the full code.


Servers
----

To start, there's a test server, configured to run as the active user from a python script.  For a more productionalized approach, there's also a twistd variant that creates a "tkap" user/group; creates /run/tkap and /var/lib/tkap, owned by tkap; copies resources into /var/lib/tkap; and drops privileges to tkap after launching.


### test server

```bash
pipenv run test_server
```

### twistd server

```bash
sudo -E pipenv run installer --install
sudo -E pipenv run twistd -ny /var/lib/tkap/resources/examples/server.tac
```

### systemd

```bash
sudo -E pipenv run installer --install
sudo systemctl enable /var/lib/tkap/resources/examples/tkap.service
sudo systemctl start tkap.service
```
