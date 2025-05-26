# scraper.py

import requests
from bs4 import BeautifulSoup
from firebase_client import save_horoscope, is_horoscope_saved_today
from datetime import datetime
from horoscope import ZODIAC_NAMES, ZODIAC_KO_TO_EN
import schedule
import time

# ✅ 별자리 전체를 순회하면서 저장하는 함수
def fetch_all_zodiacs():
    print(f"\n📆 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 별자리 운세 수집 시작")

    already_saved = True
    for zodiac in ZODIAC_NAMES:
        if not is_horoscope_saved_today(zodiac):
            already_saved = False
            break

    if already_saved:
        print("✅ 오늘의 모든 별자리 운세가 이미 저장되어 있습니다. 크롤링을 건너뜁니다.\n")
        return
    
    for zodiac in ZODIAC_NAMES:
        url = f"https://cafeastrology.com/{ZODIAC_KO_TO_EN[zodiac]}dailyhoroscope.html"
        try:
            print(f"→ {zodiac} 크롤링 중: {url}")
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            content = soup.select_one('.entry-content')
            summary = content.get_text(separator="\n", strip=True) if content else "운세를 불러오지 못했습니다."

            save_horoscope(zodiac, summary)
            print(f"[✔] {zodiac} 저장 완료 ✅")
        except Exception as e:
            print(f"[❌] {zodiac} 오류 발생: {e}")

    print("✅ 모든 운세 저장 완료\n")

# 하루에 한 번 오전 6시에 실행
schedule.every().day.at("06:00").do(fetch_all_zodiacs)

# 실행 즉시 한 번 수집
fetch_all_zodiacs()

if __name__ == "__main__":
    # 실행 즉시 한 번 수집
    fetch_all_zodiacs()
    while True:   
        schedule.run_pending()
        time.sleep(60)


##  tbody = soup.select_one(".conForture #star #con_box tbody")