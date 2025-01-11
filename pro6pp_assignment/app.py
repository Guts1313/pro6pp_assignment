import os
import sys
import polars as pl
from data_manager import DataManager


def main():
    """
    A simple script to test DataManager's filter_by_city method..

    Usage:
        python app.py <csv_file_path> <city_name>

    """
    if len(sys.argv) < 3:
        print("Usage: python app.py <csv_file_path> <city_name>")
        sys.exit(1)

    csv_file = sys.argv[1]
    city_name = sys.argv[2]

    try:
        # Create the DataManager instance with the provided CSV file
        manager = DataManager(csv_file)

        # Use filter_by_city to collect the Polars DataFrame
        df_result = manager.filter_by_city(city_name)

        print(f"Filtering for city: {city_name}")
        if df_result.is_empty():
            print(f"No rows found for city: {city_name}")
        else:
            print("Rows found:")
            print(df_result)

    except FileNotFoundError as fnf_err:
        print(fnf_err)
    except OSError as os_err:
        print(f"Error reading CSV file: {os_err}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")


if __name__ == "__main__":
    main()
