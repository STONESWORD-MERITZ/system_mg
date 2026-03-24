import streamlit as st
import pdfplumber
import pandas as pd
import re
from datetime import datetime
from collections import defaultdict

# ==========================================
# 1. 웹 페이지 기본 설정 & 테마
# ==========================================
st.set_page_config(page_title="AdvisorHub | 스마트 고지 스캐너", layout="wide", page_icon="🏛️")

custom_css = """
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 1. 배경 설정 (라이트 모드 고정) */
    .stApp { background-color: #f4f7f9 !important; font-family: 'Pretendard', sans-serif; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stFileUploader"] section { background-color: #ffffff !important; border: 2px dashed #94a3b8 !important; border-radius: 12px !important; }
    [data-testid="stUploadedFile"] { background-color: #f1f5f9 !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; }
    div[data-testid="stAlert"] { background-color: #fefce8 !important; border: 1px solid #fef08a !important; border-radius: 12px !important; }

    /* 🚨 2. 흰색 글씨 절대 금지 (업로드된 파일명 포함 모든 태그를 진한 네이비로 강제 고정) */
    p, span, label, h1, h2, h3, h4, h5, h6, li, b, div[data-testid="stMarkdownContainer"], .stRadio div,
    [data-testid="stFileUploader"] *, [data-testid="stUploadedFile"] * {
        color: #0f172a !important;
    }
    /* 업로드된 파일명 박스 텍스트 특별 강제 고정 */
    [data-testid="stUploadedFile"] div, [data-testid="stUploadedFile"] span, [data-testid="stUploadedFile"] p {
        color: #0f172a !important; font-weight: 600 !important;
    }

    /* 🚨 2-1. 파일 업로드 버튼 색상 및 'Browse files' 영문 텍스트 강제 변경 */
    [data-testid="stFileUploader"] button {
        background-color: #1e3a8a !important; 
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
    }
    [data-testid="stFileUploader"] button p, 
    [data-testid="stFileUploader"] button span {
        font-size: 0 !important; /* 기존 영어 글씨를 크기 0으로 만들어 숨기기 */
    }
    [data-testid="stFileUploader"] button span::after {
        content: '파일 업로드' !important; /* 👈 이 부분을 수정했습니다! */
        font-size: 1rem !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* 🚨 3. 예외 복구 (우리가 직접 디자인한 컬러들만 살려두기) */
    .hero-tag, .hero-tag span { color: #2563eb !important; }
    .hero-title span { color: #1e3a8a !important; }
    .hero-subtitle { color: #475569 !important; }
    
    .info-card-header { color: #1e3a8a !important; }
    .info-title { color: #334155 !important; }
    .info-list li::before { color: #3b82f6 !important; }
    .badge-blue { color: #1d4ed8 !important; background: #dbeafe !important; }
    .badge-red { color: #b91c1c !important; background: #fee2e2 !important; }
    
    .report-title, .report-title span { color: #1e3a8a !important; }
    .duty-title, .duty-title span { color: #be123c !important; }
    .duty-tag { color: #9f1239 !important; background: #fee2e2 !important; }
    .duty-detail span { color: #be123c !important; }
    .duty-stats { color: #475569 !important; }
    
    div[data-testid="stAlert"] p, div[data-testid="stAlert"] span { color: #854d0e !important; font-weight: 600 !important; }

    /* 4. 기타 UI 레이아웃 구성 요소 */
    .info-card { background: #ffffff !important; border-radius: 16px; padding: 1.8rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); border: 1px solid #e2e8f0 !important; margin-top: 0.5rem; margin-bottom: 2.5rem; }
    .info-card-header { font-size: 1.15rem; font-weight: 800; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #f1f5f9 !important; padding-bottom: 0.8rem; }
    
    /* 🚨 [최종 수정] 좌우 박스 황금 밸런스 조정 및 중앙 여백(gap) 축소로 공간 확보 */
    .info-grid { display: grid; grid-template-columns: 4.7fr 5.3fr; gap: 1rem; }
    
    .info-col { background: #f8fafc !important; border-radius: 12px; padding: 1.2rem; border: 1px solid #f1f5f9 !important; }
    .info-title { font-weight: 800; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 6px; font-size: 1.05rem; letter-spacing: -0.02em; }
    .info-list { list-style: none; padding: 0; margin: 0; }
    
    /* 자간(letter-spacing)을 미세하게 줄여 작은 화면에서도 한 줄에 완벽히 담기도록 최적화 */
    .info-list li { font-size: 0.9rem; margin-bottom: 0.6rem; padding-left: 1.4rem; position: relative; line-height: 1.5; word-break: keep-all; letter-spacing: -0.02em; }
    
    .info-list li::before { content: '✓'; position: absolute; left: 0; font-weight: 900; }
    .badge-blue, .badge-red { padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; font-weight: 800; }

    .hero-container { background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important; border: 1px solid #e2e8f0 !important; border-radius: 24px; padding: 2.5rem 2rem; margin-bottom: 2rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); text-align: center; }
    .hero-tag { display: inline-block; background-color: #eff6ff !important; padding: 0.4rem 1.2rem; border-radius: 50px; margin-bottom: 1rem; font-size: 0.8rem; font-weight: 800; }
    .hero-title { font-size: 2.4rem; font-weight: 900; line-height: 1.3; margin-bottom: 0.8rem; }
    .hero-subtitle { font-size: 1.05rem; font-weight: 500; }
    
    .glass-card { background: #ffffff !important; border-radius: 16px; padding: 2rem; border: 1px solid #e2e8f0 !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02); margin-bottom: 1.5rem; }
    .report-title { font-weight: 900; font-size: 1.3rem; border-bottom: 2px solid #e2e8f0 !important; padding-bottom: 0.8rem; margin-bottom: 1.2rem; }
    
    .duty-box { background-color: #ffffff !important; border-radius: 12px; border: 1px solid #e2e8f0 !important; border-left: 6px solid #be123c !important; padding: 1.2rem 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .duty-title { font-weight: 900; font-size: 1.1rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 8px;}
    .duty-tag { padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 800; }
    .duty-detail { font-size: 0.95rem; font-weight: 500; line-height: 1.6; }
    .duty-stats { margin-top: 8px; padding-top: 8px; border-top: 1px dashed #e2e8f0 !important; font-size: 0.85rem; }
    
    .dataframe { font-size: 0.9rem !important; color: #0f172a !important; }
    #MainMenu, footer, header {visibility: hidden;}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

st.markdown("""
<div class="hero-container">
    <span class="hero-tag">AdvisorHub Underwriting Engine</span>
    <h1 class="hero-title">알릴 의무 완벽 매칭 <span style="color: #1e3a8a;">스마트 고지 스캐너</span></h1>
    <p class="hero-subtitle">흩어진 진료기록의 '누적 투약일수'와 '통원일수'를 AI가 자동 합산하여<br>청약서 고지 의무 질문(1번~5번)에 정확히 매칭해 드립니다.</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. 사이드바 설정 (상품 유형 선택 및 룰 안내)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#1e3a8a; font-weight:900;'>⚖️ 심사 유형 및 룰 설정</h2>", unsafe_allow_html=True)
    st.caption("고객에게 제안할 상품군을 선택하면, 해당 상품의 고지 의무 기준에 맞춰 엔진이 자동으로 필터링을 변경합니다.")
    
    st.divider()
    st.markdown("#### 🎯 상품 유형 선택")
    product_type = st.radio("알릴 의무 기준", ["건강체/표준체 (일반심사)", "간편심사 (유병자 3-5-5 기준)"])
    
    st.divider()
    st.markdown("#### 📅 심사 기준일 (청약예정일)")
    reference_date = st.date_input("기준일 설정", datetime.today())
    st.caption("날짜를 미래로 변경하여 '고지의무 소멸 시점'을 미리 시뮬레이션 할 수 있습니다.")
    
    st.divider()
    if product_type == "건강체/표준체 (일반심사)":
        st.markdown("""
        **[표준체 고지 기준]**
        1. **3개월:** 진찰,검사,치료,입원,수술,투약
        2. **1년:** 추가검사 (재검사)
        3. **5년:** 입원, 수술, 7일 이상 치료, 30일 이상 투약
        4. **5년 (12대 질병):** 암, 백혈병, 고혈압, 협심증, 심근경색, 심장판막증, 간경화, 뇌출혈, 뇌경색, 당뇨, 에이즈, 직장/항문 질환
        """)
    else:
        st.markdown("""
        **[3-5-5 간편심사 고지 기준]**
        1. **3개월:** 입원, 수술, 추가/재검사 소견 <br>
        <span style='color:#be123c; font-size:0.85rem; line-height:1.4; display:block; margin-top:4px;'>
        <b>[🔥실무 심사 룰 완벽 적용]</b><br>
        - 3개월 내 <b>최초 진단</b>: 치료 중(투약 포함) 거절, <b>완치 다음날부터 승인</b><br>
        - 3개월 이전 <b>만성 질환</b>: 동일 약(정기검사) 통과, <b>약 변경/추가 시 거절</b></span>
        2. **5년:** 입원, 수술 <br><span style='color:#be123c; font-size:0.8rem;'>(※7일 통원/30일 투약 면제)</span>
        3. **5년 (6대 질병):** 암, 뇌출혈, 뇌경색, 심근경색, 협심증, 심장판막증, 간경화 등
        """, unsafe_allow_html=True)
    
