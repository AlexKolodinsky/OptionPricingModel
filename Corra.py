import requests

def get_latest_value(observations, seriesName):
    """Safely find the latest valid value for a given series ID."""
    for entry in reversed(observations):
        if seriesName in entry and "v" in entry[seriesName]:
            return float(entry[seriesName]["v"]) / 100
    raise Exception(f"No recent value found for series {seriesName}")

def get_latest_rates():
    print("Fetching latest rates from Bank of Canada API...")  # Debug print

    corra_url = "https://www.bankofcanada.ca/valet/observations/AVG.INTWO/json"
    t_bill_series = {
        "1m": "TB.CDN.30D.MID",
        "3m": "TB.CDN.90D.MID",
        "6m": "TB.CDN.180D.MID",
        "1y": "TB.CDN.1Y.MID"
    }

    # Fetch CORRA
    corra_response = requests.get(corra_url)
    corra_response.raise_for_status()
    corra_data = corra_response.json()
    corra_observations = corra_data["observations"]

    if not corra_observations:
        raise Exception("No CORRA observations found.")

    corra = get_latest_value(corra_observations, "AVG.INTWO")
    print(f"Fetched CORRA rate: {corra:.4%}")  # Debug print

    # Fetch T-bill rates
    t_bill_rates = {}

    for label, seriesName in t_bill_series.items():
        print(f"Fetching T-Bill rate for: {label}")  # Debug print to make sure all rates are fetched
        t_bill_url = f"https://www.bankofcanada.ca/valet/observations/{seriesName}/json"
        
        response = requests.get(t_bill_url)
        response.raise_for_status()
        data = response.json()
        observations = data["observations"]

        if not observations:
            print(f"Warning: No data found for {label} T-bill.")  # Debug warning
            continue  # Skip missing data instead of raising an exception

        rate = get_latest_value(observations, seriesName)
        t_bill_rates[label] = rate  # Store the correct rate

    # Debug output
    print(f"Final Rates:\n"
          f"  CORRA:     {corra:.4%}")
    
    for label, rate in t_bill_rates.items():
        print(f"  {label.upper()} T-Bill: {rate:.4%}")  # Print all fetched rates

    return {
        "CORRA": corra,
        "1m": t_bill_rates.get("1m", None),  
        "3m": t_bill_rates.get("3m", None),
        "6m": t_bill_rates.get("6m", None),
        "1y": t_bill_rates.get("1y", None)
    }

rates = get_latest_rates()
print("Final fetched rates:", rates)  # Debug statement