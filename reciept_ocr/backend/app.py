# import os
# import cv2
# import pytesseract
# import re
# from flask import Flask, request, jsonify
# from flask_cors import CORS

# # Windows環境用（Tesseractのインストールパスを指定）
# # Mac/Linuxの場合はこの行を削除してOK
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = 'uploads'
# OUTPUT_FOLDER = 'output'

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# @app.route('/')
# def index():
#     return '領収書OCRサーバーが起動しています。'

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'image' not in request.files:
#         return '画像が見つかりませんでした', 400

#     image = request.files['image']
#     if image.filename == '':
#         return 'ファイル名が空です', 400

#     filepath = os.path.join(UPLOAD_FOLDER, image.filename)
#     image.save(filepath)

#     # 処理実行
#     results = split_and_ocr_receipts(filepath)

#     return f'処理完了：{len(results)} 件のレシートを出力しました。'

# def split_and_ocr_receipts(filepath):
#     img = cv2.imread(filepath)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     gray = cv2.GaussianBlur(gray, (5, 5), 0)
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

#     # 輪郭検出でレシートごとに分割
#     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours = sorted(contours, key=lambda cnt: cv2.boundingRect(cnt)[0])  # 左→右順に

#     results = []
#     for i, cnt in enumerate(contours):
#         x, y, w, h = cv2.boundingRect(cnt)

#         # ノイズ除去：小さすぎる輪郭は無視
#         if w < 200 or h < 200:
#             continue

#         roi = img[y:y+h, x:x+w]
#         roi = cv2.resize(roi, (600, int(600 * h / w)))  # 認識精度アップのためリサイズ

#         # OCR（日本語＋英語）
#         text = pytesseract.image_to_string(roi, lang='jpn+eng')

#         # 日付の抽出（例: 2025-03-24 / 2025/03/24）
#         date_match = re.search(r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', text)
#         date_str = date_match.group().replace('/', '-') if date_match else f'unknown{i+1}'

#         # 店名の抽出（「店」含む行 or 長めの最初の行）
#         store_name = 'unknown'
#         for line in text.split('\n'):
#             if '店' in line or len(line.strip()) >= 4:
#                 store_name = line.strip()
#                 break

#         # ファイル名整形
#         safe_store = re.sub(r'[\\/*?:"<>|]', '', store_name)
#         filename = f'{date_str}_{safe_store}.png'

#         output_path = os.path.join(OUTPUT_FOLDER, filename)
#         cv2.imwrite(output_path, roi)

#         results.append({
#             'file': filename,
#             'date': date_str,
#             'store': store_name,
#             'text': text,
#         })

#     return results

# if __name__ == '__main__':
#     app.run(debug=True)

import os
import cv2
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import vision
from google.oauth2 import service_account

# Google Cloud Vision の認証設定
SERVICE_ACCOUNT_FILE = 'service_account_key.json'
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
vision_client = vision.ImageAnnotatorClient(credentials=credentials)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return '領収書OCRサーバー（Cloud Vision API対応）が起動しています。'

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return '画像が見つかりませんでした', 400

    image = request.files['image']
    if image.filename == '':
        return 'ファイル名が空です', 400

    filepath = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(filepath)

    # 処理実行
    results = split_and_ocr_receipts(filepath)

    return jsonify({
        'message': f'処理完了：{len(results)} 件のレシートを出力しました。',
        'results': results
    })

def split_and_ocr_receipts(filepath):
    img = cv2.imread(filepath)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda cnt: cv2.boundingRect(cnt)[0])  # 左→右順

    results = []

    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if w < 200 or h < 200:
            continue

        roi = img[y:y+h, x:x+w]
        roi = cv2.resize(roi, (600, int(600 * h / w)))

        # OpenCV画像をJPEG形式に変換してCloud Visionへ
        _, encoded_image = cv2.imencode('.jpg', roi)
        content = encoded_image.tobytes()
        vision_image = vision.Image(content=content)
        response = vision_client.text_detection(image=vision_image)
        texts = response.text_annotations
        text = texts[0].description if texts else ""

        # 日付の抽出
        date_match = re.search(r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', text)
        date_str = date_match.group().replace('/', '-') if date_match else f'unknown{i+1}'

        # 店名の抽出（「店」を含むか、長めの行）
        store_name = 'unknown'
        for line in text.split('\n'):
            if '店' in line or len(line.strip()) >= 4:
                store_name = line.strip()
                break

        # ファイル名整形
        safe_store = re.sub(r'[\\/*?:"<>|]', '', store_name)
        filename = f'{date_str}_{safe_store}.png'

        output_path = os.path.join(OUTPUT_FOLDER, filename)
        cv2.imwrite(output_path, roi)

        results.append({
            'file': filename,
            'date': date_str,
            'store': store_name,
            'text': text
        })

    return results

if __name__ == '__main__':
    app.run(debug=True)
