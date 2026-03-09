```
yaml types are basic types: num, str, list
str type is root abstract type
```

```
# abstract type
- is: <yaml_type>

- is:
    type: <type> # str, num, list or custom
    value: <val>

- is:
    type: astronomy/star
    as:
      - astronomomy/object:
          mass:
            value: 1.989e30
```

```
- has:
    <attr>:
      type: <type> # [str,num,list] | custom_type
      value: <val>

# example
- has:
    mass:
      type: num


- has:
    <attr>:
      type: <type> # custom_type
        as: <supertype>
        value: <val>

- has:
    <attr>: <yaml_val>
    # type is deduced

```
