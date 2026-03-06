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
    df.columns = [c.strip() for c in df.columns]
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


def clean_accident_data(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_column_names(df)

    df = df.drop_duplicates()

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # filter lat/lon ไทยโดยประมาณ
    if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:
        df = df[df["LATITUDE"].between(5, 21, inclusive="both")]
        df = df[df["LONGITUDE"].between(97, 106, inclusive="both")]

    if TARGET in df.columns:
        df = df.dropna(subset=[TARGET])

    df = build_time_features(df)

    # เติมค่าว่างหมวดหมู่ด้วย Unknown
    cat_cols = ["จังหวัด", "สภาพอากาศ", "ลักษณะการเกิดเหตุ", "มูลเหตุสันนิษฐาน", "บริเวณที่เกิดเหตุ"]
    for c in cat_cols:
        if c in df.columns:
            df[c] = df[c].astype(str).fillna("Unknown").replace("nan", "Unknown")

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
