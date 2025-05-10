# OptionPricingModel

Update May 10 2025: Fixed memory issues and circular redundancy.

Attempt at an option pricing model using the Factory Method design pattern. 

This model was used to gain exposure to object oriented programming, attempt to implement the Factory Method desing pattern, and attempt to design for scalability. 

This model takes a user input by running main.py, and returns all "profitable" contracts found in a .csv file.

The .csv file is populated with market data by running Data_Processing.py, and was used to help visualize data while creating the model. 

Model is a work-in-progress. I am still working on the best way to work with instances while balancing the computational overhead, and the best way to structure classes/subclasses.


Please refer to the block diagrams to further explain the design thought process. 
