"""
Read-only dataset schema inspection.
Reads CSV headers and a few sample rows; does not modify source files.
"""
import csv
import sys
from pathlib import Path


PROJECT_ROOT = Path(r"D:\resume\10 - chatbot")
DATA_ROOT = PROJECT_ROOT / "DATA"

DATASETS = {
    "StackSample / Questions": (
        DATA_ROOT / "StackSample 10% of Stack Overflow Q&A" / "Questions.csv"
    ),
    "StackSample / Answers": (
        DATA_ROOT / "StackSample 10% of Stack Overflow Q&A" / "Answers.csv"
    ),
    "StackSample / Tags": (
        DATA_ROOT / "StackSample 10% of Stack Overflow Q&A" / "Tags.csv"
    ),
    "Bug & Fix Pairs": (
        DATA_ROOT / "Python Code Bug & Fix Pairs" / "code_bug_fix_pairs.csv"
    ),
    "Glaive Python QA": (
        DATA_ROOT / "Glaive Python Code QA Dataset" / "train.csv"
    ),
}

try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(2**31 - 1)


def inspect_csv(path: Path, sample_count: int = 2) -> None:
    print(f"\n{'=' * 72}")
    print(f"File: {path}")
    print(f"Exists: {path.is_file()}")

    if not path.is_file():
        return

    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as file:
                reader = csv.DictReader(file)
                print(f"Encoding: {encoding}")
                print(f"Columns: {reader.fieldnames}")

                for index, row in enumerate(reader):
                    if index >= sample_count:
                        break

                    print(f"\nSample row {index + 1}:")
                    for key, value in row.items():
                        text = (value or "").replace("\n", "\\n")
                        if len(text) > 300:
                            text = text[:300] + "... [truncated]"
                        print(f"  {key}: {text}")

            return

        except UnicodeDecodeError:
            continue
        except Exception as exc:
            print(f"Could not inspect file: {type(exc).__name__}: {exc}")
            return

    print("Could not decode the file using the attempted encodings.")


if __name__ == "__main__":
    for dataset_name, csv_path in DATASETS.items():
        print(f"\n### {dataset_name}")
        inspect_csv(csv_path)
