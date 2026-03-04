from pathlib import Path
import pandas as pd


def _read_csv_fallback(file_path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp874", "tis-620"]
    last_err = None
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except Exception as e:
            last_err = e
    raise ValueError(f"อ่านไฟล์ไม่สำเร็จ: {file_path} | {last_err}")


def load_csvs_from_raw(raw_dir: str = "data/raw") -> pd.DataFrame:
    files = sorted(Path(raw_dir).glob("*.csv"))
    if not files:
        raise FileNotFoundError("ไม่พบไฟล์ .csv ในโฟลเดอร์ data/raw")

    dfs = []
    for f in files:
        df = _read_csv_fallback(f)
        df["source_file"] = f.name
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    return combined


if __name__ == "__main__":
    df = load_csvs_from_raw("data/raw")
    print("shape:", df.shape)
    print("columns:", df.columns.tolist())