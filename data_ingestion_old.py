import os
from datetime import datetime
import time
import pandas as pd
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
TICKERS = {
    'JPMorgan_Chase': 'JPM',
    'Bank_of_America': 'BAC',
    'Citigroup': 'C',
    'EUR_USD': 'EURUSD'
}
OUTPUT_DIR = 'data/bronze'


def fetch_bank_data():
    """
    Fetches daily market data from Alpha Vantage API,
    cleans the columns, and saves the data to the Bronze layer.
    """
    combined_data = []

    print("--- STARTING DATA INGESTION (ALPHA VANTAGE) ---")

    for name, ticker in TICKERS.items():
        try:
            time.sleep(3)
            # Call the Alpha Vantage API for daily data
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}'
            response = requests.get(url, verify=False)
            data = response.json()

            # Check if the API returned valid data
            if "Time Series (Daily)" in data:
                raw_time_series = data["Time Series (Daily)"]
            elif "Time Series FX (Daily)" in data:
                raw_time_series = data["Time Series FX (Daily)"]
            else:
                print(f"Warning: Could not fetch {name}. API Message: {data.get('Information', data.get('Note', 'Error'))}")
                continue

            # Convert JSON response to Pandas DataFrame
            df = pd.DataFrame.from_dict(raw_time_series, orient='index')
            
            # Clean column names
            df = df.rename(columns={
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            })
            
            # Reset index and name it Datetime to match the old format
            df = df.reset_index().rename(columns={'index': 'Datetime'})
            df['Entity'] = name
            
            # Convert text values to numbers
            numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
            
            # Keep only the last 30 days of data
            df = df.head(30)
            
            # Order columns
            standard_cols = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Entity']
            df = df[standard_cols]

            combined_data.append(df)
            print(f"Successfully ingested data for: {name}")

        except Exception as e:
            print(f"Error ingesting data for {name}: {e}")

    # Save all collected data into a single CSV file
    if combined_data:
        final_df = pd.concat(combined_data, ignore_index=True)
        
        # Create output directory if it does not exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        file_path = f'{OUTPUT_DIR}/market_data_{timestamp}.csv'
        
        final_df.to_csv(file_path, index=False)
        print("--- INGESTION SUCCESSFUL ---")
        print(f"File saved to: {file_path}")
    else:
        print("--- INGESTION FAILED: No data collected ---")


if __name__ == "__main__":
    fetch_bank_data()