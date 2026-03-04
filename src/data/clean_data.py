import pandas as pd


TARGET_COL = "รวมจำนวนผู้บาดเจ็บ"


def clean_accident_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ลบข้อมูลซ้ำ
    df = df.drop_duplicates()

    # แปลงตัวเลขที่สำคัญ
    numeric_cols = ["LATITUDE", "LONGITUDE", TARGET_COL, "ผู้เสียชีวิต", "ผู้บาดเจ็บสาหัส", "ผู้บาดเจ็บเล็กน้อย"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # กรองพิกัดผิดปกติ (ประเทศไทยโดยประมาณ)
    if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:
        df = df[df["LATITUDE"].between(5, 21, inclusive="both")]
        df = df[df["LONGITUDE"].between(97, 106, inclusive="both")]

    # target ต้องไม่ว่าง
    if TARGET_COL in df.columns:
        df = df.dropna(subset=[TARGET_COL])

    return df