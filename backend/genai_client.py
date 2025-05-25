import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. .env 파일에서 환경 변수 로드
load_dotenv()

# 2. Gemini API 키 가져오기
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경 변수를 .env 파일에 설정해주세요.")

# 3. Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)

# 4. 사용할 모델 초기화 (OpenAI의 client = OpenAI(...) 와 유사한 역할)
# system_instruction을 사용하여 모델에 역할 부여
# "너는 별자리 운세 전문가야."
try:
    # gemini-1.5-flash-latest: 빠르고 비용 효율적이며 system_instruction 지원
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest',
        system_instruction="너는 별자리 운세 전문가야."
        # 안전 설정 (필요에 따라 기본값 외에 커스텀 설정 가능)
        # safety_settings=[
        #     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        #     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        #     {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        #     {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        # ]
    )
    print(f"Gemini 모델 ('{model.model_name}')이 성공적으로 로드되었습니다.")
except Exception as e:
    print(f"Gemini 모델 초기화 중 오류 발생: {e}")
    print("사용 가능한 모델 목록을 확인하거나 API 키 설정을 점검해주세요.")
    model = None # 모델 로드 실패 시 None으로 설정


# 5. 별자리 운세 응답 생성 함수
def get_horoscope_response_gemini(prompt: str) -> str:
    """
    Gemini API를 사용하여 별자리 운세 응답을 생성합니다.
    OpenAI의 client.chat.completions.create와 유사한 역할을 합니다.
    """
    if not model:
        return "오류: Gemini 모델이 로드되지 않았습니다. API 키와 모델 이름을 확인하세요."

    try:
        # OpenAI의 messages=[{"role": "user", "content": prompt}] 부분에 해당
        # system 역할은 모델 초기화 시 system_instruction으로 이미 전달됨
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=300
            )
        )
        # OpenAI의 response.choices[0].message.content.strip() 에 해당
        return response.text.strip()
    except Exception as e:
        error_message = f"Gemini API 호출 중 오류 발생: {e}"
        # 응답 객체가 생성되었고, prompt_feedback 속성이 있는지 확인
        # (오류 발생 시 response 객체가 없을 수 있으므로 안전하게 접근)
        # API 호출 중단 등 좀 더 구체적인 오류 원인 파악 시도
        if 'response' in locals() and hasattr(response, 'prompt_feedback'):
            block_reason = response.prompt_feedback.block_reason
            if block_reason:
                reason_message = response.prompt_feedback.block_reason_message or str(block_reason)
                error_message += f"\n차단 사유: {reason_message}"
        print(error_message)
        return "죄송합니다, 운세를 생성하는 데 예상치 못한 문제가 발생했습니다."

# --- 메인 실행 부분 (테스트용) ---
if __name__ == "__main__":
    if model: # 모델이 성공적으로 로드되었을 경우에만 실행
        user_prompt_1 = "오늘 물병자리의 전체적인 운세를 알려줘."
        horoscope_1 = get_horoscope_response_gemini(user_prompt_1)
        print(f"\n[사용자 질문 1]: {user_prompt_1}")
        print(f"[Gemini 운세 결과 1]:\n{horoscope_1}")

        user_prompt_2 = "내일 게자리의 연애운은 어떨까? 조언도 함께 해줘."
        horoscope_2 = get_horoscope_response_gemini(user_prompt_2)
        print(f"\n[사용자 질문 2]: {user_prompt_2}")
        print(f"[Gemini 운세 결과 2]:\n{horoscope_2}")
    else:
        print("\n테스트를 실행할 수 없습니다. Gemini 모델이 성공적으로 로드되지 않았습니다.")