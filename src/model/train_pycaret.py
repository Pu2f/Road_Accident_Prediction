import numpy as np
import pandas as pd
from pycaret.regression import (
    setup, compare_models, tune_model, finalize_model,
    save_model, pull, predict_model
)
from src.data.feature_engineering import build_model_features
from src.model.evaluate import regression_metrics, save_metrics, save_predictions_sample
from src.utils.config import (
    DATA_DIR,
    MODEL_BASENAME,
    LEADERBOARD_CSV,
    METRICS_JSON,
    PREDICTIONS_SAMPLE_CSV,
    ensure_project_dirs,
)
from src.utils.logger import get_logger

TARGET = "รวมจำนวนผู้บาดเจ็บ"
DATA_PATH = DATA_DIR / "processed" / "cleaned_accidents.parquet"
logger = get_logger("train")

FEATURES = [
    "จังหวัด", "สภาพอากาศ", "ลักษณะการเกิดเหตุ", "มูลเหตุสันนิษฐาน",
    "บริเวณที่เกิดเหตุ", "hour", "day_of_week", "month", "is_peak_hour",
    "LATITUDE", "LONGITUDE"
]

def main():
    ensure_project_dirs()

    df = pd.read_parquet(DATA_PATH)
    df = build_model_features(df)

    use_cols = [c for c in FEATURES if c in df.columns] + [TARGET]
    df = df[use_cols].copy()

    # target ต้องเป็นตัวเลข และไม่ว่าง
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    df = df.dropna(subset=[TARGET])

    # แยกชนิดคอลัมน์
    cat_cols = df.drop(columns=[TARGET]).select_dtypes(include=["object", "string", "category"]).columns.tolist()
    num_cols = [c for c in df.columns if c not in cat_cols + [TARGET]]

    # จัดการ categorical: ห้ามเหลือ pd.NA
    for c in cat_cols:
        df[c] = df[c].astype("object")
        df[c] = df[c].replace({pd.NA: np.nan})
        df[c] = df[c].fillna("Unknown")
        df[c] = df[c].astype(str).str.strip()
        df.loc[df[c].isin(["", "nan", "None", "<NA>"]), c] = "Unknown"

    # จัดการ numerical
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # ตัดแถวที่ feature หายเยอะเกินไป
    df = df.dropna(subset=num_cols, how="any").reset_index(drop=True)

    setup(
        data=df,
        target=TARGET,
        session_id=42,
        fold=5,
        train_size=0.8,
        verbose=False,
        numeric_imputation="median",
        categorical_imputation="most_frequent"
    )

    best = compare_models()
    tuned = tune_model(best)
    final_model = finalize_model(tuned)
    save_model(final_model, str(MODEL_BASENAME))

    leaderboard = pull()
    leaderboard.to_csv(LEADERBOARD_CSV, index=False, encoding="utf-8-sig")

    pred_df = predict_model(final_model, data=df)
    metrics = regression_metrics(pred_df[TARGET], pred_df["prediction_label"])
    save_metrics(metrics, METRICS_JSON)
    save_predictions_sample(pred_df, PREDICTIONS_SAMPLE_CSV)

    logger.info("saved: %s.pkl", MODEL_BASENAME)
    logger.info("saved: %s", LEADERBOARD_CSV)
    logger.info("saved: %s", METRICS_JSON)
    logger.info("saved: %s", PREDICTIONS_SAMPLE_CSV)

if __name__ == "__main__":
    main()