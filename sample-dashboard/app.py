import pandas as pd
import requests
from io import StringIO
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    col1, col2 = st.columns(2)
    
    with col1:
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

        fig.update_layout(barmode='overlay', showlegend=True, height=600, width=600)
        st.plotly_chart(fig)

    with col2:
        st.subheader("地域データ")
        fig_pie = px.pie(data, names='area', title='Users by Area', height=400)
        st.plotly_chart(fig_pie)

        area_counts = data['area'].value_counts()
        fig_bar = px.bar(area_counts, x=area_counts.index, y=area_counts.values, title='Measurements by Area', height=400)
        fig_bar.update_xaxes(title_text='Area')
        fig_bar.update_yaxes(title_text='Number of Measurements')
        st.plotly_chart(fig_bar)

    # Row 2: Scatter Matrix and Box plots
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("散布図行列")
        scatter_matrix_fig = px.scatter_matrix(data, dimensions=['height', 'weight', 'body_fat_per'], color='area', height=800)
        st.plotly_chart(scatter_matrix_fig)

    with col2:
        st.subheader("箱ひげ図")
        fig_box = make_subplots(rows=3, cols=1, subplot_titles=["Height by Area", "Weight by Area", "Body Fat % by Area"])

        fig_box.add_trace(go.Box(y=data['height'], x=data['area'], name='Height'), row=1, col=1)
        fig_box.add_trace(go.Box(y=data['weight'], x=data['area'], name='Weight'), row=2, col=1)
        fig_box.add_trace(go.Box(y=data['body_fat_per'], x=data['area'], name='Body Fat %'), row=3, col=1)

        fig_box.update_layout(showlegend=False, height=900, width=600)
        st.plotly_chart(fig_box)

    # Row 3: Correlation heatmap
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("相関ヒートマップ")
        corr = data[['height', 'weight', 'body_fat_per']].corr()
        fig_heatmap = px.imshow(corr, text_auto=True, aspect="auto", title='Correlation Heatmap', height=600, width=600)
        st.plotly_chart(fig_heatmap)
