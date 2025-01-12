import os
import polars as pl


class DataManager:
    def __init__(self, csv_path: str):
        """
        Initializes the data manager instance.

        If the CSV does not exist but a corresponding .parquet file is present,
        we'll skip reading from CSV. Conversely, if both are missing,
        we raise FileNotFoundError.

        :param csv_path: The path to the original CSV file (e.g., 'df_files/addresses.csv').
        """
        self.csv_path = csv_path

        # 1) Derive a .parquet filename from the CSV path
        base_dir = os.path.dirname(csv_path)
        csv_filename = os.path.splitext(os.path.basename(csv_path))[0]  # e.g., 'addresses'
        self.parquet_path = os.path.join(base_dir, f"{csv_filename}.parquet")
        self._df = None

        # 2) If both are missing, fail
        if not os.path.exists(self.csv_path) and not os.path.exists(self.parquet_path):
            raise FileNotFoundError(
                f"No CSV or Parquet file found. Expecting at least one:\n"
                f"  - CSV: {self.csv_path}\n"
                f"  - Parquet: {self.parquet_path}"
            )

    def load_data(self) -> pl.LazyFrame:
        """
        1) If a Parquet file already exists, load it directly as lazy.
        2) Otherwise, read CSV lazily, convert to Parquet, then reload as lazy.

        :rtype: pl.LazyFrame
        :return: The lazy Polars DataFrame.
        """
        if self._df is None:
            try:
                print("loading data into memory...")

                # If Parquet exists, skip loading the CSV again and build a lazy_pl.df from the parquet
                if os.path.exists(self.parquet_path):
                    print(f"Found existing Parquet file: {self.parquet_path}")
                    print(f"loading pl data into memory...")
                    self._df = pl.scan_parquet(self.parquet_path)
                else:
                    print(f"No Parquet found, reading CSV: {self.csv_path}")
                    lazy_df = pl.scan_csv(self.csv_path)
                    lazy_df.sink_parquet(self.parquet_path)
                    self._df = pl.scan_parquet(self.parquet_path)

            except (OSError, pl.exceptions.ComputeError) as e:
                raise OSError(f"Error loading from {self.csv_path} or {self.parquet_path}: {e}") from e

        return self._df


    def filter_by_city(self, city_name: str) -> pl.DataFrame:
        """
        Ensures data is loaded. Filters the lazy DF by city, then collects to a Polars DataFrame.

        :type city_name: str
        :param city_name: Name of the city (case-insensitive).
        :rtype: pl.DataFrame
        :return: A Polars DataFrame filtered by `city_name`.
        """
        lazy_df = self.load_data()
        return (
            lazy_df
            .filter(pl.col("city").str.to_lowercase() == city_name.lower())
            .collect()
        )
