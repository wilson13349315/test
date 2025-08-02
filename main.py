import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration for a wider layout
st.set_page_config(layout="wide", page_title="European Gas Storage Monitoring")

# --- Data Loading and Preprocessing ---
@st.cache_data
def load_data():
    """
    Loads the gas storage data from a CSV file and performs initial preprocessing.
    Caches the data to improve performance.
    """
    try:
        # Attempt to read with utf-8, then fall back to latin1 if UnicodeDecodeError occurs
        try:
            df = pd.read_csv('Storage.csv', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv('Storage.csv', encoding='latin1')

        # Convert 'Date' column to datetime objects
        df['Date'] = pd.to_datetime(df['Date'])
        # Ensure numerical columns are of the correct type, handling potential errors
        numerical_cols = ['gasInStorage', 'full', 'injection', 'withdrawal',
                          'workingGasVolume', 'injectionCapacity', 'withdrawalCapacity']
        for col in numerical_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("Error: Storage.csv not found. Please ensure the file is in the root directory.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
        st.stop()

df = load_data()

# Check if data loaded successfully
if df is None:
    st.stop()

# --- Country Coordinates (added based on user request) ---
country_coordinates = {
    'United Kingdom': {'latitude': 55.38, 'longitude': -3.44},
    'Czechia': {'latitude': 49.82, 'longitude': 15.47},
    'Austria': {'latitude': 47.52, 'longitude': 14.55},
    'Germany': {'latitude': 51.17, 'longitude': 10.45},
    'Hungary': {'latitude': 47.16, 'longitude': 19.5},
    'France': {'latitude': 46.23, 'longitude': 2.21},
    'Romania': {'latitude': 45.94, 'longitude': 24.97},
    'Italy': {'latitude': 42.00, 'longitude': 12.05},
    'Netherlands': {'latitude': 52.13, 'longitude': 5.29},
    'Ukraine': {'latitude': 48.38, 'longitude': 31.17},
    'Sweden': {'latitude': 62.199806, 'longitude': 17.637493},
    'Poland': {'latitude': 51.92, 'longitude': 19.15},
    'Belgium': {'latitude': 50.5, 'longitude': 4.47},
    'Spain': {'latitude': 40.46, 'longitude': -3.75},
    'Bulgaria': {'latitude': 42.73, 'longitude': 25.49},
    'Slovakia': {'latitude': 48.67, 'longitude': 19.64},
    'Latvia': {'latitude': 56.88, 'longitude': 24.6},
    'Croatia': {'latitude': 45.1, 'longitude': 15.2},
    'Denmark': {'latitude': 56.0, 'longitude': 10.0},
    'Portugal': {'latitude': 39.4, 'longitude': -8.22}
}

# --- Dashboard Title and Introduction ---
st.title("European Gas Storage Monitoring Dashboard")
st.markdown("""
    This dashboard provides a comprehensive overview of European gas storage facilities,
    offering real-time analytics, trend analysis, and country-level comparisons.
""")

# --- Sidebar for Filters ---
st.sidebar.header("Filters")

# Date Range Slider
min_date = df['Date'].min().to_pydatetime()
max_date = df['Date'].max().to_pydatetime()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
else:
    filtered_df = df.copy()
    st.sidebar.warning("Please select a complete date range.")


# Country Multiselect with 'All' option
all_countries = sorted(filtered_df['Country'].unique().tolist())
country_options = ["All"] + all_countries

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=country_options,
    default=["All"]
)

# If 'All' is selected or nothing is selected, use all countries
if "All" in selected_countries or not selected_countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(all_countries)]
else:
    filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]

# Facility Multiselect
all_facilities = sorted(filtered_df['Name'].unique().tolist())
selected_facilities = st.sidebar.multiselect(
    "Select Facilities",
    options=all_facilities,
    default=[] # No facility selected by default for detailed view
)

if selected_facilities:
    filtered_df_facility = filtered_df[filtered_df['Name'].isin(selected_facilities)]
else:
    filtered_df_facility = filtered_df.copy() # If no specific facility selected, use all filtered data


# --- Main Content Area ---

tab1, tab2, tab3, tab4 = st.tabs(["Overview & Key Metrics", "Trend Analysis", "Country Comparison", "Facility Details"])

