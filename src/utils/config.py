from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
MODELS_DIR = ROOT_DIR / "models"

PROCESSED_PARQUET = PROCESSED_DIR / "cleaned_accidents.parquet"
PROCESSED_CSV = PROCESSED_DIR / "cleaned_accidents.csv"
MODEL_BASENAME = MODELS_DIR / "final_model"

LEADERBOARD_CSV = ARTIFACTS_DIR / "leaderboard.csv"
METRICS_JSON = ARTIFACTS_DIR / "metrics.json"
PREDICTIONS_SAMPLE_CSV = ARTIFACTS_DIR / "predictions_sample.csv"


def ensure_project_dirs() -> None:
	PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
	ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
	MODELS_DIR.mkdir(parents=True, exist_ok=True)
