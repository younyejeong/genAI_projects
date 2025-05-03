##### 기본 정보 입력 #####
import streamlit as st
from openai import OpenAI
from instagrapi import Client
from PIL import Image
import urllib.request
from deep_translator import GoogleTranslator

client = None  # OpenAI 클라이언트

##### 기능 구현 함수 #####
# 영어로 번역
def google_trans(messages):
    return GoogleTranslator(source='auto', target='en').translate(messages)

# 인스타 업로드
def uploadinstagram(description):
    cl = Client()
    cl.login(st.session_state["instagram_ID"], st.session_state["instagram_Password"])
    cl.photo_upload("instaimg_resize.jpg", description)

# ChatGPT에게 질문/답변받기
def getdescriptionFromGPT(topic, mood):
    prompt = f'''
Write me the Instagram post description or caption in just a few sentences for the post 
-topic : {topic}
-Mood : {mood}
Format every new sentence with new lines so the text is more readable.
Include emojis and the best Instagram hashtags for that post.
The first caption sentence should hook the readers.
write all output in korean.'''
    messages_prompt = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages_prompt
    )
    return response.choices[0].message.content

# DALL·E 이미지 생성
def getImageURLFromDALLE(topic, mood):
    t_topic = google_trans(topic)
    t_mood = google_trans(mood)
    prompt_ = f"Draw a picture about {t_topic}. The mood is {t_mood}."

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt_,
        n=1,
        size="1024x1024"
    )

    image_url = response.data[0].url
    urllib.request.urlretrieve(image_url, "instaimg.jpg")

##### 메인 함수 #####
def main():
    global client
    st.set_page_config(page_title="Instabot", page_icon="📸")

    # session state 초기화
    for key in ["description", "flag", "instagram_ID", "instagram_Password"]:
        if key not in st.session_state:
            st.session_state[key] = "" if "ID" in key or "Password" in key else False if key == "flag" else ""

    st.header('인스타그램 포스팅 생성기')
    st.markdown('---')

    with st.expander("인스타그램 포스팅 생성기", expanded=True):
        st.write(
        """     
        - 이미지는 OpenAI DALL·E 3 (gpt-4-turbo)을 통해 생성합니다. 
        - 포스팅 글은 GPT-3.5를 이용해 자동 작성됩니다.
        - 인스타그램 업로드는 instagrapi를 이용합니다.
        """
        )

    with st.sidebar:
        open_apikey = st.text_input(label='🔑 OPENAI API 키', type="password")
        if open_apikey:
            client = OpenAI(api_key=open_apikey)
        st.markdown('---')

    topic = st.text_input(label="📌 주제", placeholder="예: 고양이, 축구, 인공지능 등")
    mood = st.text_input(label="🎭 분위기", placeholder="예: 재미있는, 감성적인")

    if st.button(label="✨ 생성", type="primary") and not st.session_state["flag"]:
        if client is None:
            st.error("🔑 OpenAI API 키를 입력해 주세요.")
        else:
            with st.spinner('콘텐츠 생성 중...'):
                st.session_state["description"] = getdescriptionFromGPT(topic, mood)
                getImageURLFromDALLE(topic, mood)
                st.session_state["flag"] = True

    if st.session_state["flag"]:
        image = Image.open("instaimg.jpg")
        st.image(image)

        txt = st.text_area(label="✏️ 캡션 수정", value=st.session_state["description"], height=100)
        st.session_state["description"] = txt

        st.markdown('🔐 인스타그램 로그인')
        st.session_state["instagram_ID"] = st.text_input(label='ID', placeholder='Instagram ID')
        st.session_state["instagram_Password"] = st.text_input(label='Password', type='password', placeholder='Instagram Password')

        if st.button(label='📤 업로드'):
            image = Image.open("instaimg.jpg").convert("RGB")
            new_image = image.resize((1080, 1080))
            new_image.save("instaimg_resize.jpg")
            uploadinstagram(st.session_state["description"])
            st.success("인스타그램에 업로드 완료!")
            st.session_state["flag"] = False

if __name__ == "__main__":
    main()