with tab1:
    st.header("Overview & Key Metrics")

    if not filtered_df.empty:
        # Calculate key metrics for the selected period
        latest_data = filtered_df.sort_values(by='Date', ascending=False).drop_duplicates(subset=['Name', 'Country'])

        total_gas_in_storage = latest_data['gasInStorage'].sum()  if not latest_data.empty else 0 # Convert to BCM
        avg_fill_percentage = latest_data['full'].mean() if not latest_data.empty else 0
        total_working_volume = latest_data['workingGasVolume'].sum()  if not latest_data.empty else 0 # Convert to BCM
        sum_injection_capacity = latest_data['injection'].sum() if not latest_data.empty else 0
        sum_withdrawal_capacity = latest_data['withdrawal'].sum() if not latest_data.empty else 0

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(label="Total Gas in Storage (BCM)", value=f"{total_gas_in_storage:,.2f}")
        with col2:
            st.metric(label="Average Fill Percentage (%)", value=f"{avg_fill_percentage:,.2f}%")
        with col3:
            st.metric(label="Total Working Volume (BCM)", value=f"{total_working_volume:,.2f}")
        with col4:
            st.metric(label="Total Injection (GWh/d)", value=f"{sum_injection_capacity:,.2f}")
        with col5:
            st.metric(label="Total Withdrawal (GWh/d)", value=f"{sum_withdrawal_capacity:,.2f}")

        st.subheader(f"Current Gas Storage Status by Country on {max_date.strftime('%Y-%m-%d')}")
        # Aggregate latest data by country
        country_summary = latest_data.groupby('Country').agg(
            GasInStorage=('gasInStorage', 'sum'),
            FillPercentage=('full', 'mean'),
            WorkingGasVolume=('workingGasVolume', 'sum')
        ).reset_index()

        # Convert to BCM for display
        country_summary['GasInStorage (BCM)'] = country_summary['GasInStorage']
        country_summary['WorkingGasVolume (BCM)'] = country_summary['WorkingGasVolume']
        country_summary['FillPercentage (%)'] = country_summary['FillPercentage']

        st.dataframe(country_summary[['Country', 'GasInStorage (BCM)', 'FillPercentage (%)', 'WorkingGasVolume (BCM)']].round(2), use_container_width=True)

        st.subheader("Storage Status Map")
        # Merge country coordinates with the summary data
        country_summary['latitude'] = country_summary['Country'].map(lambda x: country_coordinates.get(x, {}).get('latitude'))
        country_summary['longitude'] = country_summary['Country'].map(lambda x: country_coordinates.get(x, {}).get('longitude'))

        # Drop rows where coordinates are not found
        country_summary_with_coords = country_summary.dropna(subset=['latitude', 'longitude'])

        if not country_summary_with_coords.empty:
            fig_map = px.scatter_geo(
                country_summary_with_coords,
                lat="latitude",
                lon="longitude",
                locations="Country",
                locationmode="country names",
                color="FillPercentage (%)",
                hover_name="Country",
                size="GasInStorage (BCM)",
                color_continuous_scale=px.colors.sequential.Viridis,
            )

            fig_map.update_layout(
                title="Gas Storage Fill Percentage by Country",
                geo=dict(
                    scope='europe',
                    projection_type='natural earth',
                    showland=True,
                    landcolor='rgb(217, 217, 217)',
                )
            )

            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info(
                "Map visualization is not available as geographical coordinates are missing for the selected countries.")
    else:
        st.warning("No data available for the selected filters.")

with tab2:
    st.header("Trend Analysis")

    if not filtered_df.empty:
        # Group by date and calculate average fill percentage and total gas in storage
        trend_data = filtered_df.groupby('Date').agg(
            AvgFillPercentage=('full', 'mean'),
            TotalGasInStorage=('gasInStorage', 'sum')
        ).reset_index()

        # Convert to BCM for plotting
        trend_data['TotalGasInStorage (BCM)'] = trend_data['TotalGasInStorage'] / 1_000_000_000

        st.subheader("Average Fill Percentage Over Time")
        fig_fill_trend = px.line(
            trend_data,
            x='Date',
            y='AvgFillPercentage',
            title='Average Gas Storage Fill Percentage Trend',
            labels={'AvgFillPercentage': 'Average Fill Percentage (%)'}
        )
        fig_fill_trend.update_traces(mode='lines+markers')
        st.plotly_chart(fig_fill_trend, use_container_width=True)

        st.subheader("Total Gas in Storage Over Time")
        fig_gas_trend = px.line(
            trend_data,
            x='Date',
            y='TotalGasInStorage (BCM)',
            title='Total Gas in Storage Trend',
            labels={'TotalGasInStorage (BCM)': 'Total Gas in Storage (BCM)'}
        )
        fig_gas_trend.update_traces(mode='lines+markers')
        st.plotly_chart(fig_gas_trend, use_container_width=True)

        st.subheader("Daily Injection/Withdrawal Volumes Over Time")
        # Sum injection and withdrawal for the selected period
        daily_flow = filtered_df.groupby('Date').agg(
            TotalInjection=('injection', 'sum'),
            TotalWithdrawal=('withdrawal', 'sum')
        ).reset_index()

        fig_flow = go.Figure()
        fig_flow.add_trace(go.Scatter(x=daily_flow['Date'], y=daily_flow['TotalInjection'], mode='lines', name='Total Injection'))
        fig_flow.add_trace(go.Scatter(x=daily_flow['Date'], y=daily_flow['TotalWithdrawal'], mode='lines', name='Total Withdrawal'))
        fig_flow.update_layout(
            title='Daily Total Injection/Withdrawal Volumes',
            xaxis_title='Date',
            yaxis_title='Volume (MCM/day)',
            hovermode="x unified"
        )
        st.plotly_chart(fig_flow, use_container_width=True)

    else:
        st.warning("No data available for trend analysis with the selected filters.")

