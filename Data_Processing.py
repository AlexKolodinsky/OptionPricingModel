"""
Filename: Data_Processing.py
Author: Alex Kolodinsky
Created: 2025-05-03
Description: 
    Create a dataset to store option parameters.
"""
#Libraries 

from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt


tickers = ["AAPL", "NVDA", "MSFT", "GOOG", "TSLA", "V", "JPM", "AMZN", "AVGO", "PLTR"]                                  # This can be fed in by the user in the future

def compile_options_data(ticker_symbol):                                            # Compiles put and call options data for a singular ticker
    ticker = yf.Ticker(ticker_symbol)
    options_dates = ticker.options
    
    if not options_dates:
        return None
    
    expiry = options_dates[0]                                                        # options with the earliest expiry
    expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
    today = datetime.today()
    ttm_days = (expiry_date - today).days
    ttm_years = ttm_days / 365                                                       # Calculate ttm in days.

    stock_data = ticker.history(period="1y")                                         # Attempt at calculating volatility from online resources.
    returns = stock_data["Close"].pct_change().dropna()                              # Assuming volatility should be dependant on ttm.
    rolling_window = max(5, int(ttm_days))                                           # Annualied volatility doesnt make sense for short ttm options
    rolling_volatility = returns.rolling(window=rolling_window).std()
    scaled_volatility = rolling_volatility * np.sqrt(252)
    latest_volatility = scaled_volatility.iloc[-1]
   
    options_chain = ticker.option_chain(expiry)                                     # Option_dates[0] = nearest expiry date
    close_price = ticker.info.get("previousClose")                                  # Fetches underlying price at close (did this for simplicity)
   
    calls = options_chain.calls.assign(
        Ticker=ticker_symbol, 
        Type="Call", 
        Underlying_Price = close_price, 
        Vol = latest_volatility, 
        rfr = 0.0275,                                                               # I looked this value up - in the future this should be dynamic
        ttm = ttm_years
    )
    
    puts = options_chain.puts.assign(
        Ticker=ticker_symbol, 
        Type="Put", 
        Underlying_Price = close_price, 
        Vol = latest_volatility, 
        rfr = 0.0275, 
        ttm = ttm_years
    )    
    calls = calls[(calls['bid'] != 0) & (calls['ask'] != 0)]                        # Removing any call / put that has a bid or ask of 0
    puts = puts[(puts['bid'] != 0) & (puts['ask'] != 0)]

    return pd.concat([calls, puts])                                                 # Concatinating calls and puts data using pandas 

def combine_options_data(tickers):                                                  # Combining data from compile_options_data function and list "tickers"
    options_data_list = []
    for ticker in tickers:
        data = compile_options_data(ticker)
        if data is not None:
            options_data_list.append(data)

    return pd.concat(options_data_list, ignore_index=True) if options_data_list else None       #Checks to see if the options data list is emptly before returning, done to prevent crashes (found)

def create_csv(tickers, filename="contract_data.csv"):                                 # Saves options data into a single csv
    contract_data = combine_options_data(tickers)
    if contract_data is not None:
        contract_data.to_csv(filename, index=False)
        print(f"Options data successfully saved to {filename}")
    else:
        print("No options data found")

create_csv(tickers)

"""------------------------------------------------------------------------------------------------------------------------------------------------------"""