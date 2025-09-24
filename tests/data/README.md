
`tar` is fussy about non-file properties, e.g. owner, group, permissions, timestamps.  
To address this, create a compressed tarball in a known state:

```bash
tar -C foo --sort=name --owner=0 --group=0 --mtime='1970-01-01' -c . \
  | gzip -n \
  | base64 \
  > foo_encoded
```
