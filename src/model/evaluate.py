import json
from pathlib import Path

import numpy as np
import pandas as pd


def regression_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
	y_true = pd.to_numeric(y_true, errors="coerce")
	y_pred = pd.to_numeric(y_pred, errors="coerce")
	mask = y_true.notna() & y_pred.notna()
	y_true = y_true[mask]
	y_pred = y_pred[mask]

	if len(y_true) == 0:
		return {"mae": None, "rmse": None, "mape": None, "n_rows": 0}

	err = y_true - y_pred
	mae = float(np.abs(err).mean())
	rmse = float(np.sqrt((err**2).mean()))
	denom = y_true.replace(0, np.nan)
	mape = float((np.abs(err) / denom).dropna().mean() * 100) if denom.notna().any() else None
	return {"mae": mae, "rmse": rmse, "mape": mape, "n_rows": int(len(y_true))}


def save_metrics(metrics: dict, metrics_path: str | Path) -> None:
	path = Path(metrics_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		json.dump(metrics, f, ensure_ascii=False, indent=2)


def save_predictions_sample(pred_df: pd.DataFrame, out_path: str | Path, sample_size: int = 3000) -> None:
	path = Path(out_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	sample = pred_df.sample(min(sample_size, len(pred_df)), random_state=42) if len(pred_df) else pred_df
	sample = sample.copy()

	# Normalize prediction columns so downstream charts can use a stable schema.
	rename_map = {
		"รวมจำนวนผู้บาดเจ็บ": "actual",
		"prediction_label": "predicted",
	}
	sample = sample.rename(columns=rename_map)

	if {"actual", "predicted"}.issubset(sample.columns):
		sample["actual"] = pd.to_numeric(sample["actual"], errors="coerce")
		sample["predicted"] = pd.to_numeric(sample["predicted"], errors="coerce")
		sample["abs_error"] = (sample["actual"] - sample["predicted"]).abs()

	sample.to_csv(path, index=False, encoding="utf-8-sig")
