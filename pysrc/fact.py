import logging
from kg import KgIface
from typing import Dict
from fact_decorator import fact

log = logging.getLogger(__name__)

@fact("app/org/igorlesik/fact/pysrc/fact_module")
class Fact:
    """Element of knowledge"""

    def __init__(self, kg: KgIface, fact_name: str):
        self.kg = kg
        self.name = fact_name

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_construct")
    def construct(self) -> int:
        """Construct fact, create fields"""

        if self.name not in self.kg.get_dict():
            log.error("can not find %s in KG", self.name)
            return 1

        self.data = self.kg.get_fact(self.name)

        if "def" not in self.data:
            return 0

        self.data["info"] = {}

        result = self.construct_what_it_is()
        if result != 0:
            return result

        result = self.construct_what_it_has()
        if result != 0:
            return result

        result = self.construct_what_it_part()
        if result != 0:
            return result

        log.info("%s constructed: %s", self.name, self.data['info'])

        # free parsed YAML tags, only constructed "info" is needed from now on
        del self.data["def"]

        return 0

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_construct_what_it_is")
    def construct_what_it_is(self) -> int:
        """Check 'is' tags"""

        self.data["info"]["type"] = []
        self.data["info"]["val_as"] = {}

        for tag in self.data["def"]:
            if "is" in tag:
                log.debug("is tag: %s", tag)
                if 0 != self.construct_tag_is(tag):
                    return 1

        return 0

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_construct_tag_is")
    def construct_tag_is(self, tag: dict) -> int:
        """Construct what fact is"""

        data = tag["is"]
        log.debug("is data: %s", data)

        fact_types = self.data["info"]["type"]

        ret_status = 0

        match data:
            case str():
                log.debug("fact is 'str' type")
                fact_types.append("str")
            case dict():
                log.debug("fact is 'dict' type")
                ret_status = self.parse_construct_tag_is_dict(data)
            case _:
                log.error("unknown type of %s", data)
                return 1

        return ret_status

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_parse_construct_tag_is_dict")
    def parse_construct_tag_is_dict(self, info: dict) -> int:
        """Construct phase parse is dict"""

        if "type" not in info:
            log.error("no 'type' in %s", info)
            return 1

        fact_types = self.data["info"]["type"]
        info_type = info["type"]

        match info_type:
            case "str":
                fact_types.append("str")
            case "num":
                fact_types.append("num")
            case _:
                if self.kg.load(info_type) != 0:
                    log.error("can't load fact '%s'", info_type)
                    return 2
                fact_types.append(info_type)

        if "as" in info:
            for as_type in info["as"]:
                err, type_name, as_type_val = self.parse_construct_tag_is_as_type(as_type)
                if err != 0:
                    log.error("can't parse '%s'", as_type)
                    return 3
                self.data["info"]["val_as"][type_name] = as_type_val

        return 0

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_parse_construct_tag_is_as_type")
    def parse_construct_tag_is_as_type(self, as_type: dict) -> tuple[int, str, dict]:
        log.debug("as type %s", as_type)
        err = 0
        as_type_val = {}
        type_name = next(iter(as_type))

        attrs = as_type[type_name]
        for attr_name in attrs:
            attr_data = attrs[attr_name]
            if "value" in attr_data:
                as_type_val[attr_name] = attr_data["value"]
            elif "as" in attr_data:
                nested = {}
                for nested_as in attr_data["as"]:
                    nested_err, nested_type, nested_vals = self.parse_construct_tag_is_as_type(nested_as)
                    if nested_err != 0:
                        return (nested_err, type_name, {})
                    nested.update(nested_vals)
                as_type_val[attr_name] = nested

        return (err, type_name, as_type_val)

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_construct_what_it_part")
    def construct_what_it_part(self) -> int:
        """Check 'part' tags"""

        self.data["info"]["part"] = []

        for tag in self.data["def"]:
            if "part" in tag:
                log.debug("part tag: %s", tag)
                if 0 != self.construct_tag_part(tag):
                    return 1

        return 0

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_construct_tag_part")
    def construct_tag_part(self, tag: dict) -> int:
        """Construct what fact belongs to"""

        data = tag["part"]
        log.debug("part data: %s", data)

        fact_owners = self.data["info"]["part"]

        ret_status = 0

        match data:
            case str():
                log.debug("fact belongs to '%s'", data)
                if self.kg.load(data) != 0:
                    log.error("can't load fact '%s'", data)
                    return 2
                fact_owners.append(data)
            #case dict():
            #    log.debug("fact is 'dict' type")
            #    ret_status = self.parse_construct_tag_is_dict(data)
            case _:
                log.error("unknown type of %s", data)
                return 1

        return ret_status

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_construct_what_it_has")
    def construct_what_it_has(self) -> int:
        """Check 'has' tags"""

        self.data["info"]["has"] = {}

        for tag in self.data["def"]:
            if "has" in tag:
                log.debug("has tag: %s", tag)
                if 0 != self.construct_tag_has(tag):
                    return 1

        return 0

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_construct_tag_has")
    def construct_tag_has(self, tag: dict) -> int:
        """Construct what fact has"""

        data = tag["has"]
        log.debug("has data: %s", data)

        fact_has = self.data["info"]["has"]

        ret_status = 0

        match data:
            case str():
                log.debug("fact has '%s'", data)
                return 1  # TODO: handle 'has' with bare string value (no dict)
            case dict():
                log.debug("'has' tag data type is 'dict'")
                ret_status = self.parse_construct_tag_has_dict(data)
            case _:
                log.error("unknown type of %s", data)
                return 1

        return ret_status

    @fact("app/org/igorlesik/fact/pysrc/fact_module", "method_parse_construct_tag_has_dict")
    def parse_construct_tag_has_dict(self, info: dict) -> int:
        """Construct phase parse has dict"""

        attr_name = next(iter(info))
        attr = {}

        if isinstance(info[attr_name], dict) and "type" in info[attr_name]:
            attr_type = info[attr_name]["type"]
            attr["type"] = attr_type
            if "value" in info[attr_name]:
                attr["val"] = info[attr_name]["value"]
            if attr_type not in ("str", "num", "list"):
                if self.kg.load(attr_type) != 0:
                    log.error("has attr '%s' references unknown type '%s'", attr_name, attr_type)
                    return 1
            if "as" in info[attr_name]:
                attr["val_as"] = {}
                for as_type in info[attr_name]["as"]:
                    err, type_name, as_type_val = self.parse_construct_tag_is_as_type(as_type)
                    if err != 0:
                        log.error("can't parse 'as' in has attr '%s'", attr_name)
                        return 1
                    attr["val_as"][type_name] = as_type_val
        else:
            match info[attr_name]:
                case str():
                    attr["type"] = "str"
                    attr["val"] = info[attr_name]
                case int():
                    attr["type"] = "num"
                    attr["val"] = info[attr_name]
                case _:
                    log.error("unknown type %s", info[attr_name])
                    return 1

        fact_has = self.data["info"]["has"]
        if attr_name in fact_has:
            log.error("already exists attr %s", attr_name)
            return 1
        fact_has[attr_name] = attr

        return 0
