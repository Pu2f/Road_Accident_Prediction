import pandas as pd

import src.model.predict as predict_module


def test_predict_injury_loads_model_with_expected_path(monkeypatch):
	calls = {}

	def fake_load_model(path):
		calls["path"] = path
		return "fake-model"

	def fake_predict_model(model, data):
		calls["model"] = model
		calls["data"] = data.copy()
		return pd.DataFrame({"prediction_label": [3.0]})

	monkeypatch.setattr(predict_module, "load_model", fake_load_model)
	monkeypatch.setattr(predict_module, "predict_model", fake_predict_model)

	_ = predict_module.predict_injury({"hour": 9})

	assert calls["path"] == predict_module.MODEL_PATH
	assert calls["model"] == "fake-model"
	assert isinstance(calls["data"], pd.DataFrame)


def test_predict_injury_returns_float(monkeypatch):
	monkeypatch.setattr(predict_module, "load_model", lambda _path: "fake-model")
	monkeypatch.setattr(
		predict_module,
		"predict_model",
		lambda _model, data: pd.DataFrame({"prediction_label": [7]}),
	)

	result = predict_module.predict_injury({"month": 12})

	assert isinstance(result, float)
	assert result == 7.0


def test_predict_injury_merges_defaults_with_custom_input(monkeypatch):
	captured = {}

	def fake_predict_model(_model, data):
		captured["row"] = data.iloc[0].to_dict()
		return pd.DataFrame({"prediction_label": [1.23]})

	monkeypatch.setattr(predict_module, "load_model", lambda _path: "fake-model")
	monkeypatch.setattr(predict_module, "predict_model", fake_predict_model)

	_ = predict_module.predict_injury({"hour": 18, "จังหวัด": "เชียงใหม่"})

	assert captured["row"]["hour"] == 18
	assert captured["row"]["จังหวัด"] == "เชียงใหม่"
	assert captured["row"]["month"] == predict_module.DEFAULT_INPUT["month"]


def test_predict_injury_uses_defaults_when_input_is_none(monkeypatch):
	captured = {}

	def fake_predict_model(_model, data):
		captured["row"] = data.iloc[0].to_dict()
		return pd.DataFrame({"prediction_label": [0.0]})

	monkeypatch.setattr(predict_module, "load_model", lambda _path: "fake-model")
	monkeypatch.setattr(predict_module, "predict_model", fake_predict_model)

	_ = predict_module.predict_injury(None)

	assert captured["row"] == predict_module.DEFAULT_INPUT
