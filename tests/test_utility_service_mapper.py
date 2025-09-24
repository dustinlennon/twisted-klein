import pytest
import pytest_twisted

from tk.utility_service import UtilityService

@pytest.fixture
def mapper():
  def _mapper(fsmap, fsid):
    us = UtilityService(fsmap)
    return us.map(fsid)
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
  with pytest.raises(KeyError):
    yield mapper({}, 'bar')

