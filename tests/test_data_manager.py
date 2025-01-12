import sys

import pytest
import polars as pl
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_manager import DataManager

@pytest.fixture
def sample_csv(tmp_path):
    """
    Creates a small CSV file with city/street data in a temporary directory.
    Returns the path to that CSV.
    """
    csv_content = """city,street
Madrid,CALLE PALMA
Barcelona,RAMBLA DE CATALUNYA
Madrid,CALLE GRAN VIA
"""
    csv_file = tmp_path / "addresses.csv"
    csv_file.write_text(csv_content)
    return csv_file

def test_csv_exists(sample_csv):
    """
    Ensure our fixture indeed creates a CSV file.
    """
    assert sample_csv.exists(), "CSV file should exist"
    assert sample_csv.stat().st_size > 0, "CSV file should not be empty"

def test_init_with_csv_only(sample_csv):
    """
    Test DataManager __init__ when CSV exists (no Parquet yet).
    Should not raise FileNotFoundError.
    """
    try:
        dm = DataManager(str(sample_csv))
    except FileNotFoundError:
        pytest.fail("DataManager raised FileNotFoundError unexpectedly!")

def test_init_no_files(tmp_path):
    """
    Test DataManager __init__ if neither CSV nor Parquet is present.
    Should raise FileNotFoundError.
    """
    missing_csv = tmp_path / "non_existent.csv"
    with pytest.raises(FileNotFoundError):
        DataManager(str(missing_csv))  # No CSV & no addresses.parquet

def test_load_data_creates_parquet(sample_csv):
    """
    If only CSV exists, load_data() should create addresses.parquet and then read it.
    """
    dm = DataManager(str(sample_csv))
    lazy_df = dm.load_data()  # Should create addresses.parquet in the same folder
    assert isinstance(lazy_df, pl.LazyFrame)

    # Check that the parquet file got created
    base_dir = os.path.dirname(str(sample_csv))
    parquet_file = os.path.join(base_dir, "addresses.parquet")
    assert os.path.exists(parquet_file), "Parquet file was created"

def test_load_data_if_parquet_already_exists(sample_csv):
    """
    Ensure that if addresses.parquet already exists, we skip CSV conversion step.
    We do this by calling load_data() once,
    then 'removing' the CSV to confirm the second load doesn't fail.
    """
    dm = DataManager(str(sample_csv))
    dm.load_data()  # Creates addresses.parquet

    # Remove the CSV to prove we don't need it anymore
    os.remove(str(sample_csv))

    # Re-call load_data(); if properly designed, it loads from addresses.parquet instead
    lazy_df_2 = dm.load_data()
    assert isinstance(lazy_df_2, pl.LazyFrame)

def test_filter_by_city(sample_csv):
    """
    Test filtering by a known city.
    Should return rows that match 'Madrid' ignoring case.
    """
    dm = DataManager(str(sample_csv))
    df_result = dm.filter_by_city("madrid")  # Case-insensitive
    assert not df_result.is_empty()
    # We had "Madrid" in 2 lines (CALLE PALMA, CALLE GRAN VIA)
    assert df_result.shape[0] == 2
    streets = df_result.select("street").to_series().to_list()
    assert "CALLE PALMA" in streets
    assert "CALLE GRAN VIA" in streets

def test_filter_by_unknown_city(sample_csv):
    """
    If we filter by a city not in the data, we should get an empty DataFrame.
    """
    dm = DataManager(str(sample_csv))
    df_result = dm.filter_by_city("UnknownCity")
    assert df_result.is_empty()
