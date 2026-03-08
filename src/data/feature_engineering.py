import numpy as np
import pandas as pd


def add_geo_bins(df: pd.DataFrame, lat_col: str = "LATITUDE", lon_col: str = "LONGITUDE") -> pd.DataFrame:
	out = df.copy()
	if lat_col in out.columns and lon_col in out.columns:
		out["lat_bin"] = (pd.to_numeric(out[lat_col], errors="coerce") * 20).round() / 20
		out["lon_bin"] = (pd.to_numeric(out[lon_col], errors="coerce") * 20).round() / 20
	return out


def add_time_cyclical_features(df: pd.DataFrame, hour_col: str = "hour", month_col: str = "month") -> pd.DataFrame:
	out = df.copy()
	if hour_col in out.columns:
		h = pd.to_numeric(out[hour_col], errors="coerce")
		out["hour_sin"] = np.sin(2 * np.pi * h / 24)
		out["hour_cos"] = np.cos(2 * np.pi * h / 24)

	if month_col in out.columns:
		m = pd.to_numeric(out[month_col], errors="coerce")
		out["month_sin"] = np.sin(2 * np.pi * m / 12)
		out["month_cos"] = np.cos(2 * np.pi * m / 12)
	return out


def build_model_features(df: pd.DataFrame) -> pd.DataFrame:
	out = add_geo_bins(df)
	out = add_time_cyclical_features(out)
	return out
