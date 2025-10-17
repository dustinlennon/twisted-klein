class UnknownFsidError(FileNotFoundError):
  pass

class SshKeyValueError(Exception):
  pass

class ProcessError(RuntimeError):
  pass

class CloudconfServiceError(Exception):
  pass

class CloudConfigKeyError(CloudconfServiceError):
  pass

class SshKeyError(CloudconfServiceError):
  pass
