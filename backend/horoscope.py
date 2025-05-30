from datetime import datetime


# horoscope.py

ZODIAC_NAMES = [
    "양자리", "황소자리", "쌍둥이자리", "게자리", "사자자리", "처녀자리",
    "천칭자리", "전갈자리", "사수자리", "염소자리", "물병자리", "물고기자리"
]

ZODIAC_KO_TO_EN = {
    "양자리": "aries",
    "황소자리": "taurus",
    "쌍둥이자리": "gemini",
    "게자리": "cancer",
    "사자자리": "leo",
    "처녀자리": "virgo",
    "천칭자리": "libra",
    "전갈자리": "scorpio",
    "사수자리": "sagittarius",
    "염소자리": "capricorn",
    "물병자리": "aquarius",
    "물고기자리": "pisces"
}


def get_zodiac_sign(birth_date_str):
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    month, day = birth_date.month, birth_date.day

    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "양자리"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "황소자리"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
        return "쌍둥이자리"
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return "게자리"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "사자자리"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "처녀자리"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 23):
        return "천칭자리"
    elif (month == 10 and day >= 24) or (month == 11 and day <= 22):
        return "전갈자리"
    elif (month == 11 and day >= 23) or (month == 12 and day <= 24):
        return "사수자리"
    elif (month == 12 and day >= 25) or (month == 1 and day <= 19):
        return "염소자리"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "물병자리"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "물고기자리"

def build_prompt(zodiac: str, date_str: str, external_content: str) -> str:
    return f"""
안녕하세요! 오늘은 {date_str}이네요. 저는 여러분의 일상에 작은 영감을 드리는 점성술사입니다.

{zodiac} 분들을 위한 오늘의 운세 정보를 받았어요:

[운세 원문]
{external_content}을 한글로 번역하고 요약.

이 내용을 토대로 {zodiac}에 맞는 오늘의 운세를 자연스럽고 편안한 말투로 요약해 주세요.

다음과 같이 작성해주세요:
- 자연스럽고 편안한 말투로
- 3-4문장으로 오늘의 전반적인 흐름을 요약
- 실생활에서 바로 적용할 수 있는 구체적인 조언 포함
- 희망적이고 긍정적인 메시지로 마무리
- 전문성은 유지하되 어려운 용어는 피해서 누구나 쉽게 이해할 수 있게
"""