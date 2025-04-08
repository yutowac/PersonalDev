import pandas as pd
import requests
from io import StringIO
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 100%;
        padding-left: 5%;
        padding-right: 5%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

def calculate_percentage_difference(value1, value2):
    return (value1 - value2) / value2 * 100

# Example statistics calculations
mean_height_area1 = data[data['area'] == 'area1']['height'].mean()
mean_height_area2 = data[data['area'] == 'area2']['height'].mean()
height_difference = calculate_percentage_difference(mean_height_area1, mean_height_area2)

mean_weight_area1 = data[data['area'] == 'area1']['weight'].mean()
mean_weight_area2 = data[data['area'] == 'area2']['weight'].mean()
weight_difference = calculate_percentage_difference(mean_weight_area1, mean_weight_area2)

mean_body_fat_area1 = data[data['area'] == 'area1']['body_fat_per'].mean()
mean_body_fat_area2 = data[data['area'] == 'area2']['body_fat_per'].mean()
body_fat_difference = calculate_percentage_difference(mean_body_fat_area1, mean_body_fat_area2)

# Streamlit app
st.title("ユーザーデータレポート")

# Sidebar navigation
st.sidebar.title("メニュー")
page = st.sidebar.radio("Go to", ["ホーム", "分析"])

if page == "ホーム":
    st.header("ようこそ")
    st.write(f"""
    ### データ概要
    このレポートは、ユーザーデータに基づいた分析結果を提供します。
    以下の指標についての詳細な視覚化を「分析」ページで確認できます：
    - 性別
    - 身長
    - 体重
    - 体脂肪率
    - 地域

    ### 主な分析結果
    - **身長**：`area1`地域では`area2`地域よりも身長の平均値が{height_difference:.2f}%大きかったです。
    - **体重**：`area1`地域では`area2`地域よりも体重の平均値が{weight_difference:.2f}%大きかったです。
    - **体脂肪率**：`area1`地域では`area2`地域よりも体脂肪率の平均値が{body_fat_difference:.2f}%大きかったです。

    ### データの視覚化
    データの詳細な視覚化は「分析」ページで確認できます。
    ユーザーデータをさまざまな視点から分析し、データの理解を深めるための視覚化を提供します。
    """)
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
    
    # with col1:
    st.subheader("相関ヒートマップ")
    corr = data[['height', 'weight', 'body_fat_per']].corr()
    fig_heatmap = px.imshow(corr, text_auto=True, aspect="auto", title='Correlation Heatmap', height=600, width=600)
    st.plotly_chart(fig_heatmap)
