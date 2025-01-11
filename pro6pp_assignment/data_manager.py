import os
import polars as pl


# File paths

class DataManager:
    def __init__(self, csv_path: str):
        """
        Initializes the data manager instance.
        Raises FileNotFoundError if the CSV does not exist at initialization.

        :type csv_path: str
        :param csv_path: Path to the CSV file.
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        self.csv_path = csv_path
        self._df = None

    def load_data(self) -> pl.LazyFrame:
        """
        Loads or returns a lazy Polars DataFrame, writes it to Parquet, then re-loads as lazy.
        Called once to initialize the df we work with.

        :rtype: pl.LazyFrame
        :return: The lazy Polars DataFrame.
        """
        if self._df is None:
            try:
                print("loading data into memory...")  # Will print only once
                # 1) scan CSV as lazy
                lazy_df = pl.scan_csv(self.csv_path)
                # 2) convert CSV data to Parquet for additional optimisation
                lazy_df.sink_parquet("addresses.parquet")
                # 3) load lazy again from Parquet
                self._df = pl.scan_parquet("addresses.parquet")
            except (OSError, pl.exceptions.ComputeError) as e:
                raise OSError(f"Error loading CSV from {self.csv_path}: {e}") from e
        return self._df

    def filter_by_city(self, city_name: str) -> pl.DataFrame:
        """
        Checks if there is a df loaded in memory if not -> loads the df
        Filters the lazy DF by a city name, then collects to a DataFrame.

        :type city_name: str
        :param city_name: Name of the city.
        :rtype: pl.DataFrame
        :return: The lazy Polars DataFrame.
        """
        lazy_df = self.load_data()
        return lazy_df.filter(pl.col("city").str.to_lowercase() == city_name.lower()).collect(engine="gpu")