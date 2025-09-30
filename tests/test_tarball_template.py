
import jinja2

import pytest
import pytest_twisted

from twisted.internet import defer

from tkap.pipe_factory import PipeFactory
from tkap.tarball_template import TarballTemplate

@pytest.fixture
def encoded_tarball():
  def _encoded_tarball(fsid):
    return TarballTemplate.from_raw("{{ b64encoded_tarball }}").generate(fsid)
     
  return _encoded_tarball

@pytest.fixture
def md5sum_pipe():
  return PipeFactory( ["/usr/bin/md5sum"] )

@pytest.fixture
def foo_encoded():
  with open("./tests/data/foo_encoded", "rb") as f:
    data = f.read()
  return data  

@pytest.fixture
def foo_hash(foo_encoded, md5sum_pipe):
  d = defer.succeed(foo_encoded)
  d.addCallback( md5sum_pipe.run )
  return pytest_twisted.blockon(d)

@pytest_twisted.inlineCallbacks
def test_tarball_template(encoded_tarball, testdir, md5sum_pipe, foo_hash):
  d = encoded_tarball(testdir)
  d.addCallback( md5sum_pipe.run )
  assert (yield d) == foo_hash
