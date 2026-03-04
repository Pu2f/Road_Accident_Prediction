import pandas as pd
from pycaret.regression import setup, compare_models, tune_model, finalize_model, save_model


TARGET = "รวมจำนวนผู้บาดเจ็บ"
INPUT_PATH = "data/processed/cleaned_accidents.parquet"


def train():
    df = pd.read_parquet(INPUT_PATH)

    exp = setup(
        data=df,
        target=TARGET,
        session_id=42,
        fold=5,
        verbose=False
    )

    best = compare_models()
    tuned = tune_model(best)
    final_model = finalize_model(tuned)
    save_model(final_model, "models/final_model")
    print("saved: models/final_model.pkl")


if __name__ == "__main__":
    train()