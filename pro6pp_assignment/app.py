import os
import polars as pl
from flask import Flask, request, jsonify
from data_manager import DataManager

app = Flask(__name__)

# Determine the CSV file path (relative to this script)
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(base_dir, "df_files", "addresses.csv")

# Create the DataManager instance at startup
try:
    data_manager = DataManager(csv_file)
    data_manager.load_data()  # Force-load the dataset once
    print("Data loaded successfully.")
except FileNotFoundError as e:
    print(f"File not found at startup: {e}")
    data_manager = None
except OSError as e:
    print(f"Error reading CSV: {e}")
    data_manager = None
except Exception as e:
    print(f"Unexpected error on startup: {e}")
    data_manager = None

@app.route("/addresses", methods=["GET"])
def get_addresses():
    """
    Endpoint to retrieve addresses for a given city.
    Usage:
      /addresses?city=Madrid
    Returns JSON with the city, total matches, and unique addresses.
    """
    if data_manager is None:
        return jsonify({"error": "DataManager is not initialized or CSV missing."}), 500

    # Extract city from query param
    city_param = request.args.get("city", "").strip()
    if not city_param:
        return jsonify({"error": "Missing city parameter"}), 400

    try:
        # Use DataManager to filter by city
        unique_addresses = data_manager.filter_by_city(city_param).unique().to_dicts()
    except ValueError as ve:
        # Raised if no rows found
        return jsonify({"error": str(ve)}), 404
    except OSError as oe:
        # Issues reading or parsing
        return jsonify({"error": f"Data error: {oe}"}), 500
    except Exception as ex:
        # Catch-all for anything unexpected
        return jsonify({"error": str(ex)}), 500

    response = {
        "city": city_param,
        "total_matches": len(unique_addresses),
        "unique_addresses": unique_addresses
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
