import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Initialize session state for storing charts
if 'saved_charts' not in st.session_state:
    st.session_state.saved_charts = {}


# Load your data
@st.cache_data
def load_data():
    data = pd.read_csv("df_balance.csv", parse_dates=["Date"])
    return data


# Main app function
def main():
    st.markdown("<h1 style='font-size: 40px;'>European Monthly Storage Forecast</h1>", unsafe_allow_html=True)

    # Load data
    data = load_data()

    # Filter for forecasted months
    current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    forecast_data = data[data['Date'] >= current_date]

    # Sidebar for chart management
    st.sidebar.header("Chart Management")

    # User inputs for adjustments
    selected_columns = st.multiselect(
        "Select variables to adjust:",
        ['EU27+UK', 'Demand', 'Algeria', 'Azerbaijan', 'Libya', 'Russia', 'Turkey', 'NOR Pipe', 'LNG']
    )

    # Adjustment inputs
    adjustment_values = {}
    for col in selected_columns:
        adjustment_values[col] = st.number_input(f"Adjust {col} by (%)", min_value=-100, max_value=100, value=0)

    # Month selection for Demand adjustment
    if 'Demand' in selected_columns:
        month_range = pd.date_range(start=forecast_data['Date'].min(), end=forecast_data['Date'].max(), freq='MS')
        selected_months = st.multiselect("Select months to adjust Demand (default is all)", month_range,
                                         default=month_range)
    else:
        selected_months = []

    # Apply adjustments
    def apply_adjustments(data, adjustment_values, selected_months):
        adjusted_data = data.copy()
        for col, percent in adjustment_values.items():
            if col == 'Demand' and selected_months:
                adjusted_data.loc[adjusted_data['Date'].isin(selected_months), col] = \
                    adjusted_data.loc[adjusted_data['Date'].isin(selected_months), col] * (1 + percent / 100)
            else:
                adjusted_data[col] = adjusted_data[col] * (1 + percent / 100)

        # Recalculate Net_injection and Storage
        first_index = adjusted_data['Storage_FC_normal'].first_valid_index()
        adjusted_data['Net_injection_changes'] = (
                (adjusted_data['EU27+UK'] + adjusted_data['Algeria'] + adjusted_data['Azerbaijan'] +
                 adjusted_data['Libya'] + adjusted_data['Russia'] + adjusted_data['Turkey'] +
                 adjusted_data['NOR Pipe'] + adjusted_data['LNG'] - adjusted_data['Demand']) -
                adjusted_data['Net_injection_normal']
        )
        adjusted_data['Net_injection_final'] = adjusted_data['Net_injection_normal'] + adjusted_data[
            'Net_injection_changes']

        # Update storage forecast
        adjusted_data.loc[first_index + 1:, 'Storage_FC_normal'] = adjusted_data.loc[first_index + 1:,
                                                                   'Net_injection_final']
        adjusted_data.loc[first_index:, 'Storage_FC_normal'] = adjusted_data.loc[first_index:,
                                                               'Storage_FC_normal'].cumsum()

        return adjusted_data

    # Apply adjustments
    adjusted_data = apply_adjustments(forecast_data, adjustment_values, selected_months)

    # Merge with historical data
    df_merge = pd.concat([adjusted_data, data.loc[data['Date'] < current_date]], axis=0).sort_values(by='Date')

    # Create Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_merge['Date'], y=df_merge['Storage'], mode='lines', name='Storage',
                             line=dict(color='blue', shape='spline')))
    fig.add_trace(go.Scatter(x=df_merge['Date'], y=df_merge['Storage_FC_normal'], mode='lines', name='Storage Forecast',
                             line=dict(color='orange', dash='dash', shape='spline')))

    fig.update_layout(
        title="European Storage Forecast Over Time",
        yaxis_title="TWh",
        legend_title="Legend",
        hovermode="x unified"
    )

    # Display the chart
    st.plotly_chart(fig)

    # Chart saving functionality
    chart_name = st.text_input("Enter a name for this chart:")
    if st.button("Save Current Chart") and chart_name:
        st.session_state.saved_charts[chart_name] = {
            'figure': fig,
            'adjustments': adjustment_values,
            'selected_months': selected_months
        }
        st.success(f"Chart '{chart_name}' saved successfully!")

    # Chart comparison section
    st.markdown("## Compare Saved Charts")

    # Select charts to compare
    comparison_charts = st.multiselect("Select charts to compare:", list(st.session_state.saved_charts.keys()))

    if comparison_charts:
        # Create a comparison figure
        comparison_fig = go.Figure()

        # Add original storage trace
        comparison_fig.add_trace(go.Scatter(
            x=df_merge['Date'],
            y=df_merge['Storage'],
            mode='lines',
            name='Original Storage',
            line=dict(color='blue', shape='spline')
        ))

        # Add traces for saved charts
        colors = ['red', 'green', 'purple', 'brown']
        for i, chart_name in enumerate(comparison_charts):
            saved_chart = st.session_state.saved_charts[chart_name]['figure']
            comparison_fig.add_trace(saved_chart.data[1].update(
                name=f'{chart_name} Forecast',
                line=dict(color=colors[i % len(colors)], dash='dash', shape='spline')
            ))

        comparison_fig.update_layout(
            title="Comparison of Storage Forecasts",
            yaxis_title="TWh",
            legend_title="Legend",
            hovermode="x unified"
        )

        # Display comparison chart
        st.plotly_chart(comparison_fig)

        # Display adjustments for comparison
        st.markdown("### Adjustments for Compared Charts")
        for chart_name in comparison_charts:
            st.write(f"**{chart_name}** Adjustments:")
            saved_data = st.session_state.saved_charts[chart_name]
            st.write(saved_data['adjustments'])
            if 'selected_months' in saved_data and saved_data['selected_months']:
                st.write("Adjusted Months:", saved_data['selected_months'])


# Run the app
if __name__ == "__main__":
    main()