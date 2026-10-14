import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import datetime as dt

# set layout of streamlit page
st.set_page_config(page_title='dashboard', layout='wide')
# cache the data loading
@ st.cache_data
def load_cleandata(file_path, sheet_name_to_load):
    dtf = pd.read_excel(file_path, sheet_name = sheet_name_to_load)
    return dtf

# styling of tabs layout
st.markdown(
    """
    <style>
        /* Style the entire tab container */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }

        /* Style individual unselected tabs */
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: white;
            border-radius: 6px;
            border: 1px solid #dcdcdc;
            color: #333333;
            font-weight: 600;
            padding: 0 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        /* Style the active/selected tab to pop out prominently */
        .stTabs [aria-selected="true"] {
            background-color: #1f77b4 !important; /* Professional corporate blue */
            color: white !important;
            border: 1px solid #1f77b4 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
# create tabs for dashboard , data quality , and report
tab1, tab2, tab3 = st.tabs(['Data Quality', 'Main Dashboard', 'Report'])
with tab1:
    col_header, col_requirements = st.columns([3,1])
    with col_header:
        col_a, col_b, col_c = st.columns([0.5,1,0.5])
        with col_b:
            st.markdown("# *Data Exploration & Quality*")
        
    with col_requirements:
         with st.container(border=True):
              st.markdown("#### **Client Requirements:**")
              st.write(
                   """
- Clean the dataset which is completely messy.
- Calculate monthly total Rapido fee and net earning after fuel.
"""
              )
              
    df = load_cleandata("222. Balaji Travels - Rapido.xlsx", "Tips Data (Raw)")
    col_unclean, col_clean = st.columns([1, 1])
    with col_unclean:
        with st.expander('Overview of UnClean Data'):
            st.dataframe(df.head(), use_container_width=True)

# clean the excel file, the raw data alternate among the rows
#"""Splitting the data into separate tables (or ranges) based on the rows and then merging them side-by-side is actually one of the cleanest ways to solve this.
#Because your data alternates between metadata rows (Date, Car No, Driver) and transaction rows (City, Place, Trips, Fare, etc.), you can split them, structure them properly, and rejoin them into a single unified table."""
# apply slicing, select every second row and create 2 seperate tables
#table1 = df.iloc[1::2][['Trip Date', 'Car No', 'Driver']].reset_index(drop = True)
#table3 = df.iloc[2::2, 3:][['Gross Fare', 'Rapido Fee', 'Net Earnings', 'Fuel Cost', 'Rating']].reset_index(drop = True)
# for table2  header are in 2nd row
#df = pd.read_excel("222. Balaji Travels - Rapido.xlsx", sheet_name = "Tips Data (Raw)", header = 1)
#table2 = df.iloc[1::2][['City', 'Place', 'Trips']].reset_index(drop = True)

# combine the data
#clean_df = pd.concat([table1, table2, table3], axis=1)
    # convert into excel
#clean_df.to_excel("Cleaned_Balaji_Travels.xlsx", index=False)

        
# load the data
    df_clean = load_cleandata('Cleaned_Balaji_Travels.xlsx', 'Tips Data')
# change the dtypes of columns
    df_clean['Trip Date'] = pd.to_datetime(df_clean['Trip Date'].astype(float), unit='D', origin='1899-12-30').dt.date
    with col_clean:
        with st.expander('Overview of Cleanned data'):
            st.dataframe(df_clean.head(), use_container_width= True)
    st.markdown("----")
    # check records and unique cars
    col_rows, col_drivers = st.columns([1, 1])
    with col_rows:
        st.metric('Total Records:', len(df_clean), delta=f"Found {len(df_clean)} records in dataset.")
    with col_drivers:
        st.metric('Drivers:', df_clean['Driver'].nunique(), delta=f"{df_clean['Driver'].nunique()} unique drivers.")
    # vehicles and ratings
    col_veh, col_rat = st.columns([1, 1])
    with col_veh:
        st.metric("Total Vehicles", df_clean['Car No'].nunique(), delta=f"Total {df_clean['Car No'].nunique()} cars.")
    with col_rat:
        st.metric("Average Rating", f"{df_clean['Rating'].mean():.2f}")
    # check dupllicate and null values
    duplicated =  df_clean.duplicated().sum()
    null_values = df_clean.isnull().sum().sum()
    # present in app
    col_dup, col_null = st.columns([1, 1])
    with col_dup:
        st.metric(label='Total Duplicate Rows:', value=duplicated, delta=('Clean Data' if duplicated == 0 else 'Action Required'))
    with col_null:
        st.metric(label='Missing Values', value=null_values, delta=('Clean Data' if null_values== 0 else 'Action Required'))
    # date range and columns types
    col_date, col_col = st.columns([1, 1])
    with col_date:
        st.metric("Date Range", f"({df_clean['Trip Date'].min()} , {df_clean['Trip Date'].max()})")
    with col_col:
        st.markdown("#### **Column names with datatypes**")
        for col in df_clean.columns:
            st.write(f"{col}    {df_clean[col].dtype}")
        # complete description of whole dataset
        st.markdown("### Complete Description of Numerical Columns")
        st.dataframe(df_clean.describe())
with tab2:
    # extract month and net earning after fuel
    df_clean['NetEarningAfterFuel'] = df_clean['Net Earnings'] - df_clean['Fuel Cost']
    #df_clean['Trip Date'] = pd.to_datetime(df_clean['Trip Date'])
    # for sorting first extract the month with number
    df_series = pd.to_datetime(df_clean['Trip Date'])
    df_clean['month#'] = df_series.dt.month
    df_clean['month'] = df_series.dt.strftime('%b')
        

    col_h, col_f = st.columns([2, 1])
    with col_h:
        st.markdown("<h1 style = 'text-align: center; color: #1f77b4;'>Fleet Overview & Financial Insights</h1>", unsafe_allow_html=True)
    with col_f:
        with st.expander('Car Filter'):
            car_list = ["All Cars"] + sorted(df_clean['Car No'].unique().tolist())
            selected_car = st.multiselect("Select Car Number", car_list, default=["All Cars"])
            # apply filter
            if not selected_car or 'All Cars' in selected_car:
                filtered_df = df_clean
            else:
                filtered_df = df_clean[df_clean['Car No'].isin(selected_car)]
    
    # main kpi's; grooss fare, net earning , rapido fee and fuel cost
    with st.container(border=True):
        col_1, col_2, col_3, col_4 = st.columns([1,1,1,1])
    with col_1:
        st.metric("Total Gross Fare", f"Rs {filtered_df['Gross Fare'].sum()}")
    with col_2:
        st.metric("Total Rapido Fee", f"Rs {filtered_df['Rapido Fee'].sum()}")
    with col_3:
        st.metric("Total Net Earnings", f" Rs {filtered_df['Net Earnings'].sum()}")
    with col_4:
        st.metric("Average Fuel Cost", f"Rs {filtered_df['Fuel Cost'].mean():.2f}")
    st.markdown("<h3 style = 'text-align: center; color: #1f77b4;'>Monthly Rapido Fee & Net Earnings</h3>", unsafe_allow_html=True)

    # pivot table
    monthly_pivot = filtered_df.pivot_table(index = ['month#', 'month'], values = ['Rapido Fee', 'NetEarningAfterFuel'], aggfunc = 'sum').reset_index()
    monthly_pivot = monthly_pivot.sort_values('month#').drop(columns = ['month#'])
    col_left, col_right = st.columns([2,4])
    with col_left:
        st.dataframe(monthly_pivot, use_container_width=True, hide_index=True)
    with col_right:    
        # Create professional grouped bar chart styled for general/light mode presentation
        fig = px.bar(
        monthly_pivot,
        x="month",
        y=["NetEarningAfterFuel", "Rapido Fee"],
        barmode="group",
        labels={
        "value": "Amount (Rs)",
        "month": "Month",
        "variable": "Financial Metric",
        },
        color_discrete_map={
        "NetEarningAfterFuel": "#1f77b4",  # Professional corporate blue
        "Rapido Fee": "#ff7f0e",  # Clean accent orange
        },
        )

        # Professional layout for general audiences (clean white card look)
        fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color="#262730",
        title=dict(
        text="Monthly Net Earnings vs Rapido Fee",
        font=dict(size=18, weight="bold"),
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        title=None,
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(
        showgrid=False, linecolor="#d3d3d3", tickfont=dict(size=12, color="#333")
        ),
        yaxis=dict(
        showgrid=True,
        gridcolor="#eaeaea",
        linecolor="#d3d3d3",
        tickfont=dict(size=12, color="#333"),
        ),
        )

        st.plotly_chart(fig, use_container_width=True)

# professional report tab
with tab3:
    st.markdown(
    """
    <h2 style = 'color: #1f77b4;'>📋 Exective Audit & Financial Report</h2>
    <p style = 'color: #555;'>Prepared from raw trip logs: Data Cleaning, Rapido Commission Analysis & Net Profitability Audit</p>
    <hr style = 'margin-top: 0px;'>
    """,
    unsafe_allow_html=True
    )
    # main kpi's 
    col_1a, col_1b, col_1c, col_1d = st.columns(4)
    col_1a.metric("Total Gross Fare", f"Rs {filtered_df['Gross Fare'].sum()}")
    col_1b.metric("Total Rapido Fee", f"Rs {filtered_df['Rapido Fee'].sum()}")
    col_1c.metric("Net Earning After Fuel", f"Rs {filtered_df['NetEarningAfterFuel'].sum()}")
    col_1d.metric("Average Fuel Cost", f"Rs {filtered_df['Fuel Cost'].mean():.2f}")
    st.markdown("----")
    # data cleaning overview
    st.markdown("<h3 style = 'text-align: center; color: #1f77b4'>Daata Cleaning Overview</h3", unsafe_allow_html=True)
    st.success("**Data Integrity Confirmed:** The dataset was successfully processed and clean through the combination of automated python scripts and excel within few steps. Missing values, unconsistent date format and unformatted text entries were sanatizd to ensure 100% reliable financial report.")
    # deep dive analysis
    st.markdown("<h3 style = 'text-align: center; color: #1f77b4;'>Rapido Fee & Net Earning Analysis</h3>", unsafe_allow_html=True)
    # calculate metrics for insights
    rapido_percentage = (filtered_df['Rapido Fee'].sum() / filtered_df['Gross Fare'].sum()) * 100
    net_percentage = (filtered_df['NetEarningAfterFuel'].sum() / filtered_df['Gross Fare'].sum()) * 100
    st.info(f"- **Platform Commission Overhead:**  \nTotal Rs {filtered_df['Rapido Fee'].sum()} rapido fee represents approximately {rapido_percentage:.1f} % of total gross revenue across filtered dataset.  \n- **True bottom-line Profitability:**  \nAfter accounting for direct fuel consumption, the fleet retains Rs {filtered_df['NetEarningAfterFuel'].sum()} in net earnings ({net_percentage:.2f}%) of gross fare.  \n- **Monthly Trajectory:**  \nPeak net margins aligns with high-volume months (July, August), showing optimal operational scaling against platform fixed cost")
    # vehicale performance
    st.markdown("<h3 style = 'text-align: center; color: #1f77b4'>Vehicle level performance breakdown</h3>", unsafe_allow_html=True)
    car_summary = df_clean.groupby('Car No').agg({'Trip Date': 'count', 'Gross Fare': 'sum', 'Rapido Fee': 'sum', 'Fuel Cost': 'sum', 'NetEarningAfterFuel': 'sum'}).rename(columns = {'Trip Date': 'Total Trips'}).reset_index()
    st.dataframe(car_summary, use_container_width=True, hide_index=True)
    # recommendation
    st.markdown("<h3 style = 'text-align: center; color: #1f77b4'>Recommendations</h3>", unsafe_allow_html=True)
    st.markdown("- With Rapido taking ~20% off the top, management should evaluate whether high-fee months correlate with surge pricing or if alternative booking channels can be integrated to improve margins.  \n- Track vehicles showing higher fuel burn relative to trip counts to catch maintenance inefficiencies early.")
