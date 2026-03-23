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
    
    .stApp {
        background-color: #f4f7f9; 
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
        letter-spacing: -0.02em; 
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .hero-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 24px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 5px;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6, #0ea5e9);
    }
    .hero-tag {
        display: inline-block;
        background-color: #eff6ff; color: #2563eb;
        font-size: 0.8rem; font-weight: 800;
        padding: 0.4rem 1.2rem; border-radius: 50px;
        margin-bottom: 1rem;
    }
    .hero-title { color: #0f172a; font-size: 2.4rem; font-weight: 900; line-height: 1.3; margin-bottom: 0.8rem; }
    .hero-subtitle { color: #64748b; font-size: 1.05rem; font-weight: 500; }

    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    
    .glass-card {
        background: white; border-radius: 16px; padding: 2rem;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        margin-bottom: 1.5rem;
    }
    
    .report-title {
        color: #1e3a8a; font-weight: 900; font-size: 1.3rem;
        border-bottom: 2px solid #e2e8f0; padding-bottom: 0.8rem; margin-bottom: 1.2rem;
    }
    
    /* 청약서 고지 의무 매칭 박스 디자인 */
    .duty-box {
        background-color: #ffffff; border-radius: 12px;
        border: 1px solid #e2e8f0; border-left: 6px solid #be123c;
        padding: 1.2rem 1.5rem; margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .duty-title { color: #be123c; font-weight: 900; font-size: 1.1rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 8px;}
    .duty-tag { background: #fee2e2; color: #9f1239; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 800; }
    .duty-detail { color: #334155; font-size: 0.95rem; font-weight: 500; line-height: 1.6; }
    .duty-stats { margin-top: 8px; padding-top: 8px; border-top: 1px dashed #e2e8f0; font-size: 0.85rem; color: #64748b; }
    
    .dataframe { font-size: 0.9rem !important; }
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
        1. **3개월:** 입원, 수술, 추가/재검사 소견 <br><span style='color:#be123c; font-size:0.8rem;'>(※단순 통원/투약은 면제)</span>
        2. **5년:** 입원, 수술 <br><span style='color:#be123c; font-size:0.8rem;'>(※7일 통원/30일 투약 면제)</span>
        3. **5년 (6대 질병):** 암, 뇌졸중, 심근경색, 협심증, 심장판막증, 간경화 등
        """, unsafe_allow_html=True)
    
    # 엔진에서 사용할 고정 변수 세팅
    search_years = 5
    disease_12_list = ["C", "D0", "I10", "I11", "I12", "I13", "I14", "I15", "I20", "I21", "I22", "I05", "I06", "I07", "I08", "I09", "I34", "I35", "I36", "I37", "I38", "K703", "K74", "I60", "I61", "I62", "I63", "I64", "E10", "E11", "E12", "E13", "E14", "B20", "B21", "B22", "B23", "B24", "K60", "K61", "K62", "K64", "K65"]
    disease_6_list = ["C", "D0", "I60", "I61", "I62", "I63", "I64", "I20", "I21", "I22", "I05", "I06", "I07", "I08", "I09", "I34", "I35", "I36", "I37", "I38", "K703", "K74"]
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
                # 1차 분석: 질병별 누적 일수(중복 제거) 및 치료 종료일 정밀 계산
                # ---------------------------------------------------------
                from datetime import timedelta
                
                # dict 형태로 세밀한 데이터 트래킹
                disease_stats = defaultdict(lambda: {
                    'visit_dates': set(),     # 중복 제거된 실제 통원일자
                    'med_dates': {},          # {처방일자: 투약일수(최대값)} -> 중복 처방 합산 방지
                    'tests_found': set(),     # 발견된 검사명 (1년 내 재검사 판별용)
                    'is_inpatient': False,
                    'is_surgery': False,
                    'latest_date': '2000-01-01',
                    'name': ''
                })
                
                for idx, row in df.iterrows():
                    date_str = get_val(row, ['진료시작일'])
                    code_str = get_val(row, ['코드']).upper()
                    name_str = get_val(row, ['상병명', '약품명', '진료내역'])
                    in_out = get_val(row, ['입원', '외래'])
                    
                    # 숫자 파싱 시 에러 방지
                    v_days_raw = get_val(row, ['내원일수', '진료일수'])
                    m_days_raw = get_val(row, ['투약일수'])
                    v_days = int(re.findall(r'\d+', v_days_raw)[0]) if re.findall(r'\d+', v_days_raw) else 0
                    m_days = int(re.findall(r'\d+', m_days_raw)[0]) if re.findall(r'\d+', m_days_raw) else 0
                    
                    group_key = code_str if code_str and code_str != "$" else name_str[:15]
                    if not group_key: continue
                    
                    stats = disease_stats[group_key]
                    
                    # 날짜 형식 표준화
                    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str) or re.search(r'(\d{8})', date_str)
                    clean_date = ""
                    if date_match:
                        clean_date = date_match.group()
                        if len(clean_date) == 8 and "-" not in clean_date:
                            clean_date = f"{clean_date[:4]}-{clean_date[4:6]}-{clean_date[6:]}"
                    
                    if clean_date:
                        # 통원일 누적 (Set으로 중복 날짜 자동 제거)
                        stats['visit_dates'].add(clean_date)
                        
                        # 투약일 누적 (같은 날짜면 가장 긴 처방일수 1개만 적용하여 중복 뻥튀기 방지)
                        if clean_date not in stats['med_dates'] or m_days > stats['med_dates'][clean_date]:
                            stats['med_dates'][clean_date] = m_days
                            
                        if clean_date > stats['latest_date']:
                            stats['latest_date'] = clean_date

                    if '입원' in in_out or '입원' in name_str: stats['is_inpatient'] = True
                    if any(kw in name_str for kw in surg_keywords if kw): stats['is_surgery'] = True
                    
                    # 1년 이내 추가검사 판별을 위한 검사 키워드 수집
                    for kw in test_keywords:
                        if kw in name_str:
                            stats['tests_found'].add(name_str)
                            break
                            
                    if name_str and not stats['name']: stats['name'] = name_str

                # ---------------------------------------------------------
                # 2차 분석: "정확도 중심"의 고지 의무 룰 매칭 (상품 유형별 분기)
                # ---------------------------------------------------------
                today = datetime.now()
                summary_reports = defaultdict(list)
                flagged_codes = set()
                
                for key, stats in disease_stats.items():
                    if stats['latest_date'] == '2000-01-01': continue
                    
                    total_visit_days = len(stats['visit_dates'])
                    total_med_days = sum(stats['med_dates'].values())
                    
                    latest_d = datetime.strptime(stats['latest_date'], "%Y-%m-%d")
                    latest_med_days = stats['med_dates'].get(stats['latest_date'], 0)
                    treatment_end_d = latest_d + timedelta(days=latest_med_days)
                    
                    days_passed_from_end = (today - treatment_end_d).days
                    days_passed_from_start = (today - latest_d).days
                    
                    reasons = []
                    
                    if product_type == "건강체/표준체 (일반심사)":
                        # --- [표준체 일반심사 룰] ---
                        # [1번 질문] 최근 3개월 이내 (투약은 처방 종료일 기준)
                        if days_passed_from_end <= 90:
                            reasons.append(("[1번 질문] 3개월 이내 의료행위 (투약 포함)", f"치료/투약 완료 후 90일 미경과 (종료추정일: {treatment_end_d.strftime('%Y-%m-%d')})"))
                        
                        # [2번 질문] 최근 1년 이내 추가검사/재검사 의심
                        if 90 < days_passed_from_start <= 365:
                            if stats['tests_found']:
                                tests_str = ", ".join(list(stats['tests_found'])[:2])
                                reasons.append(("[2번 질문] 1년 이내 추가검사(재검사) 의심", f"세부내역 내 검사기록 발견 ({tests_str} 등)"))
                                
                        # [3번 질문] 최근 5년 이내 7일/30일/입원/수술
                        if days_passed_from_end <= 1825:
                            if stats['is_inpatient']: reasons.append(("[3번 질문] 5년 이내 입원", "입원 이력 확인"))
                            if stats['is_surgery']: reasons.append(("[3번 질문] 5년 이내 수술", "수술/시술 관련 키워드 확인"))
                            if total_visit_days >= 7: reasons.append(("[3번 질문] 5년 이내 계속하여 7일 이상 치료", f"동일 원인 누적 통원 {total_visit_days}일"))
                            if total_med_days >= 30: reasons.append(("[3번 질문] 5년 이내 계속하여 30일 이상 투약", f"동일 원인 누적 투약 {total_med_days}일"))
                        
                        # [4번 질문] 최근 5년 이내 12대 중증 질환 (직장/항문 포함)
                        if days_passed_from_start <= 1825 and key != "":
                            if any(key.startswith(c) for c in disease_12_list):
                                reasons.append(("[4번 질문] 5년 이내 12대 중증/항문 질환", f"12대 질환(직장/항문 포함) 코드 매칭 ({key})"))
                                
                    else:
                        # --- [간편심사 (3-5-5 기준) 룰] ---
                        # [1번 질문] 3개월 이내 입원/수술/추가검사소견 (단순 통원/투약 면제)
                        if days_passed_from_start <= 90:
                            if stats['is_inpatient'] or stats['is_surgery'] or stats['tests_found']:
                                reasons.append(("[간편 1번] 3개월 이내 입원/수술/검사 소견", "3개월 내 입원/수술 또는 검사 이력 발견 (단순 통원/투약 아님)"))
                        
                        # [2번 질문] 5년 이내 입원/수술 (7일 통원, 30일 투약 면제)
                        if days_passed_from_end <= 1825:
                            if stats['is_inpatient']: reasons.append(("[간편 2번] 5년 이내 입원", "입원 이력 확인"))
                            if stats['is_surgery']: reasons.append(("[간편 2번] 5년 이내 수술", "수술/시술 관련 키워드 확인"))
                        
                        # [3번 질문] 5년 이내 6대 중증질환 (암, 뇌졸중, 심근경색, 협심증, 심장판막, 간경화)
                        if days_passed_from_start <= 1825 and key != "":
                            if any(key.startswith(c) for c in disease_6_list):
                                reasons.append(("[간편 3번] 5년 이내 6대 중증 질환", f"6대 중증 질환 코드 매칭 ({key})"))

                    # 리포트 생성
                    if reasons:
                        flagged_codes.add(key)
                        for q_title, detail in reasons:
                            summary_reports[q_title].append({
                                'date': stats['latest_date'],
                                'code': key if re.match(r'^[A-Z]', key) else "-",
                                'name': stats['name'],
                                'visit': total_visit_days,
                                'med': total_med_days,
                                'detail': detail
                            })
                            
                # ---------------------------------------------------------
                # 화면 출력 1: 알릴 의무 요약 리포트 (청약서용)
                # ---------------------------------------------------------
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<div class='report-title'>📝 알릴 의무(고지) 판정 리포트 <span style='font-size:0.9rem; color:#64748b; font-weight:500;'>(청약서 입력용)</span></div>", unsafe_allow_html=True)
                
                if not summary_reports:
                    st.success("✅ **고지 대상 없음:** 설정하신 기간 내에 알릴 의무에 해당하는 위험 이력이 발견되지 않았습니다. 표준체로 심사를 진행하십시오.")
                else:
                    st.warning("⚠️ 아래 항목들은 AI가 누적 일수를 계산하여 찾아낸 **필수 고지 대상**입니다. 청약서 해당 번호에 정확히 기재하십시오.")
                    
                   # 1번부터 5번 질문 순서대로 정렬하여 출력
                    for q_title in sorted(summary_reports.keys()):
                        items = summary_reports[q_title]
                        box_html = f"<div class='duty-box'>\n<div class='duty-title'><span class='duty-tag'>해당</span> {q_title}</div>\n"
                        for item in items:
                            box_html += f"<div class='duty-detail'>\n• <b>최종진료: {item['date']}</b> | {item['name']} ({item['code']}) <br>\n<span style='color:#be123c; font-size:0.85rem; margin-left:12px;'>↳ 매칭사유: {item['detail']}</span>\n</div>\n"
                            box_html += f"<div class='duty-stats' style='margin-left:12px; margin-bottom:10px;'>📊 이 질환의 전체 이력: 누적 통원 <b>{item['visit']}일</b> / 누적 투약 <b>{item['med']}일</b></div>\n"
                        box_html += "</div>"
                        st.markdown(box_html, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

                # ---------------------------------------------------------
                # 화면 출력 2: 원본 데이터 (개별 파일별 분리 출력 및 하이라이트)
                # ---------------------------------------------------------
                st.markdown("#### 🔍 심평원 추출 원본 데이터 (파일별 분리)")
                
                def highlight_danger(row):
                    # 개별 표에서도 위험 코드가 있는지 확인하여 빨간색 칠하기
                    c_str = get_val(row, ['코드']).upper()
                    n_str = get_val(row, ['상병명', '약품명', '진료내역'])
                    row_key = c_str if c_str and c_str != "$" else n_str[:15]
                    
                    if row_key in flagged_codes:
                        return ['background-color: #fff1f2; color: #be123c; font-weight: 500;'] * len(row)
                    return [''] * len(row)

                # 파일 이름별로 깔끔하게 나누어서 표를 그려줍니다.
                for file_name, f_df in file_dataframes.items():
                    st.markdown(f"**📄 {file_name}**")
                    styled_f_df = f_df.style.apply(highlight_danger, axis=1)
                    st.dataframe(styled_f_df, use_container_width=True)
                
            else:
                st.error("PDF 파일에서 표 데이터를 추출하지 못했습니다. 비밀번호가 걸려있거나, 스캔된 이미지 형태인지 확인해 주세요.")
        except Exception as e:
            st.error(f"시스템 분석 중 오류가 발생했습니다: {e}")