with tab3:
    st.header("Country-Level Comparison")

    if not filtered_df.empty:
        # Group by country and get the latest available data for each country
        latest_data_by_country = filtered_df.sort_values(by='Date', ascending=False).drop_duplicates(subset=['Country'])

        st.subheader("Current Fill Percentage by Country")
        fig_country_fill = px.bar(
            latest_data_by_country.sort_values(by='full', ascending=False),
            x='Country',
            y='full',
            title='Current Gas Storage Fill Percentage by Country',
            labels={'full': 'Fill Percentage (%)'},
            color='full',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig_country_fill, use_container_width=True)

        st.subheader("Gas in Storage by Country (Latest Data)")
        fig_country_gas = px.bar(
            latest_data_by_country.sort_values(by='gasInStorage', ascending=False),
            x='Country',
            y='gasInStorage',
            title='Gas in Storage by Country (Latest Available Data)',
            labels={'gasInStorage': 'Gas in Storage (MCM)'},
            color='gasInStorage',
            color_continuous_scale=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig_country_gas, use_container_width=True)

        st.subheader("Working Gas Volume by Country")
        fig_country_working = px.bar(
            latest_data_by_country.sort_values(by='workingGasVolume', ascending=False),
            x='Country',
            y='workingGasVolume',
            title='Working Gas Volume by Country',
            labels={'workingGasVolume': 'Working Gas Volume (MCM)'},
            color='workingGasVolume',
            color_continuous_scale=px.colors.sequential.Cividis
        )
        st.plotly_chart(fig_country_working, use_container_width=True)

    else:
        st.warning("No data available for country-level comparison with the selected filters.")

with tab4:
    st.header("Facility Details")

    if not filtered_df_facility.empty:
        if not selected_facilities:
            st.info("Please select specific facilities from the sidebar to view their detailed information.")
        else:
            for facility_name in selected_facilities:
                st.subheader(f"Details for: {facility_name}")
                facility_data = filtered_df_facility[filtered_df_facility['Name'] == facility_name].sort_values(by='Date')

                if not facility_data.empty:
                    # Display key information for the facility
                    latest_facility_info = facility_data.iloc[-1] # Get the latest entry for static info
                    st.write(f"**Country:** {latest_facility_info['Country']}")
                    st.write(f"**Operator:** {latest_facility_info['operator']}")
                    st.write(f"**Type:** {latest_facility_info['Type']}")
                    st.write(f"**Working Gas Volume:** {latest_facility_info['workingGasVolume']:,.2f} MCM")
                    st.write(f"**Max Injection Capacity:** {latest_facility_info['injectionCapacity']:,.2f} MCM/day")
                    st.write(f"**Max Withdrawal Capacity:** {latest_facility_info['withdrawalCapacity']:,.2f} MCM/day")

                    # Plot historical fill percentage for the facility
                    fig_facility_fill = px.line(
                        facility_data,
                        x='Date',
                        y='full',
                        title=f'Fill Percentage Trend for {facility_name}',
                        labels={'full': 'Fill Percentage (%)'}
                    )
                    st.plotly_chart(fig_facility_fill, use_container_width=True)

                    # Plot historical gas in storage for the facility
                    fig_facility_gas = px.line(
                        facility_data,
                        x='Date',
                        y='gasInStorage',
                        title=f'Gas in Storage Trend for {facility_name}',
                        labels={'gasInStorage': 'Gas in Storage (MCM)'}
                    )
                    st.plotly_chart(fig_facility_gas, use_container_width=True)

                    # Plot historical injection/withdrawal for the facility
                    fig_facility_io = go.Figure()
                    fig_facility_io.add_trace(go.Scatter(x=facility_data['Date'], y=facility_data['injection'], mode='lines', name='Injection'))
                    fig_facility_io.add_trace(go.Scatter(x=facility_data['Date'], y=facility_data['withdrawal'], mode='lines', name='Withdrawal'))
                    fig_facility_io.update_layout(
                        title=f'Daily Injection/Withdrawal for {facility_name}',
                        xaxis_title='Date',
                        yaxis_title='Volume (MCM/day)',
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig_facility_io, use_container_width=True)

                    st.markdown("---") # Separator for multiple facilities
                else:
                    st.warning(f"No data available for facility: {facility_name} within the selected date range.")
    else:
        st.info("No facilities selected or no data available for the selected filters.")

st.markdown("---")
st.markdown("Data Source: Storage.csv")
