import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import numpy as np
import pytz
#from datetime import datetime
#import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

@st.cache_data()
def load_data_process():
    filepath = "Process_details.xlsx"
    return pd.read_excel(filepath, sheet_name="Process_Details")

@st.cache_data()
def load_data_schedule():
    filepath = "Process_Details.xlsx"
    df = pd.read_excel(filepath, sheet_name="Bot Schedule")
    return df

def process():
    st.header("RPA Process Details",divider='rainbow')
    df = load_data_process()
    # Columns to display
    columns_to_display = [
        'Process', 'Department', 'Frequency', 'Priority & Impact','Required',
        'Business Critical?', 'System Used', 'Process Complexity', 'No. of steps in automation','Assigned To'
    ]
    # Filter the DataFrame to only include these columns
    df = df[columns_to_display]

    # Initialize session state for filter selections if not already set
    if 'update' not in st.session_state:
        st.session_state['update'] = False
    
    pods = df['Assigned To'].dropna().unique().tolist()
    departments = df['Department'].dropna().unique().tolist()
    complexity = df['Process Complexity'].dropna().unique().tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_pod = st.multiselect('Select POD', options=pods, key='pod', on_change=toggle_update)
    with col2:
        selected_department = st.multiselect("Select Department", options=departments, key='dept', on_change=toggle_update)
    with col3:
        selected_complexity = st.multiselect("Select Complexity", options=complexity, key='comp', on_change=toggle_update)

    if st.session_state['update'] or (selected_pod or selected_department or selected_complexity):
        df_filtered = update_df(df, selected_pod, selected_department, selected_complexity)
        with st.expander("Click here to Expand the Table"):
            st.dataframe(df_filtered, use_container_width=True,hide_index=True)
            st.info(len(df_filtered))
        st.session_state['update'] = False  # Reset update trigger after processing

def toggle_update():
    st.session_state['update'] = not st.session_state['update']

def update_df(df, pods, departments, complexity):
    query = []
    if pods:
        query.append(df["Assigned To"].isin(pods))
    if departments:
        query.append(df["Department"].isin(departments))
    if complexity:
        query.append(df["Process Complexity"].isin(complexity))
    if query:
        df = df[np.logical_and.reduce(query)]
    return df

selected = option_menu(
    menu_title="",
    options=["Process", 'Schedule', 'All Exceptions'],
    icons=['book', 'stopwatch', 'emoji-smile'],
    menu_icon='cast',
    default_index=0,
    orientation='horizontal'
)

def convert_timezones(df):
    timezones = {
        'PST': 'America/Los_Angeles',
        'EST': 'America/New_York',
        'MST': 'America/Denver',
        'IST': 'Asia/Kolkata'
    }
    
    df['Schedule Start Time(PST)'] = pd.to_datetime(df['Schedule Start Time(PST)'], errors='coerce')
    not_na_mask = df['Schedule Start Time(PST)'].notna()

    for tz_label, tz_name in timezones.items():
        timezone = pytz.timezone(tz_name)
        column_name = tz_label  # Column names will be 'PST', 'EST', etc.
        if tz_label == 'PST':
            df.loc[not_na_mask, column_name] = df.loc[not_na_mask, 'Schedule Start Time(PST)'].dt.tz_localize(timezone)
        else:
            df.loc[not_na_mask, column_name] = df.loc[not_na_mask, 'PST'].dt.tz_convert(timezone)
            
    return df

def display_schedule_page():
    st.subheader("Schedule Page")
    df = load_data_schedule()
    converted_df = convert_timezones(df)
    # Optionally, use format to align datetime display
    st.dataframe(converted_df[['Process', 'PST', 'EST', 'MST', 'IST',]], width=700)
# Set up the page and option menu

if selected == 'Process':
    process()
elif selected == 'Schedule':
    display_schedule_page()
elif selected == 'All Exceptions':
    st.subheader("All Exceptions Page")
    st.write("This is an All Exceptions page.")