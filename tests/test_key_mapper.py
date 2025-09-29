import pytest
import pytest_twisted

from tk.errors import UnknownFsidError
from tk.mapper import KeyMapper

@pytest.fixture
def mapper():
  def _mapper(fsmap, fsid):
    km = KeyMapper(fsmap)
    return km.mapper(fsid)
  return _mapper

@pytest_twisted.inlineCallbacks
def test_mapper(mapper):
  mapped = yield mapper({'foo':'./tests/data/foo'}, 'foo')
  assert mapped == "./tests/data/foo"

@pytest_twisted.inlineCallbacks
def test_passthrough(mapper):
  mapped = yield mapper(None, './tests/data/foo')
  assert mapped == "./tests/data/foo"

@pytest_twisted.inlineCallbacks
def test_keyerror(mapper):
  with pytest.raises(UnknownFsidError):
    yield mapper({}, 'bar')

