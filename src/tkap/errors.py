class UnknownFsidError(FileNotFoundError):
  pass

class ProcessError(RuntimeError):
  pass

class CloudconfServiceError(Exception):
  pass

class CloudConfigKeyError(CloudconfServiceError):
  pass

class SshKeyError(CloudconfServiceError):
  pass
