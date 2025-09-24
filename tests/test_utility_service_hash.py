import pytest
import pytest_twisted

from tk.utility_service import UtilityService

@pytest.fixture(params=['getDirectoryHashMD5', 'getDirectoryHashSHA256'])
def hash_factory(request):
  def _hash_factory(fsmap, fsid):
    us      = UtilityService(fsmap)
    hasher  = getattr(us, request.param)
    return (request.param, hasher(fsid))

  return _hash_factory

@pytest_twisted.inlineCallbacks
def test_hash_match(hash_factory, known_hashes):
  method_name, d = hash_factory(None, './tests/data/foo')
  assert (yield d) == known_hashes[method_name]

@pytest_twisted.inlineCallbacks
def test_elsewhere(hash_factory, testdir, known_hashes):
  method_name, d = hash_factory(None, testdir)
  assert (yield d) == known_hashes[method_name]

@pytest_twisted.inlineCallbacks
def test_filenotfound(hash_factory):
  with pytest.raises(FileNotFoundError):
    yield hash_factory(None, 'bar')[1]

