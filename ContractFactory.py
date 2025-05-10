"""
Filename: ContractFactory.py
Author: Alex Kolodinsky
Created: 2025-05-06
Description: 
    Try to implement factory method.
"""
from datetime import datetime
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import DataFactory as df
import PricingModels as pf


class BaseContract(ABC):
    """ Create Base Contract Class"""                     
    def __init__(self, name, underlying_price, strike_price, ttm, risk_free_rate, volatility, contract_type, ask):
        self.name = name
        self.S = underlying_price
        self.K = strike_price
        self.T = ttm                           # Already in years
        self.r = risk_free_rate
        self.sigma = volatility
        self.type = contract_type
        self.ask = ask

        # Calculated later  - initialization
        self.calc_price = None
        self.trading_edge = None
        self.trading_edge_percent = None
        self.pricing_model_name = None
            
    def __str__(self):
        return f"{self.name} {self.S} {self.K} {self.T} {self.r} {self.sigma} {self.type} {self.ask}, {self.calc_price}, {self.trading_edge}, {type(self.pricing_model).__name__}"


"""Further Separate Base Contract into Types of Contracts"""

class CallOption(BaseContract):
    pass                    # For future use
        

class PutOption(BaseContract):
    pass                     # For future use


# Fully flush out key differences of each contract that would be valuable to users and enter here
# Expand in the future for different types of contract subclasses