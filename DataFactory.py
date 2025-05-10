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
        
        df.dropna(subset=["Type", "ask"], inplace=True)          # Filtering dataset
        df["Type"] = df["Type"].astype(str).str.strip()
        df = df[df["ask"] != 0]
       
        pricing_factory = pf.PricingModelFactory()        # Using dependency injection to help with previous pricing memory issue.
        
        for _, row in df.iterrows():
            contract_type = row["Type"] 

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
            
            ContractLoader.apply_correct_pricing(contract, pricing_factory)                 # Consider dding a filter to only price ITM contracts
            ContractLoader.apply_trading_edge(contract)
            
            if contract.trading_edge > 0:                                   # Only append contracts that have a positive trading edge  
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

    @staticmethod
    def apply_correct_pricing(contract, pricing_model):
        pricing_model = pricing_model.select_pricing_model(contract)
        
        if pricing_model:
            contract.calc_price = pricing_model.compute_price()
            contract.pricing_model_name = pricing_model.get_pricing_model_name()

    @staticmethod
    def apply_trading_edge(contract):
        # Create and apply TradingEdge logic
        trading_edge = pf.TradingEdge(contract)
        trading_edge.compute_trading_edge()
        trading_edge.compute_trading_edge_percent()

        # Store the calculated values back into the BaseContract instance
        contract.trading_edge = trading_edge.trading_edge
        contract.trading_edge_percent = trading_edge.trading_edge_percent