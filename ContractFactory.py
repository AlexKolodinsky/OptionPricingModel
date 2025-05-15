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
    def __init__(self, name, underlying_price, strike_price, itm, ttm, risk_free_rate, volatility, contract_type, ask):
        self.name = name
        self.S = underlying_price
        self.K = strike_price
        self.itm = itm
        self.T = ttm                           # Already in years
        self.r = risk_free_rate
        self.sigma = volatility
        self.type = contract_type
        self.ask = ask

        # Calculated later  - initialization
        self.fair_value = None
        self.trading_edge = None
        self.trading_edge_percent = None
        self.pricing_model_name = None

        # Greeks
        self.delta = None
        self.gamma = None
        self.vega = None
        self.theta = None
        self.rho = None

            
    def __str__(self):
        return f"{self.name} {self.S} {self.K} {self.T} {self.r} {self.sigma} {self.type} {self.ask}, {self.fair_value}, {self.trading_edge}, {type(self.pricing_model).__name__}, {self.delta}, {self.gamma}, {self.vega}, {self.theta}, {self.rho}"


"""Further Separate Base Contract into Types of Contracts"""

class CallOption(BaseContract):
    
    def payoff(self):
        return max(0, self.S - self.K)
    
    def in_the_money(self):
        return self.S > self.K
                            
        
class PutOption(BaseContract):
    def payoff(self):
        return max(0, self.K - self.S)
    
    def in_the_money(self):
        return self.S < self.K

class VerticalSpread(BaseContract):
    pass                    # Future use - same maturity, different strike

class HorizontalSpread(BaseContract):    
    pass                    # Future use - different maturity, same strike (will have to change the way our data is imported)

class DiagonalSpread(BaseContract):
    pass

# Fully flush out key differences of each contract that would be valuable to users and enter here
# Expand in the future for different types of contract subclasses