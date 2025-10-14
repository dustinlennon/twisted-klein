import pytest
import pytest_twisted

from tkap.directory_hash import DirectoryHash

@pytest.fixture(params=['md5', 'sha256'])
def hash_factory(request):
  def _hash_factory(fsid):
    dh      = DirectoryHash()
    hasher  = getattr(dh, request.param)
    return (request.param, hasher(fsid))

  return _hash_factory

@pytest_twisted.inlineCallbacks
def test_hash_match(hash_factory, known_hashes, foo_path):
  method_name, d = hash_factory( foo_path )
  assert (yield d) == known_hashes[method_name]

@pytest_twisted.inlineCallbacks
def test_elsewhere(hash_factory, testdir, known_hashes):
  method_name, d = hash_factory(testdir)
  assert (yield d) == known_hashes[method_name]

@pytest_twisted.inlineCallbacks
def test_filenotfound(hash_factory):
  with pytest.raises(FileNotFoundError):
    yield hash_factory('bar')[1]

