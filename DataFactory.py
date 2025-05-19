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
from Corra import get_latest_corra

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
               
        try:                                              # Fetching CORRA rate - can be changed in future to add a spread. 
            corra_rate = get_latest_corra()
        except Exception as e:
            print(f"Warning: Could not fetch CORRA. Using default rate of 2.75%. Error: {e}")
            corra_rate = 0.0275
        
        pricing_factory = pf.PricingModelFactory()        # Initializing PricingModelFactory

        for _, row in df.iterrows():

            contract = ContractLoader.assign_contract_type(row, corra_rate)
            ContractLoader.apply_correct_pricing(contract, pricing_factory)                 # Consider doing a filter to only price ITM contracts
            ContractLoader.apply_price_difference(contract)
            ContractLoader.calculate_greeks(contract)
            
            if contract.price_difference > 0:                                   # Only append contracts that have a positive trading edge  
                contract_data.append(contract)

        return contract_data

    @staticmethod
    def assign_contract_type(row, corra_rate):                          

        name = row["contractSymbol"] 
        underlying_price = row["Underlying_Price"] 
        strike_price = row["strike"] 
        itm = row["inTheMoney"]
        ttm = row["ttm"] 
        risk_free_rate = corra_rate 
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