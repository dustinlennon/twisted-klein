# twisted-klein-and-pipes


Components: Hello World
----

Start with an interface,

```python
class IHello(Interface):
  def hello(self) -> str:
    pass
```

Next, create an adapter.  `twisted-klein-and-pipes` provides two base classes to facilitate this, a "netcat" adapter and a Klein HTTP adapter.

### netcat adapter

The "netcat" adapter creates an `IProtocolFactory` from an `IHello` interface using the `NetcatServerFactory` base class.  For our purposes, this takes the form:

```python
@implementer(IProtocolFactory)
class NetcatFactoryFromIHello(NetcatServerFactory):
  def __init__(self, delegate : IHello):
    self.delegate = delegate

  def cmd_hello(self, to_whom = None) -> defer.Deferred:
    response = self.delegate.hello(to_whom)
    return defer.succeed( response.encode("utf8") )
```

A client call might take the form `echo "hello world" | nc -C localhost 8120`, and this would map to the `cmd_hello` function with `to_whom` populated by "world".

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

A client call might take the form `curl -L -s http://localhost:8122/hello` or `curl -L -s http://localhost:8122/hello/world`.  The former redirects into `hello_unknown`; the latter, without redirection, into `hello`.

### register adapters

The component model requires adapters to be registered.  This happens as:

```python
components.registerAdapter(NetcatFactoryFromIHello, IHello, IProtocolFactory)
components.registerAdapter(ResourceFromIHello, IHello, IResource)
```

### A Concrete Implementation

To provide functionality, we need at least one concrete implementation of `IHello` from which to instantiate a component.  

```python
@implementer(IHello)
class ConcreteHello(object):
  def __init__(self, whoami):
    self.whoami = whoami

  def hello(self, to_whom) -> str:
    if to_whom is None:
      msg = f"Hello, I'm {self.whoami}.\n"

    elif to_whom == self.whoami:
      msg = "Thanks!\n"

    else:
      msg = f"I'm not {to_whom}.\n"

    return msg
```


### `main`

The `main` block need only do a few things.  For example, the below code initializes twisted logging; creates an `adaptable` component; starts netcat and HTTP endpoints.  Finally, it starts the reactor.

```python
def main():
  # initialize logging
  observers = [ 
    FileLogObserver(sys.stdout, formatEventAsClassicLogText)
  ]
  globalLogBeginner.beginLoggingTo( observers )

  # Create an adaptable component
  adaptable = ConcreteHello("world")

  # set up a "netcat" endpoint
  endpoint = endpoints.serverFromString(reactor, "tcp:8120")
  endpoint.listen( IProtocolFactory(adaptable) )

  # set up an HTTP endpoint
  site = server.Site( IResource(adaptable) )
  endpoint = endpoints.serverFromString(reactor, "tcp:8122")
  endpoint.listen( site )
  
  reactor.run()


if __name__ == '__main__':
  main()
```

From the components perspective, the interesting bit is that calls to the `NetcatFactoryFromIHello` and `ResourceFromIHello` adapters are implicit.  In particular, the code that defines the adaptable component functionality is well-separated from the network code.

See [src/tkap/resources/examples/hello_world.py](src/tkap/resources/examples/hello_world.py) for the full code.


Cloudconf Servers
----

Each of the following Cloudconf invocations provides a different execution context which we demonstrate subsequently.


### script

To start, there's a variant configured to run as the active user from a python script.

```bash
pipenv run python3 src/tkap/resources/examples/cloudconf.py
```

```
$ echo "env_pwd" | nc -C localhost 8121
/home/dnlennon/Workspace/Sandbox/twisted-klein

$ echo "env_id" | nc -C localhost 8121
uid=1000(dnlennon) gid=1000(dnlennon) groups=1000(dnlennon),...
```

### twistd

For a more productionalized approach, there's a twistd variant that drops privileges after launching.  In order to enjoy these features, there is an installer that creates a `tkap` user/group as well as the `/run/tkap` and `/var/lib/tkap` directories owned by `tkap`.

```bash
sudo -E pipenv run installer --install
```

To enable HTTPS connections, host certificates signed by a trusted site CA are be required.  The `cert.sh` script can be used to generate these; or, use ones of your choosing.  Configuration is via `.env.tkap`.

```bash
$(pipenv run installer)/resources/scripts/cert.sh
```

Now, invoking twistd:

```bash
sudo -E pipenv run twistd -ny src/tkap/resources/examples/tkap.tac
```

Now, the reported active user/group is `tkap:tkap`.

```
$ echo "env_id" | nc -C localhost 8121
uid=137(tkap) gid=144(tkap) groups=144(tkap)
```


### systemd

Finally, there's a systemd service.  

```bash
sudo -E pipenv run installer --install
src/tkap/resources/scripts/service-install.sh .tkap-service
sudo systemctl enable src/tkap/resources/examples/tkap.service
sudo systemctl start tkap.service
```

The environmental context is

```
$ echo "env_pwd" | nc -C localhost 8121
/run/tkap

$ echo "env_id" | nc -C localhost 8121
uid=137(tkap) gid=144(tkap) groups=144(tkap)
```

#### uninstall systemd

```bash
sudo systemctl stop tkap.service
sudo systemctl disable tkap.service
sudo -E pipenv run installer --uninstall
```