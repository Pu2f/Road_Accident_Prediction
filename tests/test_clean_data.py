import pandas as pd

from src.data.clean_data import (
	build_time_features,
	clean_accident_data,
	normalize_column_names,
)


def test_normalize_column_names_trims_and_maps_aliases():
	df = pd.DataFrame(
		{
			"ปีที่เกิดเหตุ ": [2024],
			"เวลา ": ["08:30"],
			"LATITUDE ": [13.75],
		}
	)

	out = normalize_column_names(df)

	assert "ปีที่เกิดเหตุ" in out.columns
	assert "เวลา" in out.columns
	assert "LATITUDE" in out.columns
	assert "ปีที่เกิดเหตุ " not in out.columns


def test_build_time_features_supports_hhmm_and_hhmmss():
	df = pd.DataFrame(
		{
			"เวลา": ["08:15", "19:10:30", "bad"],
			"วันที่เกิดเหตุ": ["01/03/2024", "02/03/2024", "03/03/2024"],
		}
	)

	out = build_time_features(df)

	assert out.loc[0, "hour"] == 8
	assert out.loc[1, "hour"] == 19
	assert pd.isna(out.loc[2, "hour"])
	assert out.loc[0, "is_peak_hour"] == 1
	assert out.loc[1, "is_peak_hour"] == 1
	assert out.loc[2, "is_peak_hour"] == 0
	assert set(["day_of_week", "month"]).issubset(set(out.columns))
