
import pytest
import pytest_twisted

from twisted.internet import defer

from tk.utility_service import UtilityService
from tk.pipe_factory import PipeFactory

@pytest.fixture
def encoded_tarball():
  """
  Reduce a directory to an encoded tarball
  """
  def _encoded_tarball(fsid):
    us  = UtilityService(None)
    d   = us.getSelfExtractor(fsid, "./tests/templates", "encoded_tarball.j2")
    return d
    
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
def test_self_extractor(encoded_tarball, testdir, md5sum_pipe, foo_hash):
  d : defer.Deferred  = encoded_tarball(testdir)
  d.addCallback( md5sum_pipe.run )

  assert (yield d) == foo_hash

