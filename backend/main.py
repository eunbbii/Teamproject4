from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

from horoscope import get_zodiac_sign, build_prompt, ZODIAC_NAMES, ZODIAC_KO_TO_EN
from gpt_client import get_horoscope_response
from gemini_client import get_horoscope_response_gemini
from firebase_client import get_horoscope, log_horoscope_request
from scraper import fetch_all_zodiacs


app = FastAPI()

# 사용자 요청 모델
class BirthDateRequest(BaseModel):
    birth_date: str  # 형식: "YYYY-MM-DD"
    style: str = "전문가"  # 기본값은 "친구", 선택지: "친구", "전문가", "시적"

# API 라우트 정의
@app.post("/horoscope")
def get_user_horoscope(data: BirthDateRequest):
    try:
        zodiac = get_zodiac_sign(data.birth_date)
        today = datetime.today().strftime("%Y-%m-%d")

        # 요청 로그 저장
        log_horoscope_request(zodiac)

        # Firebase에서 실시간 운세 데이터 가져오기
        external_content = get_horoscope(zodiac)
        if not external_content:
            raise ValueError("운세 데이터를 찾을 수 없습니다.")

        # GPT 프롬프트 생성 및 요약 요청
        prompt = build_prompt(zodiac, date_str=today, external_content=external_content, style=data.style)
        summary = get_horoscope_response_gemini(prompt) # Gemini API 사용
        # summary = get_horoscope_response(prompt)  #  OpenAI API 사용

        return {
            "zodiac": zodiac,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# app.get("/horoscope/{zodiac}")
@app.get("/horoscope/{zodiac}")
def get_horoscope_by_zodiac(zodiac: str):
    try:
        if zodiac not in ZODIAC_NAMES:
            raise ValueError("유효하지 않은 별자리입니다.")

        # 요청 로그 저장
        log_horoscope_request(zodiac)   

        # Firebase에서 오늘자 운세 데이터 가져오기
        content = get_horoscope(zodiac)
        if not content:
            raise ValueError("오늘자 운세 데이터를 찾을 수 없습니다.")

        return {
            "zodiac": zodiac,
            "content": content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    