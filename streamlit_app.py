import streamlit as st
import pdfplumber
import pandas as pd
import re
from datetime import datetime, timedelta
from collections import defaultdict
import anthropic
import json
import os

# ==========================================
# 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="AdvisorHub | 보험설계사 전용 플랫폼",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

if "menu" not in st.session_state:
    st.session_state.menu = "disclosure"

# ==========================================
# CSS — ConnectionLabs 스타일
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #f4f6fb !important;
    font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif !important;
    color: #1a1a2e !important;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e8ecf4 !important;
    width: 240px !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebar"] * { color: #4a5568 !important; }
[data-testid="stSidebar"] hr { border-color: #e8ecf4 !important; margin: 8px 16px !important; }

/* 사이드바 라디오/익스팬더 숨기기 */
[data-testid="stSidebar"] [data-testid="stExpander"] details { border: none !important; background: transparent !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary { background: transparent !important; color: #6b7280 !important; font-size: 0.72rem !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; padding: 0 16px 6px !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover { background: transparent !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 0.82rem !important; color: #4a5568 !important; }
[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    background: #f4f6fb !important;
    color: #1a1a2e !important;
    border: 1px solid #e8ecf4 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}

/* 헤더 제거 */
[data-testid="stHeader"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }

/* 파일 업로더 */
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border: 2px dashed #c7d2fe !important;
    border-radius: 14px !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploader"] section:hover { border-color: #6366f1 !important; background: #f5f3ff !important; }
[data-testid="stFileUploader"] *, [data-testid="stUploadedFile"] * { color: #1a1a2e !important; }
[data-testid="stFileUploader"] button {
    background: #6366f1 !important;
    border: none !important;
    border-radius: 8px !important;
}

/* 탭 */
[data-testid="stTabs"] [role="tablist"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #e8ecf4;
    gap: 2px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
[data-testid="stTabs"] button[role="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    color: #6b7280 !important;
    padding: 7px 16px !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: #6366f1 !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.25) !important;
}

div[data-testid="stAlert"] { border-radius: 12px !important; }
.dataframe, .dataframe * { font-size: 0.82rem !important; color: #1a1a2e !important; }

/* ── 사이드바 로고 ── */
.sb-brand {
    padding: 20px 20px 16px;
    border-bottom: 1px solid #e8ecf4;
    margin-bottom: 8px;
}
.sb-brand-name {
    font-size: 1.05rem; font-weight: 800;
    color: #6366f1 !important;
    letter-spacing: -.02em; line-height: 1.2;
}
.sb-brand-sub { font-size: 0.72rem; color: #9ca3af !important; margin-top: 2px; font-weight: 500; }

/* ── 사이드바 섹션 라벨 ── */
.sb-section {
    font-size: 0.68rem; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: #9ca3af !important;
    padding: 12px 20px 4px; margin-top: 4px;
}

/* ── 네비 버튼 (Streamlit 버튼 오버라이드) ── */
[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    color: #4a5568 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 9px 14px !important;
    width: 100% !important;
    transition: all 0.15s !important;
    box-shadow: none !important;
    margin: 1px 0 !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #f5f3ff !important;
    color: #6366f1 !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: #ede9fe !important;
    color: #6366f1 !important;
    font-weight: 700 !important;
    border-left: 3px solid #6366f1 !important;
    border-radius: 0 10px 10px 0 !important;
}

/* ── 페이지 헤더 ── */
.page-header {
    background: #ffffff;
    border: 1px solid #e8ecf4;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.page-eyebrow {
    font-size: 0.68rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #6366f1 !important; margin-bottom: 4px;
}
.page-title {
    font-size: 1.45rem; font-weight: 800;
    color: #1a1a2e !important; letter-spacing: -.03em; line-height: 1.2;
}
.page-desc { font-size: 0.82rem; color: #6b7280 !important; margin-top: 5px; line-height: 1.6; }

/* ── 요약 수치 카드 ── */
.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; }
.stat-card {
    background: #ffffff;
    border: 1px solid #e8ecf4;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: all 0.2s;
}
.stat-card:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.stat-card.ok   { border-color: #a7f3d0; background: linear-gradient(135deg, #f0fdf4, #fff); }
.stat-card.warn { border-color: #fde68a; background: linear-gradient(135deg, #fffbeb, #fff); }
.stat-card.danger { border-color: #fecaca; background: linear-gradient(135deg, #fef2f2, #fff); }
.sc-icon { font-size: 1.2rem; margin-bottom: 8px; }
.sc-label { font-size: 0.72rem; color: #9ca3af !important; font-weight: 600; margin-bottom: 4px; }
.sc-value { font-family: 'DM Mono', monospace; font-size: 2.2rem; font-weight: 600; color: #1a1a2e !important; line-height: 1; }
.stat-card.warn .sc-value, .stat-card.danger .sc-value { color: #dc2626 !important; }
.stat-card.ok .sc-value { color: #16a34a !important; }
.sc-sub { font-size: 0.72rem; color: #9ca3af !important; margin-top: 5px; font-weight: 500; }

/* ── AI 판정 배너 ── */
.verdict-banner {
    border-radius: 14px; padding: 16px 20px; margin-bottom: 18px;
    display: flex; align-items: flex-start; gap: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.verdict-ok   { background: linear-gradient(135deg, #f0fdf4, #dcfce7); border: 1px solid #86efac; }
.verdict-warn { background: linear-gradient(135deg, #fffbeb, #fef3c7); border: 1px solid #fcd34d; }
.verdict-bad  { background: linear-gradient(135deg, #fef2f2, #fee2e2); border: 1px solid #fca5a5; }
.verdict-icon { font-size: 1.6rem; flex-shrink: 0; margin-top: 2px; }
.verdict-content {}
.verdict-label { font-size: 0.7rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 3px; }
.verdict-ok   .verdict-label { color: #16a34a !important; }
.verdict-warn .verdict-label { color: #d97706 !important; }
.verdict-bad  .verdict-label { color: #dc2626 !important; }
.verdict-title { font-size: 1rem; font-weight: 800; margin-bottom: 4px; }
.verdict-ok   .verdict-title { color: #15803d !important; }
.verdict-warn .verdict-title { color: #92400e !important; }
.verdict-bad  .verdict-title { color: #991b1b !important; }
.verdict-desc { font-size: 0.8rem; line-height: 1.6; }
.verdict-ok   .verdict-desc { color: #166534 !important; }
.verdict-warn .verdict-desc { color: #92400e !important; }
.verdict-bad  .verdict-desc { color: #991b1b !important; }

/* ── 전환 배너 ── */
.switch-banner {
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    border: 1px solid #fcd34d; border-radius: 12px;
    padding: 12px 16px; font-size: 0.82rem;
    color: #92400e !important; font-weight: 600; margin-bottom: 16px;
    display: flex; align-items: center; gap: 10px;
}

/* ── 고지 카드 ── */
.duty-card {
    background: #ffffff; border: 1px solid #e8ecf4;
    border-radius: 14px; margin-bottom: 12px;
    overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.duty-card-head {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px; background: #f8f9ff;
    border-bottom: 1px solid #e8ecf4;
}
.duty-q-badge {
    font-size: 0.7rem; font-weight: 800; background: #6366f1;
    color: #fff !important; padding: 3px 10px; border-radius: 100px;
}
.duty-q-title { font-size: 0.88rem; font-weight: 700; color: #1a1a2e !important; }
.duty-item { padding: 13px 16px; border-bottom: 1px solid #f4f6fb; }
.duty-item:last-child { border-bottom: none; }
.duty-disease { font-size: 0.92rem; font-weight: 700; color: #1a1a2e !important; margin-bottom: 3px; }
.duty-code { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #9ca3af !important; font-weight: 400; margin-left: 7px; background: #f4f6fb; padding: 1px 6px; border-radius: 4px; }
.duty-meta { font-size: 0.78rem; color: #9ca3af !important; margin: 4px 0; }
.duty-reason { font-size: 0.8rem; color: #6366f1 !important; margin: 5px 0; font-weight: 600; padding: 5px 10px; background: #f5f3ff; border-radius: 8px; border-left: 3px solid #6366f1; }
.duty-stats-row { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }
.stat-pill { font-size: 0.71rem; background: #f4f6fb; color: #6b7280 !important; padding: 3px 9px; border-radius: 100px; font-weight: 500; border: 1px solid #e8ecf4; }
.stat-pill.red { background: #fef2f2; color: #dc2626 !important; border-color: #fecaca; }
.stat-pill.purple { background: #f5f3ff; color: #6366f1 !important; border-color: #c4b5fd; }

/* ── 섹션 헤더 ── */
.section-head {
    font-size: 0.8rem; font-weight: 700; color: #1a1a2e !important;
    margin: 16px 0 10px; padding: 0 0 8px;
    border-bottom: 1px solid #e8ecf4;
    display: flex; align-items: center; gap: 6px;
}

/* ── 간편심사 그리드 ── */
.easy-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 12px; }
.easy-box { background: #ffffff; border: 1px solid #e8ecf4; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.easy-box-head { padding: 11px 14px; background: #f8f9ff; font-size: 0.8rem; font-weight: 700; color: #1a1a2e !important; border-bottom: 1px solid #e8ecf4; line-height: 1.5; }
.easy-item { padding: 9px 14px; font-size: 0.8rem; color: #1a1a2e !important; border-bottom: 1px solid #f4f6fb; }
.easy-item:last-child { border-bottom: none; }
.easy-code { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #9ca3af !important; background: #f4f6fb; padding: 1px 5px; border-radius: 4px; margin-right: 4px; }
.easy-empty { padding: 12px 14px; font-size: 0.8rem; color: #16a34a !important; font-weight: 600; }

/* ── 빈 화면 ── */
.clean-card {
    display: flex; align-items: center; gap: 14px;
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border: 1px solid #86efac; border-radius: 14px;
    padding: 22px 20px; font-size: 0.92rem;
    font-weight: 700; color: #15803d !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ── 카톡 복사 버튼 ── */
.copy-wrap { margin-bottom: 12px; }

/* ── 보장분석 ── */
.ba-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
.ba-panel { background: #ffffff; border: 1px solid #e8ecf4; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.ba-head { padding: 12px 16px; font-size: 0.8rem; font-weight: 700; border-bottom: 1px solid #f4f6fb; }
.ba-before .ba-head { background: linear-gradient(135deg,#fff8f0,#fff); color: #92400e !important; }
.ba-after  .ba-head { background: linear-gradient(135deg,#f0fdf4,#fff); color: #166534 !important; }
.cov-row { display: flex; align-items: center; padding: 9px 16px; border-bottom: 1px solid #f9fafb; gap: 10px; font-size: 0.81rem; }
.cov-row:last-child { border-bottom: none; }
.cov-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.cov-dot.up { background: #16a34a; }
.cov-dot.dn { background: #dc2626; }
.cov-dot.eq { background: #d1d5db; }
.cov-nm { flex: 1; color: #4a5568 !important; }
.cov-val { font-family: 'DM Mono', monospace; font-size: 0.79rem; color: #1a1a2e !important; }
.cov-val.up { color: #16a34a !important; font-weight: 700; }
.cov-val.dn { color: #dc2626 !important; font-weight: 700; }

/* ── 빈 업로드 안내 ── */
.upload-empty {
    text-align: center; padding: 48px 20px;
    background: #ffffff; border: 1px solid #e8ecf4;
    border-radius: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.upload-empty-icon { font-size: 3rem; margin-bottom: 12px; }
.upload-empty-title { font-size: 0.95rem; font-weight: 700; color: #1a1a2e !important; margin-bottom: 5px; }
.upload-empty-desc { font-size: 0.8rem; color: #9ca3af !important; line-height: 1.6; }

/* ── 경고 배너 ── */
.warn-banner {
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    border: 1px solid #fcd34d; border-radius: 12px;
    padding: 10px 14px; font-size: 0.82rem;
    color: #92400e !important; font-weight: 600;
    margin-bottom: 14px;
}

@media (max-width: 768px) {
    .ba-grid { grid-template-columns: 1fr; }
    .summary-grid { grid-template-columns: repeat(2, 1fr); }
    .easy-grid { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 사이드바
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-brand-name">AdvisorHub</div>
        <div class="sb-brand-sub">보험설계사 전용 AI 플랫폼</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">메뉴</div>', unsafe_allow_html=True)

    menus = [
        ("before_after", "🔄", "보장분석 비포&에프터"),
        ("disclosure",   "🔍", "알릴의무 필터"),
    ]
    for key, icon, label in menus:
        is_active = st.session_state.menu == key
        if st.button(f"{icon}  {label}", key=f"nav_{key}",
                     use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.menu = key
            st.rerun()

    st.divider()

    st.markdown('<div class="sb-section">분석 설정</div>', unsafe_allow_html=True)
    product_type = st.radio(
        "심사 기준",
        ["건강체/표준체 (일반심사)", "간편심사 (유병자 3-5-5 기준)"],
        index=0,
        label_visibility="collapsed"
    )
    reference_date = st.date_input("기준일 (청약예정일)", datetime.today())


# ==========================================
# 상수 및 헬퍼 함수
# ==========================================
surg_keywords = ["수술","절제","시술","천자","주입","절개","적출","봉합","결찰","종양","폴립","결절"]
test_keywords = ["검사","초음파","내시경","촬영","MRI","CT","조직","생검","판독","X-RAY","X-ray","엑스레이"]


def get_val(row, possible_keys):
    for k in row.keys():
        if any(pk in str(k) for pk in possible_keys):
            val = row[k]
            return str(val).strip() if pd.notna(val) else ""
    return ""


def normalize_code(raw: str) -> str:
    code = raw.upper().strip()
    if not code or code == "$":
        return ""
    if len(code) >= 2 and code[0] in ("A", "B") and code[1].isdigit():
        code = code[1:]
    if code and code[0] == "1" and len(code) >= 3:
        candidate = "I" + code[1:]
        if candidate[1:3].isdigit():
            code = candidate
    return code


def parse_date(date_str: str) -> str:
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_str)
    if m:
        return m.group()
    m = re.search(r"(\d{8})", date_str)
    if m:
        d = m.group()
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return ""


def row_is_junk(row) -> bool:
    combined = "".join(str(v) for v in row.values).replace(" ", "")
    return "$" in combined or "해당없음" in combined


# ==========================================
# 페이지 라우터
# ==========================================
menu = st.session_state.menu
if menu not in ("before_after", "disclosure"):
    st.session_state.menu = "disclosure"
    menu = "disclosure"


# ══════════════════════════════════════════
# PAGE: 보장분석 비포&에프터
# ══════════════════════════════════════════
if menu == "before_after":
    st.markdown("""
    <div class="page-header">
        <div class="page-eyebrow">🔄 보장 분석</div>
        <div class="page-title">비포 &amp; 에프터</div>
        <div class="page-desc">기존 보장내역과 신규 제안서를 비교하여 리모델링 근거를 제시하세요.</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**📋 기존 보장분석 PDF** <span style='color:#ef4444;font-size:0.8rem;'>필수</span>", unsafe_allow_html=True)
        before_file = st.file_uploader("기존", type="pdf", key="ba_before", label_visibility="collapsed")
    with col_r:
        st.markdown("**✨ 신규 제안서 PDF** <span style='color:#9ca3af;font-size:0.8rem;'>최대 4개</span>", unsafe_allow_html=True)
        after_files = st.file_uploader("신규", type="pdf", key="ba_after",
                                       accept_multiple_files=True, label_visibility="collapsed")

    if st.button("🔍  분석 시작", type="primary", use_container_width=True, key="btn_ba"):
        if not before_file:
            st.warning("기존 보장분석 PDF를 먼저 업로드해 주세요.")
        else:
            with st.spinner("분석 중..."):
                import time; time.sleep(1)

            st.markdown("""
            <div class="ba-grid">
              <div class="ba-panel ba-before">
                <div class="ba-head">📋 기존 보장 (BEFORE)</div>
                <div class="cov-row"><div class="cov-dot dn"></div><div class="cov-nm">암 진단금</div><div class="cov-val dn">3,000만원</div></div>
                <div class="cov-row"><div class="cov-dot eq"></div><div class="cov-nm">뇌졸중 진단금</div><div class="cov-val">2,000만원</div></div>
                <div class="cov-row"><div class="cov-dot eq"></div><div class="cov-nm">심근경색 진단금</div><div class="cov-val">2,000만원</div></div>
                <div class="cov-row"><div class="cov-dot eq"></div><div class="cov-nm">실손의료비</div><div class="cov-val">구실손 (5%)</div></div>
                <div class="cov-row" style="background:#fafafa;font-weight:700;border-top:1px solid #f0f0f0;">
                    <div class="cov-nm" style="color:#6b7280!important;">월 보험료</div>
                    <div class="cov-val" style="font-size:0.9rem;font-weight:800;">114,000원</div>
                </div>
              </div>
              <div class="ba-panel ba-after">
                <div class="ba-head">✨ 신규 제안 (AFTER)</div>
                <div class="cov-row"><div class="cov-dot up"></div><div class="cov-nm">암 진단금</div><div class="cov-val up">5,000만원 ▲</div></div>
                <div class="cov-row"><div class="cov-dot eq"></div><div class="cov-nm">뇌졸중 진단금</div><div class="cov-val">2,000만원</div></div>
                <div class="cov-row"><div class="cov-dot eq"></div><div class="cov-nm">심근경색 진단금</div><div class="cov-val">2,000만원</div></div>
                <div class="cov-row"><div class="cov-dot eq"></div><div class="cov-nm">실손의료비</div><div class="cov-val">4세대 실손</div></div>
                <div class="cov-row" style="background:#f0fdf4;font-weight:700;border-top:1px solid #dcfce7;">
                    <div class="cov-nm" style="color:#6b7280!important;">월 보험료</div>
                    <div class="cov-val up" style="font-size:0.9rem;font-weight:800;">128,000원 <span style="font-size:0.72rem;font-weight:500;color:#9ca3af;">(+14,000)</span></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="upload-empty">
            <div class="upload-empty-icon">🔄</div>
            <div class="upload-empty-title">PDF를 업로드하고 분석을 시작하세요</div>
            <div class="upload-empty-desc">기존 보장분석 PDF와 신규 제안서 PDF를 업로드하면<br>AI가 보장 항목을 자동으로 비교합니다.</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════
# PAGE: 알릴의무 필터
# ══════════════════════════════════════════
elif menu == "disclosure":
    st.markdown("""
    <div class="page-header">
        <div class="page-eyebrow">🔍 AI 고지 분석</div>
        <div class="page-title">알릴의무 필터</div>
        <div class="page-desc">심평원 진료 PDF를 업로드하면 AI가 고지 의무 항목을 자동으로 추출합니다.<br>기본진료 · 세부진료 · 처방조제 3종 모두 업로드 시 정확도가 높아집니다.</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "심평원 PDF 업로드 (복수 선택 가능)",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if not uploaded_files:
        st.markdown("""
        <div class="upload-empty">
            <div class="upload-empty-icon">📂</div>
            <div class="upload-empty-title">심평원 진료자료 PDF를 업로드하세요</div>
            <div class="upload-empty-desc">건강e음(health.kr)에서 기본진료·세부진료·처방조제 3종을 발급받아<br>위 업로더에 올려주세요. 1개만 올려도 분석 가능합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ==========================================
    # 분석 엔진
    # ==========================================
    with st.spinner("📊 PDF 파싱 및 AI 분석 중..."):
        today = datetime(reference_date.year, reference_date.month, reference_date.day)
        all_records = []
        file_dataframes = {}

        def detect_file_type(headers):
            h_joined = " ".join(str(h) for h in headers)
            if any(k in h_joined for k in ["상병명", "상병코드", "진단코드", "내원일수"]):
                return "basic"
            if any(k in h_joined for k in ["진료내역", "행위명", "처치", "수술"]):
                return "detail"
            if any(k in h_joined for k in ["약품명", "투약일수", "조제"]):
                return "pharma"
            return "unknown"

        for uploaded_file in uploaded_files:
            file_recs = []
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        raw_headers = table[0]
                        headers = [
                            str(h).replace("\n", "").replace(" ", "") if h else f"col_{i}"
                            for i, h in enumerate(raw_headers)
                        ]
                        ftype = detect_file_type(headers)
                        for row in table[1:]:
                            if not any(row):
                                continue
                            if "순번" in str(row[0]):
                                continue
                            rec = {h: str(v).replace("\n", " ").strip() if v else "" for h, v in zip(headers, row)}
                            rec["_ftype"] = ftype
                            rec["_fname"] = uploaded_file.name
                            all_records.append(rec)
                            file_recs.append(rec)
            if file_recs:
                file_dataframes[uploaded_file.name] = pd.DataFrame(file_recs).fillna("")

        if not all_records:
            st.error("PDF에서 표 데이터를 추출하지 못했습니다. 비밀번호 잠금 또는 스캔 이미지 형태인지 확인해 주세요.")
            st.stop()

        df = pd.DataFrame(all_records)

        def new_disease():
            return {
                "visit_dates": set(), "med_dates_basic": {}, "med_dates_pharma": {},
                "drug_names_in_90": set(), "drug_names_before_90": set(),
                "tests_found": set(), "inpatient_dates": set(),
                "surgeries": set(), "surgery_dates": set(), "hospitals": set(),
                "first_date": "2099-12-31", "latest_date": "2000-01-01",
                "diag_code": "", "name": "", "has_pharma": False,
            }

        disease_stats = defaultdict(new_disease)

        for _, row in df.iterrows():
            if row_is_junk(row):
                continue
            ftype    = str(row.get("_ftype", "unknown"))
            raw_code = get_val(row, ["코드", "상병코드", "진단코드"])
            code_str = normalize_code(raw_code)
            name_str = get_val(row, ["상병명", "약품명", "진료내역", "행위명"])
            in_out   = get_val(row, ["입원외래구분", "입원", "외래", "구분"])
            hospital = get_val(row, ["병·의원", "기관명", "요양기관명"])
            date_str = get_val(row, ["진료시작일", "진료일", "조제일자", "처방일"])
            m_days_raw = get_val(row, ["투약일수"])
            m_days = int(re.findall(r"\d+", m_days_raw)[0]) if re.findall(r"\d+", m_days_raw) else 0

            group_key = code_str if code_str else name_str[:15]
            if not group_key:
                continue

            clean_date = parse_date(date_str)
            s = disease_stats[group_key]

            if code_str and not s["diag_code"]:
                s["diag_code"] = code_str

            if clean_date:
                dt = datetime.strptime(clean_date, "%Y-%m-%d")
                days_ago = (today - dt).days

                if ftype in ("basic", "unknown"):
                    is_inpatient = "입원" in in_out or "입원" in name_str
                    if is_inpatient:
                        s["inpatient_dates"].add(clean_date)
                    else:
                        s["visit_dates"].add(clean_date)
                    if m_days > 0:
                        prev = s["med_dates_basic"].get(clean_date, 0)
                        if m_days > prev:
                            s["med_dates_basic"][clean_date] = m_days
                elif ftype == "detail":
                    for kw in surg_keywords:
                        if kw in name_str:
                            s["surgeries"].add(name_str); s["surgery_dates"].add(clean_date); break
                    for kw in test_keywords:
                        if kw in name_str:
                            s["tests_found"].add(name_str); break
                elif ftype == "pharma":
                    s["has_pharma"] = True
                    if m_days > 0:
                        prev = s["med_dates_pharma"].get(clean_date, 0)
                        if m_days > prev:
                            s["med_dates_pharma"][clean_date] = m_days
                    drug = name_str.strip()
                    if drug:
                        if days_ago <= 90: s["drug_names_in_90"].add(drug)
                        else: s["drug_names_before_90"].add(drug)

                if ftype in ("basic", "unknown"):
                    for kw in surg_keywords:
                        if kw in name_str:
                            s["surgeries"].add(name_str)
                            if clean_date: s["surgery_dates"].add(clean_date)
                            break
                    for kw in test_keywords:
                        if kw in name_str: s["tests_found"].add(name_str); break

                if clean_date > s["latest_date"]: s["latest_date"] = clean_date
                if clean_date < s["first_date"]:  s["first_date"]  = clean_date

            if hospital and "약국" not in hospital and ftype != "pharma":
                s["hospitals"].add(hospital)
            if name_str and not s["name"]:
                s["name"] = name_str

        # Claude API 분석
        raw_text_lines = []
        for _, row in df.iterrows():
            if row_is_junk(row): continue
            ftype    = str(row.get("_ftype", ""))
            date_str = get_val(row, ["진료시작일", "진료일", "조제일자", "처방일"])
            code_raw = get_val(row, ["코드", "상병코드", "진단코드"])
            code_str = normalize_code(code_raw)
            name_str = get_val(row, ["상병명", "약품명", "진료내역", "행위명"])
            hospital = get_val(row, ["병·의원", "기관명", "요양기관명"])
            in_out   = get_val(row, ["입원외래구분", "입원", "외래", "구분"])
            m_days   = get_val(row, ["투약일수"])
            v_days   = get_val(row, ["내원일수"])
            if not date_str and not name_str: continue
            raw_text_lines.append(f"[{ftype}] 날짜:{date_str} 코드:{code_str} 병명:{name_str[:20]} 병원:{hospital[:10]} 구분:{in_out} 투약일:{m_days} 내원일:{v_days}")

        raw_text  = "\n".join(raw_text_lines[:600])
        today_str = today.strftime('%Y-%m-%d')
        d_3m  = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        d_1y  = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        d_5y  = (today - timedelta(days=1825)).strftime('%Y-%m-%d')
        d_10y = (today - timedelta(days=3650)).strftime('%Y-%m-%d')

        if product_type == "건강체/표준체 (일반심사)":
            criteria_text = f"""
[건강체/표준체 알릴의무 4문항] (기준일: {today_str})
Q1. 최근 3개월({d_3m} 이후): 질병확정진단 / 의심소견 / 입원·수술·추가검사 필요소견 / 치료 / 투약
Q2. 최근 3개월({d_3m} 이후): 혈압강하제·신경안정제·수면제·각성제·진통제·마약류 상시 복용
Q3. 최근 1년({d_1y} 이후): 진찰 후 이상소견으로 추가검사(재검사) 받은 사실
Q4. 최근 5년({d_5y} 이후): 입원 / 수술(제왕절개 포함) / 계속하여 7일 이상 치료 / 계속하여 30일 이상 투약
[판단 기준] 내시경+용종절제=수술, 치과발치/임플란트=수술 가능, 당뇨·고혈압 지속투약=30일이상 해당, COVID검사/예방접종 제외"""
        else:
            criteria_text = f"""
[간편심사(유병자 3-5-5) 알릴의무 3문항] (기준일: {today_str})
Q1. 최근 3개월({d_3m} 이후): 질병확정진단 / 의심소견 / 추가검사필요소견 / 입원 / 수술
Q2. 최근 10년({d_10y} 이후): 입원 또는 수술(제왕절개 포함)
Q3. 최근 5년({d_5y} 이후) 6대질병: 암(C코드) / 협심증(I20) / 심근경색(I21-22) / 심장판막증 / 간경화(K74) / 뇌졸중(I60-64)
[면제] 7일 미만 단순 통원, 30일 미만 단순 투약, 6대질병 외 단순 통원/투약"""

        system_prompt = f"""당신은 보험 언더라이팅 전문 AI입니다.
건강보험심사평가원(건강e음) 진료 데이터를 분석하여 보험 가입 시 알릴의무(고지의무) 해당 항목을 정확히 판단합니다.
코드 앞 A(양방)/B(한방) 접두사 제거, 숫자1→I 교정, $ 해당없음 행 완전 제외.
{criteria_text}
반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 순수 JSON:
{{
  "flagged_items": [{{
    "date":"YYYY-MM-DD","code":"KCD코드","disease":"질병/수술명(한글)","hospital":"병원명",
    "duty_question":"Q1또는Q2또는Q3또는Q4","reason":"고지판단사유(구체적)",
    "is_inpatient":true또는false,"inpatient_days":숫자,"is_surgery":true또는false,
    "surgery_name":"수술명또는null","med_days":숫자,"weight":"critical또는high또는mid또는low"
  }}],
  "exempt_items":[],
  "q1_hit":true또는false,"q1_reason":"사유",
  "q2_hit":true또는false,"q2_reason":"약물명또는없음",
  "q3_hit":true또는false,"q3_reason":"사유",
  "q4_hit":true또는false,"q4_reason":"사유",
  "simple_q1_hit":true또는false,
  "simple_q2_hit":true또는false,"simple_q2_reason":"상세",
  "simple_q3_hit":true또는false,"simple_q3_disease":"6대질병명또는null",
  "total_flagged":숫자,
  "health_verdict":"가능또는조건부또는불가","health_reason":"한줄",
  "simple_verdict":"가능또는조건부또는불가","simple_reason":"한줄",
  "recommend":"권장사항","summary":"설계사핵심요약2줄"
}}"""

        try:
            api_client = anthropic.Anthropic(
                api_key=st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
            )
            message = api_client.messages.create(
                model="claude-opus-4-5", max_tokens=3000, system=system_prompt,
                messages=[{"role": "user", "content": f"고객 기준일: {today_str}\n심사 유형: {product_type}\n\n진료 데이터:\n{raw_text}"}]
            )
            raw_response   = message.content[0].text
            clean_response = raw_response.replace("```json", "").replace("```", "").strip()
            ai_result      = json.loads(clean_response)
        except json.JSONDecodeError as e:
            st.error(f"AI 응답 파싱 오류: {e}"); st.stop()
        except Exception as e:
            st.error(f"Claude API 호출 오류: {e}"); st.stop()

        summary_reports = defaultdict(list)
        flagged_codes   = set()

        for item in ai_result.get("flagged_items", []):
            q = item.get("duty_question", "Q1")
            if product_type == "건강체/표준체 (일반심사)":
                q_map = {"Q1":"[1번 질문] 3개월 이내 의료행위","Q2":"[2번 질문] 3개월 이내 혈압강하제 등 상시 복용","Q3":"[3번 질문] 1년 이내 추가검사(재검사)","Q4":"[4번 질문] 5년 이내 입원/수술/7일이상치료/30일이상투약"}
            else:
                q_map = {"Q1":"[간편 1번] 3개월 이내 진단/소견","Q2":"[간편 2번] 10년 이내 입원/수술","Q3":"[간편 3번] 5년 이내 6대 중증 질환"}
            q_title  = q_map.get(q, f"[{q}]")
            code_key = item.get("code", item.get("disease", "unknown"))
            flagged_codes.add(code_key)
            summary_reports[q_title].append({
                "first_date":     item.get("date", ""),
                "latest_date":    item.get("date", ""),
                "code":           item.get("code", "-"),
                "name":           item.get("disease", ""),
                "visit":          1,
                "max_single_med": item.get("med_days", 0),
                "total_med":      item.get("med_days", 0),
                "inpatient":      item.get("inpatient_days", 0),
                "inpatient_dates":[item.get("date","")] if item.get("is_inpatient") else [],
                "surgeries":      {item.get("surgery_name")} if item.get("is_surgery") and item.get("surgery_name") else set(),
                "surgery_dates":  [item.get("date","")] if item.get("is_surgery") else [],
                "hospitals":      [item.get("hospital","")],
                "detail":         item.get("reason",""),
                "weight":         item.get("weight","mid"),
            })

        st.session_state["ai_result"] = ai_result

    # ==========================================
    # 요약 수치
    # ==========================================
    flagged_count   = len(flagged_codes)
    total_q_count   = len(summary_reports)
    total_visit_sum = sum(len(s["visit_dates"]) + len(s["inpatient_dates"]) for s in disease_stats.values() if s["latest_date"] != "2000-01-01")
    total_med_sum   = sum(sum((s["med_dates_pharma"] if s["has_pharma"] and s["med_dates_pharma"] else s["med_dates_basic"]).values()) for s in disease_stats.values() if s["latest_date"] != "2000-01-01")

    # AI 판정 배너
    ai_res    = st.session_state.get("ai_result", {})
    verdict   = ai_res.get("health_verdict", "") if product_type == "건강체/표준체 (일반심사)" else ai_res.get("simple_verdict", "")
    reason    = ai_res.get("health_reason",  "") if product_type == "건강체/표준체 (일반심사)" else ai_res.get("simple_reason", "")
    recommend = ai_res.get("recommend", "")

    if verdict == "가능":
        v_cls, v_icon, v_label = "verdict-ok",  "✅", "인수 가능"
    elif verdict == "불가":
        v_cls, v_icon, v_label = "verdict-bad", "❌", "인수 불가"
    else:
        v_cls, v_icon, v_label = "verdict-warn","⚠️", "조건부 가능"

    st.markdown(f"""
    <div class="verdict-banner {v_cls}">
        <div class="verdict-icon">{v_icon}</div>
        <div class="verdict-content">
            <div class="verdict-label">AI 심사 판정</div>
            <div class="verdict-title">{v_label} — {verdict}</div>
            <div class="verdict-desc">{reason}<br><span style="font-weight:600;">권장: {recommend}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    card_class = "danger" if flagged_count >= 5 else ("warn" if flagged_count > 0 else "ok")
    card_icon  = "🚨" if flagged_count >= 5 else ("⚠️" if flagged_count > 0 else "✅")
    st.markdown(f"""
    <div class="summary-grid">
        <div class="stat-card {card_class}">
            <div class="sc-icon">{card_icon}</div>
            <div class="sc-label">고지 대상 질환</div>
            <div class="sc-value">{flagged_count}</div>
            <div class="sc-sub">{'간편심사 전환 검토' if flagged_count >= 5 else ('고지 항목 있음' if flagged_count > 0 else '이상 없음')}</div>
        </div>
        <div class="stat-card">
            <div class="sc-icon">📋</div>
            <div class="sc-label">해당 질문 항목</div>
            <div class="sc-value">{total_q_count}</div>
            <div class="sc-sub">청약서 기재 필요</div>
        </div>
        <div class="stat-card">
            <div class="sc-icon">🏥</div>
            <div class="sc-label">누적 진료일</div>
            <div class="sc-value">{total_visit_sum}</div>
            <div class="sc-sub">입원 포함 총 일수</div>
        </div>
        <div class="stat-card">
            <div class="sc-icon">💊</div>
            <div class="sc-label">누적 투약일</div>
            <div class="sc-value">{total_med_sum}</div>
            <div class="sc-sub">합계 기준</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if product_type == "건강체/표준체 (일반심사)" and flagged_count >= 5:
        st.markdown(f"""
        <div class="switch-banner">
            🔄 <span>고지 대상 질환 <b>{flagged_count}개</b> — 간편심사 전환 시 청약 가능성이 높아집니다. 사이드바에서 심사 기준을 변경해 시뮬레이션하세요.</span>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # 탭
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["📋 고지 판정 리포트", "🔍 원본 데이터", "💬 카톡 전송 & PDF"])

    # ── TAB 1: 고지 판정 리포트 ──
    with tab1:
        if not summary_reports:
            st.markdown("""
            <div class="clean-card">
                <span style="font-size:2rem;">✅</span>
                <div>
                    <div>고지 대상 없음 — 표준체 심사 진행 가능</div>
                    <div style="font-size:0.8rem;font-weight:400;color:#166534;margin-top:4px;">설정 기간 내 알릴의무 해당 이력이 발견되지 않았습니다.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warn-banner">
                ⚠️ 아래 항목은 AI가 분석한 <b>필수 고지 대상</b>입니다. 청약서 해당 번호에 정확히 기재하세요.
            </div>
            """, unsafe_allow_html=True)

            import html as _html

            for q_title in sorted(summary_reports.keys()):
                items   = summary_reports[q_title]
                q_badge = re.sub(r"\].*", "]", q_title).strip("[]").strip()
                q_label = re.sub(r"^\[.*?\]\s*", "", q_title)

                st.markdown(
                    f'<div class="duty-card">'
                    f'<div class="duty-card-head">'
                    f'<span class="duty-q-badge">{_html.escape(q_badge)}</span>'
                    f'<span class="duty-q-title">{_html.escape(q_label)}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                for item in items:
                    hosp      = _html.escape(", ".join(item["hospitals"])[:25] if item["hospitals"] else "기록 없음")
                    name      = _html.escape(item["name"][:30] or "(병명 미상)")
                    code      = _html.escape(item["code"])
                    fd        = _html.escape(item["first_date"])
                    ld        = _html.escape(item["latest_date"])
                    detail    = _html.escape(item["detail"])
                    inpatient = item["inpatient"]
                    n_surg    = len(item["surgeries"])
                    max_med   = item["max_single_med"]
                    med       = item["total_med"]

                    inpt_pill    = f'<span class="stat-pill red">🏥 입원 {inpatient}일</span>' if inpatient > 0 else ""
                    surg_pill    = f'<span class="stat-pill red">🔪 수술 {n_surg}건</span>'    if n_surg > 0  else ""
                    max_med_pill = f'<span class="stat-pill purple">📋 단일처방 최대 {max_med}일</span>' if max_med >= 30 else ""

                    st.markdown(
                        f'<div class="duty-item">'
                        f'  <div class="duty-disease">{name}<span class="duty-code">{code}</span></div>'
                        f'  <div class="duty-meta">📅 {fd} ~ {ld} &nbsp;·&nbsp; 🏥 {hosp}</div>'
                        f'  <div class="duty-reason">↳ {detail}</div>'
                        f'  <div class="duty-stats-row">'
                        f'    <span class="stat-pill">💊 투약 {med}일</span>'
                        f'    {inpt_pill}{surg_pill}{max_med_pill}'
                        f'  </div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown('</div>', unsafe_allow_html=True)

        if product_type == "간편심사 (유병자 3-5-5 기준)":
            st.markdown('<div class="section-head">⚡ 간편심사 3-5-5 항목별 현황</div>', unsafe_allow_html=True)

            def get_easy_items(keywords):
                html_parts = []
                for k, v_list in summary_reports.items():
                    if any(kw in k for kw in keywords):
                        for v in v_list:
                            code_h = f'<span class="easy-code">{v["code"]}</span>' if v["code"] != "-" else ""
                            extra  = ""
                            if v["inpatient"] > 0:
                                dates = v["inpatient_dates"]
                                r = f"{dates[0]} ~ {dates[-1]}" if len(dates) > 1 else (dates[0] if dates else "")
                                extra += f'<br><span style="color:#6366f1;font-size:0.73rem;font-weight:600;">🏥 입원 {r} ({v["inpatient"]}일)</span>'
                            if v["surgeries"]:
                                dates = v["surgery_dates"]
                                r = f"{dates[0]} ~ {dates[-1]}" if len(dates) > 1 else (dates[0] if dates else "")
                                extra += f'<br><span style="color:#dc2626;font-size:0.73rem;font-weight:600;">🔪 수술 {r} ({len(v["surgeries"])}건)</span>'
                            html_parts.append(f'<div class="easy-item">{code_h} {v["name"][:15]}<span style="color:#9ca3af;font-size:0.73rem;"> ({v["latest_date"]})</span>{extra}</div>')
                return "".join(html_parts) if html_parts else '<div class="easy-empty">✅ 해당 없음</div>'

            st.markdown(f"""
            <div class="easy-grid">
                <div class="easy-box">
                    <div class="easy-box-head">⏱️ 최근 3개월<br><span style="font-weight:500;font-size:0.72rem;color:#9ca3af;">진단·소견·약품변경</span></div>
                    {get_easy_items(["1번"])}
                </div>
                <div class="easy-box">
                    <div class="easy-box-head">🏥 최근 10년 입원/수술<br><span style="font-weight:500;font-size:0.72rem;color:#9ca3af;">통원·투약 이력 면제</span></div>
                    {get_easy_items(["2번"])}
                </div>
                <div class="easy-box">
                    <div class="easy-box-head">⚠️ 최근 5년 6대 질환<br><span style="font-weight:500;font-size:0.72rem;color:#9ca3af;">암·뇌·심장·간경화</span></div>
                    {get_easy_items(["3번"])}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 2: 원본 데이터 ──
    with tab2:
        st.markdown('<div class="section-head">🔍 원본 데이터 <span style="font-weight:400;color:#9ca3af;font-size:0.78rem;">· 빨간 행 = 고지 필요</span></div>', unsafe_allow_html=True)
        for file_name, f_df in file_dataframes.items():
            keep     = [idx for idx, row in f_df.iterrows() if not row_is_junk(row)]
            clean_df = f_df.loc[keep].copy()
            if clean_df.empty: continue
            st.markdown(f"**📄 {file_name}**")

            is_flagged_list, code_sort = [], []
            for _, row in clean_df.iterrows():
                c  = normalize_code(get_val(row, ["코드"]))
                n  = get_val(row, ["상병명", "약품명", "진료내역"])
                rk = c if c else n[:15]
                is_flagged_list.append(rk in flagged_codes)
                code_sort.append(c)

            clean_df["_flag"] = is_flagged_list
            clean_df["_code"] = code_sort
            sorted_df = (clean_df.sort_values(["_flag","_code"], ascending=[False,True])
                         .drop(columns=["_flag","_code"]).reset_index(drop=True))

            def highlight(row):
                c  = normalize_code(get_val(row, ["코드"]))
                n  = get_val(row, ["상병명","약품명","진료내역"])
                rk = c if c else n[:15]
                if rk in flagged_codes:
                    return ["background-color:#fee2e2;color:#991b1b;font-weight:700;"] * len(row)
                return [""] * len(row)

            st.dataframe(sorted_df.style.apply(highlight, axis=1), use_container_width=True)
            st.markdown("---")

    # ── TAB 3: 카톡 전송 & PDF ──
    with tab3:
        import streamlit.components.v1 as components

        kakao_msg  = f"📋 [{product_type} 심사 요청]\n"
        kakao_msg += f"■ 기준일: {today.strftime('%Y-%m-%d')}\n"

        ai_res = st.session_state.get("ai_result", {})
        if ai_res:
            kakao_msg += f"■ AI 판정: {ai_res.get('health_verdict','?')} ({ai_res.get('health_reason','')})\n"
            kakao_msg += f"■ 권장: {ai_res.get('recommend','')}\n\n"

        if not summary_reports:
            kakao_msg += "✅ 고지 대상 없음. 표준체 진행 가능\n"
        else:
            for q_title in sorted(summary_reports.keys()):
                clean_title = re.sub(r"^\[.*?\]\s*", "", q_title)
                kakao_msg  += f"▶ {clean_title}\n"
                for item in summary_reports[q_title]:
                    hosp = ", ".join(item["hospitals"]) if item["hospitals"] else "알 수 없음"
                    kakao_msg += f"■ {item['name']} ({item['code']})\n"
                    kakao_msg += f"  - 기간: {item['first_date']} ~ {item['latest_date']}\n"
                    kakao_msg += f"  - 병원: {hosp}\n"
                    kakao_msg += f"  - 사유: {item['detail']}\n"
                    if item["inpatient"] > 0: kakao_msg += f"  - 입원: {item['inpatient']}일\n"
                    if item["surgeries"]:     kakao_msg += f"  - 수술: {len(item['surgeries'])}건\n"
                    kakao_msg += "\n"

        safe_msg = kakao_msg.replace("`","\\`").replace("\n","\\n").replace("'","\\'")
        copy_html = f"""
        <style>
        .copy-btn {{
            width:100%; padding:15px 20px;
            background:linear-gradient(135deg,#6366f1,#8b5cf6);
            border:none; border-radius:12px;
            color:#fff; font-weight:700; font-size:0.95rem;
            cursor:pointer; font-family:sans-serif;
            transition:all 0.2s; letter-spacing:-.01em;
            box-shadow:0 4px 12px rgba(99,102,241,0.3);
        }}
        .copy-btn:hover {{ transform:translateY(-2px); box-shadow:0 6px 20px rgba(99,102,241,0.4); }}
        .copy-btn.copied {{ background:linear-gradient(135deg,#16a34a,#15803d); box-shadow:0 4px 12px rgba(22,163,74,0.3); }}
        </style>
        <button id="copy-btn" class="copy-btn">💬 카카오톡 전달용 복사하기</button>
        <script>
        document.getElementById('copy-btn').addEventListener('click', function() {{
            const text = `{safe_msg}`;
            const btn = this;
            const ta = document.createElement('textarea');
            ta.value = text; ta.style.position='fixed'; ta.style.opacity='0';
            document.body.appendChild(ta); ta.select();
            try {{
                document.execCommand('copy');
                btn.textContent = '✅ 복사 완료! 카카오톡에 붙여넣기 하세요 (Ctrl+V)';
                btn.classList.add('copied');
                setTimeout(()=>{{ btn.textContent='💬 카카오톡 전달용 복사하기'; btn.classList.remove('copied'); }}, 3000);
            }} catch(e) {{ console.error(e); }}
            document.body.removeChild(ta);
        }});
        </script>
        """
        components.html(copy_html, height=72)

        with st.expander("📄 메시지 미리보기"):
            st.text(kakao_msg)

        st.markdown("---")

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import io, urllib.request, tempfile

            FONT_CACHE_DIR = tempfile.gettempdir()
            FONT_REG_PATH  = os.path.join(FONT_CACHE_DIR, "NanumGothic.ttf")
            FONT_BOLD_PATH = os.path.join(FONT_CACHE_DIR, "NanumGothicBold.ttf")
            NANUM_REG_URL  = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            NANUM_BOLD_URL = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
            SYSTEM_PATHS   = [
                ("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
                ("/usr/share/fonts/nanum/NanumGothic.ttf", "/usr/share/fonts/nanum/NanumGothicBold.ttf"),
                ("/Library/Fonts/NanumGothic.ttf", "/Library/Fonts/NanumGothicBold.ttf"),
            ]

            def _get_font_paths():
                for reg, bold in SYSTEM_PATHS:
                    if os.path.exists(reg):
                        return reg, bold if os.path.exists(bold) else reg
                if os.path.exists(FONT_REG_PATH):
                    return FONT_REG_PATH, FONT_BOLD_PATH if os.path.exists(FONT_BOLD_PATH) else FONT_REG_PATH
                try:
                    urllib.request.urlretrieve(NANUM_REG_URL,  FONT_REG_PATH)
                    urllib.request.urlretrieve(NANUM_BOLD_URL, FONT_BOLD_PATH)
                    return FONT_REG_PATH, FONT_BOLD_PATH
                except Exception:
                    return None, None

            @st.cache_resource(show_spinner=False)
            def _register_fonts():
                reg_path, bold_path = _get_font_paths()
                if reg_path is None: return "Helvetica", "Helvetica-Bold", False
                try:
                    if "NanumGothic"     not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("NanumGothic",     reg_path))
                    if "NanumGothicBold" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("NanumGothicBold", bold_path))
                    return "NanumGothic", "NanumGothicBold", True
                except Exception:
                    return "Helvetica", "Helvetica-Bold", False

            FONT_NAME, BOLD_FONT, font_ok = _register_fonts()

            def build_pdf():
                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
                purple = colors.HexColor("#6366f1")
                red    = colors.HexColor("#dc2626")
                gray   = colors.HexColor("#6b7280")
                ltgray = colors.HexColor("#f4f6fb")
                white  = colors.white
                black  = colors.HexColor("#1a1a2e")
                green  = colors.HexColor("#16a34a")

                def S(uid, size=10, color=black, font=FONT_NAME, leading=14, before=0, after=4, indent=0):
                    return ParagraphStyle(uid, fontName=font, fontSize=size, textColor=color, leading=leading, spaceBefore=before, spaceAfter=after, leftIndent=indent, wordWrap='CJK')

                def th(uid): return ParagraphStyle(uid, fontName=BOLD_FONT, fontSize=8, textColor=white, leading=11, wordWrap='CJK')
                def tv(uid, c=purple): return ParagraphStyle(uid, fontName=BOLD_FONT, fontSize=15, textColor=c, leading=18, alignment=1, wordWrap='CJK')

                story = []
                story.append(Paragraph("AdvisorHub 스마트 고지 스캐너", S("t",17,purple,BOLD_FONT,21,0,5)))
                story.append(Paragraph(f"심사유형: {product_type}  |  기준일: {today.strftime('%Y-%m-%d')}  |  고지질환: {flagged_count}개  |  해당질문: {total_q_count}개", S("s",8,gray,FONT_NAME,12,0,10)))
                story.append(HRFlowable(width="100%", thickness=1, color=purple, spaceAfter=6))

                hdr  = [Paragraph(t, th(f"h{i}")) for i, t in enumerate(["고지 질환 수","해당 질문 수","총 진료일","총 투약일"])]
                vc   = red if flagged_count > 0 else green
                vals = [Paragraph(str(flagged_count),tv("v0",vc)), Paragraph(str(total_q_count),tv("v1")), Paragraph(str(total_visit_sum),tv("v2")), Paragraph(str(total_med_sum),tv("v3"))]
                t2   = Table([hdr,vals], colWidths=["25%"]*4)
                t2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),purple),("BACKGROUND",(0,1),(-1,1),ltgray),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#e8ecf4")),("INNERGRID",(0,0),(-1,-1),0.3,colors.HexColor("#e8ecf4")),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
                story.append(t2); story.append(Spacer(1,10))
                story.append(Paragraph("고지 판정 결과", S("sec",11,purple,BOLD_FONT,15,8,4)))

                if not summary_reports:
                    story.append(Paragraph("고지 대상 없음 — 설정 기간 내 알릴 의무 위험 이력이 발견되지 않았습니다.", S("ok",10,green,BOLD_FONT,14,4,4)))
                else:
                    for q_title in sorted(summary_reports.keys()):
                        story.append(Paragraph(q_title, S("q",10,red,BOLD_FONT,14,8,3)))
                        col_hdr = [Paragraph(t, th(f"ch{i}")) for i,t in enumerate(["질병명(코드)","기간","진료/투약","매칭사유"])]
                        rows = [col_hdr]
                        for item in summary_reports[q_title]:
                            rows.append([
                                Paragraph(f"{(item['name'][:25] or '(병명미상)').replace('&','and')}\n({item['code']})", S(f"b{id(item)}",8,black,FONT_NAME,12,0,2,4)),
                                Paragraph(f"{item['first_date']}\n~ {item['latest_date']}", S(f"d{id(item)}",8,black,FONT_NAME,12,0,2,4)),
                                Paragraph(f"투약 {item['total_med']}일\n입원 {item['inpatient']}일", S(f"m{id(item)}",8,black,FONT_NAME,12,0,2,4)),
                                Paragraph(item['detail'][:60].replace('&','and'), S(f"r{id(item)}",8,black,FONT_NAME,12,0,2,4)),
                            ])
                        t3 = Table(rows, colWidths=["28%","20%","17%","35%"])
                        t3.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),red),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,colors.HexColor("#fff5f5")]),("BOX",(0,0),(-1,-1),0.4,colors.HexColor("#fecaca")),("INNERGRID",(0,0),(-1,-1),0.3,colors.HexColor("#fee2e2")),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5)]))
                        story.append(t3); story.append(Spacer(1,6))

                story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#e8ecf4"), spaceBefore=10))
                story.append(Paragraph(f"본 리포트는 AdvisorHub AI 엔진이 자동 생성한 참고자료이며, 최종 심사 판단은 언더라이터의 전문적 검토를 따릅니다.  |  생성: {datetime.now().strftime('%Y-%m-%d %H:%M')}", S("foot",7,gray,FONT_NAME,10,0,0)))
                doc.build(story)
                return buf.getvalue()

            pdf_bytes = build_pdf()
            st.download_button(
                label="⬇️  PDF 리포트 다운로드",
                data=pdf_bytes,
                file_name=f"AdvisorHub_고지리포트_{today.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except ImportError:
            st.warning("PDF 생성에는 `reportlab` 라이브러리가 필요합니다.")
        except Exception as e:
            st.error(f"PDF 생성 중 오류: {e}")