# 엔진에서 사용할 고정 변수 세팅
    search_years = 5
    # 1. 영문/숫자 질병코드 (ICD-10)
    disease_12_list = ["C", "D0", "I10", "I11", "I12", "I13", "I14", "I15", "I20", "I21", "I22", "I05", "I06", "I07", "I08", "I09", "I34", "I35", "I36", "I37", "I38", "K703", "K74", "I60", "I61", "I62", "I63", "I64", "E10", "E11", "E12", "E13", "E14", "B20", "B21", "B22", "B23", "B24", "K60", "K61", "K62", "K64"]
    disease_6_list = ["C", "D0", "I60", "I61", "I62", "I63", "I20", "I21", "I22", "I05", "I06", "I07", "I08", "I09", "I34", "I35", "I36", "I37", "I38", "K703", "K74"]
    
    # 2. 한글 병명 키워드 (코드가 누락되고 $표시만 있을 때를 대비한 이중 필터망)
    disease_12_names = ["암", "악성", "백혈병", "고혈압", "협심증", "심근경색", "심장판막", "간경화", "간경변", "뇌출혈", "뇌경색", "당뇨", "에이즈", "HIV", "치핵", "치루", "치열", "항문", "직장"]
    disease_6_names = ["암", "악성", "백혈병", "뇌출혈", "뇌경색", "심근경색", "협심증", "심장판막", "간경화", "간경변"]
    
    surg_keywords = ["수술", "절제", "시술", "천자", "주입", "절개", "적출", "봉합", "결찰", "종양", "폴립", "결절"]
    test_keywords = ["검사", "초음파", "내시경", "촬영", "MRI", "CT", "조직", "생검", "판독", "X-RAY", "X-ray"]

