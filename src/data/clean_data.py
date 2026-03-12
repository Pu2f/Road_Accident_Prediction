import pandas as pd

TARGET = "รวมจำนวนผู้บาดเจ็บ"

COLUMN_ALIASES = {
    "ปีที่เกิดเหตุ ": "ปีที่เกิดเหตุ",
    "วันที่เกิดเหตุ ": "วันที่เกิดเหตุ",
    "เวลา ": "เวลา",
    "จังหวัด ": "จังหวัด",
    "LATITUDE ": "LATITUDE",
    "LONGITUDE ": "LONGITUDE",
    "ผู้เสียชีวิต ": "ผู้เสียชีวิต",
    "ผู้บาดเจ็บสาหัส ": "ผู้บาดเจ็บสาหัส",
    "ผู้บาดเจ็บเล็กน้อย ": "ผู้บาดเจ็บเล็กน้อย",
    "รวมจำนวนผู้บาดเจ็บ ": "รวมจำนวนผู้บาดเจ็บ",
}

NUMERIC_COLS = [
    "LATITUDE",
    "LONGITUDE",
    "ผู้เสียชีวิต",
    "ผู้บาดเจ็บสาหัส",
    "ผู้บาดเจ็บเล็กน้อย",
    "รวมจำนวนผู้บาดเจ็บ",
]


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.replace("\ufeff", "").strip() for c in df.columns]
    df = df.rename(columns=COLUMN_ALIASES)
    return df


def build_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "เวลา" in df.columns:
        time_str = df["เวลา"].astype(str).str.strip()
        # รองรับ HH:MM หรือ HH:MM:SS
        parsed_time = pd.to_datetime(time_str, format="%H:%M", errors="coerce")
        parsed_time2 = pd.to_datetime(time_str, format="%H:%M:%S", errors="coerce")
        parsed_time = parsed_time.fillna(parsed_time2)

        df["hour"] = parsed_time.dt.hour
        df["is_peak_hour"] = df["hour"].isin([7, 8, 9, 16, 17, 18, 19]).astype(int)

    if "วันที่เกิดเหตุ" in df.columns:
        d = pd.to_datetime(df["วันที่เกิดเหตุ"], errors="coerce", dayfirst=True)
        df["day_of_week"] = d.dt.dayofweek
        df["month"] = d.dt.month

    return df


def fix_shifted_2026_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Repair accident2026 rows where ACC_CODE is missing and columns shift left by 1."""
    required_cols = [
        "source_file",
        "ACC_CODE",
        "หน่วยงาน",
        "สายทางหน่วยงาน",
        "รหัสสายทาง",
        "สายทาง",
        "KM",
        "จังหวัด",
        "รถคันที่1",
        "บริเวณที่เกิดเหตุ",
        "มูลเหตุสันนิษฐาน",
        "ลักษณะการเกิดเหตุ",
        "สภาพอากาศ",
        "LATITUDE",
        "LONGITUDE",
        "รถที่เกิดเหตุ",
        "รถและคนที่เกิดเหตุ",
        "รถจักรยานยนต์",
        "รถสามล้อเครื่อง",
        "รถยนต์นั่งส่วนบุคคล",
        "รถตู้",
        "รถปิคอัพโดยสาร",
        "รถโดยสารมากกว่า4ล้อ",
        "รถปิคอัพบรรทุก4ล้อ",
        "รถบรรทุก6ล้อ",
        "รถบรรทุกไม่เกิน10ล้อ",
        "รถบรรทุกมากกว่า10ล้อ",
        "รถอีแต๋น",
        "รถอื่นๆ",
        "คนเดินเท้า",
        "ผู้เสียชีวิต",
        "ผู้บาดเจ็บสาหัส",
        "ผู้บาดเจ็บเล็กน้อย",
        "รวมจำนวนผู้บาดเจ็บ",
    ]
    if any(c not in df.columns for c in required_cols):
        return df

    out = df.copy()
    is_2026 = out["source_file"].astype("string").eq("accident2026.csv")
    if not is_2026.any():
        return out

    acc_code = out["ACC_CODE"].astype("string")
    lat = pd.to_numeric(out["LATITUDE"], errors="coerce")
    lon = pd.to_numeric(out["LONGITUDE"], errors="coerce")

    shifted_mask = is_2026 & (
        acc_code.str.contains("กรมทางหลวง|การทางพิเศษ", na=False)
        | ((lat > 30) & (lon <= 10))
    )
    if not shifted_mask.any():
        return out

    shift_block = required_cols[1:]
    before = out.loc[shifted_mask, shift_block].copy()
    out.loc[shifted_mask, shift_block[1:]] = before[shift_block[:-1]].to_numpy()
    out.loc[shifted_mask, shift_block[0]] = pd.NA

    return out


def clean_accident_data(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_column_names(df)
    df = fix_shifted_2026_rows(df)

    df = df.drop_duplicates()

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # filter lat/lon ไทยโดยประมาณ
    if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:
        df = df[df["LATITUDE"].between(5, 21, inclusive="both")]
        df = df[df["LONGITUDE"].between(97, 106, inclusive="both")]

    if TARGET in df.columns:
        if {"ผู้บาดเจ็บสาหัส", "ผู้บาดเจ็บเล็กน้อย"}.issubset(df.columns):
            reconstructed = (
                pd.to_numeric(df["ผู้บาดเจ็บสาหัส"], errors="coerce").fillna(0)
                + pd.to_numeric(df["ผู้บาดเจ็บเล็กน้อย"], errors="coerce").fillna(0)
            )
            df[TARGET] = df[TARGET].fillna(reconstructed)
        df = df.dropna(subset=[TARGET])

    df = build_time_features(df)

    # เติมค่าว่างหมวดหมู่ด้วย Unknown (รองรับ mixed types เช่น bytes/str/None)
    cat_cols = [
        "จังหวัด",
        "สภาพอากาศ",
        "ลักษณะการเกิดเหตุ",
        "มูลเหตุสันนิษฐาน",
        "บริเวณที่เกิดเหตุ",
    ]
    present_cat_cols = [c for c in cat_cols if c in df.columns]
    for c in present_cat_cols:
        df[c] = df[c].map(
            lambda x: (
                x.decode("utf-8", errors="ignore")
                if isinstance(x, (bytes, bytearray))
                else x
            )
        )
        df[c] = df[c].astype("string").str.strip()
        df[c] = df[c].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
        df[c] = df[c].fillna("Unknown")

    # 🔴 ลบทุกแถวที่มี Unknown ในคอลัมน์หมวดหมู่
    if present_cat_cols:
        df = df.loc[~df[present_cat_cols].eq("Unknown").any(axis=1)]

    # กันปัญหา mixed type ในคอลัมน์ object ตอนเขียน parquet (เช่น str/int/bytes ปนกัน)
    object_cols = df.select_dtypes(include=["object"]).columns
    for c in object_cols:
        df[c] = df[c].map(
            lambda x: (
                x.decode("utf-8", errors="ignore")
                if isinstance(x, (bytes, bytearray))
                else x
            )
        )
        df[c] = df[c].astype("string")

    return df.reset_index(drop=True)
