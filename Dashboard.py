"""
Filename: main.py
Author: Alex Kolodinsky
Created: 2025-05-04
Description: 
    Try to implement factory method.
"""

import streamlit as st
import pandas as pd
import numpy as np
import main
from datetime import datetime
from Corra import get_latest_rates
import plotly.graph_objects as go
from scipy.interpolate import make_interp_spline


# Initialization - store time of last run
if "last_run" not in st.session_state:
    st.session_state.last_run = "Not run yet"

if "model_run" not in st.session_state:
    st.session_state.model_run = False

st.header("Options Pricing Model")

column1, column2 = st.columns([3, 1])

with column1:
# Dashboard button to re-run program    
    if st.button("Run Pricing Model & Update CSV"):
        with st.spinner("Running pricing model..."):
            main.main()  # call the function from your main.py
            st.session_state.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.model_run = True
            st.success(f"CSV updated! Last run time: {st.session_state.last_run}")

    try:
        rates = get_latest_rates()  # Reuse this call or pass it in
        maturity_labels = ["Overnight", "1M", "3M", "6M", "1Y"]
        x_vals = np.array([0.0027, 1/12, 3/12, 6/12, 1.0])  # in years
        y_vals = np.array([
            rates['CORRA'],
            rates['1m'],
            rates['3m'],
            rates['6m'],
            rates['1y'],
        ])

        #fig = go.Figure()
        #fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines+markers', name='Yield Curve'))
        #Commented out the linear interpolation in favor of quadratic
        spline = make_interp_spline(x_vals, y_vals, k=2)  # k=2 quadratic
        x_smooth = np.linspace(x_vals.min(), x_vals.max(), 300)
        y_smooth = spline(x_smooth)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_smooth, y=y_smooth, mode='lines', name='Yield Curve', showlegend = False))
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', name='Observed Points', showlegend = False))        
        fig.update_layout(
            title="Short-Term Yield Curve",
            xaxis_title="Maturity (Years)",
            yaxis_title="Rate",
            margin=dict(l=10, r=10, t=30, b=10),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Yield curve could not be rendered: {e}")        

with column2:
    # Create Corra
    try:
        rates = get_latest_rates()  # returns a dictionary now
        st.metric("CORRA Rate", f"{rates['CORRA']*100:.2f}%")
        st.metric("T-Bill 1 Month", f"{rates['1m']*100:.2f}%")
        st.metric("T-Bill 3 Months", f"{rates['3m']*100:.2f}%")
        st.metric("T-Bill 6 Months", f"{rates['6m']*100:.2f}%")
        st.metric("T-Bill 1 Year", f"{rates['1y']*100:.2f}%")

    except Exception as e:
        st.error(f"Could not fetch CORRA/T-Bill data: {e}")

if st.session_state.model_run:
    st.session_state.model_run = False

df = pd.read_csv('profitable_contracts_output.csv')

# Create Select Column
if "Select" not in df.columns:
    df.insert(0, "Select", False)

# Sidebar Filters
st.sidebar.header("Filters")

# Contract type filter
st.sidebar.subheader("Contract Type:")
contract_options = df["Type"].unique()
selected_contract_type = st.sidebar.pills(
    label = "Select Contract Type(s)",
    selection_mode = "multi",
    options = contract_options,
    default = contract_options
)
# Change boolean values to str for dashboard
df["Moneyness"] = df["In The Money"].map({True: "In the Money", False: "Out of the Money"})

# ITM filter
st.sidebar.subheader("Moneyness Filter:")
moneyness = df["Moneyness"].unique()
selected_moneyness = st.sidebar.pills(
    label = "Filter by Moneyness",
    selection_mode = "multi",
    options = moneyness,
    default = moneyness
)

# **Sort by Trading Edge**
st.sidebar.subheader("Price Difference (%):")
sort_order = st.sidebar.radio(
    "Sort Order:", 
    ["Low-to-High", "High-to-Low"],
)

#Trading Edge slide filter
min_price_difference = st.sidebar.slider(
    "Minimum Price Difference (%)",
    min_value=0.0,
    max_value=float(df["Price Difference"].max()),
    value=0.0,
    step=0.1
)

#Company Filter
st.sidebar.subheader("Sort by Company")
selected_companies = st.sidebar.multiselect(
    "Select Company to Filter:",  # Non-empty label for accessibility
    options=df["Company"].unique(),
    default=df["Company"].unique(),
    #label_visibility="hidden"  # Hides the label visually while keeping accessibility intact
)

st.sidebar.markdown(
    "[![GitHub - Option Pricing Model](https://img.shields.io/badge/Github:_-Option_Pricing_Model_Repository-brightgreen)](https://github.com/AlexKolodinsky/OptionPricingModel) \n"
    "![Author: Alex Kolodinsky](https://img.shields.io/badge/Author:-Alex_Kolodinsky-blue)    \n"
    "![Date: 2025-05-10](https://img.shields.io/badge/Date:-2025--05--20-lightgrey)    \n"
)

# Applying all filtering
filtered_df = df[
    (df["Company"].isin(selected_companies)) & 
    (df["Price Difference"] >= min_price_difference) &
    (df["Type"].isin(selected_contract_type)) &
    (df["Moneyness"].isin(selected_moneyness))
    ].copy()

# Remove boolean ITM column
filtered_df = filtered_df.drop(columns=["In The Money"])

#apply sorting by trading edge
filtered_df = filtered_df.sort_values(
    by="Price Difference", ascending=(sort_order == "Low-to-High"))

# Selection state
if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

def handle_selection(index):
    for i in range(len(filtered_df)):
        df.at[i, "Select"] = False
    df.at[index, "Select"] = True
    st.session_state.selected_index = index
    

# **Editable table with checkboxes**
st.subheader("Options Contracts:")
st.write("The following options displayed have a calculated value greater than their current market ask")
st.info("Select one contract at a time to expand data")
# Track Selected Contract in Session State
edited_df = st.data_editor(filtered_df, key="editor", use_container_width=True)
selected_rows = edited_df[edited_df["Select"] == True]

if not selected_rows.empty:
    selected_index = selected_rows.index[0]
    st.session_state.selected_index = selected_index
    #Deselect everything else
    df["Select"] = False
    df.loc[selected_index, "Select"] = True

# Display selected contract details
if st.session_state.selected_index is not None:
    selected_contract = df.loc[st.session_state.selected_index].to_dict()
    st.write("### Contract Details")
    st.json(selected_contract)

