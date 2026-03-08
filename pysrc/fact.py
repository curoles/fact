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

        match info["type"]:
            case "str":
                fact_types.append("str")
            case _:
                print(f"ERROR: implement me")
                return 1

        return 0

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

        # must have type

        fact_has = self.data["info"]["has"]
        if attr_name in fact_has:
            print(f"ERROR: already exists attr {attr_name}")
            return 1
        fact_has[attr_name] = attr

        return 0