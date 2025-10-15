class UnknownFsidError(FileNotFoundError):
  pass

class SshKeyValueError(Exception):
  pass

class ProcessError(RuntimeError):
  pass