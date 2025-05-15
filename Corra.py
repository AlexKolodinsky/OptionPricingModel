"""
Filename: Corra.py
Author: Alex Kolodinsky
Created: 2025-05-04
Description: 
    Try to implement factory method.
"""

import requests

def get_latest_corra():
    url = "https://www.bankofcanada.ca/valet/observations/AVG.INTWO/json"
    corra_response = requests.get(url)

    if corra_response.status_code != 200:
        raise Exception("Failed to fetch CORRA data.")

    data = corra_response.json()
    observations = data["observations"]

    if not observations:
        raise Exception("No CORRA observations found.")

    latest = observations[-1]
    corra = float(latest["AVG.INTWO"]["v"])

    print(corra_response.status_code)
    
    return corra / 100 
