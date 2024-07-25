import pandas as pd
import requests
from io import StringIO
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Load the data
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
    columns_to_plot = ['gender', 'height', 'weight', 'body_fat_per']
    fig = make_subplots(rows=2, cols=2, subplot_titles=[f"Histogram of {col} by Area" for col in columns_to_plot])

    row_col_map = [(1, 1), (1, 2), (2, 1), (2, 2)]
    for (col, (row, col_idx)) in zip(columns_to_plot, row_col_map):
        for area in data['area'].unique():
            hist_data = data[data['area'] == area][col].dropna()
            fig.add_trace(go.Histogram(x=hist_data, name=area, opacity=0.6), row=row, col=col_idx)
        fig.update_xaxes(title_text=col, row=row, col=col_idx)
        fig.update_yaxes(title_text='Frequency', row=row, col=col_idx)

    fig.update_layout(barmode='overlay', showlegend=True)
    st.plotly_chart(fig)

    # Row 2: Pie chart and bar chart
    st.subheader("地域データ")
    fig_pie = px.pie(data, names='area', title='Users by Area')
    st.plotly_chart(fig_pie)

    area_counts = data['area'].value_counts()
    fig_bar = px.bar(area_counts, x=area_counts.index, y=area_counts.values, title='Measurements by Area')
    fig_bar.update_xaxes(title_text='Area')
    fig_bar.update_yaxes(title_text='Number of Measurements')
    st.plotly_chart(fig_bar)
