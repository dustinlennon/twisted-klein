import uuid

def dig_trim(value : bytes | None, alt : str):
  if value:
    result = value.decode().rstrip("\n.")
  else:
    result = alt
  return result

def from_path(path : str):
  with open(path) as f:
    content = f.read()
  return content

def instance_id():
  return uuid.uuid4()
