import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go

# Load your data
data = pd.read_csv("df_balance.csv", parse_dates=["Date"])

# Filter for forecasted months (based on current date)
current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
forecast_data = data[data['Date'] >= current_date]

# User inputs with direct input for figures
st.markdown("<h1 style='font-size: 40px;'>European Monthly Storage Forecast</h1>", unsafe_allow_html=True)

selected_columns = st.multiselect(
    "Select variables to adjust:",
    ['EU27+UK', 'Demand', 'Algeria', 'Azerbaijan', 'Libya', 'Russia', 'Turkey', 'NOR Pipe', 'LNG']
)

adjustment_values = {}
for col in selected_columns:
    adjustment_values[col] = st.number_input(f"Adjust {col} by (%)", min_value=-100, max_value=100, value=0)

# If Demand is selected, allow month selection
if 'Demand' in selected_columns:
    month_range = pd.date_range(start=forecast_data['Date'].min(), end=forecast_data['Date'].max(), freq='MS')
    selected_months = st.multiselect("Select months to adjust Demand (default is all)", month_range, default=month_range)

# Apply adjustments only to forecasted months
adjusted_data = forecast_data.copy()
for col, percent in adjustment_values.items():
    if col == 'Demand' and selected_months:
        adjusted_data.loc[adjusted_data['Date'].isin(selected_months), col] = adjusted_data.loc[adjusted_data['Date'].isin(selected_months), col] * (1 + percent / 100)
    else:
        adjusted_data[col] = adjusted_data[col] * (1 + percent / 100)

# Recalculate Net_injection_normal
adjusted_data['Net_injection_changes'] = (
    (adjusted_data['EU27+UK'] + adjusted_data['Algeria'] + adjusted_data['Azerbaijan'] +
     adjusted_data['Libya'] + adjusted_data['Russia'] + adjusted_data['Turkey'] +
     adjusted_data['NOR Pipe'] + adjusted_data['LNG'] - adjusted_data['Demand']) - adjusted_data['Net_injection_normal']
)
adjusted_data['Net_injection_final'] = adjusted_data['Net_injection_normal'] + adjusted_data['Net_injection_changes']

# Refresh the storage forecast
first_index = adjusted_data['Storage_FC_normal'].first_valid_index()
adjusted_data.loc[first_index+1:, 'Storage_FC_normal'] = adjusted_data.loc[first_index+1:, 'Net_injection_final']
adjusted_data.loc[first_index:, 'Storage_FC_normal'] = adjusted_data.loc[first_index:, 'Storage_FC_normal'].cumsum()

df_merge = pd.concat([adjusted_data, data.loc[data['Date'] < current_date]], axis=0).sort_values(by='Date')

# Plotting charts
fig = go.Figure()

# Plot Storage vs Forecasted Storage
fig.add_trace(go.Scatter(x=df_merge['Date'], y=df_merge['Storage'], mode='lines', name='Storage', line=dict(color='blue', shape='spline')))
fig.add_trace(go.Scatter(x=df_merge['Date'], y=df_merge['Storage_FC_normal'], mode='lines', name='Storage Forecast', line=dict(color='orange', dash='dash', shape='spline')))

fig.update_layout(
    title="European Storage Forecast Over Time",
    yaxis_title="TWh",
    legend_title="Legend",
    hovermode="x unified"
)

st.plotly_chart(fig)
