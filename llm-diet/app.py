import streamlit as st
import hydralit_components as hc
from config import *
from helper import *
from streamlit_option_menu import option_menu
import warnings
# from io import StringIO
import certifi
import requests

API_URL = "https://vqwj9yovdil3tfux.us-east-1.aws.endpoints.huggingface.cloud"
headers = {
   "Accept" : "application/json",
   "Authorization": "Bearer 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",
   "Content-Type": "application/json",
}

warnings.filterwarnings('ignore')

# ページセットアップ
st.set_page_config(
  page_title=PAGE_TITLE,
  layout='wide'
)

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload, verify=False)
	return response.json()

def get_response(prompt):
    res = query({
      "inputs": prompt,
      "parameters": {
        "max_new_tokens": 500
      }
    })
    print(res)
    return res

# CSS
local_css("style.css")

# サイドバー
with st.sidebar:
    with st.form("form"):
        st.header("ユーザー情報")
        col1, col2 = st.columns(2)
        with col1:
            st.header("年齢")
            st.header("性別")
            st.header("体重 (kg)")
            st.header("身長 (cm)")
            st.header("活動レベル")
            st.header("目標")
        with col2:
            age = st.number_input("年齢を入力してください", min_value=5, value=person_info["年齢"], step=1, label_visibility="collapsed")
            gender = option = st.selectbox("性別を選んでください", gender_list, label_visibility="collapsed")
            weight = st.number_input("体重を入力してください", value=person_info["体重"], min_value=20, step=1, label_visibility="collapsed")
            height = st.number_input("身長を入力してください", value=person_info["身長"], min_value=100, step=1, label_visibility="collapsed")
            activity_level = st.selectbox('活動レベルを選択してください', activity_level, help=activity_details, label_visibility="collapsed")
            goal = st.selectbox('目標を選択してください', goal_list, label_visibility="collapsed")

        c = st.columns((1,4,1))
        with c[1]:
            submitted = st.form_submit_button("登録", type="primary")
            person_info["年齢"] = age
            person_info["性別"] = gender
            person_info["体重"] = weight
            person_info["身長"] = height
            person_info["活動レベル"] = activity_level
            person_info["目標"] = goal

# メインコンテンツ
def home(person_info):
    bmi, bmi_class = calculate_bmi(person_info)
    bmr, tdee = energy_calc(person_info)
    macros_req = macro_perc(person_info, tdee)
    hc_theme = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange','icon_color': 'orange', 'icon': 'fa fa-question-circle'}

    cols = st.columns(3)
    with cols[0]:
      if bmi_class == "標準体重":
        hc.info_card(title='BMI', content=f'{round(bmi, 2)}' + " kcal", sentiment='good')
      else:
        hc.info_card(title='BMI', content=f'{round(bmi, 2)}', sentiment='bad')
    with cols[1]:
      hc.info_card(title='基礎代謝', content=f'{round(bmr, 2)} kcal',theme_override=hc_theme)

    st.header("PFCバランス")
    cols = st.columns(3)
    theme_neutral = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}
    with cols[0]:
      hc.info_card(title='タンパク質', content=f'{round(macros_req["タンパク質"], 2)} g', theme_override=theme_neutral)
    with cols[1]:
      hc.info_card(title='脂質', content=f'{round(macros_req["脂質"], 2)} g',theme_override=theme_neutral)
    with cols[2]:
      hc.info_card(title='炭水化物', content=f'{round(macros_req["炭水化物"], 2)} g',theme_override=theme_neutral)

def diet(person_info):
  search = st.text_input("食べた物を入力してください！", placeholder="焼きそば")
  f = st.button("決定", type="primary")
  if f:
    with st.spinner(f"**{search}** について情報を探しています...."):
      prompt = f"""
      表形式で栄養データを生成してください。テキストではなくテーブルだけを返すようにします。
      対象は{search}についてです。
      テーブルは栄養データとして、以下の6つの特徴を必ず持ちます：
      1.量
      2.材料
      3.タンパク質
      4.脂質
      5.炭水化物
      6.カロリー
      """
      res = get_response(prompt)
      res = res[0]["generated_text"].split("\n\n ")[1]
      st.write(res)

def plan(person_info):
  with st.form("食事プラン"):
    st.header("あなたの情報")
    cols = st.columns(3)
    with cols[0]:
      loc = st.selectbox('あなたの住んでいる国はどこですか？', ["日本", "日本以外の国"])
    with cols[1]:
      remarks = st.text_input("食事の好み", placeholder="例：野菜が好き、肉が嫌い")
    s = st.form_submit_button("食事プランをつくる", type="primary")
  if s:
    with st.spinner('プランを生成中です....'):
      bmi, bmi_class = calculate_bmi(person_info)
      bmr, tdee = energy_calc(person_info)

      prompt = f"""
      表形式で食事プランを生成してください。テキストではなくテーブルだけを返すようにします。
      対象者の性別は{person_info["性別"]}、{loc}に住む人で、BMRが {bmr} kcal、 BMIは{bmi}、1日の消費エネルギーは{tdee} kcalの人です。
      そして、食事プランのメニューに反映させるべき次の嗜好を持っています：{remarks}。
      目標は、{person_info["目標"]}です。
      テーブルは食事プランとして、以下の特徴を必ず持ちます：
      1.食事時間（朝食、昼食、夕食の3回）
      2.メニュー
      3.材料
      4.栄養素(g)
      5.カロリー(kcal)
      """
      res = get_response(prompt)
      res = res[0]["generated_text"].split("```")[1]
      st.write(res)


selected = option_menu(
    menu_title=None,
    options=["ホーム", "栄養計算", "食事プラン"],
    icons=["house", "calculator", "envelope"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# 画面遷移
if selected == "ホーム":
  home(person_info)
elif selected == "栄養計算":
  diet(person_info)
elif selected == "食事プラン":
  plan(person_info)
else:
  st.error("あなたの情報を登録してください")
