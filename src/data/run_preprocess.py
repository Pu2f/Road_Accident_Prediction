from src.data.load_data import load_accident_files
from src.data.clean_data import clean_accident_data
from src.utils.config import (
    RAW_DIR,
    PROCESSED_CSV,
    PROCESSED_PARQUET,
    ensure_project_dirs,
)
from src.utils.logger import get_logger


logger = get_logger("preprocess")


def main():
    ensure_project_dirs()

    df_raw = load_accident_files(str(RAW_DIR))
    logger.info("raw shape: %s", df_raw.shape)

    df_clean = clean_accident_data(df_raw)
    logger.info("clean shape: %s", df_clean.shape)

    df_clean.to_parquet(PROCESSED_PARQUET, index=False)
    df_clean.to_csv(PROCESSED_CSV, index=False, encoding="utf-8-sig")
    logger.info("saved: %s", PROCESSED_PARQUET)
    logger.info("saved: %s", PROCESSED_CSV)


if __name__ == "__main__":
    main()