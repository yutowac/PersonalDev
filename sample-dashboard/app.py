import pandas as pd
import requests
from io import StringIO
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
# file_path = 'sample.csv' 
# data = pd.read_csv(file_path)
# https://github.com/yutowac/PersonalDev/blob/main/sample-dashboard/sample.csv
def load_original_data():
    url = 'https://raw.githubusercontent.com/yutowac/PersonalDev/sample-dashboard/main/sample.csv'
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))

data = load_original_data()

# Streamlit app
st.title("Dashboard")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Analytics"])

if page == "Home":
    st.header("ようこそ")

elif page == "Analytics":
    st.header("Analytics")

    # Row 1: Histograms for gender, height, weight, body_fat_per by area
    st.subheader("Histograms by Area")
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    columns_to_plot = ['gender', 'height', 'weight', 'body_fat_per']
    for ax, col in zip(axs.flatten(), columns_to_plot):
        data[col] = pd.to_numeric(data[col], errors='coerce')
        data.dropna(subset=[col], inplace=True)
        data.groupby('area')[col].plot(kind='hist', ax=ax, alpha=0.6, legend=True)
        ax.set_title(f'Histogram of {col} by Area')
        ax.set_xlabel(col)
        ax.set_ylabel('Frequency')

    st.pyplot(fig)

    # Row 2: Pie chart and bar chart
    st.subheader("Pie Chart and Bar Chart by Area")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Pie chart
    area_counts = data['area'].value_counts()
    ax1.pie(area_counts, labels=area_counts.index, autopct='%1.1f%%', startangle=140)
    ax1.set_title('Distribution of Areas')

    # Bar chart
    player_counts = data.groupby('area')['player_id'].nunique()
    player_counts.plot(kind='bar', ax=ax2)
    ax2.set_title('Number of Players by Area')
    ax2.set_xlabel('Area')
    ax2.set_ylabel('Number of Players')

    st.pyplot(fig)
