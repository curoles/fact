#!/usr/bin/env python3

# xp -a pysrc/kg.py pysrc/check.py astronomy/universe

import argparse
from pathlib import Path

from kg import Kg
from fact import Fact

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Check a fact")
    # Positional argument fact_name (required)
    parser.add_argument("name", help="The name of the user.")
    args = parser.parse_args()

    fact_name = args.name
    print(f"Checking fact '{fact_name}'")

    script_dir = Path(__file__).resolve().parent
    kg_dir = script_dir.parent / "kg"
    print(f"KG path: {kg_dir}")

    file_path = kg_dir / (fact_name + ".yaml")

    if file_path.exists():
        print(f"The path exists: {file_path}")
    else:
        print(f"ERROR: the path does NOT exist: {file_path}")
        return 1

    kg = Kg(kg_dir)

    if 0 != kg.load(fact_name):
        print("ERROR: could not load the fact")
        return 2

    print(kg.get_dict()[fact_name])

    fact = Fact(kg, fact_name)
    if 0 != fact.construct():
        print("ERROR: can not construct fact")

    return 0

if __name__ == "__main__":
    main()
