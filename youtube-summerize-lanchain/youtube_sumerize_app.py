##### 기본 정보 입력 #####
import streamlit as st
import re
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from deep_translator import GoogleTranslator

##### 기능 구현 함수 #####
def google_trans(messages):
    max_len = 5000
    if len(messages) > max_len:
        messages = messages[:max_len]
    return GoogleTranslator(source='auto', target='ko').translate(messages)

def youtube_url_check(url):
    pattern = r'^https:\/\/www\.youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)(\&ab_channel=[\w\d]+)?$'
    return re.match(pattern, url) is not None

##### 메인 함수 #####
def main():
    st.set_page_config(page_title="YouTube Summerize", layout="wide")

    if "flag" not in st.session_state:
        st.session_state["flag"] = True
    if "OPENAI_API" not in st.session_state:
        st.session_state["OPENAI_API"] = ""
    if "summerize" not in st.session_state:
        st.session_state["summerize"] = ""

    st.header("📹 영어 YouTube 내용 요약 / 대본 번역기")
    st.markdown('---')

    st.subheader("YouTube URL을 입력하세요")
    youtube_video_url = st.text_input("  ", placeholder="https://www.youtube.com/watch?v=**********")

    with st.sidebar:
        open_apikey = st.text_input(label='OPENAI API 키', placeholder='Enter Your API Key', value='', type='password')
        if open_apikey:
            st.session_state["OPENAI_API"] = open_apikey
        st.markdown('---')

    if len(youtube_video_url) > 2:
        if not youtube_url_check(youtube_video_url):
            st.error("YouTube URL을 확인하세요.")
        else:
            _, container, _ = st.columns([25, 50, 25])
            container.video(data=youtube_video_url)

            loader = YoutubeLoader.from_youtube_url(youtube_video_url)
            transcript = loader.load()

            st.subheader("요약 결과")
            if st.session_state["flag"]:
                llm = ChatOpenAI(
                    temperature=0,
                    openai_api_key=st.session_state["OPENAI_API"],
                    max_tokens=3000,
                    model_name="gpt-3.5-turbo",
                    request_timeout=120
                )

                prompt = PromptTemplate(
                    template="""Summarize the youtube video whose transcript is provided within backticks 
                    ```{text}```""",
                    input_variables=["text"]
                )
                combine_prompt = PromptTemplate(
                    template="""Combine all the youtube video transcripts provided within backticks 
                    ```{text}``` 
                    Provide a concise summary between 8 to 10 sentences.""",
                    input_variables=["text"]
                )

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=0)
                text = text_splitter.split_documents(transcript)

                chain = load_summarize_chain(
                    llm, chain_type="map_reduce", verbose=False,
                    map_prompt=prompt, combine_prompt=combine_prompt
                )
                st.session_state["summerize"] = chain.run(text)
                st.session_state["flag"] = False

            st.success(st.session_state["summerize"])

            # 요약 번역
            try:
                transe = google_trans(st.session_state["summerize"])
                st.subheader("요약 번역 결과")
                st.info(transe)
            except Exception as e:
                st.warning(f"요약 번역 실패: {e}")

            # 대본 전체 번역
            st.subheader("대본 번역하기")
            if st.button("대본 번역실행"):
                if transcript and len(transcript) > 0:
                    try:
                        script_text = transcript[0].page_content
                        translated_script = google_trans(script_text)
                        st.markdown(translated_script)
                    except Exception as e:
                        st.warning(f"대본 번역 실패: {e}")
                else:
                    st.warning("자막을 불러올 수 없습니다. 자막이 없는 영상일 수 있습니다.")

if __name__ == "__main__":
    main()