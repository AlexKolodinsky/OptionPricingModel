import streamlit as st
import pandas as pd
import numpy as np
import main
from datetime import datetime

# Initialization - store time of last run
if "last_run" not in st.session_state:
    st.session_state.last_run = "Not run yet"

# Dashboard button to re-run program    
if st.button("Run Pricing Model & Update CSV"):
    with st.spinner("Running pricing model..."):
        main.main()  # call the function from your main.py
        st.session_state.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success("CSV updated!")
        st.rerun()
        
#Display the last time the dashboard was run
st.write(f"Last run time: {st.session_state.last_run}")

df = pd.read_csv(r'C:\Users\alex.kolodinsky_motu\Desktop\OptionPricingModel-main/profitable_contracts_output.csv', header=0)

# Create Select Column
if "Select" not in df.columns:
    df.insert(0, "Select", False)


#Sidebar Filters
st.sidebar.header("Filters")


# **Sort by Trading Edge**
st.sidebar.write("### Sort by Trading Edge (%):")
sort_order = st.sidebar.radio(
    "Sort Order:", 
    ["Low-to-High", "High-to-Low"],
)

#Trading Edge slide filter
min_edge = st.sidebar.slider(
    "Minimum Trading Edge (%)",
    min_value=0.0,
    max_value=float(df["Percent_Edge"].max()),
    value=0.0,
    step=0.1
)
#Company Filter
st.sidebar.write("### Sort by Company")
selected_companies = st.sidebar.multiselect(
    "Filter by Company",  # Non-empty label for accessibility
    options=df["Company"].unique(),
    default=df["Company"].unique(),
    label_visibility="hidden"  # Hides the label visually while keeping accessibility intact
)


# Apply filtering

# Company filtering
filtered_df = df[
    (df["Company"].isin(selected_companies)) & 
    (df["Percent_Edge"] >= min_edge)
    ].copy()

#apply sorting by trading edge
filtered_df = filtered_df.sort_values(
    by="Percent_Edge", ascending=(sort_order == "Low-to-High"))

# Selection state
if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

def handle_selection(index):
    for i in range(len(filtered_df)):
        df.at[i, "Select"] = False
    df.at[index, "Select"] = True
    st.session_state.selected_index = index
    

# **Editable table with checkboxes**
st.write("### Profitable Options Contracts:")
st.write("Select one at a time to expand data")
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

