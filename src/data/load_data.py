from pathlib import Path
import pandas as pd


EXPECTED_FILES = [
    "accident2022.csv",
    "accident2023.csv",
    "accident2024.csv",
    "accident2025.csv",
]


def _read_csv_fallback(file_path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp874", "tis-620"]
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except Exception:
            continue
    raise ValueError(f"อ่านไฟล์ไม่สำเร็จ: {file_path}")


def load_accident_files(raw_dir: str = "data/raw") -> pd.DataFrame:
    raw_path = Path(raw_dir)
    missing = [f for f in EXPECTED_FILES if not (raw_path / f).exists()]
    if missing:
        raise FileNotFoundError(f"ไฟล์หายไป: {missing}")

    dfs = []
    for fname in EXPECTED_FILES:
        fpath = raw_path / fname
        df = _read_csv_fallback(fpath)
        df["source_file"] = fname
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)