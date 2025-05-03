##### 기본 정보 입력 #####
import streamlit as st
from PyPDF2 import PdfReader

# LangChain 최신 구조 기반 임포트
from langchain_community.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain

# 안정적인 번역기 (deep_translator)
from deep_translator import GoogleTranslator

##### 번역 함수 #####
def google_trans(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text[:4999])  # 5000자 제한 대응
    except Exception as e:
        return f"❌ 번역 실패: {str(e)}"

##### 메인 함수 #####
def main():
    st.set_page_config(page_title="📜 PDF Analyzer with Q&A", layout="wide")

    # 사이드바 – API 키 입력
    with st.sidebar:
        open_apikey = st.text_input(label='🔐 OPENAI API 키', placeholder='Enter your OpenAI API Key', type='password')
        if open_apikey:
            st.session_state["OPENAI_API"] = open_apikey
        st.markdown("---")

    # 제목
    st.title("📄 PDF 문서 기반 질문 시스템")
    st.markdown("업로드한 PDF 내용을 바탕으로 질문에 답변하고, 한국어 번역도 지원합니다.")
    st.markdown("---")

    # PDF 업로드
    st.subheader("1️⃣ PDF 파일 업로드")
    pdf = st.file_uploader("PDF 파일을 선택하세요", type="pdf")

    if pdf is not None:
        # 텍스트 추출
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        if not text.strip():
            st.error("PDF에서 텍스트를 추출할 수 없습니다.")
            return

        # 텍스트 분할
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # 질문 입력
        st.subheader("2️⃣ 질문 입력")
        user_question = st.text_input("PDF 내용에 대해 질문하세요:")

        if user_question and "OPENAI_API" in st.session_state:
            try:
                embeddings = OpenAIEmbeddings(openai_api_key=st.session_state["OPENAI_API"])
                knowledge_base = FAISS.from_texts(chunks, embeddings)
                docs = knowledge_base.similarity_search(user_question)

                llm = ChatOpenAI(
                    temperature=0,
                    openai_api_key=st.session_state["OPENAI_API"],
                    max_tokens=2000,
                    model_name="gpt-3.5-turbo",
                    request_timeout=120
                )
                chain = load_qa_chain(llm, chain_type="stuff")
                response = chain.run(input_documents=docs, question=user_question)

                st.subheader("🧠 답변")
                st.info(response)

                # 번역 버튼
                if st.button("🌐 한국어 번역"):
                    translated = google_trans(response)
                    st.success(translated)

            except Exception as e:
                st.error(f"❌ 처리 중 오류가 발생했습니다: {str(e)}")

        elif user_question:
            st.warning("🔑 먼저 OpenAI API 키를 입력해주세요.")

if __name__ == '__main__':
    main()