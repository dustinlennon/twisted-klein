import os
import tempfile
import pytest


# replicate ./tests/data/foo
@pytest.fixture
def testdir(tmp_path):  
  with open(tmp_path / "message_one", "w") as f:
    f.write("hello")

  with open(tmp_path / "message_two", "w") as f:
    f.write("bye")

  return str(tmp_path)

@pytest.fixture
def known_hashes():
  return {
    'getDirectoryHashMD5'     : b'b3786fdb6e871f8c4cb37af71d14d526  -',
    'getDirectoryHashSHA256'  : b'28225736377a687f4a37413acc99f2a9f9694402255d633ba3d4dac6e17ceb5a  -'
  }
