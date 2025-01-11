# Commit summary 

This commit introduces two core files that form the foundation of our codebase:

1. **`data_manager.py`**  
   - **Purpose**: Encapsulates the loading and filtering logic for a CSV dataset using [Polars](https://pola-rs.github.io/polars-book/user-guide/python/).
   - **Key Class**: `DataManager`
     - **Constructor** (`__init__`):  
       - Verifies that the CSV file exists; raises `FileNotFoundError` if missing.
       - Prepares a placeholder for the `_df` attribute, which will hold a Polars LazyFrame once loaded.
     - **`load_data()`**:  
       - Lazily reads the CSV, writes to a Parquet file (`addresses.parquet`), then reloads it lazily as a Parquet dataset.  
       - Catches `OSError` or `ComputeError` if something goes wrong, providing a clear error message.
     - **`filter_by_city(city_name)`**:  
       - Ensures data is loaded, applies a case-insensitive filter on the `"city"` column, then collects the resulting LazyFrame to a Polars `DataFrame`.

2. **`app.py`**  
   - **Purpose**: A simple testing script for `DataManager`—**not** a Flask application yet.
   - **Usage**:
     ```
     python app.py <csv_file_path> <city_name>
     ```
   - **Behavior**:
     - Instantiates `DataManager` with the provided CSV path.
     - Calls `filter_by_city(<city_name>)` to retrieve rows for the given city.
     - Prints any matching rows or a message if none are found.
     - Shows usage instructions if insufficient arguments are given.

## Data File Download

Instead of storing a large CSV file within this repository, I have provided a **WeTransfer** download link to retrieve the dataset used:

**Download Link**: [https://we.tl/t-okPhOal1DH](https://we.tl/t-okPhOal1DH)  
(Expires according to WeTransfer’s standard policy.)

1. **Download** the ZIP/CSV from the link.
2. **Place** the file (e.g., `addresses.csv`) in the `df_files/` folder of this project.  
   - You can also provide **any other CSV** you wish to use, as long as it matches the schema the app expects (e.g., columns for `city` and `street`).

Example folder structure (after adding your CSV):

### What’s Next
- Future commits will likely integrate Flask routes or additional logic for real-time querying.
- For now, this **initial commit** provides:
  - A robust data access layer (`DataManager`).
  - A basic CLI script (`app.py`) that verifies city-based filtering is working.