# ==========================================
# 3. 데이터 분석 및 추출 코어
# ==========================================
st.markdown("### 📑 심평원 진료자료 업로드 (여러 파일 업로드 가능)")
uploaded_files = st.file_uploader("기본진료, 세부진료, 처방조제 등 PDF 파일을 올려주세요.", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner('다중 문서 구조 분석 및 누적 일수 연산 중...'):
        try:
            unified_records = []
            file_dataframes = {} # 개별 파일별 데이터프레임 저장용
            
            # 여러 개의 PDF 파일에서 데이터 긁어오기
            for uploaded_file in uploaded_files:
                file_records = [] # 현재 파일 전용 레코드
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        tables = page.extract_tables()
                        for table in tables:
                            if not table or len(table) < 2: continue
                            # 헤더 추출 및 공백 제거
                            headers = [str(h).replace('\n', '').replace(' ', '') if h else f"col_{i}" for i, h in enumerate(table[0])]
                            
                            for row in table[1:]:
                                if not any(row): continue
                                if "순번" in str(row[0]): continue # 중간에 낀 헤더 무시
                                
                                record = {h: str(v).replace('\n', ' ').strip() if v else "" for h, v in zip(headers, row)}
                                unified_records.append(record)
                                file_records.append(record)
                                
                # 각 파일별로 깨끗한 독립 표(DataFrame) 생성
                if file_records:
                    file_df = pd.DataFrame(file_records).fillna("")
                    file_dataframes[uploaded_file.name] = file_df
            
            if unified_records:
                df = pd.DataFrame(unified_records)
                
                # 핵심 데이터 파싱 함수
                def get_val(row, possible_keys):
                    for k in row.keys():
                        if any(pk in k for pk in possible_keys): 
                            val = row[k]
                            # 빈 값(NaN 등 float 형태)을 에러 없는 문자열로 안전하게 변환
                            return str(val).strip() if pd.notna(val) else ""
                    return ""
                
                def extract_number(text):
                    nums = re.findall(r'\d+', str(text))
                    return int(nums[0]) if nums else 0

                # ---------------------------------------------------------
                # 1차 분석: 정밀 데이터 추출 (최초진단, 입원일수, 수술명 추적)
                # ---------------------------------------------------------
                from datetime import timedelta
                
                # AI 엔진의 기준 시간을 '사용자가 달력에서 선택한 날짜'로 강제 조작
                today = datetime(reference_date.year, reference_date.month, reference_date.day)
                
                disease_stats = defaultdict(lambda: {
                    'visit_dates': set(),
                    'med_dates': {},
                    'tests_found': set(),
                    'inpatient_days': 0, # [추가] 총 입원 일수 합산
                    'surgeries': set(),  # [추가] 수술/시술명 상세 수집
                    'first_date': '2099-12-31', # [추가] 최초 진단일
                    'latest_date': '2000-01-01',
                    'name': '',
                    'med_names_before_90': set(),
                    'med_names_in_90': set()
                })
                
                for idx, row in df.iterrows():
                    # 🚨 [절대 방어 필터] PDF 표의 칸이 밀리더라도, 행(Row) 전체의 글자를 뭉쳐서 '$'나 '해당없음'이 있으면 즉시 버림!
                    row_full_text = "".join(str(v) for v in row.values).replace(" ", "")
                    if "$" in row_full_text or "해당없음" in row_full_text:
                        continue
                    date_str = get_val(row, ['진료시작일'])
                    raw_code = get_val(row, ['코드']).upper()
                    
                    # 🚨 [핵심 업데이트] 심평원 양방(A) / 한방(B) 접두사 완벽 제거
                    code_str = raw_code
                    if len(code_str) >= 2 and code_str[0] in ['A', 'B']:
                        code_str = code_str[1:] # 맨 앞의 A나 B를 잘라내어 진짜 질병코드만 남김
                        
                    # 🚨 [스캔 오류 보정] 알파벳 'I(아이)'가 숫자 '1(일)'로 인식되는 치명적 현상 방어
                    if code_str.startswith('1'):
                        code_str = 'I' + code_str[1:]
                        
                    name_str = get_val(row, ['상병명', '약품명', '진료내역'])
                    in_out = get_val(row, ['입원', '외래'])
                    
                    # 🚨 [초강력 필터] 약국 조제용 더미 코드($) 및 '해당없음'은 AI 분석 엔진에서 원천 차단
                    if "$" in code_str or "해당없음" in name_str.replace(" ", ""):
                        continue
                    
                    v_days_raw = get_val(row, ['내원일수', '진료일수'])
                    m_days_raw = get_val(row, ['투약일수'])
                    v_days = int(re.findall(r'\d+', v_days_raw)[0]) if re.findall(r'\d+', v_days_raw) else 0
                    m_days = int(re.findall(r'\d+', m_days_raw)[0]) if re.findall(r'\d+', m_days_raw) else 0
                    
                    group_key = code_str if code_str and "$" not in code_str else name_str[:15]
                    if not group_key: continue
                    
                    stats = disease_stats[group_key]
                    
                    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str) or re.search(r'(\d{8})', date_str)
                    clean_date = ""
                    if date_match:
                        clean_date = date_match.group()
                        if len(clean_date) == 8 and "-" not in clean_date:
                            clean_date = f"{clean_date[:4]}-{clean_date[4:6]}-{clean_date[6:]}"
                    
                    if clean_date:
                        clean_date_dt = datetime.strptime(clean_date, "%Y-%m-%d")
                        days_from_today = (today - clean_date_dt).days
                        
                        # [핵심] 입원일수와 통원일수를 분리하여 정확히 합산
                        if '입원' in in_out or '입원' in name_str:
                            stats['inpatient_days'] += v_days if v_days > 0 else 1
                        else:
                            stats['visit_dates'].add(clean_date)
                        
                        if clean_date not in stats['med_dates'] or m_days > stats['med_dates'][clean_date]:
                            stats['med_dates'][clean_date] = m_days
                            
                        if clean_date > stats['latest_date']: stats['latest_date'] = clean_date
                        if clean_date < stats['first_date']: stats['first_date'] = clean_date
                        
                        if name_str:
                            if days_from_today <= 90:
                                stats['med_names_in_90'].add(name_str)
                            else:
                                stats['med_names_before_90'].add(name_str)

                    # 수술/시술 키워드 검출 및 상세명 저장
                    for kw in surg_keywords:
                        if kw in name_str:
                            stats['surgeries'].add(name_str)
                            break
                    
                    for kw in test_keywords:
                        if kw in name_str:
                            stats['tests_found'].add(name_str)
                            break
                            
                    if name_str and not stats['name']: stats['name'] = name_str

          # ---------------------------------------------------------
                # 2차 분석: 30일 투약, 총 입원일수 등을 적용한 룰 매칭
                # ---------------------------------------------------------
                summary_reports = defaultdict(list)
                flagged_codes = set()
                
                for key, stats in disease_stats.items():
                    if stats['latest_date'] == '2000-01-01': continue
                    
                    # 통원일수(중복제거) + 입원일수 총합
                    total_visit_days = len(stats['visit_dates']) + stats['inpatient_days']
                    total_med_days = sum(stats['med_dates'].values())
                    
                    latest_d = datetime.strptime(stats['latest_date'], "%Y-%m-%d")
                    latest_med_days = stats['med_dates'].get(stats['latest_date'], 0)
                    treatment_end_d = latest_d + timedelta(days=latest_med_days)
                    
                    first_d = datetime.strptime(stats['first_date'], "%Y-%m-%d")
                    
                    days_passed_from_end = (today - treatment_end_d).days
                    days_passed_from_start = (today - latest_d).days
                    days_passed_from_first = (today - first_d).days
                    
                    reasons = []
                    
                    if product_type == "건강체/표준체 (일반심사)":
                        if days_passed_from_end <= 90:
                            reasons.append(("[1번 질문] 3개월 이내 의료행위 (투약 포함)", f"치료/투약 완료 후 90일 미경과 (종료추정일: {treatment_end_d.strftime('%Y-%m-%d')})"))
                        
                        if 90 < days_passed_from_start <= 365:
                            if stats['tests_found']:
                                tests_str = ", ".join(list(stats['tests_found'])[:2])
                                reasons.append(("[2번 질문] 1년 이내 추가검사(재검사) 의심", f"세부내역 내 검사기록 발견 ({tests_str} 등)"))
                                
                        if days_passed_from_end <= 1825:
                            if stats['inpatient_days'] > 0: 
                                reasons.append(("[3번 질문] 5년 이내 입원", f"입원 총 {stats['inpatient_days']}일 이력 확인"))
                            if stats['surgeries']: 
                                surg_str = ", ".join(list(stats['surgeries'])[:2])
                                reasons.append(("[3번 질문] 5년 이내 수술", f"수술/시술 이력 확인 ({surg_str})"))
                            if total_visit_days >= 7: 
                                reasons.append(("[3번 질문] 5년 이내 계속하여 7일 이상 치료", f"동일 원인 누적 진료일수 {total_visit_days}일"))
                            if total_med_days >= 30: 
                                reasons.append(("[3번 질문] 5년 이내 계속하여 30일 이상 투약", f"동일 원인 누적 투약 {total_med_days}일"))
                            
                            # [핵심 수정] 12대 질병: 영문 코드 및 한글 병명 이중 체크 적용
                            is_12_disease = any(key.startswith(c) for c in disease_12_list) or any(n in stats['name'] for n in disease_12_names)
                            if is_12_disease and key != "":
                                reasons.append(("[4번/5번 질문] 5년 이내 12대 중증/항문 질환", f"12대 질환(항문 질환 포함) 매칭 ({key} / {stats['name'][:10]})"))
                                
                    else:
                        # --- [간편심사 (3-5-5 기준) 룰] ---
                        if days_passed_from_start <= 90:
                            if stats['inpatient_days'] > 0 or stats['surgeries'] or stats['tests_found']:
                                reasons.append(("[간편 1번] 3개월 이내 입원/수술/검사 소견", "3개월 내 입원, 수술 또는 검사 이력 발견"))
                        
                        if days_passed_from_end <= 90 or days_passed_from_start <= 90:
                            if days_passed_from_first <= 90:
                                if days_passed_from_end <= 0: 
                                    reasons.append(("[실무 룰] 3개월 이내 신규 진단 & 치료중", f"최초 진단일({stats['first_date']})이 3개월 이내이며 현재 치료/투약 중 (완치 전 가입 불가, {treatment_end_d.strftime('%Y-%m-%d')} 다음날부터 가능)"))
                            else:
                                new_drugs = stats['med_names_in_90'] - stats['med_names_before_90']
                                if new_drugs:
                                    diff_str = ", ".join(list(new_drugs)[:2])
                                    reasons.append(("[실무 룰] 3개월 이내 약 변경/추가 의심", f"기존과 다른 약/진료내역 발견 ({diff_str}). 동일 약 처방(정기검사)이 아닐 경우 가입 불가"))
                        
                        if days_passed_from_end <= 1825:
                            if stats['inpatient_days'] > 0: 
                                reasons.append(("[간편 2번] 5년 이내 입원", f"입원 총 {stats['inpatient_days']}일 이력 확인"))
                            if stats['surgeries']: 
                                surg_str = ", ".join(list(stats['surgeries'])[:2])
                                reasons.append(("[간편 2번] 5년 이내 수술", f"수술/시술 이력 확인 ({surg_str})"))
                            
                            # [핵심 수정] 6대 질병: 영문 코드 및 한글 병명 이중 체크 적용
                            is_6_disease = any(key.startswith(c) for c in disease_6_list) or any(n in stats['name'] for n in disease_6_names)
                            if is_6_disease and key != "":
                                reasons.append(("[간편 3번] 5년 이내 6대 중증 질환", f"6대 중증 질환 매칭 ({key} / {stats['name'][:10]})"))


                # ---------------------------------------------------------
                # 1차 분석: 정밀 데이터 추출 (입원/수술 기간, 병원명 완벽 추적)
                # ---------------------------------------------------------
                from datetime import timedelta
                today = datetime(reference_date.year, reference_date.month, reference_date.day)
                
                disease_stats = defaultdict(lambda: {
                    'visit_dates': set(),
                    'med_dates': {},
                    'tests_found': set(),
                    'inpatient_days': 0,
                    'inpatient_dates': set(), # 입원 일자 상세
                    'surgeries': set(),
                    'surgery_dates': set(),   # 수술 일자 상세
                    'hospitals': set(),       # 병원명 상세
                    'first_date': '2099-12-31',
                    'latest_date': '2000-01-01',
                    'name': '',
                    'med_names_before_90': set(),
                    'med_names_in_90': set()
                })
                
                for idx, row in df.iterrows():
                    # 🚨 [절대 방어 필터] PDF 표의 칸이 밀리더라도, 행(Row) 전체의 글자를 뭉쳐서 '$'나 '해당없음'이 있으면 즉시 버림!
                    row_full_text = "".join(str(v) for v in row.values).replace(" ", "")
                    if "$" in row_full_text or "해당없음" in row_full_text:
                        continue
                    date_str = get_val(row, ['진료시작일'])
                    raw_code = get_val(row, ['코드']).upper()
                    
                    code_str = raw_code
                    if len(code_str) >= 2 and code_str[0] in ['A', 'B']:
                        code_str = code_str[1:]
                    if code_str.startswith('1'):
                        code_str = 'I' + code_str[1:]
                        
                    name_str = get_val(row, ['상병명', '약품명', '진료내역'])
                    in_out = get_val(row, ['입원', '외래'])
                    hospital_str = get_val(row, ['병·의원', '약국', '기관명'])
                    
                    v_days_raw = get_val(row, ['내원일수', '진료일수'])
                    m_days_raw = get_val(row, ['투약일수'])
                    v_days = int(re.findall(r'\d+', v_days_raw)[0]) if re.findall(r'\d+', v_days_raw) else 0
                    m_days = int(re.findall(r'\d+', m_days_raw)[0]) if re.findall(r'\d+', m_days_raw) else 0
                    
                    group_key = code_str if code_str and code_str != "$" else name_str[:15]
                    if not group_key: continue
                    
                    stats = disease_stats[group_key]
                    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str) or re.search(r'(\d{8})', date_str)
                    clean_date = ""
                    if date_match:
                        clean_date = date_match.group()
                        if len(clean_date) == 8 and "-" not in clean_date:
                            clean_date = f"{clean_date[:4]}-{clean_date[4:6]}-{clean_date[6:]}"
                    
                    if clean_date:
                        clean_date_dt = datetime.strptime(clean_date, "%Y-%m-%d")
                        days_from_today = (today - clean_date_dt).days
                        
                        if '입원' in in_out or '입원' in name_str:
                            stats['inpatient_days'] += v_days if v_days > 0 else 1
                            stats['inpatient_dates'].add(clean_date)
                        else:
                            stats['visit_dates'].add(clean_date)
                        
                        if clean_date not in stats['med_dates'] or m_days > stats['med_dates'][clean_date]:
                            stats['med_dates'][clean_date] = m_days
                            
                        if clean_date > stats['latest_date']: stats['latest_date'] = clean_date
                        if clean_date < stats['first_date']: stats['first_date'] = clean_date
                        
                        if name_str:
                            if days_from_today <= 90:
                                stats['med_names_in_90'].add(name_str)
                            else:
                                stats['med_names_before_90'].add(name_str)

                    if hospital_str and "약국" not in hospital_str:
                        stats['hospitals'].add(hospital_str)

                    for kw in surg_keywords:
                        if kw in name_str:
                            stats['surgeries'].add(name_str)
                            if clean_date: stats['surgery_dates'].add(clean_date)
                            break
                    for kw in test_keywords:
                        if kw in name_str:
                            stats['tests_found'].add(name_str)
                            break
                    if name_str and not stats['name']: stats['name'] = name_str

                # ---------------------------------------------------------
                # 2차 분석: 룰 매칭 및 데이터 구조화
                # ---------------------------------------------------------
                summary_reports = defaultdict(list)
                flagged_codes = set()
                
                for key, stats in disease_stats.items():
                    if stats['latest_date'] == '2000-01-01': continue
                    
                    total_visit_days = len(stats['visit_dates']) + stats['inpatient_days']
                    total_med_days = sum(stats['med_dates'].values())
                    
                    latest_d = datetime.strptime(stats['latest_date'], "%Y-%m-%d")
                    latest_med_days = stats['med_dates'].get(stats['latest_date'], 0)
                    treatment_end_d = latest_d + timedelta(days=latest_med_days)
                    first_d = datetime.strptime(stats['first_date'], "%Y-%m-%d")
                    
                    days_passed_from_end = (today - treatment_end_d).days
                    days_passed_from_start = (today - latest_d).days
                    days_passed_from_first = (today - first_d).days
                    
                    reasons = []
                    
                    if product_type == "건강체/표준체 (일반심사)":
                        if days_passed_from_end <= 90: reasons.append(("[1번 질문] 3개월 이내 의료행위 (투약 포함)", f"치료/투약 완료 후 90일 미경과 (종료추정일: {treatment_end_d.strftime('%Y-%m-%d')})"))
                        if 90 < days_passed_from_start <= 365 and stats['tests_found']: reasons.append(("[2번 질문] 1년 이내 추가검사(재검사)", "세부내역 내 검사기록 발견"))
                        if days_passed_from_end <= 1825:
                            if stats['inpatient_days'] > 0: reasons.append(("[3번 질문] 5년 이내 입원", f"입원 총 {stats['inpatient_days']}일 이력 확인"))
                            if stats['surgeries']: reasons.append(("[3번 질문] 5년 이내 수술", "수술/시술 이력 확인"))
                            if total_visit_days >= 7: reasons.append(("[3번 질문] 5년 이내 계속하여 7일 이상 치료", f"동일 원인 누적 진료일수 {total_visit_days}일"))
                            if total_med_days >= 30: reasons.append(("[3번 질문] 5년 이내 계속하여 30일 이상 투약", f"동일 원인 누적 투약 {total_med_days}일"))
                            is_12_disease = any(key.startswith(c) for c in disease_12_list) or any(n in stats['name'] for n in disease_12_names)
                            if is_12_disease and key != "": reasons.append(("[4번/5번 질문] 5년 이내 12대 중증/항문 질환", f"12대 질환 매칭 ({key})"))
                    else:
                        if days_passed_from_start <= 90 and (stats['inpatient_days'] > 0 or stats['surgeries'] or stats['tests_found']):
                            reasons.append(("[간편 1번] 3개월 이내 입원/수술/검사", "3개월 내 입원, 수술 또는 검사 이력 발견"))
                        if days_passed_from_end <= 90 or days_passed_from_start <= 90:
                            if days_passed_from_first <= 90:
                                if days_passed_from_end <= 0: reasons.append(("[실무 룰] 3개월 이내 신규 진단 & 치료중", f"최초 진단일({stats['first_date']})이 3개월 이내이며 현재 치료 중"))
                            else:
                                if stats['med_names_in_90'] - stats['med_names_before_90']: reasons.append(("[실무 룰] 3개월 이내 약 변경/추가", "기존과 다른 약/진료내역 발견"))
                        if days_passed_from_end <= 1825:
                            if stats['inpatient_days'] > 0: reasons.append(("[간편 2번] 5년 이내 입원", f"입원 총 {stats['inpatient_days']}일 이력 확인"))
                            if stats['surgeries']: reasons.append(("[간편 2번] 5년 이내 수술", "수술/시술 이력 확인"))
                            is_6_disease = any(key.startswith(c) for c in disease_6_list) or any(n in stats['name'] for n in disease_6_names)
                            if is_6_disease and key != "": reasons.append(("[간편 3번] 5년 이내 6대 중증 질환", f"6대 중증 질환 매칭 ({key})"))

                    if reasons:
                        flagged_codes.add(key)
                        
                        # 🚨 [최종 수정] 질병코드 00.00 국제표준 포맷팅 (예: I671 -> I67.1, M5456 -> M54.56) 완벽 적용
                        disp_code = str(key).strip()
                        if len(disp_code) >= 4 and disp_code[0].isalpha() and disp_code[1:3].isdigit() and '.' not in disp_code:
                            disp_code = disp_code[:3] + '.' + disp_code[3:]
                        elif not re.match(r'^[A-Z]', disp_code):
                            disp_code = "-"
                            
                        for q_title, detail in reasons:
                            summary_reports[q_title].append({
                                'first_date': stats['first_date'],
                                'latest_date': stats['latest_date'],
                                'code': disp_code,
                                'name': stats['name'],
                                'visit': total_visit_days,
                                'med': total_med_days,
                                'inpatient': stats['inpatient_days'],
                                'inpatient_dates': sorted(list(stats['inpatient_dates'])),
                                'surgeries': stats['surgeries'],
                                'surgery_dates': sorted(list(stats['surgery_dates'])),
                                'hospitals': list(stats['hospitals']),
                                'detail': detail
                            })
                            
                # ---------------------------------------------------------
                # 카카오톡 메시지 백그라운드 생성 (N번 질문 텍스트 제거)
                # ---------------------------------------------------------
                import re
                import streamlit.components.v1 as components
                
                kakao_msg = f"📋 [ {product_type} 심사 요청 ]\n"
                kakao_msg += f"■ 기준일(청약예정일): {today.strftime('%Y-%m-%d')}\n\n"
                if not summary_reports:
                    kakao_msg += "✅ AI 분석 결과, 고지 대상 질환이 없습니다. (표준체 진행 가능)\n"
                else:
                    for q_title in sorted(summary_reports.keys()):
                        # 🚨 [수정] 정규식을 사용해 '[1번 질문]', '[간편 2번]' 등의 대괄호 텍스트 깔끔하게 삭제
                        clean_title = re.sub(r'^\[.*?\]\s*', '', q_title)
                        kakao_msg += f"▶ {clean_title}\n"
                        
                        for item in summary_reports[q_title]:
                            kakao_msg += f"■ 질병/증상: {item['name']} ({item['code']})\n"
                            hosp_str = ", ".join(item['hospitals']) if item['hospitals'] else "알 수 없음"
                            if product_type == "건강체/표준체 (일반심사)":
                                kakao_msg += f" - 치료기간: {item['first_date']} ~ {item['latest_date']}\n"
                                kakao_msg += f" - 병원명: {hosp_str}\n"
                                kakao_msg += f" - 상세내용: 통원 {item['visit']}일 / 투약 {item['med']}일 (입원 {item['inpatient']}일, 수술 {len(item['surgeries'])}건)\n"
                            else:
                                inpt_str = f"{item['inpatient']}일 (일자: {', '.join(item['inpatient_dates'])})" if item['inpatient'] > 0 else "해당없음"
                                surg_str = f"{len(item['surgeries'])}건 (일자: {', '.join(item['surgery_dates'])})" if item['surgeries'] else "해당없음"
                                kakao_msg += f" - 병원명: {hosp_str}\n"
                                kakao_msg += f" - 입원기간: {inpt_str}\n"
                                kakao_msg += f" - 수술여부: {surg_str}\n"
                            kakao_msg += f" - 매칭사유: {item['detail']}\n\n"

                # ---------------------------------------------------------
                # 화면 출력 0: 텍스트 숨김 처리된 '원클릭 카톡 복사 버튼' (HTML/JS)
                # ---------------------------------------------------------
                safe_kakao_msg = kakao_msg.replace('`', '\\`').replace('\n', '\\n')
                
                copy_btn_html = f"""
                <button id="copy-btn" style="width: 100%; padding: 14px; border: 1px solid #cbd5e1; border-radius: 12px; background-color: #ffffff; color: #1e3a8a; font-weight: 800; font-size: 1.05rem; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.02); transition: all 0.2s ease; margin-bottom: 5px;">
                    💬 설계 매니저님께 카톡 전달하기 (여기를 클릭하여 복사 📋)
                </button>
                <script>
                document.getElementById('copy-btn').addEventListener('click', function() {{
                    const textToCopy = `{safe_kakao_msg}`;
                    const btn = this;
                    
                    // 화면에 보이지 않는 임시 텍스트 박스를 만들어 강제 복사 진행
                    const textArea = document.createElement("textarea");
                    textArea.value = textToCopy;
                    document.body.appendChild(textArea);
                    textArea.select();
                    try {{
                        document.execCommand("copy");
                        // 성공 시 버튼 색상을 초록색으로 변경
                        btn.innerText = '✅ 복사 완료! 카카오톡에 붙여넣기 하세요 (Ctrl+V)';
                        btn.style.backgroundColor = '#dcfce3';
                        btn.style.color = '#166534';
                        btn.style.borderColor = '#bbf7d0';
                    }} catch (err) {{
                        console.error('Fallback: Oops, unable to copy', err);
                    }}
                    document.body.removeChild(textArea);
                    
                    // 2.5초 뒤에 원래 버튼 디자인으로 복구
                    setTimeout(() => {{
                        btn.innerText = '💬 설계 매니저님께 카톡 전달하기 (여기를 클릭하여 복사 📋)';
                        btn.style.backgroundColor = '#ffffff';
                        btn.style.color = '#1e3a8a';
                        btn.style.borderColor = '#cbd5e1';
                    }}, 2500);
                }});
                </script>
                """
                # Streamlit의 components.html을 사용하여 버튼 렌더링
                components.html(copy_btn_html, height=75)

                flagged_count = len(flagged_codes)
                guide_html = "<div class='info-card'><div class='info-card-header'>💡 AdvisorHub 스마트 심사 가이드 (AI 요약)</div><div class='info-grid'>"
                
                if product_type == "건강체/표준체 (일반심사)":
                    guide_html += "<div class='info-col'><div class='info-title'>🛡️ 건강체 (표준체) 심사 가이드</div><ul class='info-list'>"
                    guide_html += f"<li><b>현재 발견된 고지 질환:</b> <span class='badge-blue'>{flagged_count}개</span></li>"
                    if flagged_count >= 5: guide_html += "<li style='margin-top:10px;'><span class='badge-red' style='padding:6px 10px; display:inline-block;'>🚨 고지질환 5개 이상으로 '간편 상품'을 추천드립니다.</span></li>"
                    else: guide_html += "<li style='margin-top:10px;'><span class='badge-blue' style='padding:6px 10px; display:inline-block;'>✅ 고지질환 5개 이하로 '건강체 심사' 진행을 권장합니다.</span></li>"
                    guide_html += "</ul></div>"
                    guide_html += "<div class='info-col'><div class='info-title'>⚡ 참고: 간편심사 (유병자) 전환 시 혜택</div><ul class='info-list'>"
                    guide_html += "<li>자잘한 통원(7일 이상) 및 투약(30일 이상) 이력은 <b>고지 면제</b>됩니다.</li><li>최근 3개월 내 추가검사/입원/수술 소견이 없다면 매우 유리합니다.</li></ul></div>"
                else:
                    guide_html += "<div class='info-col' style='grid-column: span 2;'><div class='info-title'>⚡ 간편심사 (유병자 3-5-5) 해당 이력 한눈에 보기</div><div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px; margin-top:12px;'>"
                    
                    def get_items(q_keywords):
                        items = []
                        for k, v_list in summary_reports.items():
                            if any(kw in k for kw in q_keywords):
                                for v in v_list:
                                    code_disp = v['code'] if v['code'] != "-" else ""
                                    code_html = f"<b style='color:#be123c;'>[{code_disp}]</b> " if code_disp else ""
                                    extra_info = ""
                                    if v['inpatient'] > 0:
                                        inpt_range = f"{v['inpatient_dates'][0]} ~ {v['inpatient_dates'][-1]}" if len(v['inpatient_dates']) > 1 else (v['inpatient_dates'][0] if v['inpatient_dates'] else "")
                                        extra_info += f"<br><span style='color:#1d4ed8;'>🏥 입원: {inpt_range} ({v['inpatient']}일)</span>"
                                    if v['surgeries']:
                                        surg_range = f"{v['surgery_dates'][0]} ~ {v['surgery_dates'][-1]}" if len(v['surgery_dates']) > 1 else (v['surgery_dates'][0] if v['surgery_dates'] else "")
                                        extra_info += f"<br><span style='color:#b91c1c;'>🔪 수술: {surg_range} ({len(v['surgeries'])}건)</span>"
                                    items.append(f"<div style='font-size:0.85rem; color:#334155; margin-bottom:8px; line-height:1.4; padding-left:10px; border-left:3px solid #e2e8f0;'>{code_html}{v['name'][:12]}<span style='color:#64748b; font-size:0.8rem;'> ({v['latest_date']})</span>{extra_info}</div>")
                        return "".join(items) if items else "<div style='font-size:0.85rem; color:#94a3b8; padding:8px 0;'>✅ 해당 없음 (통과)</div>"
                    
                    guide_html += "<div style='background:#ffffff; padding:12px; border-radius:8px; border:1px solid #e2e8f0;'><div style='font-weight:800; color:#1e3a8a; margin-bottom:10px; font-size:0.9rem; border-bottom:1px solid #f1f5f9; padding-bottom:6px;'>⏱️ 최근 3개월 내<br><span style='font-size:0.75rem; color:#64748b; font-weight:500;'>진단/신규투약/추가검사</span></div>" + get_items(["1번", "실무"]) + "</div>"
                    guide_html += "<div style='background:#ffffff; padding:12px; border-radius:8px; border:1px solid #e2e8f0;'><div style='font-weight:800; color:#1e3a8a; margin-bottom:10px; font-size:0.9rem; border-bottom:1px solid #f1f5f9; padding-bottom:6px;'>🏥 최근 5년 내<br><span style='font-size:0.75rem; color:#64748b; font-weight:500;'>입원 및 수술 이력</span></div>" + get_items(["2번"]) + "</div>"
                    guide_html += "<div style='background:#ffffff; padding:12px; border-radius:8px; border:1px solid #e2e8f0;'><div style='font-weight:800; color:#1e3a8a; margin-bottom:10px; font-size:0.9rem; border-bottom:1px solid #f1f5f9; padding-bottom:6px;'>⚠️ 최근 5년 내<br><span style='font-size:0.75rem; color:#64748b; font-weight:500;'>6대 중대질환 이력</span></div>" + get_items(["3번"]) + "</div>"
                    guide_html += "</div></div>"
                
                guide_html += "</div></div>"
                st.markdown(guide_html, unsafe_allow_html=True)

                # ---------------------------------------------------------
                # 화면 출력 1: 종합 알릴 의무 요약 리포트 (청약서용)
                # ---------------------------------------------------------
                report_html = "<div class='glass-card'>\n<div class='report-title'>📝 알릴 의무(고지) 판정 리포트 <span style='font-size:0.9rem; color:#64748b; font-weight:500;'>(청약서 입력용)</span></div>\n"
                if not summary_reports:
                    report_html += "<div style='background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 1rem; border-radius: 8px; color: #166534; font-weight: 600; margin-bottom: 1rem;'>✅ <b>고지 대상 없음:</b> 설정하신 기간 내에 알릴 의무에 해당하는 위험 이력이 발견되지 않았습니다. 표준체로 심사를 진행하십시오.</div>\n"
                else:
                    report_html += "<div style='background-color: #fefce8; border: 1px solid #fef08a; padding: 1rem; border-radius: 8px; color: #854d0e; font-weight: 600; margin-bottom: 1rem;'>⚠️ 아래 항목들은 AI가 분석하여 찾아낸 <b>필수 고지 대상</b>입니다. 청약서 해당 번호에 기재하십시오.</div>\n"
                    for q_title in sorted(summary_reports.keys()):
                        items = summary_reports[q_title]
                        report_html += f"<div class='duty-box'>\n<div class='duty-title'><span class='duty-tag'>해당</span> {q_title}</div>\n"
                        for item in items:
                            report_html += f"<div class='duty-detail'>\n• <b>최초진단: {item['first_date']}</b> ~ <b>최종진료: {item['latest_date']}</b> | {item['name']} ({item['code']}) <br>\n<span style='color:#be123c; font-size:0.85rem; margin-left:12px;'>↳ 매칭사유: {item['detail']}</span>\n</div>\n"
                            surg_text = f" / 수술 <b>{len(item['surgeries'])}건</b>" if item['surgeries'] else ""
                            inpt_text = f" / 입원 <b>{item['inpatient']}일</b>" if item['inpatient'] > 0 else ""
                            report_html += f"<div class='duty-stats' style='margin-left:12px; margin-bottom:10px;'>📊 전체 이력: 누적 진료(입원포함) <b>{item['visit']}일</b> / 누적 투약 <b>{item['med']}일</b>{inpt_text}{surg_text}</div>\n"
                        report_html += "</div>\n"
                report_html += "</div>\n"
                st.markdown(report_html, unsafe_allow_html=True)

                # ---------------------------------------------------------
                # 화면 출력 2: 원본 데이터 ($ 삭제, 고지대상/질병코드별 정렬)
                # ---------------------------------------------------------
                st.markdown("#### 🔍 심평원 추출 원본 데이터 (고지 대상 우선 정렬)")
                
                for file_name, f_df in file_dataframes.items():
                    # 1. 🚨 원본 표에서도 $ 및 '해당없음' 기록 흔적도 없이 완전 삭제
                    filtered_indices = []
                    for idx, row in f_df.iterrows():
                        c_str = get_val(row, ['코드']).upper()
                        n_str = get_val(row, ['상병명', '약품명', '진료내역'])
                        if c_str == "$" or "해당없음" in n_str.replace(" ", ""):
                            continue
                        filtered_indices.append(idx)
                    
                    clean_df = f_df.loc[filtered_indices].copy()
                    if clean_df.empty: continue
                    
                    st.markdown(f"**📄 {file_name}**")
                    
                    is_flagged_list = []
                    code_for_sort = []
                    
                    for _, row in clean_df.iterrows():
                        c_str = get_val(row, ['코드']).upper()
                        if len(c_str) >= 2 and c_str[0] in ['A', 'B']: c_str = c_str[1:]
                        if c_str.startswith('1'): c_str = 'I' + c_str[1:]
                        
                        n_str = get_val(row, ['상병명', '약품명', '진료내역'])
                        row_key = c_str if c_str and c_str != "$" else n_str[:15]
                        
                        is_flagged_list.append(row_key in flagged_codes)
                        code_for_sort.append(c_str) # 질병 코드를 정렬용 변수로 수집
                        
                    clean_df['is_flagged'] = is_flagged_list
                    clean_df['sort_code'] = code_for_sort
                    
                    # 2. 🚨 [개선] 1순위: 고지대상(위로), 2순위: 질병코드 알파벳순(끼리끼리 묶임)
                    sorted_df = clean_df.sort_values(by=['is_flagged', 'sort_code'], ascending=[False, True]).drop(columns=['is_flagged', 'sort_code']).reset_index(drop=True)
                    
                    # 3. 색상 하이라이트 유지
                    def highlight_danger(row):
                        c_str = get_val(row, ['코드']).upper()
                        if len(c_str) >= 2 and c_str[0] in ['A', 'B']: c_str = c_str[1:]
                        if c_str.startswith('1'): c_str = 'I' + c_str[1:]
                        
                        n_str = get_val(row, ['상병명', '약품명', '진료내역'])
                        row_key = c_str if c_str and c_str != "$" else n_str[:15]
                        
                        if row_key in flagged_codes:
                            return ['background-color: #ffe4e6; color: #be123c; font-weight: 800;'] * len(row)
                        return [''] * len(row)

                    styled_f_df = sorted_df.style.apply(highlight_danger, axis=1)
                    st.dataframe(styled_f_df, use_container_width=True)
                
            else:
                st.error("PDF 파일에서 표 데이터를 추출하지 못했습니다. 비밀번호가 걸려있거나, 스캔된 이미지 형태인지 확인해 주세요.")
        except Exception as e:
            st.error(f"시스템 분석 중 오류가 발생했습니다: {e}")