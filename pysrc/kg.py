import yaml
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any

class KgIface(ABC):
    @abstractmethod
    def get_dict(self) -> Dict[str, Any]:
        """Get whole dictionary."""
        pass

class Kg(KgIface):
    """Knowledge Graph."""

    # Class attribute (shared by all instances)
    # xxxxx = "xxxx"

    def __init__(self, path: Path):
        """Constructor method to initialize instance attributes."""
        self.path = path
        self.data : Dict[str, Any] = {}

    def get_dict(self) -> Dict[str, Any]:
        """Get whole dictionary."""
        return self.data

    def load(self, fact_name) -> int:
        path = self.path / (fact_name + ".yaml")
        yaml_str: str = open(
            path, "r", encoding="utf-8"
        ).read()
        self.data[fact_name] = { "def": yaml.safe_load(yaml_str) }
        return 0
