import pandas as pd
from pycaret.regression import load_model, predict_model

MODEL_PATH = "models/final_model"

DEFAULT_INPUT = {
    "จังหวัด": "กรุงเทพมหานคร",
    "สภาพอากาศ": "แจ่มใส",
    "ลักษณะการเกิดเหตุ": "อื่นๆ",
    "มูลเหตุสันนิษฐาน": "ไม่ทราบ",
    "บริเวณที่เกิดเหตุ": "อื่นๆ",
    "hour": 12,
    "day_of_week": 0,
    "month": 1,
    "is_peak_hour": 0,
    "LATITUDE": 13.7563,
    "LONGITUDE": 100.5018,
}


def predict_injury(input_dict: dict) -> float:
    model = load_model(MODEL_PATH)
    payload = DEFAULT_INPUT.copy()
    payload.update(input_dict or {})

    x = pd.DataFrame([payload])
    pred = predict_model(model, data=x)
    return float(pred["prediction_label"].iloc[0])