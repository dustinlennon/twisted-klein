# twisted-klein-and-pipes



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
