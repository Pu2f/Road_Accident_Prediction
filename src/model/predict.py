import pandas as pd
from pycaret.regression import load_model, predict_model

MODEL_PATH = "models/final_model"

def predict_injury(input_dict: dict) -> float:
    model = load_model(MODEL_PATH)
    x = pd.DataFrame([input_dict])
    pred = predict_model(model, data=x)
    return float(pred["prediction_label"].iloc[0])