# pro6pp Assignment

This repository demonstrates a small coding assignment aimed at quickly and cleanly building a Python backend (with Flask + Polars) to serve address data for Spanish cities, as well as optionally a simple frontend.

## Overview

- **Data**  
  We download a publicly available dataset containing Spanish addresses (city + street). This dataset is loaded into memory using [Polars](https://pola-rs.github.io/polars-book/user-guide/python/), which allows for efficient data parsing and querying.

- **Backend**  
  A **Flask** application exposes a **single API endpoint** that returns street names matching a requested city. The endpoint is `/addresses` with a `city` query parameter, returning results in JSON.

- **Frontend (Optional)**  
  A minimal SPA or plain HTML/JS page can be used to provide a text box for the city name and display the returned JSON in a clean format.

## Project Structure


## Key Files

1. **`data_loader.py`**  
   - Defines a `DataManager` class that:
     - Takes a CSV file path in the constructor.
     - Checks if the file exists, raising an error if missing.
     - Uses Polars to read the CSV (lazy load), optionally convert it to Parquet, then provides methods to filter by city and retrieve unique addresses.
     - Raises Python exceptions (`ValueError`, `OSError`, etc.) for data-related issues.

2. **`app.py`**  
   - Flask server logic, which:
     - Instantiates a `DataManager` (loading the dataset exactly once).
     - Exposes a route `/addresses`:
       - Requires `city` parameter (`?city=Madrid`).
       - Returns JSON listing all street names in the matching city or an error if missing or not found.
     - Adheres to standard HTTP codes: 400 (Bad Request), 404 (Not Found), and 500 (Internal Server Error).

## Running the Application

## Data File Download
Instead of storing a large CSV file within this repository, I have provided a **WeTransfer** download link to retrieve the dataset I used for the assignment:
**Download Link**: [https://we.tl/t-okPhOal1DH](https://we.tl/t-okPhOal1DH)  
(Expires according to WeTransfer’s standard policy.)
1. **Download** the ZIP/CSV from the link.
2. **Place** the file (e.g., `addresses.csv`) in the `df_files/` folder of this project.  
   - You can also provide **any other CSV** you wish to use instead  , as long as it matches the schema the app expects (e.g., columns for `city` and `street`).
   - **If NO CSV file is provided in the df_files dir** then the app will load the lazy_df from **addresses.parquet** - polar file created from the addresses.csv upon previous app launches. 
3. **Run Flask**
   ```bash
   python app.py
   ```
   By default, the server will be available at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).


4.**Example Request**
   - **Get addresses for “Madrid”**:
     ```
     GET /addresses?city=Madrid
     ```
     **Sample JSON response**:
     ```json
     {
       "city": "Madrid",
       "total_matches": 3,
       "unique_addresses": [
         { "city": "Madrid", "street": "CALLE PALMA" },
         { "city": "Madrid", "street": "CALLE HERNANDEZ DE TEJADA" },
         { "city": "Madrid", "street": "CALLE GRAN VIA" }
       ]
     }
     ```

5. **Potential Errors**
   - **No `city` parameter** → 400 Bad Request.
   - **City not found** → 404 Not Found.
   - **CSV missing or read error** → 500 Internal Server Error.
```
