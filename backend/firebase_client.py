# firebase_client.py
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "starlogue-a3d72-firebase-adminsdk-fbsvc-c6063bba34.json")

# Firestore 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ✅ 저장 함수: 날짜 기준으로 하위 컬렉션 생성
def save_horoscope(zodiac: str, content: str):
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")

    doc_ref = db.collection("horoscopes").document(zodiac).collection("daily").document(date_str)
    doc_ref.set({
        "content": content,
        "updated_at": now.strftime("%Y-%m-%d %H:%M:%S")
    })

# ✅ 불러오기 함수: 오늘자 데이터, 없으면 가장 최근 데이터 반환
def get_horoscope(zodiac: str) -> str:
    daily_ref = db.collection("horoscopes").document(zodiac).collection("daily")
    docs = daily_ref.stream()

    all_data = {doc.id: doc.to_dict() for doc in docs}

    if not all_data:
        return None

    today = datetime.utcnow().strftime("%Y-%m-%d")
    if today in all_data:
        return all_data[today]["content"]

    # fallback: 최신 날짜 선택
    latest_date = sorted(all_data.keys(), reverse=True)[0]
    return all_data[latest_date]["content"]

def is_horoscope_saved_today(zodiac: str) -> bool:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    doc_ref = db.collection("horoscopes").document(zodiac).collection("daily").document(today)
    doc = doc_ref.get()
    return doc.exists