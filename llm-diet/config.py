PAGE_TITLE = "ダイエット支援LLMアプリ"

img_url = "https://cdn-icons-png.flaticon.com/512/6750/6750831.png"

activity_level_multipliers = {
    "とても低い": 1.2,
    "やや低い": 1.375,
    "普通": 1.55,
    "やや高い": 1.725,
    "とても高い": 1.9,
}

activity_details = """
とても低い: 全く運動しない \n
やや低い: 週に1,2回程度の運動 \n
普通: 週に3-5回程度の運動 \n
やや高い: 週に6,7回程度の運動 \n
とても高い: ハードなエクササイズや肉体労働
"""

# Define the macronutrient percentages
macronutrient_percentages = {
    "炭水化物": (45, 65),
    "タンパク質": (10, 35),
    "脂質": (20, 35),
}

gender_list = ['男性', '女性', 'その他']

goal_list = ['筋肉増量', '体重減少', '維持']

activity_level = ["とても低い", "やや低い", "普通", "やや高い", "とても高い"]

# Set the person's information
person_info = {
    "年齢": 25,
    "性別": "Male",
    "身長": 165,
    "体重": 70,
    "活動レベル": "普通",
    "目標": "体重減少"
}

PAML_API_KEY = "AIzaSyDEk2sOvWa5dZZneq3f_YeiqFnKAIf49hE"
