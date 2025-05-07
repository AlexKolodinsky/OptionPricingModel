"""
Filename: PricingFactory.py
Author: Alex Kolodinsky
Created: 2025-05-04
Description: 
    Try to implement factory method.
"""

import numpy as np
from scipy.stats import norm
from abc import ABC, abstractmethod

    

class PricingModelFactory:
    """Logic for selecting price algorithm - allows for future expansion"""
    
    @staticmethod
    def select_pricing_model(contract):
        if contract.T < (365 / 365):                                 # I just set a standard rule to ensure BlackScholesPricing is always chosen for now. T seems to be stored as a string
            return BlackScholesPricing(contract)
        else:
            return MonteCarloPricing(contract)



class PricingModel(ABC):
    """Initialize an abstract class for pricing algorithms"""

    def __init__(self, contract):
        self.contract = contract

    @abstractmethod
    def compute_price(self):
        pass

    @abstractmethod
    def get_pricing_model_name(self):
        pass

        

class BlackScholesPricing(PricingModel):
    """Black Scholes pricing algorithm"""

    def compute_price(self):
        d1 = (np.log(self.contract.S / self.contract.K) + (self.contract.r + 0.5 * self.contract.sigma**2) * self.contract.T) / (self.contract.sigma * np.sqrt(self.contract.T))
        d2 = d1 - self.contract.sigma * np.sqrt(self.contract.T)
        
        if self.contract.type == "Call":
            return self.contract.S * norm.cdf(d1) - self.contract.K * np.exp(-self.contract.r * self.contract.T) * norm.cdf(d2)
        elif self.contract.type == "Put":
            return self.contract.K * np.exp(-self.contract.r * self.contract.T) * norm.cdf(-d2) - self.contract.S * norm.cdf(-d1)
        else:
            return None
        
    def get_pricing_model_name(self):                                     # Used this to try and print a string to the instantiated Base Contract for the type of calc used instead of an address.
        return "Black Scholes Pricing"

  
class MonteCarloPricing(PricingModel):
    """Monte Carlo pricing algorithm"""

    def compute_price(self, simulations=1000):                            # Placeholder for monte carlo - fully understand the sim before implementing
        return 0    
    
    def get_pricing_model_name(self):
        return "Monte Carlo Pricing"


# Expand for Binomial Pricing (future work).



    
