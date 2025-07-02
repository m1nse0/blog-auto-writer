import streamlit as st
import requests
import json
from keyword_extractor import extract_top_keywords
from gemini_vision import generate_image_captions
from blog_generator import generate_blog_post

# --------------------- 기본 설정 ---------------------
st.set_page_config(page_title="블로그 자동화 시스템", layout="wide")
st.title("📸 맛집 블로그 자동 생성기")

# --------------------- 입력 ---------------------
st.subheader("1️⃣ 음식점 정보 입력")
store_name = st.text_input("음식점 이름")
location = st.text_input("지역")
main_menu = st.text_input("대표 메뉴")
menus = st.text_area("주문한 전체 메뉴 (콤마로 구분)", placeholder="차돌박이, 키조개, 김치, 쫄면")
with_whom = st.text_input("누구와 방문했나요? (예: 친구, 연인, 혼자)")
mood = st.text_input("가게 분위기 (예: 캐주얼하고 활기참, 조용하고 감성적임)")
uploaded_files = st.file_uploader("사진 업로드 (여러 장 가능)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# --------------------- 실행 ---------------------
if st.button("✏️ 블로그 글 자동 생성"):
    if not (store_name and location and main_menu and menus and mood):
        st.warning("모든 정보를 입력해 주세요.")
    else:
        st.info("🔍 키워드 분석 및 이미지 설명 생성 중...")

        # 1. 키워드 추출
        keywords = extract_top_keywords(
            store_name=store_name,
            location=location,
            menu_list=menus.split(","),
            access_license=st.secrets["naver_access_license"],
            secret_key=st.secrets["naver_secret_key"]
        )

        # 2. 이미지 설명 생성
        image_descriptions = []
        for file in uploaded_files:
            caption = generate_image_captions(file, api_key=st.secrets["gemini_api_key"])
            image_descriptions.append((file.name, caption))

        # 3. 블로그 글 생성
        post = generate_blog_post(
            store_name=store_name,
            location=location,
            main_menu=main_menu,
            menus=menus,
            with_whom=with_whom,
            mood=mood,
            image_descriptions=image_descriptions,
            keywords=keywords
        )

        # 4. 출력
        st.success("✅ 글 생성 완료! 아래 내용을 복사해 블로그에 붙여 넣어주세요.")
        st.subheader("✍️ 블로그 본문")
        st.markdown(post.blog_body)

        st.subheader("🏷️ 추천 해시태그 (30개)")
        st.markdown(", ".join(post.hashtags))

        st.subheader("📢 최종 제목 추천")
        st.markdown(f"**{post.title}**")
