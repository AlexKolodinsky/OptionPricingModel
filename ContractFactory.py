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
import PricingFactory as pf
import DataFactory as df


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

        # Calculated later
        self.calc_price = None
        self.trading_edge = None
        self.trading_edge_percent = None
        self.pricing_model_name = None

    @abstractmethod
    def apply_correct_pricing(self):
        pricing_model = pf.PricingModelFactory.select_pricing_model(self)
        
        if pricing_model:                                                           # Changed from self.pricing_model since i dont need to store this

            self.calc_price = pricing_model.compute_price()
            self.pricing_model_name = pricing_model.get_pricing_model_name()
        
        self.compute_trading_edge()
        self.compute_trading_edge_percent()
    
    def compute_trading_edge(self):
        if self.calc_price is not None:
            self.trading_edge = self.calc_price - self.ask

    def compute_trading_edge_percent(self):
        if self.trading_edge is not None and self.ask != 0:                             # Divide by 0 - to improve this i should better filter my data set.
            self.trading_edge_percent = ((self.calc_price / self.ask) - 1) * 100
        else:
            self.trading_edge_percent = 0                                               # Placeholder solution for the divide by 0 case

            
    def __str__(self):
        return f"{self.name} {self.S} {self.K} {self.T} {self.r} {self.sigma} {self.type} {self.ask}, {self.calc_price}, {self.trading_edge}, {type(self.pricing_model).__name__}"


"""Further Separate Base Contract into Types of Contracts"""

class CallOption(BaseContract):
    def apply_correct_pricing(self):
        super().apply_correct_pricing()                     # Super is used for subclasses
        

class PutOption(BaseContract):
    def apply_correct_pricing(self):                        
        super().apply_correct_pricing()                     # Super is used for subclasses


# Fully flush out key differences of each contract that would be valuable to users and enter here
# Expand in the future for different types of contract subclasses