import openai
import urllib.request

# OpenAI API 키 설정
API_KEY = "your_api_key_here"  # ← 여기에 본인의 API 키 입력
client = openai.OpenAI(api_key=API_KEY)  # ← 여기에 본인의 API 키 입력

# DALL·E 3 기반 이미지 생성
response = client.images.generate(
    model="dall-e-3",  # 최신 모델: dall-e-3
    prompt="a white siamese cat sitting on a red sofa",
    n=1,
    size="1024x1024",       # 지원 사이즈: 1024x1024
    quality="standard",     # standard | hd
    style="vivid"           # vivid | natural (선택 사항, 생략 가능)
)

# 이미지 URL 저장 및 확인
image_url = response.data[0].url
urllib.request.urlretrieve(image_url, "test.jpg")
print(image_url)