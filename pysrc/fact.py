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

        result = Fact.construct_what_it_is(self)
        if result != 0:
            return result

        #result = Fact.construct_what_it_has(self)
        #if result != 0:
        #    return result

        #result = Fact.construct_what_it_part(self)
        #if result != 0:
        #    return result

        print(f"{self.name} constructed: {self.data['info']}")

        return 0

    def construct_what_it_is(self) -> int:
        """Check 'is' tags"""

        self.data["info"]["type"] = []

        for tag in self.data["def"]:
            if "is" in tag.keys():
                print(f"tag: {tag}")
                if 0 != self.construct_tag_is(tag):
                    return 1

        return 0

    def construct_tag_is(self, tag: dict) -> int:
        """Construct what fact is"""

        data = tag["is"]
        print(f"fact is: {data}")

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