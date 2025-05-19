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

    def __init__(self):
        self.bs = BlackScholesPricing
        self.mc = MonteCarloPricing
        
    def select_pricing_model(self,contract):
        # print("bs class:", self.bs)                                # Checking bs class - debugging
        if contract.T < (365 / 365):                                 # I just set a standard rule to ensure BlackScholesPricing is always chosen for now. T seems to be stored as a string
            return self.bs(contract)
        else:
            return self.mc(contract)



class PricingModel(ABC):
    """Initialize an abstract class for pricing algorithms"""

    def __init__(self, contract):
        self.contract = contract                                    # Initializing to not have to keep writing "self.contract"
        self.S = contract.S                                         # Code is more readable
        self.K = contract.K
        self.T = contract.T
        self.r = contract.r
        self.sigma = contract.sigma
        self.type = contract.type

    @abstractmethod
    def compute_price(self):
        pass

    @abstractmethod
    def get_pricing_model_name(self):
        pass


class BlackScholesPricing(PricingModel):
    """Black Scholes pricing algorithm"""
    def __init__(self, contract):
        super().__init__(contract)
    
    def compute_price(self):
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        
        if self.type == "Call":
            return self.S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        elif self.type == "Put":
            return self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        else:
            return None
        
    def get_pricing_model_name(self):                                     # Used this to try and print a string to the instantiated Base Contract for the type of calc used instead of an address.
        return "Black Scholes Pricing"

  
class MonteCarloPricing(PricingModel):
    """Monte Carlo pricing algorithm"""
    def __init__(self, contract):
        super().__init__(contract)

    def compute_price(self, simulations=1000):                            # Placeholder for monte carlo - fully understand the sim before implementing
        return 0    
    
    def get_pricing_model_name(self):
        return "Monte Carlo Pricing"


# Expand for Binomial Pricing (future work).

class PriceDifference:
    
    def __init__(self, contract):
        self.contract = contract
        self.price_difference = None
        self.price_difference_percent = None

    def compute_price_difference(self):
        if self.contract.fair_value is not None and self.contract.ask is not None:
            self.price_difference = self.contract.fair_value - self.contract.ask
            
    def compute_price_difference_percent(self):        
        if self.contract.fair_value is not None and self.contract.ask is not None:
            self.price_difference_percent = ((self.contract.fair_value / self.contract.ask) - 1) * 100
        else:
            self.price_difference_percent = 0   

class Greeks:

    def __init__(self, contract):
        self.contract = contract                                    # Initializing to not have to keep writing "self.contract"
        self.S = contract.S                                         # Code is more readable
        self.K = contract.K
        self.T = contract.T
        self.r = contract.r
        self.sigma = contract.sigma
        self.type = contract.type
        self.pricing_model_name = contract.pricing_model_name
        self.d1, self.d2 = self.calculate_d1_d2()
        
    def calculate_d1_d2(self):                                      # Eliminate the need to recalc d1 and d2
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        #print(f"Calculated d1: {d1}, d2: {d2}")                     # Debug
        return d1, d2

    def compute_greeks(self):
        # Calculate Greeks on demand, depending on pricing model used
        if self.pricing_model_name == "Black Scholes Pricing":
            self.delta = self.calculate_delta()
            self.gamma = self.calculate_gamma()
            self.vega = self.calculate_vega()
            self.theta = self.calculate_theta()
            self.rho = self.calculate_rho()

    def calculate_delta(self):
        if self.type == "Call":
            self.delta = norm.cdf(self.d1)
        elif self.type == "Put":
            self.delta = norm.cdf(self.d1) - 1
        return self.delta

    def calculate_gamma(self):
        self.gamma = norm.pdf(self.d1) / (self.S * self.sigma * np.sqrt(self.T))
        return self.gamma

    def calculate_vega(self):
        self.vega = self.S * norm.pdf(self.d1) * np.sqrt(self.T) / 100          # Scaled for a 1% change
        return self.vega
    
    def calculate_theta(self):
        if self.type == "Call":
            theta = (-self.S * norm.pdf(self.d1) * self.sigma) / (2 * np.sqrt(self.T)) - self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)     
        elif self.type == "Put":
            theta = (-self.S * norm.pdf(self.d1) * self.sigma) / (2 * np.sqrt(self.T)) + self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2)    
        self.theta = theta / 365                                                                # Scaled daily
        return self.theta

    def calculate_rho(self):
        if self.type == "Call":
            rho = self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2)
        elif self.type == "Put":
            rho = -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2)   
        self.rho = rho / 100                                                                    # Scaled 1% change
        return self.rho