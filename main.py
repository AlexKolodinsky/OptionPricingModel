"""
Filename: main.py
Author: Alex Kolodinsky
Created: 2025-05-04
Description: 
    Try to implement factory method.
"""


import ContractFactory as cf
import DataFactory as df
import PricingModels as pf
import numpy as np
import pandas as pd 
import random

def main():
    """Currently use trading edge as a proxy for profitability, however this should be changed to account for potential transaction costs or other factors """
    profitable_contracts = df.ContractLoader.load_contract()

    profitable_contracts.sort(key=lambda contract: contract.trading_edge_percent, reverse=True)         # sort

    for contract in profitable_contracts:
        print(f"Contract: {contract.name}, Type: {contract.type}, Price: {contract.calc_price:.2f}, Ask: {contract.ask:.2f}, Edge: {contract.trading_edge:.2f}, Percent Edge: {contract.trading_edge_percent:.2f} (%) ")
    
    if profitable_contracts:                                                                           # I use this to verify against csv (spot check)
        random_contract = random.choice(profitable_contracts)
        print(f"\nContract Details for: {random_contract.name}")
        
        for key, value in vars(random_contract).items(): 
            print(f"{key}: {value}")
    else:
        print("No profitable contracts available.")
    

if __name__ == "__main__":
    main()
