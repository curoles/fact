import yaml
import jsonschema
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any

class KgIface(ABC):
    @abstractmethod
    def get_dict(self) -> Dict[str, Any]:
        """Get whole dictionary."""
        pass

    @abstractmethod
    def load(self, fact_name, force_reload = False) -> int:
        """Load fact info from file."""
        pass

    @abstractmethod
    def is_loaded(self, fact_name) -> bool:
        """Check if fact loaded into KG memory."""
        pass

class Kg(KgIface):
    """Knowledge Graph."""

    # Class attribute (shared by all instances)
    # xxxxx = "xxxx"

    def __init__(self, path: Path, schema: str):
        """Constructor method to initialize instance attributes."""
        self.path = path
        self.schema = schema
        self.data : Dict[str, Any] = {}

    def get_dict(self) -> Dict[str, Any]:
        """Get whole dictionary."""
        return self.data

    def get_fact(self, name: str) -> Dict:
        """Get data about fact from dictionary."""
        return self.data[name]

    def is_loaded(self, fact_name) -> bool:
        """Check if fact loaded into KG memory."""
        return fact_name in self.data

    def load(self, fact_name, force_reload = False) -> int:
        if self.is_loaded(fact_name) and not force_reload:
            return 0
        path = self.path / (fact_name + ".yaml")
        yaml_str: str = open(
            path, "r", encoding="utf-8"
        ).read()
        self.data[fact_name] = { "def": yaml.safe_load(yaml_str) }
        if not self.validate_schema(self.data[fact_name]["def"]):
            return 1
        return 0

    def validate_schema(self, yaml_data: str) -> bool:
        try:
            jsonschema.validate(instance=yaml_data, schema=self.schema)
            print("valid schema")
        except jsonschema.ValidationError as e:
            print(f"ERROR: invalid schema: {e.message}")
            print(f"  at path: {list(e.absolute_path)}")
            return False
        return True
