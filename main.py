import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Title and Description
st.title("Clothing Price Forecast Tool")
st.write("Adjust parameters to dynamically forecast clothing prices based on business metrics.")

# Input Parameters
num_clients = st.slider("Number of Clients", min_value=100, max_value=10000, value=1000, step=100)
num_stores = st.slider("Number of Stores", min_value=1, max_value=100, value=10, step=1)
avg_cloth_cost = st.number_input("Average Cost to Produce a Clothing Item ($)", min_value=1.0, value=20.0)
markup = st.slider("Markup Percentage (%)", min_value=10, max_value=300, value=50, step=10)

# Forecast Calculation
demand_factor = num_clients / 1000
supply_factor = num_stores / 10
base_price = avg_cloth_cost * (1 + markup / 100)
forecast_price = base_price * demand_factor / supply_factor

# Display Results
st.subheader("Forecasted Price Per Clothing Item")
st.write(f"${forecast_price:.2f}")

# Sensitivity Analysis
st.subheader("Sensitivity Analysis")
client_range = np.linspace(100, 10000, 100)
price_sensitivity = [
    base_price * (clients / 1000) / supply_factor for clients in client_range
]
plt.figure(figsize=(8, 5))
plt.plot(client_range, price_sensitivity, label="Forecasted Price")
plt.axhline(forecast_price, color="red", linestyle="--", label="Current Forecast")
plt.xlabel("Number of Clients")
plt.ylabel("Clothing Price ($)")
plt.title("Sensitivity Analysis: Price vs. Number of Clients")
plt.legend()
st.pyplot(plt)
