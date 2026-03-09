from kg import KgIface
from typing import Dict

class Fact:
    """Element of knowledge"""

    def __init__(self, kg: KgIface, fact_name: str):
        self.kg = kg
        self.name = fact_name

    def construct(self) -> int:
        """Construct fact, create fields"""

        if self.name not in self.kg.get_dict():
            print(f"ERROR: can not find {self.name} in KG")
            return 1

        self.data = self.kg.get_fact(self.name)

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

        print(f"{self.name} constructed: {self.data['info']}")

        return 0

    def construct_what_it_is(self) -> int:
        """Check 'is' tags"""

        self.data["info"]["type"] = []
        self.data["info"]["val_as"] = {}

        for tag in self.data["def"]:
            if "is" in tag.keys():
                print(f"is tag: {tag}")
                if 0 != self.construct_tag_is(tag):
                    return 1

        return 0

    def construct_tag_is(self, tag: dict) -> int:
        """Construct what fact is"""

        data = tag["is"]
        print(f"is data: {data}")

        fact_types = self.data["info"]["type"]

        ret_status = 0

        match data:
            case str():
                print("fact is 'str' type")
                fact_types.append("str")
            case dict():
                print("fact is 'dict' type")
                ret_status = self.parse_construct_tag_is_dict(data)
            case _:
                print(f"ERROR: unknown type of {data}")
                return 1

        return ret_status

    def parse_construct_tag_is_dict(self, info: dict) -> int:
        """Construct phase parse is dict"""

        if "type" not in info:
            print(f"ERROR: no 'type' in {info}")
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
                    print(f"ERROR: can't load fact '{info_type}'")
                    return 2
                fact_types.append(info_type)

        if "as" in info:
            for as_type in info["as"]:
                err, type_name, as_type_val = self.parse_construct_tag_is_as_type(as_type)
                if err != 0:
                    print(f"ERROR: can't parse '{as_type}'")
                    return 3
                self.data["info"]["val_as"][type_name] = as_type_val

        return 0

    def parse_construct_tag_is_as_type(self, as_type: dict) -> (int, str, dict):
        print(f"as type {as_type}")
        err = 0
        as_type_val = {}
        type_name = next(iter(as_type))

        attrs = as_type[type_name]
        for attr_name in attrs:
            as_type_val[attr_name] = attrs[attr_name]["value"]

        return (err, type_name, as_type_val)

    def construct_what_it_part(self) -> int:
        """Check 'part' tags"""

        self.data["info"]["part"] = []

        for tag in self.data["def"]:
            if "part" in tag.keys():
                print(f"part tag: {tag}")
                if 0 != self.construct_tag_part(tag):
                    return 1

        return 0

    def construct_tag_part(self, tag: dict) -> int:
        """Construct what fact belongs to"""

        data = tag["part"]
        print(f"part data: {data}")

        fact_owners = self.data["info"]["part"]

        ret_status = 0

        match data:
            case str():
                print(f"fact belongs to '{data}'")
                if self.kg.load(data) != 0:
                    print(f"ERROR: can't load fact '{data}'")
                    return 2
                fact_owners.append(data)
            #case dict():
            #    print("fact is 'dict' type")
            #    ret_status = self.parse_construct_tag_is_dict(data)
            case _:
                print(f"ERROR: unknown type of {data}")
                return 1

        return ret_status

    def construct_what_it_has(self) -> int:
        """Check 'has' tags"""

        self.data["info"]["has"] = {}

        for tag in self.data["def"]:
            if "has" in tag.keys():
                print(f"has tag: {tag}")
                if 0 != self.construct_tag_has(tag):
                    return 1

        return 0

    def construct_tag_has(self, tag: dict) -> int:
        """Construct what fact has"""

        data = tag["has"]
        print(f"has data: {data}")

        fact_has = self.data["info"]["has"]

        ret_status = 0

        match data:
            case str():
                print(f"fact has '{data}'")
                #if self.kg.load(data) != 0:
                #    print(f"ERROR: can't load fact '{data}'")
                #    return 2
                #fact_has.append(data)
                return 1 # FIXME
            case dict():
                print("'has' tag data type is 'dict'")
                ret_status = self.parse_construct_tag_has_dict(data)
            case _:
                print(f"ERROR: unknown type of {data}")
                return 1

        return ret_status

    def parse_construct_tag_has_dict(self, info: dict) -> int:
        """Construct phase parse has dict"""

        attr_name = next(iter(info))
        attr = {}

        if "type" in info[attr_name]:
            attr_type = info[attr_name]["type"]
            attr["type"] = attr_type
        else:
            match info[attr_name]:
                case str():
                    attr["type"] = "str"
                    attr["val"] = info[attr_name]
                case int():
                    attr["type"] = "num"
                    attr["val"] = info[attr_name]
                case _:
                    print(f"ERROR: unknown type {info[attr_name]}")
                    return 1

        fact_has = self.data["info"]["has"]
        if attr_name in fact_has:
            print(f"ERROR: already exists attr {attr_name}")
            return 1
        fact_has[attr_name] = attr

        return 0