
import os
from flask import Flask, jsonify, request, current_app
from flask_cors import CORS

from data_manager import DataManager

def initialize_data_manager(csv_file: str) -> DataManager:
    """
    Creates and loads a DataManager instance from the given CSV file.
    Returns None if there's an error (file missing, read issue, etc.).
    """
    try:
        manager = DataManager(csv_file)
        manager.load_data()  # Force load once at startup
        print("DataManager created and data loaded at startup.")
        return manager
    except FileNotFoundError as e:
        print(f"File not found at startup: {e}")
    except OSError as e:
        print(f"Error reading CSV file: {e}")
    except Exception as e:
        print(f"Unexpected error at startup: {e}")

    return None  # If we reach here, something failed

def handle_addresses_route(data_manager: DataManager):
    """
    Processes a GET request for the '/addresses' endpoint.
      - Expects a 'city' query parameter.
      - Returns JSON with city, total matches, and unique addresses.
    """
    if data_manager is None:
        return jsonify({"error": "DataManager not loaded or CSV missing."}), 500

    city_param = get_city_param()
    if not city_param:
        return jsonify({"error": "Missing city parameter"}), 400

    try:
        return process_city_request(data_manager, city_param)
    except OSError as e:
        return jsonify({"error": f"Data error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_city_param() -> str:
    """
    Extracts and validates the 'city' query parameter from the request.
    :return: The city parameter as a string.
    """
    return request.args.get("city", "").strip()


def process_city_request(data_manager: DataManager, city_param: str):
    """
    Processes the request for a specific city, including filtering and building the response.
    :param data_manager: The DataManager instance to query.
    :param city_param: The city name to filter.
    :return: A Flask JSON response with the results or an error message.
    """
    matching_df = data_manager.filter_by_city(city_param)
    if matching_df.is_empty():
        return jsonify({"error": f"No addresses found for city: {city_param}"}), 404

    unique_addresses = matching_df.unique().to_dicts()
    return jsonify({
        "city": city_param,
        "total_matches": len(unique_addresses),
        "unique_addresses": unique_addresses
    }), 200


def create_app() -> Flask:
    """
    Creates and configures the Flask app, loading the DataManager once.
    """
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, "df_files", "addresses.csv")

    data_manager = initialize_data_manager(csv_file)
    app.config["data_manager"] = data_manager

    @app.route("/addresses", methods=["GET"])
    def get_addresses():
        """Route handler for /addresses."""
        dm = current_app.config["data_manager"]
        return handle_addresses_route(dm)

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True)
