import streamlit as st
# import pandas as pd
# import numpy as np
# import requests
import re
from config import *

def calculate_bmi(person_info):
    bmi = person_info["体重"] / (person_info["身長"] / 100) ** 2

    if bmi < 18.5:
        bmi_class = "低体重"
    elif bmi < 25:
        bmi_class = "標準体重"
    elif bmi < 30:
        bmi_class = "やや肥満"
    else:
        bmi_class = "肥満"
    return bmi, bmi_class

def energy_calc(person_info):
    if person_info["性別"] == "男性":
        bmr = 88.362 + (13.397 * person_info["体重"]) + (4.799 * person_info["身長"] / 100) - (5.677 * person_info["年齢"])
    else:
        bmr = 447.593 + (9.247 * person_info["体重"]) + (3.100 * person_info["身長"] / 100) - (4.330 * person_info["年齢"])
    tdee = bmr * activity_level_multipliers[person_info["活動レベル"]]
    return bmr, tdee

def macro_perc(person_info, calories):
    if person_info["目標"].lower() == '体重減少':
        protein_percentage = 30
        fat_percentage = 25
    elif person_info["目標"].lower() == '維持':
        protein_percentage = 25
        fat_percentage = 30
    elif person_info["目標"].lower() == '筋肉増量':
        protein_percentage = 35
        fat_percentage = 20
    else:
        raise ValueError("無効な目標")

    carb_percentage = 100 - (protein_percentage + fat_percentage)

    protein = (protein_percentage / 100) * calories / 4
    fat = (fat_percentage / 100) * calories / 9
    carbs = (carb_percentage / 100) * calories / 4

    return {'タンパク質': protein, '脂質': fat, '炭水化物': carbs}

# load css
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# # to load lottie animation
# def load_lottieurl(url):
#     r = requests.get(url)
#     if r.status_code != 200:
#         return None
#     return r.json()

# extract table from markdown
def extract_markdown_table(markdown_string):
    # Define the regular expression pattern for extracting Markdown tables
    table_pattern = re.compile(r'\|(.+?)\|(.+?)\|.*?\n((?:\|.*?\|.*?\n)+)', re.DOTALL)

    # Find the first match in the Markdown string
    match = table_pattern.search(markdown_string)

    if not match:
        print("No Markdown table found.")
        return None

    # Extract the matched table content
    table_content = match.group(0)

    return table_content
