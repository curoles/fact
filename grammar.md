```
is:
  type: <type> # [str, num]
  value: <val>

is:
  type: <type>
  as: <supertype>
  value:
    <attr>:
      type: <type>
      value: <val>
```

```
has:
  <attr>:
    type: <type> # [str,num,list] | custom_type
    value: <val>

has:
  <attr>:
    type: <type> # custom_type
    as: <supertype>
    value: <val>

has:
  <attr>: <yaml_val>
  # type is deduced

has
```
