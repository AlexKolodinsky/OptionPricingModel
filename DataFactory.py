"""
Filename: DataFactory.py
Author: Alex Kolodinsky
Created: 2025-05-06
Description: 
    Try to implement factory method.
"""

import numpy as np
import pandas as pd
import PricingFactory as pf
import ContractFactory as cf

class ContractLoader:
    """ Handles loading contracts from CSV file data and ContractFactory Parameters """
    
    csv_file = "contract_data.csv"

    @staticmethod                                         # The csv portion should be static
    def load_contract(filename=None):
        
        if filename is None:
            filename = ContractLoader.csv_file            # Allows for a default csv file.
        
        
        df = pd.read_csv(filename)                        # Reads CSV file
        contract_data = []
        
        df.dropna(subset=["Type"], inplace=True)          # Filtering dataset
        df["Type"] = df["Type"].astype(str).str.strip()
        df.dropna(subset=["ask"], inplace=True)  
        df = df[df["ask"] != 0]
       
        for _, row in df.iterrows():
            contract_type = row["Type"]
            
            # Tried a bunch of ways to precompute pricing estimate before instantiation to avoid processing unprofitable contracts
            # Tried running without trying to filter instances on a larger dataset - not great.
            # However I kept running into the problem of creating an instance just to avoid an instance.
            # For now im going to lower my dataset and figure out whats best to do, or other parameters that i could use to pre-filter contracts. 

            contract = ContractLoader.assign_contract_type(
                row["contractSymbol"], 
                row["Underlying_Price"], 
                row["strike"], 
                row["ttm"], 
                row["rfr"], 
                row["Vol"], 
                contract_type,
                row.get("ask", 0)
            )
            
            contract.apply_correct_pricing()
            if contract.trading_edge > 0:                                   # Only include contracts that have a trading edge.  
                contract_data.append(contract)

        return contract_data

    @staticmethod
    def assign_contract_type(name, underlying_price, strike_price, ttm, risk_free_rate, volatility, contract_type, ask):                          

        if contract_type == "Call":
            return cf.CallOption(name, underlying_price, strike_price, ttm, risk_free_rate, volatility, contract_type, ask)
        elif contract_type == "Put":
            return cf.PutOption(name, underlying_price, strike_price, ttm, risk_free_rate, volatility, contract_type, ask)

        else:
            raise ValueError(f"Invalid contract type: {contract_type}")

