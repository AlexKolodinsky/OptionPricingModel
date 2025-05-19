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
import re

def main():
    """Currently use trading edge as a proxy for profitability, however this should be changed to account for potential transaction costs or other factors """
    profitable_contracts = df.ContractLoader.load_contract()

    profitable_contracts.sort(key=lambda contract: contract.price_difference_percent, reverse=True)         # sort

    for contract in profitable_contracts:
        print(f"Contract: {contract.name}, Type: {contract.type}, Price: {contract.fair_value:.2f}, Ask: {contract.ask:.2f}, Price Difference: {contract.price_difference:.2f}, Price Difference (%): {contract.price_difference_percent:.2f} (%) ")
    
    
    # Done for the dashboard. There should be a better way to call correctly from the data stored in the contract factory. (Research)
    if profitable_contracts:    
        output_data = []
        for contract in profitable_contracts:
            company_name = re.match(r'^([A-Za-z]+)', contract.name)
            company_ticker = company_name.group(1) if company_name else ""
            contract_info = {
                "Company": company_ticker,
                "Name": contract.name,
                "Type": contract.type,
                "Price Difference Percent": round(contract.price_difference_percent, 2),
                "Underlying_Price": contract.S,
                "Strike": contract.K,
                "In The Money": contract.itm,
                "Algorithm Used": contract.pricing_model_name,
                "Calculated_Price": round(contract.fair_value, 4),
                "Ask": round(contract.ask, 4),
                "Price Difference": round(contract.price_difference, 4),
                "TTM": round(contract.T, 6),
                "RFR": contract.r,
                "Volatility": round(contract.sigma, 4),
                "Delta": round(contract.delta, 4),
                "Gamma": round(contract.gamma, 4),
                "Vega": round(contract.vega, 4),
                "Theta": round(contract.theta, 4),
                "Rho": round(contract.rho, 4),

            }
            output_data.append(contract_info)

        df_output = pd.DataFrame(output_data)
        df_output.to_csv("profitable_contracts_output.csv", index=False)



    if profitable_contracts:                                                                           # I use this to verify against csv (spot check)
        random_contract = random.choice(profitable_contracts)
        print(f"\nContract Details for: {random_contract.name}")
        
        for key, value in vars(random_contract).items(): 
            print(f"{key}: {value}")
    else:
        print("No profitable contracts available.")    
    


if __name__ == "__main__":
    main()
