import pytest
import pytest_twisted

from tkap.errors import UnknownFsidError
from tkap.cloudconf.mapper import KeyMapper

@pytest.fixture
def mapper():
  def _mapper(fsmap, fsid):
    km = KeyMapper(fsmap)
    return km.map(fsid)
  return _mapper

@pytest_twisted.inlineCallbacks
def test_mapper(mapper, foo_path):
  mapped = yield mapper({'foo':foo_path}, 'foo')
  assert mapped == foo_path

@pytest_twisted.inlineCallbacks
def test_passthrough(mapper, foo_path):
  mapped = yield mapper(None, foo_path)
  assert mapped == foo_path

@pytest_twisted.inlineCallbacks
def test_keyerror(mapper):
  with pytest.raises(UnknownFsidError):
    yield mapper({}, 'bar')

