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


def test_clean_accident_data_filters_invalid_rows_and_builds_features():
	df = pd.DataFrame(
		{
			"LATITUDE": [13.7, 40.0, 13.7],
			"LONGITUDE": [100.5, 100.5, 100.5],
			"รวมจำนวนผู้บาดเจ็บ": [2, 1, None],
			"ผู้เสียชีวิต": [0, 1, 0],
			"ผู้บาดเจ็บสาหัส": [0, 0, 0],
			"ผู้บาดเจ็บเล็กน้อย": [2, 0, 0],
			"เวลา": ["07:00", "08:00", "09:00"],
			"วันที่เกิดเหตุ": ["01/01/2024", "01/01/2024", "01/01/2024"],
			"จังหวัด": ["Bangkok", "Bangkok", "Bangkok"],
		}
	)

	out = clean_accident_data(df)

	assert len(out) == 1
	assert out.loc[0, "LATITUDE"] == 13.7
	assert out.loc[0, "is_peak_hour"] == 1
	assert out.loc[0, "รวมจำนวนผู้บาดเจ็บ"] == 2


def test_clean_accident_data_drops_rows_with_unknown_and_normalizes_object_dtype():
	df = pd.DataFrame(
		{
			"LATITUDE": [13.7, 13.8],
			"LONGITUDE": [100.5, 100.6],
			"รวมจำนวนผู้บาดเจ็บ": [1, 1],
			"ผู้เสียชีวิต": [0, 0],
			"ผู้บาดเจ็บสาหัส": [0, 0],
			"ผู้บาดเจ็บเล็กน้อย": [1, 1],
			"จังหวัด": ["Bangkok", None],
			"สภาพอากาศ": [b"clear", "rain"],
			"เวลา": ["10:00", "10:00"],
			"วันที่เกิดเหตุ": ["01/01/2024", "01/01/2024"],
		}
	)

	out = clean_accident_data(df)

	# Row with missing categorical value is converted to Unknown then removed.
	assert len(out) == 1
	assert out.loc[0, "จังหวัด"] == "Bangkok"
	assert out.loc[0, "สภาพอากาศ"] == "clear"
	assert str(out["สภาพอากาศ"].dtype) == "string"
