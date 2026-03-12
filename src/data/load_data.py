from pathlib import Path
import pandas as pd


EXPECTED_FILES = [
    "accident2019.csv",
    "accident2020.csv",
    "accident2021.csv",
    "accident2022.csv",
    "accident2023.csv",
    "accident2024.csv",
    "accident2025.csv",
    "accident2026.csv",
]


def _read_csv_fallback(file_path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp874", "tis-620"]
    read_modes = [
        {},
        {"sep": "\t"},
        {"sep": None, "engine": "python"},
    ]

    for enc in encodings:
        for mode in read_modes:
            try:
                df = pd.read_csv(file_path, encoding=enc, low_memory=False, **mode)
                if df.shape[1] > 1:
                    return df
            except Exception:
                continue

    # Fallback result to surface the original read error behavior.
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc, low_memory=False)
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