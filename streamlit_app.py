import streamlit as st
import pdfplumber
import pandas as pd
import re
from datetime import datetime

# ==========================================
# 웹 페이지 기본 설정
# ==========================================
st.set_page_config(page_title="심평원 분석기 & 알릴의무 체크", layout="wide")

# ==========================================
# 1. 좌측 사이드바: 표준 알릴 의무 체크리스트
# ==========================================
with st.sidebar:
    st.header("📝 표준 알릴 의무 필터링")
    st.write("청약서 질문지에 맞춰 심평원 데이터를 검증합니다.")
    
    st.subheader("1. 단기 진료 이력")
    check_3months = st.checkbox("[1번 질문] 최근 3개월 이내 모든 진료", value=True)
    check_1year = st.checkbox("[3번 질문] 최근 1년 이내 진료 (추가검사 의심)", value=False)
    
    st.divider()
    
    st.subheader("2. 장기 진료 이력 (입원/수술 등)")
    check_5years_heavy = st.checkbox("[4번 질문] 최근 5년 이내 입원, 수술, 7일 이상 치료", value=True)
    check_10years_heavy = st.checkbox("[6번 질문] 최근 10년 이내 입원, 수술", value=False)
    
    st.divider()
    
    st.subheader("3. 11대 질병 이력 (최근 5년)")
    check_11_diseases = st.checkbox("[5번 질문] 최근 5년 이내 11대 질병", value=True)
    st.caption("자동 매칭 코드: C(암), I10-15(고혈압), E10-14(당뇨), I60-64(뇌졸중), I20-22(심장), K74(간경화) 등")
    
    # 11대 질병 핵심 접두사 리스트 (단순화 버전)
    disease_11_prefixes = ["C", "D0", "I10", "I11", "I12", "I13", "I14", "I15", "I20", "I21", "I22", "I3", "K74", "I6", "E10", "E11", "E12", "E13", "E14", "B2"]

    st.divider()
    st.subheader("🔍 추가 검색 키워드")
    keyword_input = st.text_input("위험 키워드 (쉼표 구분)", "수술, 종양, 폴립, 결절")
    keywords = [k.strip() for k in keyword_input.split(",") if k.strip()]

# ==========================================
# 2. 메인 화면: 파일 업로드 및 데이터 처리
# ==========================================
st.title("📄 심평원 알릴 의무 자동 검증 시스템")

uploaded_file = st.file_uploader("심평원 PDF 파일을 업로드하세요", type="pdf")

if uploaded_file is not None:
    st.info("데이터를 분석하고 알릴 의무 조항을 교차 검증 중입니다...")
    
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
            
            # 헤더(순번) 행 제거 및 인덱스 초기화
            df = df[~df.iloc[:, 0].astype(str).str.contains("순번", na=False)]
            df = df.reset_index(drop=True)
            df.index = df.index + 1
            
            # 중요 컬럼의 인덱스(위치) 파악
            code_col_idx = -1
            in_out_col_idx = -1
            days_col_idx = -1
            
            for i, col_name in enumerate(df.columns):
                col_str = str(col_name).replace(" ", "")
                if "코드" in col_str: code_col_idx = i
                if "입원" in col_str or "외래" in col_str: in_out_col_idx = i
                if "내원일수" in col_str: days_col_idx = i

            flagged_count = 0
            
            # ==========================================
            # 3. 알릴 의무 지능형 매칭 알고리즘
            # ==========================================
            def highlight_underwriting(row):
                global flagged_count
                row_str_list = row.astype(str).tolist()
                row_text = " ".join(row_str_list)
                
                # 날짜 및 기간 계산
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
                
                # 기타 데이터 파싱 (입원여부, 내원일수, 질병코드)
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

                # --- 룰 검증 시작 ---
                
                # 1. [Q1] 3개월 이내 모든 진료
                if check_3months and days_passed <= 90:
                    is_flagged = True
                    
                # 2. [Q3] 1년 이내 진료 (단순 기간 필터)
                if check_1year and years_passed <= 1:
                    is_flagged = True
                    
                # 3. [Q4] 5년 이내 입원/수술/7일이상 통원
                if check_5years_heavy and years_passed <= 5:
                    if is_inpatient or visit_days >= 7:
                        is_flagged = True
                    for kw in keywords: # 수술 등 키워드
                        if kw and kw in row_text:
                            is_flagged = True
                            
                # 4. [Q5] 5년 이내 11대 질병
                if check_11_diseases and years_passed <= 5 and disease_code:
                    for prefix in disease_11_prefixes:
                        if disease_code.startswith(prefix):
                            is_flagged = True
                            break
                            
                # 5. [Q6] 10년 이내 입원/수술
                if check_10years_heavy and years_passed <= 10:
                    if is_inpatient:
                        is_flagged = True
                    for kw in keywords: # 수술 등 키워드
                        if kw and kw in row_text:
                            is_flagged = True
                
                # --- 룰 검증 끝 ---
                
                if is_flagged:
                    if 'is_counted' not in row:
                        flagged_count += 1
                    return ['background-color: #ffcccc; color: #900000'] * len(row)
                return [''] * len(row)

            # 표 출력
            styled_df = df.style.apply(highlight_underwriting, axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            # ==========================================
            # 4. 상품 추천 결과
            # ==========================================
            st.divider()
            st.subheader("💡 알릴 의무 심사 및 상품 매칭 결과")
            
            if flagged_count == 0:
                st.success("✅ **현재 설정된 알릴 의무 질문에 해당하는 위험 내역이 발견되지 않았습니다.**")
                col1, col2 = st.columns(2)
                with col1: st.info("🏆 **추천: 일반 건강보험 (표준체)** - 할증/부담보 없이 가입 가능 예상")
                with col2: st.info("🌟 **추천: 건강고지형 보험 (예: 10년 무사고 할인)**")
            else:
                st.warning(f"⚠️ **고지 의무 대상 의심 내역이 {flagged_count}건 발견되었습니다.** (붉은색 표시 항목)")
                col1, col2 = st.columns(2)
                with col1: st.error("🏥 **추천: 간편건강보험 (유병자 플랜)** - 발견된 내역의 시기(N년)에 맞춰 3-N-5 상품 탐색 요망")
                with col2: st.warning("⚖️ **추천: 표준체 할증/부담보 심사** - 경증인 경우 해당 부위 부담보로 일반 상품 진행")

        else:
            st.warning("PDF에서 표 데이터를 찾을 수 없습니다.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")