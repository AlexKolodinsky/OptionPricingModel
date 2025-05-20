"""
Filename: DataFactory.py
Author: Alex Kolodinsky
Created: 2025-05-06
Description: 
    Try to implement factory method.
"""

import numpy as np
import pandas as pd
import PricingModels as pf
import ContractFactory as cf
from Corra import get_latest_rates

class ContractLoader:
    """ Handles loading contracts from CSV file data and ContractFactory Parameters """
    """ Attempt to centralize all of the pricing and trading edge actions here, instead of in the Contract class """
    
    csv_file = "contract_data.csv"

    @staticmethod                                         # The csv portion should be static
    def load_contract(filename=None):
        
        if filename is None:
            filename = ContractLoader.csv_file            # Allows for a default csv file.
        
        
        df = pd.read_csv(filename)                        # Reads CSV file
        contract_data = []
        
        df.dropna(subset=["Type", "ask"], inplace=True)   # Filter again - redundant
        df["Type"] = df["Type"].astype(str).str.strip()
        df = df[df["ask"] != 0]

              
        rates = get_latest_rates()                        # Fetch risk free rates before loop
        pricing_factory = pf.PricingModelFactory()        # Initializing PricingModelFactory

        for _, row in df.iterrows():
            contract = ContractLoader.assign_contract_type(row, rates)
            ContractLoader.apply_correct_pricing(contract, pricing_factory)               
            ContractLoader.apply_price_difference(contract)
            ContractLoader.calculate_greeks(contract)
            
            if contract.price_difference > 0:                                   # Only append contracts that are undervalued  
                contract_data.append(contract)

        return contract_data

    @staticmethod
    def assign_contract_type(row, rates):                          
        name = row["contractSymbol"] 
        underlying_price = row["Underlying_Price"] 
        strike_price = row["strike"] 
        itm = row["inTheMoney"]
        ttm = row["ttm"] 
        risk_free_rate = ContractLoader.get_risk_free_rate(row["ttm"], rates) 
        volatility = row["impliedVolatility"] 
        contract_type = row["Type"]
        ask = row["ask"]        

        if contract_type == "Call":
            return cf.CallOption(name, underlying_price, strike_price, itm, ttm, risk_free_rate, volatility, contract_type, ask)
        elif contract_type == "Put":
            return cf.PutOption(name, underlying_price, strike_price, itm, ttm, risk_free_rate, volatility, contract_type, ask)

        else:
            raise ValueError(f"Invalid contract type: {contract_type}")

    @staticmethod
    def apply_correct_pricing(contract, pricing_model):
        pricing_model = pricing_model.select_pricing_model(contract)
        
        if pricing_model:
            contract.fair_value = pricing_model.compute_price()
            contract.pricing_model_name = pricing_model.get_pricing_model_name()

    @staticmethod
    def apply_price_difference(contract):
        # Create and apply TradingEdge logic
        price_difference = pf.PriceDifference(contract)
        price_difference.compute_price_difference()
        price_difference.compute_price_difference_percent()

        # Store the calculated values back into the BaseContract instance
        contract.price_difference = price_difference.price_difference
        contract.price_difference_percent = price_difference.price_difference_percent

    @staticmethod
    def calculate_greeks(contract):
        if contract.fair_value is not None:
            greeks = pf.Greeks(contract)
            greeks.compute_greeks()
            
        contract.delta = greeks.delta
        contract.gamma = greeks.gamma
        contract.vega = greeks.vega
        contract.theta = greeks.theta
        contract.rho = greeks.rho

    @staticmethod
    def get_risk_free_rate(ttm, rates):
        if ttm <= 1/12:
            return rates.get("1m", rates["CORRA"])  # Use CORRA if missing
        elif ttm <= 3/12:
            return rates.get("3m", rates["CORRA"])
        elif ttm <= 6/12:
            return rates.get("6m", rates["CORRA"])
        else:
            return rates.get("1y", rates["CORRA"])
