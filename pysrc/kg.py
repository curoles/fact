import yaml
from pathlib import Path

class Kg:
    """Knowledge Graph."""

    # Class attribute (shared by all instances)
    # xxxxx = "xxxx"

    def __init__(self, path: Path):
        """Constructor method to initialize instance attributes."""
        self.path = path
        self.data : Dict[str, Any] = {}

    def load(self, fact_name) -> int:
        path = self.path / (fact_name + ".yaml")
        yaml_str: str = open(
            path, "r", encoding="utf-8"
        ).read()
        self.data[fact_name] = yaml.safe_load(yaml_str)
        return 0
