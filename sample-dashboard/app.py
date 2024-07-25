import pandas as pd
import requests
from io import StringIO
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
# file_path = './sample.csv' 
# data = pd.read_csv(file_path)

def load_original_data():
    url = 'https://raw.githubusercontent.com/yutowac/PersonalDev/main/sample-dashboard/sample.csv'
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error("Failed to load data from GitHub.")
        return None

data = load_original_data()

# Streamlit app
st.title("ユーザーデータレポート")

# Sidebar navigation
st.sidebar.title("メニュー")
page = st.sidebar.radio("Go to", ["ホーム", "分析"])

if page == "ホーム":
    st.header("ようこそ")

elif page == "分析":
    st.header("分析")

    # Row 1: Histograms for gender, height, weight, body_fat_per by area
    st.subheader("地域別のヒストグラム")
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
    st.subheader("地域データ")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Pie chart
    area_counts = data['area'].value_counts()
    ax1.pie(area_counts, labels=area_counts.index, autopct='%1.1f%%', startangle=140)
    ax1.set_title('地域別のユーザー数')

    # Bar chart
    player_counts = data.groupby('area')['player_id'].nunique()
    player_counts.plot(kind='bar', ax=ax2)
    ax2.set_title('地域別の測定回数')
    ax2.set_xlabel('地域')
    ax2.set_ylabel('測定回数')

    st.pyplot(fig)
