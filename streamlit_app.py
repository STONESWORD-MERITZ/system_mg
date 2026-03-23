import streamlit as st
import pdfplumber
import pandas as pd
import re
from datetime import datetime

# ==========================================
# 1. 웹 페이지 기본 설정 & 테마 (타이틀 탭 변경)
# ==========================================
st.set_page_config(page_title="MG Scanner | 스마트 알릴의무 검증", layout="wide", page_icon="🛡️")

# ==========================================
# 2. 커스텀 CSS (이민규 브랜딩: 신뢰의 네이비 & 모던 UI)
# ==========================================
custom_css = """
<style>
    /* 전체 배경색을 아주 밝은 쿨그레이로 설정하여 깔끔함 강조 */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* 기본 스트림릿 메뉴 숨기기 (완성된 앱 느낌 부여) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 커스텀 헤더 디자인 */
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    .main-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* 사이드바 디자인 변경 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* 데이터프레임(표) 스타일링 */
    .dataframe {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid #e2e8f0 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. 메인 화면 헤더 (독자 브랜드 로고 영역)
# ==========================================
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🛡️ MG Medical Scanner</h1>
    <p class="main-subtitle">이민규 대표의 지능형 알릴의무 및 언더라이팅 검증 솔루션</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. 좌측 사이드바: 표준 알릴 의무 체크리스트
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2621/2621011.png", width=50) # 임시 신뢰 아이콘
    st.markdown("### ⚙️ 검증 엔진 설정")
    st.caption("고객 상담 내용에 맞춰 필터를 조정하세요.")
    
    st.divider()
    
    st.subheader("1. 단기 진료 이력")
    check_3months = st.checkbox("최근 3개월 이내 모든 진료", value=True)
    check_1year = st.checkbox("최근 1년 이내 추가검사 의심", value=False)
    
    st.divider()
    
    st.subheader("2. 장기 진료 이력")
    check_5years_heavy = st.checkbox("최근 5년 이내 입원/수술/7일치료", value=True)
    check_10years_heavy = st.checkbox("최근 10년 이내 입원/수술", value=False)
    
    st.divider()
    
    st.subheader("3. 11대 중증 질환")
    check_11_diseases = st.checkbox("최근 5년 이내 11대 질병", value=True)
    st.caption("C(암), I10-15(고혈압), E10-14(당뇨) 등")
    disease_11_prefixes = ["C", "D0", "I10", "I11", "I12", "I13", "I14", "I15", "I20", "I21", "I22", "I3", "K74", "I6", "E10", "E11", "E12", "E13", "E14", "B2"]

    st.divider()
    keyword_input = st.text_input("🔍 추가 위험 키워드", "수술, 종양, 폴립, 결절")
    keywords = [k.strip() for k in keyword_input.split(",") if k.strip()]


# ==========================================
# 5. 메인 화면: 파일 업로드 및 데이터 처리
# ==========================================
st.markdown("#### 📑 심평원 진료자료 업로드")
uploaded_file = st.file_uploader("PDF 파일을 드래그하거나 클릭하여 업로드하세요.", type="pdf")

if uploaded_file is not None:
    with st.spinner('데이터 추출 및 AI 검증 엔진 가동 중...'):
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                all_data = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        cleaned_table = [row for row in table if row and any(cell for cell in row)]
                        all_data.extend(cleaned_table)
            
            if all_data:
                df = pd.DataFrame(all_data[1:], columns=all_data[0])
                df = df.fillna("")
                
                df = df[~df.iloc[:, 0].astype(str).str.contains("순번", na=False)]
                df = df.reset_index(drop=True)
                df.index = df.index + 1
                
                code_col_idx = -1
                in_out_col_idx = -1
                days_col_idx = -1
                
                for i, col_name in enumerate(df.columns):
                    col_str = str(col_name).replace(" ", "")
                    if "코드" in col_str: code_col_idx = i
                    if "입원" in col_str or "외래" in col_str: in_out_col_idx = i
                    if "내원일수" in col_str: days_col_idx = i

                flagged_count = 0
                
                def highlight_underwriting(row):
                    global flagged_count
                    row_str_list = row.astype(str).tolist()
                    row_text = " ".join(row_str_list)
                    
                    days_passed = 9999
                    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', row_text)
                    if date_match:
                        try:
                            row_date = datetime.strptime(date_match.group(), "%Y-%m-%d")
                            days_passed = (datetime.now() - row_date).days
                        except:
                            pass
                    
                    years_passed = days_passed / 365.25
                    is_flagged = False
                    
                    is_inpatient = False
                    if in_out_col_idx != -1 and "입원" in str(row.iloc[in_out_col_idx]):
                        is_inpatient = True
                    
                    visit_days = 0
                    if days_col_idx != -1:
                        digits = re.findall(r'\d+', str(row.iloc[days_col_idx]))
                        if digits: visit_days = int(digits[0])
                        
                    disease_code = ""
                    if code_col_idx != -1:
                        disease_code = str(row.iloc[code_col_idx]).strip().upper()

                    if check_3months and days_passed <= 90: is_flagged = True
                        
                    if check_1year and years_passed <= 1: is_flagged = True
                        
                    if check_5years_heavy and years_passed <= 5:
                        if is_inpatient or visit_days >= 7: is_flagged = True
                        for kw in keywords: 
                            if kw and kw in row_text: is_flagged = True
                                
                    if check_11_diseases and years_passed <= 5 and disease_code:
                        for prefix in disease_11_prefixes:
                            if disease_code.startswith(prefix):
                                is_flagged = True
                                break
                                
                    if check_10years_heavy and years_passed <= 10:
                        if is_inpatient: is_flagged = True
                        for kw in keywords: 
                            if kw and kw in row_text: is_flagged = True
                    
                    if is_flagged:
                        if 'is_counted' not in row:
                            flagged_count += 1
                        # 고급스러운 경고 색상 (연한 주황/코랄)
                        return ['background-color: #fff7ed; color: #c2410c; font-weight: bold;'] * len(row)
                    return [''] * len(row)

                st.markdown("<br>", unsafe_allow_html=True)
                styled_df = df.style.apply(highlight_underwriting, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                # ==========================================
                # 6. 결과 리포트 섹션
                # ==========================================
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 💡 매칭 솔루션 리포트")
                
                if flagged_count == 0:
                    st.success("✅ **검증 완료: 설정된 고지 의무 위반 의심 내역이 없습니다.**")
                    col1, col2 = st.columns(2)
                    with col1: st.info("🏆 **1순위 추천**\n\n**일반 건강보험 (표준체)**\n\n할증이나 부담보 없이 최적의 조건으로 심사 진행이 가능합니다.")
                    with col2: st.info("🌟 **2순위 추천**\n\n**건강고지형/할인형 상품**\n\n고객의 우수한 건강 등급을 활용해 보험료 할인을 제안하세요.")
                else:
                    st.warning(f"⚠️ **검증 완료: 총 {flagged_count}건의 고지 의무 대상 의심 내역이 발견되었습니다.**")
                    col1, col2 = st.columns(2)
                    with col1: st.error("🏥 **1순위 추천 플랜**\n\n**간편건강보험 (유병자 3-N-5 플랜)**\n\n발견된 병력의 경과 기간을 확인하여 무서류 통과가 가능한 간편 플랜을 적용하세요.")
                    with col2: st.warning("⚖️ **2순위 추천 플랜**\n\n**표준체 부분 부담보 심사**\n\n경증 질환인 경우, 해당 신체 부위만 부담보 조건을 걸고 일반 상품으로 승인을 유도하세요.")

            else:
                st.error("PDF에서 데이터를 추출할 수 없습니다. 심평원 양식이 맞는지 확인해 주세요.")
        except Exception as e:
            st.error(f"시스템 오류: {e}")