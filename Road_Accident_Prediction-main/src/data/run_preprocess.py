from src.data.load_data import load_accident_files
from src.data.clean_data import clean_accident_data


def main():
    df_raw = load_accident_files("data/raw")
    print("raw shape:", df_raw.shape)

    df_clean = clean_accident_data(df_raw)
    print("clean shape:", df_clean.shape)

    df_clean.to_parquet("data/processed/cleaned_accidents.parquet", index=False)
    df_clean.to_csv("data/processed/cleaned_accidents.csv", index=False, encoding="utf-8-sig")
    print("saved: data/processed/cleaned_accidents.parquet")
    print("saved: data/processed/cleaned_accidents.csv")


if __name__ == "__main__":
    main()