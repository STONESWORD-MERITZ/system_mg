import streamlit as st
import streamlit.components.v1 as components
import pdfplumber
import pandas as pd
import re
import io
import time
import html as _html
from datetime import datetime, timedelta
from collections import defaultdict
from google import genai
from google.genai import types
import json
import os

# ==========================================
# 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="설계사에게 확신을 주다. SURIT",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "설계사에게 확신을 주다. SURIT"
    }
)

if "menu" not in st.session_state:
    st.session_state.menu = "home"

# ==========================================
# CSS — ConnectionLabs 스타일
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── 전체 배경 ── */
html, body, .stApp {
    background: #f5f6f8 !important;
    font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif !important;
    color: #1f2937 !important;
}

/* ── Streamlit 기본 UI 제거 ── */
[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebarHeader"],
[data-testid="collapsedControl"],
div[data-testid="stToolbar"],
#MainMenu, footer { display: none !important; visibility: hidden !important; }

/* ── 메인 여백 ── */
.main .block-container {
    padding: 0 1.5rem 2rem 1.5rem !important;
    max-width: 100% !important;
}
[data-testid="stMainBlockContainer"] { padding-top: 0 !important; }

/* ── 사이드바 완전 숨김 ── */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    min-width: 0 !important;
}

/* ══════════════════════════════
   상단 네비게이션 바
══════════════════════════════ */
.topnav {
    display: flex;
    align-items: center;
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    padding: 0 8px;
    height: 56px;
    margin: 0 -1.5rem 20px -1.5rem;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.nav-logo {
    font-size: 1rem;
    font-weight: 800;
    color: #111827 !important;
    letter-spacing: -.02em;
    padding: 0 20px;
    line-height: 1.2;
    white-space: nowrap;
    flex-shrink: 0;
}
.nav-logo-sub {
    font-size: 0.6rem;
    font-weight: 500;
    color: #9ca3af !important;
    letter-spacing: 0;
    display: block;
}
.nav-divider {
    width: 1px;
    height: 20px;
    background: #e5e7eb;
    margin: 0 4px;
    flex-shrink: 0;
}

/* 네비 탭 버튼 스타일 */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton button,
div[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton button {
    height: 56px !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    padding: 0 18px !important;
    box-shadow: none !important;
    transition: all 0.15s !important;
    margin-bottom: -1px !important;
    white-space: nowrap !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton button:hover,
div[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton button:hover {
    color: #111827 !important;
    background: #f9fafb !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton button[kind="primary"],
div[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton button[kind="primary"] {
    color: #3b82f6 !important;
    border-bottom: 3px solid #3b82f6 !important;
    font-weight: 700 !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* ══════════════════════════════
   페이지 헤더
══════════════════════════════ */
.page-header {
    padding: 20px 0 14px;
    margin-bottom: 16px;
    border-bottom: 1px solid #e5e7eb;
}
.page-eyebrow {
    font-size: 0.7rem; font-weight: 600;
    color: #3b82f6 !important; margin-bottom: 4px;
    letter-spacing: .04em;
}
.page-title {
    font-size: 1.3rem; font-weight: 800;
    color: #111827 !important; letter-spacing: -.03em; line-height: 1.2;
}
.page-desc { font-size: 0.78rem; color: #6b7280 !important; margin-top: 4px; line-height: 1.5; }

/* ══════════════════════════════
   카드 공통
══════════════════════════════ */
.cl-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ══════════════════════════════
   요약 수치 카드
══════════════════════════════ */
.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px; }
.stat-card {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 14px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.stat-card.ok     { border-color: #bbf7d0; background: #f0fdf4; }
.stat-card.warn   { border-color: #fde68a; background: #fffbeb; }
.stat-card.danger { border-color: #fecaca; background: #fef2f2; }
.sc-label { font-size: 0.7rem; color: #9ca3af !important; font-weight: 600; margin-bottom: 6px; }
.sc-value { font-family: 'DM Mono', monospace; font-size: 2rem; font-weight: 700; color: #111827 !important; line-height: 1; }
.stat-card.ok .sc-value { color: #16a34a !important; }
.stat-card.warn .sc-value, .stat-card.danger .sc-value { color: #dc2626 !important; }
.sc-sub { font-size: 0.7rem; color: #9ca3af !important; margin-top: 4px; }

/* ══════════════════════════════
   AI 판정 배너
══════════════════════════════ */
.verdict-banner {
    border-radius: 12px; padding: 14px 18px; margin-bottom: 16px;
    display: flex; align-items: flex-start; gap: 12px;
    border: 1px solid #e5e7eb;
}
.verdict-ok   { background: #f0fdf4; border-color: #86efac; }
.verdict-warn { background: #fffbeb; border-color: #fcd34d; }
.verdict-bad  { background: #fef2f2; border-color: #fca5a5; }
.verdict-icon { font-size: 1.5rem; flex-shrink: 0; margin-top: 1px; }
.verdict-label { font-size: 0.68rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 2px; }
.verdict-ok   .verdict-label { color: #16a34a !important; }
.verdict-warn .verdict-label { color: #d97706 !important; }
.verdict-bad  .verdict-label { color: #dc2626 !important; }
.verdict-title { font-size: 0.95rem; font-weight: 700; margin-bottom: 3px; }
.verdict-ok   .verdict-title { color: #15803d !important; }
.verdict-warn .verdict-title { color: #92400e !important; }
.verdict-bad  .verdict-title { color: #991b1b !important; }
.verdict-desc { font-size: 0.78rem; line-height: 1.6; }
.verdict-ok   .verdict-desc { color: #166534 !important; }
.verdict-warn .verdict-desc { color: #92400e !important; }
.verdict-bad  .verdict-desc { color: #991b1b !important; }

/* ══════════════════════════════
   전환 배너
══════════════════════════════ */
.switch-banner {
    background: #fffbeb; border: 1px solid #fcd34d; border-radius: 10px;
    padding: 10px 14px; font-size: 0.8rem;
    color: #92400e !important; font-weight: 600; margin-bottom: 14px;
    display: flex; align-items: center; gap: 8px;
}

/* ══════════════════════════════
   고지 카드
══════════════════════════════ */
.duty-card {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 12px; margin-bottom: 10px;
    overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.duty-card-head {
    display: flex; align-items: center; gap: 10px;
    padding: 11px 16px; background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
}
.duty-q-badge {
    font-size: 0.68rem; font-weight: 700; background: #3b82f6;
    color: #fff !important; padding: 2px 9px; border-radius: 100px;
}
.duty-q-title { font-size: 0.86rem; font-weight: 700; color: #111827 !important; }
.duty-item { padding: 12px 16px; border-bottom: 1px solid #f3f4f6; }
.duty-item:last-child { border-bottom: none; }
.duty-disease { font-size: 0.9rem; font-weight: 700; color: #111827 !important; margin-bottom: 2px; }
.duty-code { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #9ca3af !important; margin-left: 6px; background: #f3f4f6; padding: 1px 5px; border-radius: 4px; }
.duty-meta { font-size: 0.76rem; color: #9ca3af !important; margin: 3px 0; }
.duty-reason { font-size: 0.78rem; color: #1d4ed8 !important; margin: 4px 0; font-weight: 600; padding: 4px 10px; background: #eff6ff; border-radius: 6px; border-left: 3px solid #3b82f6; }
.duty-stats-row { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 7px; }
.stat-pill { font-size: 0.7rem; background: #f3f4f6; color: #6b7280 !important; padding: 2px 8px; border-radius: 100px; font-weight: 500; border: 1px solid #e5e7eb; }
.stat-pill.red { background: #fef2f2; color: #dc2626 !important; border-color: #fecaca; }
.stat-pill.blue { background: #eff6ff; color: #1d4ed8 !important; border-color: #bfdbfe; }

/* ══════════════════════════════
   섹션 헤더
══════════════════════════════ */
.section-head {
    font-size: 0.78rem; font-weight: 700; color: #111827 !important;
    margin: 14px 0 8px; padding: 0 0 8px;
    border-bottom: 1px solid #e5e7eb;
    display: flex; align-items: center; gap: 6px;
}

/* ══════════════════════════════
   간편심사 그리드
══════════════════════════════ */
.easy-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }
.easy-box { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.easy-box-head { padding: 10px 14px; background: #f9fafb; font-size: 0.78rem; font-weight: 700; color: #111827 !important; border-bottom: 1px solid #e5e7eb; line-height: 1.5; }
.easy-item { padding: 8px 14px; font-size: 0.78rem; color: #1f2937 !important; border-bottom: 1px solid #f3f4f6; }
.easy-item:last-child { border-bottom: none; }
.easy-code { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #9ca3af !important; background: #f3f4f6; padding: 1px 5px; border-radius: 4px; margin-right: 4px; }
.easy-empty { padding: 10px 14px; font-size: 0.78rem; color: #16a34a !important; font-weight: 600; }

/* ══════════════════════════════
   빈 화면
══════════════════════════════ */
.clean-card {
    display: flex; align-items: center; gap: 12px;
    background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;
    padding: 18px 20px; font-size: 0.88rem;
    font-weight: 700; color: #15803d !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ══════════════════════════════
   보장분석
══════════════════════════════ */
.ba-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.ba-panel { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.ba-head { padding: 11px 16px; font-size: 0.78rem; font-weight: 700; border-bottom: 1px solid #f3f4f6; }
.ba-before .ba-head { background: #fffbeb; color: #92400e !important; }
.ba-after  .ba-head { background: #f0fdf4; color: #166534 !important; }
.cov-row { display: flex; align-items: center; padding: 8px 16px; border-bottom: 1px solid #f9fafb; gap: 10px; font-size: 0.8rem; }
.cov-row:last-child { border-bottom: none; }
.cov-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.cov-dot.up { background: #16a34a; }
.cov-dot.dn { background: #dc2626; }
.cov-dot.eq { background: #d1d5db; }
.cov-nm { flex: 1; color: #6b7280 !important; }
.cov-val { font-family: 'DM Mono', monospace; font-size: 0.78rem; color: #1f2937 !important; }
.cov-val.up { color: #16a34a !important; font-weight: 700; }
.cov-val.dn { color: #dc2626 !important; font-weight: 700; }

/* ══════════════════════════════
   파일 업로더
══════════════════════════════ */
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border: 1px dashed #d1d5db !important;
    border-radius: 12px !important;
    transition: all 0.15s !important;
}
[data-testid="stFileUploader"] section:hover { border-color: #3b82f6 !important; background: #eff6ff !important; }
[data-testid="stFileUploader"] *, [data-testid="stUploadedFile"] * { color: #1f2937 !important; }
[data-testid="stFileUploader"] button { background: #3b82f6 !important; border: none !important; border-radius: 8px !important; }
[data-testid="stUploadedFileData"] { padding: 4px 0 !important; }

/* ══════════════════════════════
   탭
══════════════════════════════ */
[data-testid="stTabs"] [role="tablist"] {
    background: #ffffff; border-radius: 10px; padding: 3px;
    border: 1px solid #e5e7eb; gap: 2px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
[data-testid="stTabs"] button[role="tab"] {
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 0.82rem !important; color: #6b7280 !important; padding: 6px 16px !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: #3b82f6 !important; color: #ffffff !important;
    box-shadow: 0 1px 4px rgba(59,130,246,0.3) !important;
}

/* ══════════════════════════════
   빈 업로드 안내
══════════════════════════════ */
.upload-empty {
    text-align: center; padding: 56px 20px;
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.upload-empty-icon { font-size: 2.8rem; margin-bottom: 12px; }
.upload-empty-title { font-size: 0.92rem; font-weight: 700; color: #111827 !important; margin-bottom: 5px; }
.upload-empty-desc { font-size: 0.78rem; color: #9ca3af !important; line-height: 1.6; }

/* ══════════════════════════════
   경고 배너
══════════════════════════════ */
.warn-banner {
    background: #fffbeb; border: 1px solid #fcd34d; border-radius: 10px;
    padding: 9px 14px; font-size: 0.8rem;
    color: #92400e !important; font-weight: 600; margin-bottom: 12px;
}

div[data-testid="stAlert"] { border-radius: 10px !important; }
.dataframe, .dataframe * { font-size: 0.8rem !important; color: #1f2937 !important; }
.copy-wrap { margin-bottom: 10px; }

@media (max-width: 768px) {
    .ba-grid, .easy-grid { grid-template-columns: 1fr; }
    .summary-grid { grid-template-columns: repeat(2, 1fr); }
}

/* ══════════════════════════════
   홈 히어로 섹션
══════════════════════════════ */
.home-wrap {
    min-height: calc(100vh - 56px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 24px 60px;
    background: #ffffff;
}
.home-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #eff6ff;
    color: #3b82f6 !important;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: .06em;
    padding: 5px 14px;
    border-radius: 100px;
    border: 1px solid #bfdbfe;
    margin-bottom: 28px;
}
.home-logo {
    font-size: 2.2rem;
    font-weight: 900;
    color: #111827 !important;
    letter-spacing: -.04em;
    line-height: 1;
    margin-bottom: 20px;
    text-align: center;
}
.home-logo span { color: #3b82f6 !important; }
.home-headline {
    font-size: 3.2rem;
    font-weight: 900;
    color: #111827 !important;
    letter-spacing: -.04em;
    line-height: 1.15;
    text-align: center;
    margin-bottom: 20px;
    word-break: keep-all;
}
.home-headline .hl { color: #3b82f6 !important; }
.home-sub {
    font-size: 1.05rem;
    color: #6b7280 !important;
    text-align: center;
    line-height: 1.7;
    margin-bottom: 52px;
    word-break: keep-all;
}
.home-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    width: 100%;
    max-width: 760px;
    margin-bottom: 48px;
}
.home-card {
    background: #ffffff;
    border: 1.5px solid #e5e7eb;
    border-radius: 20px;
    padding: 32px 28px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    text-align: left;
}
.home-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 8px 24px rgba(59,130,246,0.12);
    transform: translateY(-2px);
}
.home-card-icon {
    font-size: 2rem;
    margin-bottom: 16px;
    display: block;
}
.home-card-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #111827 !important;
    margin-bottom: 8px;
    letter-spacing: -.02em;
}
.home-card-desc {
    font-size: 0.82rem;
    color: #6b7280 !important;
    line-height: 1.6;
    word-break: keep-all;
}
.home-card-arrow {
    margin-top: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #3b82f6 !important;
}
.home-footer {
    font-size: 0.75rem;
    color: #d1d5db !important;
    text-align: center;
    letter-spacing: .02em;
}

/* ── 홈 카드 CTA 버튼 ── */
button[data-testid="baseButton-secondary"][kind="secondary"] {
    background: #f8faff !important;
    border: 1.5px solid #bfdbfe !important;
    border-radius: 10px !important;
    color: #3b82f6 !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
    padding: 10px 0 !important;
    box-shadow: none !important;
    transition: all 0.15s !important;
}

/* ── 네비 로고 버튼 ── */
.nav-logo-btn button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    color: #111827 !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    letter-spacing: -.02em !important;
    height: auto !important;
}
.nav-logo-btn button:hover { opacity: 0.7 !important; }

/* ── 홈일 때 배경 흰색 ── */
.page-home .stApp { background: #ffffff !important; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 상단 네비게이션 바
# ==========================================
_m = st.session_state.menu
st.markdown('<div class="topnav">', unsafe_allow_html=True)
_nc0, _nc1, _nc2, _nc3, _nsp = st.columns([1.6, 2.2, 3, 2.2, 6])
with _nc0:
    st.markdown('<div class="nav-logo-btn">', unsafe_allow_html=True)
    if st.button("SURIT", key="nav_home", use_container_width=True):
        st.session_state.menu = "home"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with _nc1:
    if st.button("🔍  알릴의무 필터", key="nav_disclosure",
                 use_container_width=True,
                 type="primary" if _m == "disclosure" else "secondary"):
        st.session_state.menu = "disclosure"
        st.rerun()
with _nc2:
    if st.button("🔄  보장분석 비포&에프터", key="nav_before_after",
                 use_container_width=True,
                 type="primary" if _m == "before_after" else "secondary"):
        st.session_state.menu = "before_after"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 상수 및 헬퍼 함수
# ==========================================
surg_keywords = ["수술","절제","시술","천자","주입","절개","적출","봉합","결찰","종양","폴립","결절","치환","이식","절단","재건","거상","관혈","제거","소작","배농","레이저","냉동"]
test_keywords = ["검사","초음파","내시경","촬영","MRI","CT","조직","생검","판독","X-RAY","X-ray","엑스레이"]
# 건강보험 요양급여내역 상병명에서 수술을 나타내는 키워드
nhis_surg_keywords = ["매복","발치","치핵","치루","충수","탈장","담석","담낭","제왕절개","루봉합","루절제","치아이식"]


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
    # 건강보험 요양급여내역 형식: YYYY.MM.DD
    m = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", date_str)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
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
if menu not in ("home", "before_after", "disclosure"):
    st.session_state.menu = "home"
    menu = "home"


# ══════════════════════════════════════════
# PAGE: 홈 (랜딩 페이지)
# ══════════════════════════════════════════
if menu == "home":
    st.markdown("""
    <div class="home-wrap">
        <div class="home-badge">🛡️ 설계사 전용 AI 플랫폼</div>
        <div class="home-logo">SUR<span>IT</span></div>
        <div class="home-headline">
            보험의 확신,<br>
            <span class="hl">슈릿</span>에서 쉽고 간편하게.
        </div>
        <div class="home-sub">
            심평원 진료 데이터를 AI가 분석해 알릴의무 항목을 자동 추출하고<br>
            기존·신규 보장을 한눈에 비교해 드립니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 4, 1])
    with col_c:
        card_col1, card_col2 = st.columns(2)
        with card_col1:
            st.markdown("""
            <div class="home-card">
                <span class="home-card-icon">🔍</span>
                <div class="home-card-title">알릴의무 필터</div>
                <div class="home-card-desc">
                    심평원 진료 PDF를 업로드하면<br>
                    AI가 고지 항목을 자동으로 추출합니다.<br>
                    건강체·간편심사 기준 모두 지원합니다.
                </div>
                <div class="home-card-arrow">시작하기 →</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("알릴의무 필터 시작", key="home_to_disclosure", use_container_width=True):
                st.session_state.menu = "disclosure"
                st.rerun()

        with card_col2:
            st.markdown("""
            <div class="home-card">
                <span class="home-card-icon">🔄</span>
                <div class="home-card-title">보장분석 비포&amp;에프터</div>
                <div class="home-card-desc">
                    기존 보장내역과 신규 제안서를 비교해<br>
                    리모델링 근거를 시각적으로 제시합니다.<br>
                    고객 설득에 바로 활용 가능합니다.
                </div>
                <div class="home-card-arrow">시작하기 →</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("보장분석 시작", key="home_to_before_after", use_container_width=True):
                st.session_state.menu = "before_after"
                st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:8px;padding-bottom:40px;">
        <span style="font-size:0.72rem;color:#d1d5db;">
            SURIT · 설계사에게 확신을 주다 · Powered by Google Gemini
        </span>
    </div>
    """, unsafe_allow_html=True)


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
                time.sleep(1)

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
        <div class="page-desc">심평원 진료 PDF를 업로드하면 AI가 고지 의무 항목을 자동으로 추출합니다.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 인라인 설정 (사이드바에서 이동) ──
    col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
    with col_s1:
        product_type = st.radio(
            "심사 기준",
            ["건강체/표준체 (일반심사)", "간편심사 (유병자 3-5-5 기준)"],
            horizontal=True,
            index=0
        )
    with col_s2:
        reference_date = st.date_input("기준일 (청약예정일)", datetime.today())
    with col_s3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

    # ── 생년월일 입력 (업로드 전에 표시) ──
    st.markdown("""
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;
                padding:14px 16px;margin-bottom:6px;">
        <div style="font-size:0.88rem;font-weight:700;color:#111827;margin-bottom:3px;">
            고객 생년월일 <span style="font-size:0.78rem;font-weight:400;color:#9ca3af;">(선택)</span>
        </div>
        <div style="font-size:0.76rem;color:#6b7280;">
            심평원 PDF에 비밀번호가 걸려있는 경우, 생년월일로 자동 해제합니다
        </div>
    </div>
    """, unsafe_allow_html=True)
    birthdate_pw = st.text_input(
        "생년월일", placeholder="예: 19900101 또는 900101",
        key="pdf_birthdate", label_visibility="collapsed"
    )

    # 업로더
    has_stored = bool(st.session_state.get("stored_pdf_files"))
    if has_stored:
        file_count = len(st.session_state["stored_pdf_files"])
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;
                    background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;
                    padding:7px 14px;margin-bottom:8px;">
            <span style="font-size:0.78rem;font-weight:700;color:#1d4ed8;">✅ 파일 {file_count}개 업로드 완료</span>
        </div>
        """, unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "심평원 자료 업로드",
        type="pdf", accept_multiple_files=True,
        label_visibility="collapsed" if has_stored else "visible"
    )

    # 새 파일 업로드 시 session_state에 bytes 저장
    if uploaded_files:
        st.session_state["stored_pdf_files"] = {
            f.name: f.read() for f in uploaded_files
        }

    # 저장된 파일로 분석 대상 결정 (상품 변경 시에도 재업로드 불필요)
    if st.session_state.get("stored_pdf_files"):
        class _PDFFile:
            def __init__(self, name, data):
                self.name = name
                self._data = data
            def read(self):
                return self._data
        active_files = [
            _PDFFile(name, data)
            for name, data in st.session_state["stored_pdf_files"].items()
        ]
    else:
        st.markdown("""
        <div class="upload-empty">
            <div class="upload-empty-icon">📂</div>
            <div class="upload-empty-title">심평원 진료자료 PDF를 업로드하세요</div>
            <div class="upload-empty-desc">건강e음(health.kr)에서 기본진료·세부진료·처방조제 3종을 발급받아 올려주세요.<br>1개만 올려도 분석 가능합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    run_btn = st.button(
        "🔍  AI 고지사항 추출", type="primary",
        use_container_width=True, key="btn_analyze"
    )

    # 심사 유형이 바뀌면 이전 분석 결과를 초기화 → 혼용 방지
    if (st.session_state.get("ai_result")
            and st.session_state.get("analysis_product_type") != product_type):
        for _k in ("ai_result", "summary_reports", "flagged_codes",
                   "prescription_end_details", "drug_change_summary",
                   "analysis_product_type", "analysis_today"):
            st.session_state.pop(_k, None)
        st.info(f"심사 기준이 **{product_type}**으로 변경되었습니다. PDF를 다시 업로드하고 분석을 실행해 주세요.")
        st.stop()

    if not run_btn and not st.session_state.get("ai_result"):
        st.stop()

    # ==========================================
    # 분석 엔진
    # ==========================================
    if run_btn:
      with st.spinner("📊 PDF 파싱 및 AI 분석 중..."):
        today = datetime(reference_date.year, reference_date.month, reference_date.day)
        st.session_state["analysis_today"] = today
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

        def parse_nhis_text(text, fname):
            """건강보험 요양급여내역 텍스트에서 진료 레코드 파싱"""
            records = []
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            # 날짜+기관 행: YYYY.MM.DD N 기관명 전화번호 금액
            date_re  = re.compile(r'^(\d{4}\.\d{2}\.\d{2})\s+\d+\s+(.+?)\s+\d{2,4}-\d{3,4}-\d{4}')
            # 방문유형 행: 외래|입원|약국 N [상병명 상병코드 금액]
            visit_re = re.compile(r'^(외래|입원|약국)\s+(\d+)\s*(.*)')
            seq_re   = re.compile(r'^\d+$')
            cur_date, cur_hospital = None, None
            i = 0
            while i < len(lines):
                line = lines[i]
                m_d = date_re.match(line)
                if m_d:
                    cur_date     = m_d.group(1)
                    cur_hospital = m_d.group(2).strip()
                    i += 1
                    continue
                if seq_re.match(line) and cur_date:
                    i += 1
                    if i < len(lines):
                        m_v = visit_re.match(lines[i])
                        if m_v:
                            in_out_v = m_v.group(1)
                            # 약국 행은 상병명/코드 없이 금액만 있어 건너뜀
                            if in_out_v == "약국":
                                i += 1
                                continue
                            days_v   = m_v.group(2)
                            rest     = m_v.group(3).strip()
                            # 상병코드 추출 (알파벳+숫자 패턴, 금액 앞)
                            parts   = rest.split()
                            code_v  = ""
                            name_v  = ""
                            for pi, p in enumerate(parts):
                                if re.match(r'^[A-Z]\d', p):
                                    code_v = p
                                    name_v = " ".join(parts[:pi])
                                    break
                            if not name_v and not code_v:
                                name_v = rest
                            if name_v or code_v:  # 유효한 레코드만 저장
                                records.append({
                                    "진료개시일": cur_date,
                                    "요양기관명": cur_hospital or "",
                                    "입내원구분": in_out_v,
                                    "요양일수":   days_v,
                                    "상병명":     name_v,
                                    "상병코드":   code_v,
                                    "_ftype":     "nhis",
                                    "_fname":     fname,
                                })
                        i += 1
                    continue
                i += 1
            return records

        def _open_pdf(data, bdate_str):
            """비밀번호 없이 시도 후 실패하면 생년월일 조합으로 재시도"""
            bd = (bdate_str or "").strip()
            candidates = [""]
            if bd:
                candidates.append(bd)
                if len(bd) == 8:
                    candidates.append(bd[2:])          # 19900101 → 900101
                elif len(bd) == 6:
                    prefix = "20" if int(bd[:2]) <= 24 else "19"
                    candidates.append(prefix + bd)     # 900101 → 19900101
            for pw in candidates:
                try:
                    return pdfplumber.open(io.BytesIO(data), password=pw)
                except Exception:
                    continue
            raise ValueError("PDF 비밀번호 해제 실패 — 생년월일을 확인해 주세요.")

        try:
         for uploaded_file in active_files:
            file_recs = []
            with _open_pdf(uploaded_file.read(), st.session_state.get("pdf_birthdate", "")) as pdf:
                # 건강보험 요양급여내역 감지
                first_text = pdf.pages[0].extract_text() or "" if pdf.pages else ""
                is_nhis = "건강보험 요양급여내역" in first_text

                if is_nhis:
                    # 텍스트 기반 파싱 (건강보험 요양급여내역 전용)
                    for page in pdf.pages:
                        page_text = page.extract_text() or ""
                        if "건강보험 요양급여내역" in page_text:
                            recs = parse_nhis_text(page_text, uploaded_file.name)
                            file_recs.extend(recs)
                            all_records.extend(recs)
                else:
                    # 기존 테이블 기반 파싱 (심평원 자료)
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
        except ValueError as _pw_err:
            st.error(f"🔒 {_pw_err}")
            st.stop()

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
            in_out   = get_val(row, ["입내원구분", "입원외래구분", "입원", "외래", "구분"])
            hospital = get_val(row, ["병·의원", "기관명", "요양기관명"])
            date_str = get_val(row, ["진료개시일", "진료시작일", "진료일", "조제일자", "처방일"])
            m_days_raw = get_val(row, ["투약일수", "요양일수"])
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
                    # 진료세부내역: 행위명칭 열에서 수술·검사 키워드 검색 (상병명 열이 아닌 행위명 열)
                    act_name = get_val(row, ["행위명칭", "행위명", "진료내역", "처치"])
                    surg_target = act_name if act_name else name_str
                    for kw in surg_keywords:
                        if kw in surg_target:
                            s["surgeries"].add(surg_target); s["surgery_dates"].add(clean_date); break
                    for kw in test_keywords:
                        if kw in surg_target:
                            s["tests_found"].add(surg_target); break
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
                elif ftype == "nhis":
                    # 건강보험 요양급여내역: 입내원구분으로 입원 직접 확정
                    if in_out == "입원":
                        s["inpatient_dates"].add(clean_date)
                    elif in_out == "약국":
                        s["has_pharma"] = True
                    else:
                        s["visit_dates"].add(clean_date)
                    # 수술: surg_keywords + 건강보험 전용 수술 상병명 키워드
                    for kw in surg_keywords + nhis_surg_keywords:
                        if kw in name_str:
                            s["surgeries"].add(name_str)
                            if clean_date: s["surgery_dates"].add(clean_date)
                            break
                    for kw in test_keywords:
                        if kw in name_str: s["tests_found"].add(name_str); break

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

        # ══════════════════════════════════════════════════════
        # [1순위] 코드 기반 결정론적 알릴의무 — disease_stats 직접 분석
        # 입원/수술/투약/코드는 AI 없이 확정 가능
        # ══════════════════════════════════════════════════════
        _d3m_dt  = today - timedelta(days=90)
        _d5y_dt  = today - timedelta(days=1825)
        _d10y_dt = today - timedelta(days=3650)

        SIMPLE_Q3_CODES = (
            "C",
            "I60","I61","I62","I63","I64",
            "I20","I21","I22",
            "I05","I06","I07","I08","I09","I34","I35","I36","I37","I38","I39",
            "K74",
        )
        HEALTH_Q5_CODES = (
            "C",
            "I10","I11","I12","I13","I14","I15",
            "I20","I21","I22",
            "I05","I06","I07","I08","I09","I34","I35","I36","I37","I38","I39",
            "I60","I61","I62","I63","I64",
            "K74",
            "E10","E11","E12","E13","E14",
            "B24",
        )

        def _code_in(code, prefixes):
            c = code.upper().strip()
            return any(c.startswith(p) for p in prefixes)

        def _dts_in_range(date_set, since_dt):
            result = []
            for d in date_set:
                try:
                    if d and datetime.strptime(d, "%Y-%m-%d") >= since_dt:
                        result.append(d)
                except ValueError:
                    pass
            return sorted(result)

        def _max_presc(med_dict, since_dt):
            return max(
                (v for d, v in med_dict.items()
                 if d and datetime.strptime(d, "%Y-%m-%d") >= since_dt),
                default=0,
            ) if med_dict else 0

        code_based_items = []  # AI flagged_item 포맷, _source="code"

        for _ck, _s in disease_stats.items():
            _dc  = (_s.get("diag_code") or _ck).strip()
            if not _dc or _dc in ("$", "해당없음"):
                continue
            _nm  = _s.get("name") or _ck
            _hp  = " / ".join(list(_s["hospitals"])[:2]) or "정보 없음"
            _med = _s["med_dates_pharma"] if _s.get("has_pharma") and _s["med_dates_pharma"] else _s["med_dates_basic"]

            def _ci(q, reason, date="", is_inp=False, inp_days=0,
                    is_surg=False, surg_name=None, med_days=0, weight="mid"):
                return {
                    "date": date or _s.get("latest_date",""),
                    "code": _dc, "disease": _nm, "hospital": _hp,
                    "duty_question": q, "reason": reason,
                    "is_inpatient": is_inp, "inpatient_days": inp_days,
                    "is_surgery": is_surg, "surgery_name": surg_name,
                    "med_days": med_days, "weight": weight, "_source": "code",
                }

            inp_3m   = _dts_in_range(_s["inpatient_dates"], _d3m_dt)
            surg_3m  = _dts_in_range(_s["surgery_dates"], _d3m_dt)
            inp_10y  = _dts_in_range(_s["inpatient_dates"], _d10y_dt)
            surg_10y = _dts_in_range(_s["surgery_dates"], _d10y_dt)
            all_5y   = _dts_in_range(_s["visit_dates"] | _s["inpatient_dates"] | _s["surgery_dates"], _d5y_dt)
            inp_5y   = _dts_in_range(_s["inpatient_dates"], _d5y_dt)
            surg_5y  = _dts_in_range(_s["surgery_dates"], _d5y_dt)
            presc_10y = _max_presc(_med, _d10y_dt)
            _sn = next(iter(_s["surgeries"]), None)
            _wt = "critical" if _code_in(_dc, ("C","I60","I61","I62","I63","I64","I21","I22","K74")) else "high" if _code_in(_dc, ("I10","I11","I12","I13","I14","I15","E10","E11","E12","E13","E14","I20")) else "mid"

            # ── 공통: Q1 입원·수술 (3개월 이내) ────────────────
            if inp_3m:
                code_based_items.append(_ci("Q1", f"3개월 이내 입원 ({len(inp_3m)}회) — 기본진료 확정",
                    date=max(inp_3m), is_inp=True, inp_days=len(inp_3m), weight=_wt))
            if surg_3m:
                code_based_items.append(_ci("Q1", f"3개월 이내 수술: {_sn or '수술'} — 세부진료 확정",
                    date=max(surg_3m), is_surg=True, surg_name=_sn, weight=_wt))

            if product_type == "간편심사 (유병자 3-5-5 기준)":
                # ── 간편 Q2: 10년 이내 입원 ─────────────────────
                if inp_10y:
                    code_based_items.append(_ci("Q2", f"10년 이내 입원 ({len(inp_10y)}회) — 기본진료 확정",
                        date=max(inp_10y), is_inp=True, inp_days=len(inp_10y), weight=_wt))
                # ── 간편 Q2: 10년 이내 수술 ─────────────────────
                if surg_10y:
                    code_based_items.append(_ci("Q2", f"10년 이내 수술: {_sn or '수술'} — 세부진료 확정",
                        date=max(surg_10y), is_inp=bool(inp_10y), inp_days=len(inp_10y),
                        is_surg=True, surg_name=_sn, weight=_wt))
                # ── 간편 Q3: 5년 이내 6대 중증질환 코드 ──────────
                if _code_in(_dc, SIMPLE_Q3_CODES) and all_5y:
                    code_based_items.append(_ci("Q3", f"5년 이내 6대 중증질환: {_nm} (코드: {_dc})",
                        date=max(all_5y), is_inp=bool(inp_5y), inp_days=len(inp_5y),
                        is_surg=bool(surg_5y), surg_name=_sn if surg_5y else None, weight="critical"))
            else:
                # ── 건강체 Q4: 10년 이내 입원 ────────────────────
                if inp_10y:
                    code_based_items.append(_ci("Q4", f"10년 이내 입원 ({len(inp_10y)}회) — 기본진료 확정",
                        date=max(inp_10y), is_inp=True, inp_days=len(inp_10y),
                        med_days=presc_10y, weight=_wt))
                # ── 건강체 Q4: 10년 이내 수술 ────────────────────
                if surg_10y:
                    code_based_items.append(_ci("Q4", f"10년 이내 수술: {_sn or '수술'} — 세부진료 확정",
                        date=max(surg_10y), is_inp=bool(inp_10y), inp_days=len(inp_10y),
                        is_surg=True, surg_name=_sn, med_days=presc_10y, weight=_wt))
                # ── 건강체 Q4: 30일이상 투약 ─────────────────────
                if presc_10y >= 30 and not inp_10y and not surg_10y:
                    src = "처방조제 확정" if _s.get("has_pharma") and _s["med_dates_pharma"] else "기본진료"
                    code_based_items.append(_ci("Q4", f"10년 이내 30일이상 투약 ({presc_10y}일) — {src}",
                        med_days=presc_10y, weight=_wt))
                # ── 건강체 Q5: 5년 이내 중증질환 코드 ───────────
                if _code_in(_dc, HEALTH_Q5_CODES) and all_5y:
                    code_based_items.append(_ci("Q5", f"5년 이내 중증질환: {_nm} (코드: {_dc})",
                        date=max(all_5y), is_inp=bool(inp_5y), inp_days=len(inp_5y),
                        is_surg=bool(surg_5y), surg_name=_sn if surg_5y else None,
                        weight="critical" if _wt=="critical" else "high"))

        # Claude API 분석
        raw_text_lines = []
        seen_code_dates = set()  # 동일 코드+날짜 중복 제거

        for _, row in df.iterrows():
            if row_is_junk(row): continue
            ftype    = str(row.get("_ftype", ""))
            date_str = get_val(row, ["진료개시일", "진료시작일", "진료일", "조제일자", "처방일"])
            code_raw = get_val(row, ["코드", "상병코드", "진단코드"])
            code_str = normalize_code(code_raw)
            name_str = get_val(row, ["상병명", "약품명", "진료내역", "행위명"])
            hospital = get_val(row, ["병·의원", "기관명", "요양기관명"])
            in_out   = get_val(row, ["입내원구분", "입원외래구분", "입원", "외래", "구분"])
            m_days   = get_val(row, ["투약일수", "요양일수"])
            cost_raw = get_val(row, ["총진료비", "진료비", "총 진료비"])

            if not date_str and not name_str: continue

            # 약국($) 단순 조제 행 → 기본진료에 투약일수 있으면 생략
            if ftype == "pharma" and not m_days:
                continue

            # 동일 코드+날짜 중복 제거 (병원·약국 중복 방지)
            # detail(진료세부내역)은 동일 코드+날짜에 여러 행위가 있으므로 행위명도 포함해 중복 제거
            if ftype == "detail":
                act_name_raw = get_val(row, ["행위명칭", "행위명", "진료내역", "처치"])
                display_name = name_str[:20]  # AI에는 질병명 전달 (코드 인식 정확도 유지)
                dedup_key = (code_str + "|" + (act_name_raw or name_str)[:15], date_str)
            else:
                display_name = name_str[:20]
                dedup_key = (code_str or name_str[:10], date_str)
            if dedup_key in seen_code_dates:
                continue
            seen_code_dates.add(dedup_key)

            # 입원 여부 압축 표시
            inpatient_flag = "입원" if "입원" in in_out else ""

            # NHIS 날짜(YYYY.MM.DD)를 YYYY-MM-DD로 정규화 (태그 파싱 호환)
            line_date = parse_date(date_str) or date_str

            # detail 타입은 행위명도 함께 전달해 AI가 수술·시술 인식 가능하게
            act_suffix = ""
            if ftype == "detail":
                _act = get_val(row, ["행위명칭", "행위명", "진료내역", "처치"])
                if _act:
                    act_suffix = f" 행위:{_act[:25]}"
            raw_text_lines.append(
                f"{line_date} [{ftype}] {code_str} {display_name}{act_suffix} {hospital[:10]}"
                + (f" 투약{m_days}일" if m_days and m_days != "0" else "")
                + (f" 진료비{cost_raw}" if cost_raw else "")
                + (f" {inpatient_flag}" if inpatient_flag else "")
            )

        today_str = today.strftime('%Y-%m-%d')
        d_3m  = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        d_1y  = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        d_5y  = (today - timedelta(days=1825)).strftime('%Y-%m-%d')
        d_10y = (today - timedelta(days=3650)).strftime('%Y-%m-%d')

        # ══════════════════════════════════════════════
        # 약 변경 감지 (간편심사 Q1 핵심 판단 로직)
        # ══════════════════════════════════════════════
        # disease_stats에서 처방조제 데이터로 약 변경 여부 판단
        drug_change_summary = []

        # 진단코드별로 3개월 이전/이내 약품명 비교
        for group_key, s in disease_stats.items():
            drugs_in_90    = s.get("drug_names_in_90", set())
            drugs_before_90 = s.get("drug_names_before_90", set())

            if not drugs_in_90 or not drugs_before_90:
                continue  # 둘 다 있어야 비교 가능

            # 약품명에서 성분명(문자)과 용량(숫자) 분리
            def extract_drug_info(name: str):
                """(성분명, 용량_mg) 튜플 반환. 용량 없으면 0"""
                dose_match = re.search(r'(\d+(?:\.\d+)?)\s*(mg|mcg|ml|g|ug|IU)', name, flags=re.IGNORECASE)
                dose = float(dose_match.group(1)) if dose_match else 0.0
                base = re.sub(r'\d+(\.\d+)?\s*(mg|mcg|ml|g|ug|IU|정|캡|앰|바이알)', '', name, flags=re.IGNORECASE).strip()
                return base, dose

            # {성분명: 용량} 딕셔너리로 변환
            info_in_90     = {extract_drug_info(d)[0]: extract_drug_info(d)[1] for d in drugs_in_90}
            info_before_90 = {extract_drug_info(d)[0]: extract_drug_info(d)[1] for d in drugs_before_90}

            norm_in_90     = set(info_in_90.keys())
            norm_before_90 = set(info_before_90.keys())

            # 3개월 이전에만 있던 약 (중단)
            stopped_drugs   = norm_before_90 - norm_in_90
            # 3개월 이내 새로 나타난 약 (추가/변경)
            new_drugs       = norm_in_90 - norm_before_90
            # 계속 유지 중인 약
            continued_drugs = norm_in_90 & norm_before_90

            # 용량 변화 감지 (동일 약 이름, 용량만 다른 경우)
            dose_increased = []  # 용량 증가 → 가입 불가
            dose_decreased = []  # 용량 감소 → 가입 가능
            for drug_name in continued_drugs:
                dose_before = info_before_90.get(drug_name, 0)
                dose_after  = info_in_90.get(drug_name, 0)
                if dose_before > 0 and dose_after > 0:
                    if dose_after > dose_before:
                        dose_increased.append(f"{drug_name} ({dose_before}→{dose_after})")
                    elif dose_after < dose_before:
                        dose_decreased.append(f"{drug_name} ({dose_before}→{dose_after})")

            # 변경 유형 판단
            has_change = bool(new_drugs or dose_increased)
            if has_change or stopped_drugs:
                if new_drugs and stopped_drugs:
                    change_type = "약 종류 변경"
                elif new_drugs:
                    change_type = "새 약 추가"
                elif dose_increased:
                    change_type = "용량 증가"
                else:
                    change_type = "약 중단"

                # 가입 불가 케이스만 drug_change_summary에 추가
                if new_drugs or dose_increased:
                    drug_change_summary.append({
                        "group":          group_key,
                        "name":           s.get("name", group_key),
                        "continued":      list(continued_drugs)[:3],
                        "stopped":        list(stopped_drugs)[:3],
                        "new":            list(new_drugs)[:3],
                        "dose_increased": dose_increased[:3],
                        "dose_decreased": dose_decreased[:3],
                        "change_type":    change_type,
                    })

        # ── [1순위] 처방조제 약 변경 → 간편 Q1 코드 확정 ──────────
        # 조건: 3개월 이전부터 복용하던 약이 3개월 이내에 변경(종류·용량 증가)된 경우
        # 해당 없음: 동일 약 계속 복용, 용량 감소, 약 중단
        if product_type == "간편심사 (유병자 3-5-5 기준)":
            for dc in drug_change_summary:
                change_type = dc["change_type"]
                new_d  = dc.get("new", [])
                inc_d  = dc.get("dose_increased", [])

                # 변경 유형별 reason 구성
                reason_parts = []
                if change_type == "약 종류 변경":
                    reason_parts.append(f"3개월 이전 약에서 신규 약으로 변경: {', '.join(new_d[:2])}")
                elif change_type == "새 약 추가":
                    reason_parts.append(f"3개월 이전부터 복용 중 새 약 추가: {', '.join(new_d[:2])}")
                elif change_type == "용량 증가":
                    reason_parts.append(f"복용 중 약 용량 증가: {', '.join(inc_d[:2])}")
                else:
                    # new_drugs와 dose_increased 모두 있는 혼합 케이스
                    if new_d:
                        reason_parts.append(f"새 약 추가: {', '.join(new_d[:2])}")
                    if inc_d:
                        reason_parts.append(f"용량 증가: {', '.join(inc_d[:2])}")

                # 해당 질환의 최근 처방 날짜 찾기
                _grp_s = disease_stats.get(dc["group"], {})
                _pm = _grp_s.get("med_dates_pharma", {}) if _grp_s else {}
                _in_3m_dates = [d for d in _pm if _dts_in_range([d], _d3m_dt)]
                _date = max(_in_3m_dates) if _in_3m_dates else ""

                code_based_items.append({
                    "date":           _date or "",
                    "code":           dc["group"] if dc["group"] else "-",
                    "disease":        dc["name"],
                    "hospital":       "처방조제내역",
                    "duty_question":  "Q1",
                    "reason":         f"3개월 이내 처방 변경 ({change_type}) — 처방조제 확정 | " + " / ".join(reason_parts),
                    "is_inpatient":   False,
                    "inpatient_days": 0,
                    "is_surgery":     False,
                    "surgery_name":   None,
                    "med_days":       0,
                    "weight":         "high",
                    "_source":        "code",
                })

        # 약 변경 요약 텍스트 생성 (AI에게 전달)
        drug_change_text = ""
        if drug_change_summary:
            drug_change_text = "\n[처방약 변경 감지 결과 — 간편심사 Q1 판단 필수 참고]\n"
            for dc in drug_change_summary:
                drug_change_text += (
                    f"- 질환: {dc['name']} / 변경유형: {dc['change_type']}\n"
                    f"  · 3개월 이전 약(중단): {', '.join(dc['stopped']) if dc['stopped'] else '없음'}\n"
                    f"  · 3개월 이내 신규약(추가/변경): {', '.join(dc['new']) if dc['new'] else '없음'}\n"
                    f"  · 용량 증가 약(가입불가): {', '.join(dc['dose_increased']) if dc['dose_increased'] else '없음'}\n"
                    f"  · 용량 감소 약(가입가능): {', '.join(dc['dose_decreased']) if dc['dose_decreased'] else '없음'}\n"
                    f"  · 계속 유지 중인 약: {', '.join(dc['continued']) if dc['continued'] else '없음'}\n"
                )
            drug_change_text += (
                "※ 가입 불가: 약 종류 변경 / 새 약 추가 / 용량 증가\n"
                "※ 가입 가능: 동일 약 지속 복용(변경 없음) / 용량 감소 / 약 중단\n"
            )

        # ══════════════════════════════════════════════
        # 처방 종료일 계산 (가입 가능 최소 날짜)
        # ══════════════════════════════════════════════
        # 원칙: 처방일 + 투약일수 = 처방 종료일. 다음날부터 가입 가능
        # 3개월 이내 처방이 있는 경우에만 의미 있음
        earliest_available_date = None
        prescription_end_details = []

        for group_key, s in disease_stats.items():
            # 처방조제 우선, 없으면 기본진료 투약일수 사용
            med_dict = s["med_dates_pharma"] if s["has_pharma"] and s["med_dates_pharma"] else s["med_dates_basic"]
            if not med_dict:
                continue

            for presc_date_str, m_days_val in med_dict.items():
                if not presc_date_str or m_days_val <= 0:
                    continue
                try:
                    presc_dt = datetime.strptime(presc_date_str, "%Y-%m-%d")
                except ValueError:
                    continue

                days_ago = (today - presc_dt).days
                if days_ago > 90:
                    continue  # 3개월 이전 처방은 제외

                # 처방 종료일 = 처방일 + 투약일수 - 1
                # 가입 가능 날짜 = 처방 종료일 + 1
                end_dt       = presc_dt + timedelta(days=m_days_val - 1)
                available_dt = end_dt + timedelta(days=1)

                prescription_end_details.append({
                    "name":       s.get("name", group_key),
                    "presc_date": presc_date_str,
                    "m_days":     m_days_val,
                    "end_date":   end_dt.strftime("%Y-%m-%d"),
                    "available":  available_dt.strftime("%Y-%m-%d"),
                    "already_ok": available_dt <= today,  # 이미 가입 가능한지
                })

                if earliest_available_date is None or available_dt > earliest_available_date:
                    earliest_available_date = available_dt

        # 처방 종료일 요약 텍스트 생성
        presc_end_text = ""
        if prescription_end_details:
            presc_end_text = "\n[3개월 이내 처방 종료일 분석 — 가입 가능 날짜 계산]\n"
            for p in prescription_end_details:
                status = "✅ 이미 복약 완료 (가입 가능)" if p["already_ok"] else f"❌ 복약 중 (가입불가 ~ {p['end_date']})"
                presc_end_text += (
                    f"- 질환: {p['name']}\n"
                    f"  처방일: {p['presc_date']} / 투약일수: {p['m_days']}일 / 종료일: {p['end_date']}\n"
                    f"  → 가입 가능 날짜: {p['available']} / 상태: {status}\n"
                )
            if earliest_available_date and earliest_available_date > today:
                presc_end_text += (
                    f"\n★ 전체 처방 기준 최소 가입 가능 날짜: {earliest_available_date.strftime('%Y-%m-%d')}\n"
                    f"  (이 날짜 이전에 청약하면 3개월 이내 투약으로 Q1 해당)\n"
                )
            elif earliest_available_date and earliest_available_date <= today:
                presc_end_text += "\n★ 3개월 이내 처방이 있으나 모두 복약 완료 상태 — 투약 관련 Q1은 면제 가능\n"

        # ── 날짜 필터링: AI에게 넘기기 전에 코드가 직접 처리 ──
        filtered_lines = []
        for line in raw_text_lines:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if not date_match:
                filtered_lines.append(line)
                continue
            line_date = date_match.group(1)
            try:
                dt = datetime.strptime(line_date, "%Y-%m-%d")
            except ValueError:
                filtered_lines.append(line)
                continue
            days_ago = (today - dt).days

            if days_ago > 3650:
                continue

            tags = []
            if days_ago <= 90:   tags.append("IN_3M")
            if days_ago <= 365:  tags.append("IN_1Y")
            if days_ago <= 1825: tags.append("IN_5Y")
            if days_ago <= 3650: tags.append("IN_10Y")

            filtered_lines.append(line + " [" + ",".join(tags) + "]")

        raw_text = "\n".join(filtered_lines[:800])

        # ── 질병코드별 통원횟수·처방일수 집계 (건강체 Q4 "계속하여 7일 이상 치료" 판단용) ──
        # 7일이상치료 기준: ① 동일 질병코드 통원횟수 7회 이상  OR  ② 단일 처방일수 7일 이상
        d_10y_dt = today - timedelta(days=3650)
        visit_count_lines = []
        for _code, _s in disease_stats.items():
            _visits_in_10y = []
            for _d in _s["visit_dates"]:
                try:
                    if datetime.strptime(_d, "%Y-%m-%d") >= d_10y_dt:
                        _visits_in_10y.append(_d)
                except ValueError:
                    pass

            # 처방일수: 처방조제 우선, 없으면 기본진료 투약일수
            _med_dict = _s["med_dates_pharma"] if _s.get("has_pharma") and _s["med_dates_pharma"] else _s["med_dates_basic"]
            _max_presc_days = 0
            for _pd, _pv in _med_dict.items():
                try:
                    if datetime.strptime(_pd, "%Y-%m-%d") >= d_10y_dt:
                        if _pv > _max_presc_days:
                            _max_presc_days = _pv
                except ValueError:
                    pass

            _name = _s.get("name", "")[:15]
            if _visits_in_10y or _max_presc_days >= 7:
                _cnt   = len(_visits_in_10y)
                _first = min(_visits_in_10y) if _visits_in_10y else "-"
                _last  = max(_visits_in_10y) if _visits_in_10y else "-"
                _presc_note = f" 최대처방{_max_presc_days}일" if _max_presc_days > 0 else ""
                visit_count_lines.append(
                    f"[통원집계] {_code} {_name} 10년내통원{_cnt}회 ({_first}~{_last}){_presc_note}"
                )
        if visit_count_lines:
            raw_text = "[10년내 질병코드별 통원횟수·처방일수 집계 — Q4 7일이상치료 판단 기준]\n" \
                       + "\n".join(visit_count_lines) + "\n\n" + raw_text

        # 약 변경 감지 결과 추가
        if drug_change_text:
            raw_text = drug_change_text + "\n" + raw_text
        # 처방 종료일 분석 결과 추가
        if presc_end_text:
            raw_text = presc_end_text + "\n" + raw_text

        if product_type == "건강체/표준체 (일반심사)":
            criteria_text = f"""
[건강체/표준체 알릴의무 4문항] (기준일: {today_str})
Q1. 최근 3개월({d_3m} 이후) — 태그 [IN_3M] 항목만: 질병확정진단 / 의심소견 / 입원·수술·추가검사 필요소견 / 치료 / 투약
Q2. 최근 3개월({d_3m} 이후) — 태그 [IN_3M] 항목만: 혈압강하제·신경안정제·수면제·각성제·진통제·마약류 상시 복용
Q3. 최근 1년({d_1y} 이후) — 태그 [IN_1Y] 항목만: 진찰 후 이상소견으로 추가검사(재검사) 받은 사실
    ★ Q3 추가검사(재검사) 정확한 정의:
       [해당 O] 진찰 결과 이상소견이 확인되어 더 정확한 진단을 위해 시행한 추가 검사
               예) X-RAY 촬영 후 이상소견 → MRI·CT·혈액검사 등 추가 시행 (당일이 아니어도 동일 질병으로 연결되면 해당)
       [해당 X — 반드시 Q3 면제] 아래 경우는 절대 Q3 배정 불가:
               - 단순 1회 검사만 시행하고 종결 (X-RAY 1회, 혈액검사 1회 등 단독 검사)
               - 이상소견 없이 단순 확인·스크리닝 목적의 검사
               - 정기검사 또는 추적관찰 (치료 없이 유지 상태에서 주기적으로 시행하는 검사)
               - 검사 후 추가 검사 없이 단순 치료로만 이어진 경우 → Q3 아닌 Q1/Q4로 판단
Q4. 최근 10년({d_10y} 이후) — 태그 [IN_10Y] 항목만:
    - 입원
    - 수술 (제왕절개 포함)
    - 계속하여 7일 이상 치료 ★ = 아래 둘 중 하나라도 해당:
        ① 동일 질병코드(KCD) 기준 통원횟수 7회 이상 ([통원집계]에서 10년내통원7회 이상인 코드)
        ② 단일 처방일수 7일 이상 ([통원집계]에서 최대처방7일 이상인 코드)
    - 계속하여 30일 이상 투약 (단일 처방 30일 이상 OR 만성질환 매월 지속 처방)
Q5. 최근 5년({d_5y} 이후) — 태그 [IN_5Y] 항목만: 아래 중증질환 확정진단만 해당
    ① 암 (악성신생물): C00~C97
    ② 백혈병: C91~C95 (암 포함)
    ③ 고혈압: I10~I15
    ④ 협심증: I20
    ⑤ 심근경색: I21~I22
    ⑥ 심장판막증: I05~I09, I34~I39
    ⑦ 간경화증: K74
    ⑧ 뇌출혈: I60~I62
    ⑨ 뇌경색: I63~I64
    ⑩ 당뇨병: E10~E14
    ⑪ 에이즈: B20~B24, Z21
    ★ Q5 면제: 위 코드 범위에 해당하지 않는 모든 질환 → Q5 배정 불가"""
        else:
            criteria_text = f"""
[간편심사(유병자 3-5-5) 알릴의무 3문항] (기준일: {today_str})
Q1. 최근 3개월({d_3m} 이후) — 태그 [IN_3M] 항목만:
    ① 질병확정진단 / 의심소견 / 추가검사필요소견 / 입원 / 수술
    ② 3개월 이전부터 복용하던 약의 변화 → 아래 기준으로 Q1 판단:
       [가입 불가 → Q1 해당]
       - 약 종류 자체가 바뀐 경우 (성분명 변경)
       - 3개월 이내 완전히 새로운 약이 추가된 경우
       - 동일 약의 용량이 증가한 경우 (예: 메트포르민 500mg → 1000mg)
       [가입 가능 → Q1 해당 아님]
       - 동일 약을 변경 없이 계속 복용 중인 경우
       - 동일 약의 용량만 감소한 경우 (예: 메트포르민 1000mg → 500mg)
       - 복용하던 약을 중단한 경우
Q2. 최근 10년({d_10y} 이후) — 태그 [IN_10Y] 항목만: 입원 또는 수술(제왕절개 포함)
Q3. 최근 5년({d_5y} 이후) — 태그 [IN_5Y] 항목만: 아래 6대 중증질환 확정진단만 해당
    ① 암: C00~C97 (악성신생물 전체)
    ② 뇌출혈: I60~I62
    ③ 뇌경색: I63~I64
    ④ 협심증: I20
    ⑤ 심근경색: I21~I22
    ⑥ 심장판막증: I05~I09, I34~I39
    ⑦ 간경화: K74

    ★ Q3 절대 면제 (아무리 심해도 Q3 배정 불가):
    - 당뇨병 (E10~E14 계열) → Q3 해당 아님, Q4만 가능
    - 고혈압 (I10~I15) → Q3 해당 아님
    - 무릎관절증·척추협착 등 근골격계 → Q3 해당 아님
    - 만성신부전·갑상선·고지혈증 등 → Q3 해당 아님
    - 위/대장 용종 → Q3 해당 아님
    - 6대 중증질환 KCD 코드가 아닌 모든 질환 → Q3 배정 절대 불가

[면제] 통원횟수 7회 미만 AND 처방일수 7일 미만인 경우 / 30일 미만 단순 투약 / 6대 중증질환 KCD 코드가 아닌 모든 질환
[약 변경 면제] 3개월 이전부터 동일 약 지속 복용(변경 없음) → 면제 / 동일 약 용량만 감소 → 면제"""

        # ── 심사 유형별 조건부 프롬프트 섹션 ──────────────────────────
        if product_type == "건강체/표준체 (일반심사)":
            step4_surgery_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━
[4단계: Q4 수술 인정 목록 — 반드시 is_surgery=true]
━━━━━━━━━━━━━━━━━━━━━━━━━━

[소화기 내시경 수술]
- K63.5/AK635 결장용종 → 대장내시경 용종절제술 ★반드시 수술
- K31/AK31 위용종 → 위내시경 용종절제술
- K92.1 혈변+내시경 지혈술 → 수술
- 위/대장 폴립, 용종 관련 진료비 30만원 이상 외래 → 수술 가능성

[치과 수술]
- K08.1/AK081 발치 → 발치술 ★반드시 수술
- K04.7/AK047 근단주위농양 절개 → 수술
- 임플란트 시술 → 수술

[안과 수술]
- H25/AH25 백내장 → 백내장 수술 (진료비 50만원 이상)
- H33/AH33 망막박리 → 망막수술
- H40/AH40 녹내장 수술

[정형/신경외과 수술]
- 척추/관절 진료비 50만원 이상 + 입원 → 수술 가능
- 골절(S계열) + 수술 키워드 → 골절 수술

[산부인과 수술]
- O84/AO84 제왕절개 → ★반드시 수술
- D25/AD25 자궁근종 절제 → 수술
- N83/AN83 난소낭종 제거 → 수술

[피부/성형외과 수술]
- L02/AL02 농양 절개배농 → 수술
- M72.66/AM7266 괴사성근막염 → 광범위절제술 ★반드시 수술 (critical)
- L84/AL84 티눈·굳은살 → 행위명에 제거술·소작·레이저·냉동 포함 시 ★반드시 수술
- 행위명에 "제거술","소작술","냉동치료","레이저절제","배농술","절개배농" 포함 → 수술
- 피부과 진료비 10만원 이상 + 절개·제거·소작 키워드 → 수술

[공통 수술 판단 규칙]
- 입원 동반 + 외과/흉부외과/성형외과/산부인과 → 수술 가능성 높음
- 진료비 총액 100만원 이상 외래 1회 → 수술 강력 의심
- 병명/진료내역에 절제·절개·봉합·이식·성형·제거·적출 포함 → 수술"""

            step5_q4_exempt_text = """
▶ Q4 반드시 면제 처리 항목:
  ① 동일 질병코드 통원횟수 6회 이하 (7회 미만), 투약 30일 미만, 입원 없음, 수술 없음
     ★ "계속하여 7일 이상 치료"는 투약일수가 아닌 통원횟수 기준 — [통원집계]에서 해당 코드 통원횟수가 7회 미만이면 반드시 면제
     ★★ 이 규칙은 정신건강의학과(F계열)·신경과 포함 모든 진료과에 동일하게 적용
        정신건강의학과 1회 방문 + 투약 30일 미만 → Q4 절대 면제 (weight=high여도 면제)
  ② 단순 감기·비염·인후염·결막염·두드러기·타박상·염좌 (통원횟수 무관하게 Q4 면제)
  ③ 치과 스케일링·단순 충치 보존치료 (발치·임플란트 제외)
  ④ 한방 단순 침구치료 (수술/입원 미동반)
  ⑤ 단순 통원 검사만 받고 종결 (수술/입원/7일이상 치료 없음)
  ⑥ 방광염·요로감염 단순 항생제 투약 (1회성)
  ⑦ 알레르기성 피부염 단순 외래 1~2회
  ⑧ 정신건강의학과·신경과·심리검사 단순 1회 방문 (통원 7회 미만, 입원 없음, 투약 30일 미만) → Q4 면제

▶ 만성질환 30일이상 투약 판단:
  - 당뇨(E11계열): 매월 지속 처방 확인 시 → med_days=365, Q4 해당 (Q3 아님)
  - 고혈압(I10계열): 매월 지속 처방 → med_days=365, Q4 해당 (Q3 아님)
  - 고지혈증(E78계열): 매월 지속 처방 → med_days=365, Q4 해당
  - 갑상선(E03/E05): 매월 지속 처방 → med_days=365, Q4 해당
  - 단, 3개월 이내에만 처방 기록이 있고 이전 기록 없음 → Q1 해당 가능"""

            json_duty_q_values = "Q1 또는 Q2 또는 Q3 또는 Q4 또는 Q5"
            json_hit_fields = """\
  "q1_hit": true또는false, "q1_reason": "사유",
  "q2_hit": true또는false, "q2_reason": "해당 약물명 또는 없음",
  "q3_hit": true또는false, "q3_reason": "사유",
  "q4_hit": true또는false, "q4_reason": "입원/수술/7일이상/30일이상 중 해당 사유",
  "q5_hit": true또는false, "q5_reason": "중증질환명 또는 없음","""
        else:  # 간편심사
            step4_surgery_text = (
                "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "[4단계: Q2 수술 인정 목록 — 반드시 is_surgery=true]\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "간편심사 Q2는 입원 또는 수술만 해당. 아래 수술 판단 기준을 적용하세요.\n\n"
                "- O84/AO84 제왕절개 → ★반드시 수술\n"
                "- K63.5/AK635 결장용종 → 대장내시경 용종절제술 = 수술\n"
                "- K08.1/AK081 발치 → 발치술 = 수술\n"
                "- H25/AH25 백내장 수술 (진료비 50만원 이상)\n"
                "- D25/AD25 자궁근종 절제, N83/AN83 난소낭종 제거 → 수술\n"
                "- M72.66/AM7266 괴사성근막염 → 광범위절제술 = 수술 (critical)\n"
                "- 병명/진료내역에 절제·절개·봉합·이식·성형·제거·적출 포함 → 수술\n"
                "- 입원 동반 + 외과/흉부외과/성형외과/산부인과 → 수술 가능성 높음\n"
                "★ 7일 이상 치료, 30일 이상 투약은 간편심사 Q2 해당 없음 (건강체 Q4 기준). Q2에 배정 금지."
            )

            step5_q4_exempt_text = (
                "\n▶ 간편심사 Q2 면제 기준:\n"
                "  - 입원 없음 AND 수술 없음 → Q2 배정 절대 불가 (단순 통원은 Q2 해당 없음)\n"
                "  - 7일 이상 치료·30일 이상 투약 만으로는 Q2 해당 없음 (건강체 Q4 기준임)"
            )

            json_duty_q_values = "Q1 또는 Q2 또는 Q3 (Q4/Q5는 절대 사용 금지)"
            json_hit_fields = (
                '  "simple_q1_hit": true또는false, "simple_q1_reason": "사유",\n'
                '  "simple_q2_hit": true또는false, "simple_q2_reason": "입원 또는 수술 상세",\n'
                '  "simple_q3_hit": true또는false, "simple_q3_disease": "6대질병명 또는 null",'
            )

        # 건강체 Q3 추가검사 기준 (5단계 조건부 삽입용)
        if product_type == "건강체/표준체 (일반심사)":
            step5_q3_health_text = (
                "\n▶ 건강체 Q3 추가검사(재검사) 판단 기준 (★핵심 규칙):\n"
                "  Q3는 '진찰 후 이상소견 → 추가 검사' 두 단계가 반드시 존재해야 함.\n\n"
                "  [Q3 해당 O — 반드시 포함]:\n"
                "  - 진찰 결과 이상소견 발견 → 더 정확한 진단을 위해 추가 검사 시행\n"
                "  - 예: 진찰 후 X-RAY → 이상소견 → MRI/CT/혈액검사/초음파 등 추가 시행\n"
                "  - 추가 검사는 당일이 아니어도 됨 (동일 질병코드로 연결된 경우)\n"
                "  - 검사 결과 이후 치료로 이어졌어도, 이상소견으로 추가 검사를 받은 사실 자체가 Q3\n\n"
                "  [Q3 해당 X — 반드시 면제]:\n"
                "  - 단순 1회 검사만 시행하고 종결 (X-RAY 1회, 혈액검사 1회, 초음파 1회 등 단독)\n"
                "  - 이상소견 없이 단순 확인·스크리닝 목적의 1회 검사\n"
                "  - 정기검사·추적관찰 (치료 없이 병증이 유지되는 상태에서 시행하는 주기적 검사)\n"
                "  - 검사 1종만 찍고 추가 검사 없이 바로 치료로 이어진 경우 → Q1 또는 Q4로만 처리\n"
                "  - 건강검진 항목으로 시행된 검사"
            )
        else:
            step5_q3_health_text = ""

        # Q3 당뇨 불가 안내 문구
        q3_diabetes_note = "(Q4만)" if product_type == "건강체/표준체 (일반심사)" else "(간편심사 해당 없음)"

        # 2단계 태그 규칙 (심사 유형별)
        is_health = product_type == "건강체/표준체 (일반심사)"
        step2_tag_rules = (
            "건강체/표준체 기준:\n"
            "- [IN_3M] 있어야만 → Q1, Q2 배정 가능\n"
            "- [IN_1Y] 있어야만 → Q3 배정 가능\n"
            "- [IN_5Y] 있어야만 → Q5 배정 가능\n"
            "- [IN_10Y] 있어야만 → Q4 배정 가능\n"
            "- [IN_3M] 없으면 → Q1/Q2 배정 절대 불가\n"
            "- [IN_10Y]만 있고 [IN_3M] 없으면 → Q4만 배정 (Q1 절대 불가)\n"
            "★ 사용 가능한 질문번호: Q1, Q2, Q3, Q4, Q5 (Q4=10년 이내 입원/수술/7일이상/30일이상, Q5=5년 이내 중증)"
        ) if is_health else (
            "간편심사 기준:\n"
            "- [IN_3M] 있어야만 → Q1 배정 가능\n"
            "- [IN_5Y] 있어야만 → Q3 배정 가능\n"
            "- [IN_10Y] 있어야만 → Q2 배정 가능\n"
            "- [IN_3M] 없으면 → Q1 배정 절대 불가\n"
            "- [IN_10Y]만 있고 [IN_3M] 없으면 → Q2만 배정 (Q1 절대 불가)\n"
            "★ 사용 가능한 질문번호: Q1, Q2, Q3 뿐. Q4/Q5는 절대 사용 금지."
        )
        # ─────────────────────────────────────────────────────────────

        system_prompt = f"""당신은 보험 언더라이팅 전문 AI입니다.
건강보험심사평가원(건강e음) 진료 데이터를 분석하여 보험 청약 시 알릴의무(고지의무) 해당 항목을 정확히 판단합니다.
판단의 정확도가 최우선입니다. 과잉 고지도, 누락도 모두 금물입니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━
[1단계: 코드 전처리]
━━━━━━━━━━━━━━━━━━━━━━━━━━
- 코드 앞 A(양방)/B(한방) 접두사 제거 (예: AK635→K63.5, AE1150→E11.50, BM179→M17.9)
- 숫자 1로 시작하는 코드 → I로 교정 (OCR 오류, 예: 1670→I67.0)
- $ 또는 해당없음 행 → 완전 제외
- COVID 검사(AZ115/AU071/AU072) · 예방접종(AZ코드) → 완전 제외

━━━━━━━━━━━━━━━━━━━━━━━━━━
[2단계: 날짜 태그 기반 질문 배정 — 절대 규칙]
━━━━━━━━━━━━━━━━━━━━━━━━━━
각 진료 데이터 끝에 붙은 태그만으로 해당 질문을 결정합니다.
태그에 없는 기간의 질문에는 절대 배정하지 마세요.
{step2_tag_rules}

{criteria_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━
[3단계: 간편심사 약 변경 판단 — 핵심 규칙]
━━━━━━━━━━━━━━━━━━━━━━━━━━
상단에 [처방약 변경 감지 결과]가 있으면 반드시 아래 기준으로 판단하세요.

▶ 간편심사 Q1 해당 (가입 불가):
  - 3개월 이전부터 복용하던 약의 종류가 변경된 경우
  - 3개월 이전에 없던 새로운 약이 3개월 이내 추가된 경우
  - 동일 약의 용량이 증가한 경우 (예: 500mg → 1000mg) ← 악화 신호
  → duty_question="Q1", reason에 구체적 변경 내용 명시

▶ 간편심사 Q1 해당 아님 (가입 가능):
  - 3개월 이전부터 동일 약을 변경 없이 계속 복용 중인 경우
  - 동일 약의 용량만 감소한 경우 (예: 1000mg → 500mg) ← 호전 신호
  - 복용하던 약이 중단된 경우 ← 호전 신호

━━━━━━━━━━━━━━━━━━━━━━━━━━
[3-1단계: 처방 종료일 기준 가입 가능 날짜 판단]
━━━━━━━━━━━━━━━━━━━━━━━━━━
상단에 [3개월 이내 처방 종료일 분석]이 있으면 반드시 아래 기준으로 판단하세요.

▶ 처방 종료일 계산 원칙:
  - 처방일 + 투약일수 = 처방 종료일 (마지막 복약일)
  - 처방 종료일 다음날 = 가입 가능 최소 날짜
  - 예: 3월 1일 처방 + 7일치 → 종료일 3월 7일 → 가입가능 3월 8일부터

▶ 3개월 이내 처방이 있는 경우 Q1 판단:
  - 복약 중(오늘 < 가입가능날짜): Q1 해당 → 가입불가, reason에 "복약 중 (가입가능날짜: YYYY-MM-DD)" 명시
  - 복약 완료(오늘 >= 가입가능날짜): Q1 해당 아님 → 투약 자체는 면제 가능
    단, 진단/소견 자체가 3개월 이내이면 Q1 해당 여부 별도 판단 필요

▶ 분석 데이터에서 "✅ 이미 복약 완료" 표시된 항목:
  - 해당 처방으로 인한 투약 Q1은 면제. 단 진단 자체가 3개월 이내면 Q1 해당 가능

▶ 분석 데이터에서 "❌ 복약 중" 표시된 항목:
  - 반드시 Q1 포함, reason에 "복약 중 — 가입 가능 날짜: [날짜]" 명시

{step4_surgery_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━
[5단계: Q3 추가검사 판단 + 면제 — 과잉 고지 방지]
━━━━━━━━━━━━━━━━━━━━━━━━━━
{step5_q3_health_text}

▶ 간편심사 Q3 절대 면제 규칙 (★최우선 적용):
  간편심사 Q3는 아래 7가지 KCD 코드 계열만 해당. 나머지는 모두 Q3 배정 절대 불가.
  허용: C00~C97(암) / I60~I62(뇌출혈) / I63~I64(뇌경색) / I20(협심증) / I21~I22(심근경색) / I05~I09·I34~I39(심장판막증) / K74(간경화)

  Q3에 절대 배정하면 안 되는 대표 질환:
  - 당뇨병 E10~E14 계열 → Q3 불가{q3_diabetes_note}
  - 고혈압 I10~I15 → Q3 불가
  - 무릎관절증 M17 / 척추협착 M48 → Q3 불가
  - 망막장애 H35 → Q3 불가
  - 위·대장 용종 K63.5 / K31 → Q3 불가
  - 메니에르 H81 / 위장출혈 K92 → Q3 불가
  - 발치 K08 / 피부질환 L98 → Q3 불가
  위 질환들이 Q3에 들어와 있으면 반드시 제거하고 올바른 질문으로 재배정하세요.

{step5_q4_exempt_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━
[6단계: weight(중요도) 배정]
━━━━━━━━━━━━━━━━━━━━━━━━━━
- critical: 암(C계열)/뇌졸중(I60-64)/심근경색(I21-22)/협심증(I20)/간경화(K74)/심장판막(I05-09,I34-39)/괴사성근막염
- high: 당뇨합병증/고혈압/신부전/간질환/정신질환/척추수술/관절치환
- mid: 용종절제/발치/단순 만성질환/30일이상 투약
- low: 단순 외래 통원/감기/염좌/치과 단순치료

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 순수 JSON:
{{
  "flagged_items": [
    {{
      "date": "YYYY-MM-DD",
      "code": "정규화된 KCD코드 (예: E11.50)",
      "disease": "질병/수술명 (한글로 명확하게)",
      "hospital": "병원명",
      "duty_question": "{json_duty_q_values}",
      "reason": "고지 판단 사유 (구체적으로, 예: 대장내시경 용종절제술=수술 해당)",
      "is_inpatient": true또는false,
      "inpatient_days": 숫자또는0,
      "is_surgery": true또는false,
      "surgery_name": "수술명 또는 null",
      "med_days": 투약일수숫자또는0,
      "weight": "critical 또는 high 또는 mid 또는 low"
    }}
  ],
  "exempt_items": [],
  {json_hit_fields}
  "drug_change_hit": true또는false, "drug_change_reason": "변경된 약 정보 또는 없음",
  "total_flagged": 숫자,
  "health_verdict": "가능 또는 조건부 또는 불가",
  "health_reason": "판단 이유 한 줄",
  "simple_verdict": "가능 또는 조건부 또는 불가",
  "simple_reason": "판단 이유 한 줄",
  "recommend": "건강체 진행 또는 간편심사 전환 권장 또는 인수 불가 가능성",
  "summary": "설계사를 위한 핵심 요약 2줄"
}}

절대 규칙: 응답은 반드시 {{ 로 시작하고 }} 로 끝나는 순수 JSON만 출력하세요.
설명, 주석, 마크다운 백틱, 전후 텍스트 일체 금지."""

        def extract_json(text: str) -> dict:
            """응답 텍스트에서 JSON 추출 — 여러 방법 시도"""
            # 1) 백틱 제거 후 바로 파싱
            cleaned = text.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(cleaned)
            except Exception:
                pass

            # 2) { 시작 ~ } 끝 구간만 추출
            start = cleaned.find("{")
            end   = cleaned.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(cleaned[start:end])
                except Exception:
                    pass

            # 3) 줄 단위로 JSON 블록 찾기
            lines = cleaned.split("\n")
            json_lines = []
            in_json = False
            brace_count = 0
            for line in lines:
                if not in_json and line.strip().startswith("{"):
                    in_json = True
                if in_json:
                    json_lines.append(line)
                    brace_count += line.count("{") - line.count("}")
                    if brace_count <= 0 and json_lines:
                        break
            if json_lines:
                try:
                    return json.loads("\n".join(json_lines))
                except Exception:
                    pass

            raise ValueError(f"JSON 추출 실패. 원문 앞 200자: {text[:200]}")

        # API 호출 (503 포함 최대 4회 재시도)
        _gemini_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        api_client = genai.Client(api_key=_gemini_key)

        ai_result = None
        last_error = None
        MAX_RETRIES = 4
        RETRY_DELAYS = [3, 6, 12, 24]  # 지수 백오프 (초)

        for attempt in range(MAX_RETRIES):
            try:
                message = api_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"고객 기준일: {today_str}\n심사 유형: {product_type}\n\n진료 데이터:\n{raw_text}",
                    config=types.GenerateContentConfig(system_instruction=system_prompt),
                )
                raw_response = message.text if message.text else ""
                if not raw_response.strip():
                    raise ValueError("AI 응답이 비어있습니다.")
                ai_result = extract_json(raw_response)
                break
            except (ValueError, json.JSONDecodeError) as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    continue
                with st.expander("🔧 디버그 (개발자용)"):
                    try:
                        st.code(raw_response[:800])
                    except Exception:
                        st.write("raw_response 없음")
                st.error(f"AI 응답 파싱 오류: {e}")
                st.stop()
            except Exception as e:
                err_str = str(e)
                # 503 UNAVAILABLE: 일시적 과부하 — 재시도
                if ("503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str) \
                        and attempt < MAX_RETRIES - 1:
                    wait = RETRY_DELAYS[attempt]
                    st.warning(f"Gemini 서버 과부하로 {wait}초 후 재시도합니다... ({attempt + 1}/{MAX_RETRIES - 1})")
                    time.sleep(wait)
                    continue
                st.error(f"Gemini API 호출 오류: {e}")
                st.stop()

        if ai_result is None:
            st.error(f"AI 분석 실패: {last_error}")
            st.stop()

        summary_reports = defaultdict(list)
        flagged_codes   = set()

        # 간편심사 Q3 허용 KCD 코드 (6대 중증질환만)
        SIMPLE_Q3_ALLOWED_PREFIXES = (
            # 암
            "C",
            # 뇌출혈
            "I60","I61","I62",
            # 뇌경색
            "I63","I64",
            # 협심증
            "I20",
            # 심근경색
            "I21","I22",
            # 심장판막증
            "I05","I06","I07","I08","I09","I34","I35","I36","I37","I38","I39",
            # 간경화
            "K74",
        )

        def is_simple_q3_allowed(code: str) -> bool:
            """간편심사 Q3 허용 코드인지 확인"""
            code = code.upper().strip()
            for prefix in SIMPLE_Q3_ALLOWED_PREFIXES:
                if code.startswith(prefix):
                    return True
            return False

        # 동일 코드 + 동일 질문번호 중복 병합
        # [1순위] 코드 기반 확정 항목을 AI 결과 앞에 주입
        merged_items = {}  # key: (code, duty_question)
        code_claimed = set()  # 코드 기반이 처리한 (code, question) — AI 중복 차단

        for item in (code_based_items + ai_result.get("flagged_items", [])):
            q_raw    = item.get("duty_question", "Q1")
            code_key = item.get("code", item.get("disease", "unknown"))

            # "Q1,Q4" 또는 "Q1/Q4" 처럼 복수 질문이 묶인 경우 분리
            q_list = [q.strip() for q in re.split(r"[,/\s]+", q_raw) if re.match(r"Q\d+", q.strip())]
            if not q_list:
                q_list = [q_raw.strip()]

            source = item.get("_source", "ai")  # "code" 또는 "ai"

            for q in q_list:
                # ── 심사 유형별 유효 질문번호 강제 필터 ──────────────
                if product_type == "간편심사 (유병자 3-5-5 기준)":
                    if q not in ("Q1", "Q2", "Q3"):
                        continue
                else:
                    if q not in ("Q1", "Q2", "Q3", "Q4", "Q5"):
                        continue

                # 간편심사 Q2: 입원 또는 수술 플래그가 없으면 제거
                if product_type == "간편심사 (유병자 3-5-5 기준)" and q == "Q2":
                    if not item.get("is_inpatient", False) and not item.get("is_surgery", False):
                        continue

                # 간편심사 Q3: 6대 중증질환 코드 외 제거
                if product_type == "간편심사 (유병자 3-5-5 기준)" and q == "Q3":
                    if not is_simple_q3_allowed(code_key):
                        continue

                merge_key = (code_key, q)

                # ── [1순위] 코드 기반 항목 ────────────────────────────
                if source == "code":
                    code_claimed.add(merge_key)
                    if merge_key not in merged_items:
                        merged_items[merge_key] = {
                            "dates":          [item.get("date", "")],
                            "code":           item.get("code", "-"),
                            "name":           item.get("disease", ""),
                            "duty_question":  q,
                            "reason":         item.get("reason", ""),
                            "is_inpatient":   item.get("is_inpatient", False),
                            "inpatient_days": item.get("inpatient_days", 0),
                            "is_surgery":     item.get("is_surgery", False),
                            "surgery_name":   item.get("surgery_name"),
                            "surgery_dates":  [item.get("date","")] if item.get("is_surgery") else [],
                            "med_days":       item.get("med_days", 0),
                            "weight":         item.get("weight", "mid"),
                            "hospitals":      [item.get("hospital", "")],
                        }
                    continue  # 코드 항목은 AI 병합 로직 건너뜀

                # ── [2순위] AI 항목 — 코드가 이미 처리한 케이스는 스킵 ──
                if merge_key in code_claimed:
                    continue

                if merge_key not in merged_items:
                    merged_items[merge_key] = {
                        "dates":          [item.get("date", "")],
                        "code":           item.get("code", "-"),
                        "name":           item.get("disease", ""),
                        "duty_question":  q,
                        "reason":         item.get("reason", ""),
                        "is_inpatient":   item.get("is_inpatient", False),
                        "inpatient_days": item.get("inpatient_days", 0),
                        "is_surgery":     item.get("is_surgery", False),
                        "surgery_name":   item.get("surgery_name"),
                        "surgery_dates":  [item.get("date","")] if item.get("is_surgery") else [],
                        "med_days":       item.get("med_days", 0),
                        "weight":         item.get("weight", "mid"),
                        "hospitals":      [item.get("hospital", "")],
                    }
                else:
                    m = merged_items[merge_key]
                    if item.get("date"):
                        m["dates"].append(item.get("date",""))
                    if item.get("is_surgery"):
                        m["is_surgery"] = True
                        if item.get("date"):
                            m["surgery_dates"].append(item.get("date",""))
                    m["inpatient_days"] += item.get("inpatient_days", 0)
                    m["med_days"] = max(m["med_days"], item.get("med_days", 0))
                    weight_order = {"critical":4,"high":3,"mid":2,"low":1}
                    if weight_order.get(item.get("weight","low"),0) > weight_order.get(m["weight"],0):
                        m["weight"] = item.get("weight","mid")
                    # 병원명 추가
                    if item.get("hospital") and item["hospital"] not in m["hospitals"]:
                        m["hospitals"].append(item["hospital"])

        # 병합된 항목을 summary_reports에 추가
        for merge_key, m in merged_items.items():
            code_key = m["code"]
            q        = m["duty_question"]
            flagged_codes.add(code_key)

            if product_type == "건강체/표준체 (일반심사)":
                q_map = {"Q1":"[1번질문] 3개월 이내 의료행위","Q2":"[2번질문] 3개월 이내 혈압강하제 등 상시 복용","Q3":"[3번질문] 1년 이내 추가검사(재검사)","Q4":"[4번질문] 10년 이내 입원/수술/7일이상치료/30일이상투약","Q5":"[5번질문] 5년 이내 중증질환"}
            else:
                q_map = {"Q1":"[간편1번질문] 3개월 이내 진단/소견","Q2":"[간편2번질문] 10년 이내 입원/수술","Q3":"[간편3번질문] 5년 이내 6대 중증 질환"}
            q_title = q_map.get(q, f"[{q}번질문]")

            dates_sorted = sorted([d for d in m["dates"] if d])
            first_date   = dates_sorted[0]  if dates_sorted else ""
            latest_date  = dates_sorted[-1] if dates_sorted else ""
            surgery_count = len(set(m["surgery_dates"])) if m["is_surgery"] else 0

            summary_reports[q_title].append({
                "first_date":     first_date,
                "latest_date":    latest_date,
                "code":           m["code"],
                "name":           m["name"],
                "visit":          len(dates_sorted),
                "med_days":       m["med_days"],
                "inpatient":      m["inpatient_days"],
                "inpatient_dates":dates_sorted if m["is_inpatient"] else [],
                "surgeries":      {m["surgery_name"]} if m["is_surgery"] and m["surgery_name"] else ({"수술"} if m["is_surgery"] else set()),
                "surgery_dates":  list(set(m["surgery_dates"])),
                "hospitals":      m["hospitals"],
                "detail":         m["reason"],
                "weight":         m["weight"],
            })

        st.session_state["ai_result"]               = ai_result
        st.session_state["summary_reports"]          = {k: list(v) for k, v in summary_reports.items()}
        st.session_state["flagged_codes"]            = flagged_codes
        st.session_state["prescription_end_details"] = prescription_end_details
        st.session_state["drug_change_summary"]      = drug_change_summary
        st.session_state["analysis_product_type"]    = product_type  # 분석 시점 심사 유형 저장


    # ==========================================
    # 결과 표시
    # ==========================================
    if not st.session_state.get("ai_result"):
        st.stop()

    # 캐시된 분석 결과 복원
    summary_reports          = defaultdict(list, st.session_state.get("summary_reports", {}))
    flagged_codes            = st.session_state.get("flagged_codes", set())
    prescription_end_details = st.session_state.get("prescription_end_details", [])
    drug_change_summary      = st.session_state.get("drug_change_summary", [])
    today                    = st.session_state.get("analysis_today", datetime.today())
    # 분석 시점 심사 유형을 기준으로 표시 — 라디오 버튼이 바뀌어도 결과가 섞이지 않게 고정
    analysis_product_type    = st.session_state.get("analysis_product_type", product_type)

    flagged_count = len(flagged_codes)
    total_q_count = len(summary_reports)

    # AI 판정 — analysis_product_type 기준으로 건강체/간편 결과 선택
    ai_res    = st.session_state.get("ai_result", {})
    verdict   = ai_res.get("health_verdict", "") if analysis_product_type == "건강체/표준체 (일반심사)" else ai_res.get("simple_verdict", "")
    reason    = ai_res.get("health_reason",  "") if analysis_product_type == "건강체/표준체 (일반심사)" else ai_res.get("simple_reason", "")
    recommend = ai_res.get("recommend", "")


    # ── 판정 세분화 ──
    # 건강체: 가능 / 조건부(부담보 최대5개 AND/OR 할증) / 불가
    # 간편심사: 가능 / 불가 (조건부 없음)
    #   10년내 입원/수술 경증질환은 회사별 최대 5개까지 인수 가능 → 별도 안내
    if analysis_product_type == "건강체/표준체 (일반심사)":
        if verdict == "가능":
            v_cls, v_icon, v_label = "verdict-ok",  "✅", "인수 가능"
            v_detail = "고지 항목 없음 또는 경미 — 표준체 진행 가능합니다."
        elif verdict == "불가":
            v_cls, v_icon, v_label = "verdict-bad", "❌", "인수 불가"
            v_detail = reason
        else:  # 조건부
            v_cls, v_icon, v_label = "verdict-warn", "⚠️", "조건부 인수 가능"
            v_detail = (
                f"{reason}<br>"
                f"<span style='color:#92400e;font-size:0.78rem;'>"
                f"※ 건강체 조건부 기준: <b>부담보 부위 최대 5개</b> AND/OR <b>할증</b> 적용 시 승인 가능"
                f"</span>"
            )
    else:  # 간편심사
        if verdict == "가능":
            v_cls, v_icon, v_label = "verdict-ok",  "✅", "인수 가능"
            v_detail = "고지 항목 없음 — 간편심사 진행 가능합니다."
        else:
            # 10년내 입원/수술 건수 파악 → 경증이면 5개까지 인수 가능 안내
            simple_q2_items = summary_reports.get("[간편2번질문] 10년 이내 입원/수술", [])
            q2_count = len(simple_q2_items)
            if verdict == "조건부" or q2_count > 0:
                v_cls, v_icon, v_label = "verdict-warn", "⚠️", "추가 확인 필요"
                v_detail = (
                    f"{reason}<br>"
                    f"<span style='color:#92400e;font-size:0.78rem;'>"
                    f"※ 간편심사: 10년 이내 입원/수술이라도 <b>경증 질환(회사별 예외목록)</b>은 "
                    f"최대 <b>5개까지</b> 인수 가능 — 인수팀에 질환 종류 확인 필요"
                    f"</span>"
                )
            else:
                v_cls, v_icon, v_label = "verdict-bad", "❌", "인수 불가"
                v_detail = reason

    # 카카오 메시지 생성 (설계 의뢰용 — 고지 병력만)
    def _kakao_item(item):
        """항목 하나를 '날짜 / 입원·통원 / 코드 / (양방)병명' 형식으로 변환"""
        fd = item["first_date"]
        ld = item["latest_date"]
        date_str_k = f"{fd} ~ {ld}" if fd and ld and fd != ld else (fd or ld or "")

        code_clean = item["code"].replace(".", "")

        hosp_list  = item["hospitals"] if isinstance(item["hospitals"], list) else list(item["hospitals"])
        hosp_str   = ", ".join(hosp_list)
        kind       = "(한방)" if any(k in hosp_str for k in ["한의원", "한방", "한의"]) else "(양방)"

        if item["inpatient"] > 0:
            visit_str = f"입원{item['inpatient']}일"
        else:
            cnt = item.get("visit", 1) or 1
            visit_str = f"통원{cnt}회"

        line1 = f"{date_str_k} / {visit_str} / {code_clean} / {kind}{item['name']}\n"

        # 두 번째 줄: 수술명 또는 핵심 사유
        if item["surgeries"]:
            surg_names = [s for s in item["surgeries"] if s and s != "수술"]
            line2 = (", ".join(surg_names) if surg_names else "수술") + "\n"
        else:
            detail_short = item["detail"][:60] if item["detail"] else ""
            line2 = f"{detail_short}\n" if detail_short else ""

        return line1 + line2 + "\n"

    kakao_msg  = f"📋 [{analysis_product_type} 고지 사항]\n"
    kakao_msg += f"■ 기준일: {today.strftime('%Y-%m-%d')}\n\n"
    if not summary_reports:
        kakao_msg += "✅ 고지 대상 없음\n"
    else:
        for q_title in sorted(summary_reports.keys()):
            clean_title = re.sub(r"^\[.*?\]\s*", "", q_title)
            kakao_msg  += f"▶ {clean_title}\n"
            items_q = summary_reports[q_title]
            # 입원 → 수술(외래) → 기타 순 정렬
            inpatient_items = [i for i in items_q if i["inpatient"] > 0]
            surgery_items   = [i for i in items_q if not i["inpatient"] > 0 and i["surgeries"]]
            other_items     = [i for i in items_q if not i["inpatient"] > 0 and not i["surgeries"]]
            if inpatient_items:
                kakao_msg += "[입원]\n"
                for item in inpatient_items:
                    kakao_msg += _kakao_item(item)
            if surgery_items:
                kakao_msg += "[수술]\n"
                for item in surgery_items:
                    kakao_msg += _kakao_item(item)
            if other_items:
                kakao_msg += "[통원]\n"
                for item in other_items:
                    kakao_msg += _kakao_item(item)
            kakao_msg += "\n"

    safe_msg = kakao_msg.replace("`","\\`").replace("\n","\\n").replace("'","\\'")

    # ── 상단 액션바: 카카오복사 | PDF ── (2컬럼)
    col_k, col_p = st.columns(2)

    with col_k:
        kakao_html = f"""
        <style>
        .ab-kakao {{
            width:100%; padding:10px 8px; border:none; border-radius:10px;
            font-family:sans-serif; font-size:0.82rem; font-weight:700;
            cursor:pointer; background:linear-gradient(135deg,#6366f1,#8b5cf6);
            color:#fff; box-shadow:0 3px 10px rgba(99,102,241,0.25);
            transition:all 0.18s;
        }}
        .ab-kakao.copied {{ background:linear-gradient(135deg,#16a34a,#15803d); }}
        </style>
        <button id="kakao-btn" class="ab-kakao" onclick="copyKakao()">💬 카카오톡 복사</button>
        <script>
        function copyKakao() {{
            const text = `{safe_msg}`;
            const btn = document.getElementById('kakao-btn');
            const ta = document.createElement('textarea');
            ta.value = text; ta.style.position='fixed'; ta.style.opacity='0';
            document.body.appendChild(ta); ta.select();
            try {{
                document.execCommand('copy');
                btn.textContent = '✅ 복사 완료!';
                btn.classList.add('copied');
                setTimeout(()=>{{ btn.textContent='💬 카카오톡 복사'; btn.classList.remove('copied'); }}, 2500);
            }} catch(e) {{}}
            document.body.removeChild(ta);
        }}
        </script>
        """
        components.html(kakao_html, height=46)

    with col_p:
        # PDF 생성
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors as rl_colors
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import io as _io, urllib.request as _urlreq, tempfile as _tmpf

            _FC = _tmpf.gettempdir()
            _FR = os.path.join(_FC,"NanumGothic.ttf"); _FB2 = os.path.join(_FC,"NanumGothicBold.ttf")
            def _fp():
                for r,b in [("/usr/share/fonts/truetype/nanum/NanumGothic.ttf","/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),("/usr/share/fonts/nanum/NanumGothic.ttf","/usr/share/fonts/nanum/NanumGothicBold.ttf"),("/Library/Fonts/NanumGothic.ttf","/Library/Fonts/NanumGothicBold.ttf")]:
                    if os.path.exists(r): return r, b if os.path.exists(b) else r
                if os.path.exists(_FR): return _FR, _FB2 if os.path.exists(_FB2) else _FR
                try:
                    _urlreq.urlretrieve("https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf",_FR)
                    _urlreq.urlretrieve("https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf",_FB2)
                    return _FR,_FB2
                except: return None,None

            @st.cache_resource(show_spinner=False)
            def _rf():
                rp,bp=_fp()
                if not rp: return "Helvetica","Helvetica-Bold"
                try:
                    if "NanumGothic" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("NanumGothic",rp))
                    if "NanumGothicBold" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("NanumGothicBold",bp))
                    return "NanumGothic","NanumGothicBold"
                except: return "Helvetica","Helvetica-Bold"

            FN2,FB2 = _rf()

            def _bp():
                buf=_io.BytesIO()
                doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=18*mm,bottomMargin=18*mm)
                pu=rl_colors.HexColor("#6366f1"); rd=rl_colors.HexColor("#dc2626"); gy=rl_colors.HexColor("#6b7280")
                lg=rl_colors.HexColor("#f4f6fb"); wh=rl_colors.white; bk=rl_colors.HexColor("#1a1a2e"); gn=rl_colors.HexColor("#16a34a")
                def S(uid,sz=10,c=bk,f=FN2,ld=14,bf=0,af=4,ind=0): return ParagraphStyle(uid,fontName=f,fontSize=sz,textColor=c,leading=ld,spaceBefore=bf,spaceAfter=af,leftIndent=ind,wordWrap='CJK')
                def TH(uid): return ParagraphStyle(uid,fontName=FB2,fontSize=8,textColor=wh,leading=11,wordWrap='CJK')
                def tv(uid,c=pu): return ParagraphStyle(uid,fontName=FB2,fontSize=14,textColor=c,leading=17,alignment=1,wordWrap='CJK')
                story=[]
                story.append(Paragraph("surit 알릴의무 고지 리포트",S("t",17,pu,FB2,21,0,4)))
                story.append(Paragraph(f"심사유형: {analysis_product_type}  |  기준일: {today.strftime('%Y-%m-%d')}  |  판정: {v_label}  |  고지질환: {flagged_count}개",S("s",8,gy,FN2,12,0,8)))
                story.append(HRFlowable(width="100%",thickness=1,color=pu,spaceAfter=5))
                vc=rd if flagged_count>0 else gn
                hdr=[Paragraph(t,TH(f"h{i}")) for i,t in enumerate(["AI 판정","고지 질환 수","해당 질문 수","심사 유형"])]
                vals=[Paragraph(v_label,tv("v0",vc)),Paragraph(str(flagged_count),tv("v1",vc)),Paragraph(str(total_q_count),tv("v2")),Paragraph(analysis_product_type[:5],tv("v3"))]
                t2=Table([hdr,vals],colWidths=["25%"]*4)
                t2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),pu),("BACKGROUND",(0,1),(-1,1),lg),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOX",(0,0),(-1,-1),0.5,rl_colors.HexColor("#e8ecf4")),("INNERGRID",(0,0),(-1,-1),0.3,rl_colors.HexColor("#e8ecf4")),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
                story.append(t2); story.append(Spacer(1,8))
                story.append(Paragraph("고지 판정 결과",S("sec",11,pu,FB2,15,6,3)))
                if not summary_reports:
                    story.append(Paragraph("고지 대상 없음",S("ok",10,gn,FB2,14,4,4)))
                else:
                    for q_title in sorted(summary_reports.keys()):
                        story.append(Paragraph(q_title,S("q",10,rd,FB2,14,6,2)))
                        rows=[[Paragraph(t,TH(f"ch{i}")) for i,t in enumerate(["질병명(코드)","기간","입원/수술","판단사유"])]]
                        for item in summary_reports[q_title]:
                            inpt=f"입원 {item['inpatient']}일" if item['inpatient']>0 else ""
                            surg=f"수술 {len(item['surgeries'])}건" if item['surgeries'] else ""
                            med=f"투약 {item['med_days']}일" if item['med_days']>0 else ""
                            etc=" / ".join(filter(None,[inpt,surg,med])) or "-"
                            rows.append([Paragraph(f"{(item['name'][:20] or '(병명미상)').replace('&','and')}\n({item['code']})",S(f"b{id(item)}",8,bk,FN2,12,0,2,4)),Paragraph(f"{item['first_date']}\n~ {item['latest_date']}",S(f"d{id(item)}",8,bk,FN2,12,0,2,4)),Paragraph(etc,S(f"m{id(item)}",8,bk,FN2,12,0,2,4)),Paragraph(item['detail'][:55].replace('&','and'),S(f"r{id(item)}",8,bk,FN2,12,0,2,4))])
                        t3=Table(rows,colWidths=["28%","20%","17%","35%"])
                        t3.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),rd),("ROWBACKGROUNDS",(0,1),(-1,-1),[wh,rl_colors.HexColor("#fff5f5")]),("BOX",(0,0),(-1,-1),0.4,rl_colors.HexColor("#fecaca")),("INNERGRID",(0,0),(-1,-1),0.3,rl_colors.HexColor("#fee2e2")),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5)]))
                        story.append(t3); story.append(Spacer(1,5))
                story.append(HRFlowable(width="100%",thickness=0.4,color=rl_colors.HexColor("#e8ecf4"),spaceBefore=8))
                story.append(Paragraph(f"surit AI 자동 생성 참고자료 | 최종 심사는 언더라이터 검토를 따릅니다. | 생성: {datetime.now().strftime('%Y-%m-%d %H:%M')}",S("foot",7,gy,FN2,10,0,0)))
                doc.build(story)
                return buf.getvalue()

            pdf_bytes = _bp()
            st.download_button("⬇️ PDF 다운로드", data=pdf_bytes,
                file_name=f"surit_고지리포트_{today.strftime('%Y%m%d')}.pdf",
                mime="application/pdf", use_container_width=True)
        except ImportError:
            st.caption("PDF: reportlab 필요")
        except Exception as e:
            st.caption(f"PDF 오류: {e}")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── 고지사항 요약 3-카드 그리드 ──
    st.markdown('<div class="section-head">📋 고지사항 요약</div>', unsafe_allow_html=True)

    if analysis_product_type == "건강체/표준체 (일반심사)":
        summary_cards = [
            {"title": "3개월", "sub": "이내 의료행위", "keys": ["[1번질문]", "[2번질문]"]},
            {"title": "1년", "sub": "이내 추가검사", "keys": ["[3번질문]"]},
            {"title": "10년", "sub": "이내 입원/수술", "keys": ["[4번질문]"]},
            {"title": "5년", "sub": "이내 중증질환", "keys": ["[5번질문]"]},
        ]
    else:
        summary_cards = [
            {"title": "3개월", "sub": "이내 진단/소견", "keys": ["[간편1번질문]"]},
            {"title": "10년", "sub": "이내 입원/수술", "keys": ["[간편2번질문]"]},
            {"title": "5년 6대 중증", "sub": "중증질환 확정진단", "keys": ["[간편3번질문]"]},
        ]

    def _card_items_html(items_in_card):
        if not items_in_card:
            return '<div class="easy-empty">✅ 해당 없음</div>'
        parts = []
        for v in items_in_card:
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
            date_range = f'{v["first_date"]} ~ {v["latest_date"]}' if v["first_date"] and v["first_date"] != v["latest_date"] else v["latest_date"]
            parts.append(f'<div class="easy-item">{code_h} {v["name"][:15]}<span style="color:#9ca3af;font-size:0.73rem;"> ({date_range})</span>{extra}</div>')
        return "".join(parts)

    card_cols = st.columns(4 if analysis_product_type == "건강체/표준체 (일반심사)" else 3)
    for col, card in zip(card_cols, summary_cards):
        items_in_card = []
        for k, v_list in summary_reports.items():
            if any(key in k for key in card["keys"]):
                items_in_card.extend(v_list)
        cnt = len(items_in_card)
        bg = "linear-gradient(135deg,#3b82f6,#2563eb)" if cnt == 0 else "linear-gradient(135deg,#ef4444,#dc2626)"
        with col:
            st.markdown(f"""
            <div class="easy-box" style="border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.10);">
                <div style="background:{bg};padding:12px 14px;">
                    <div style="font-size:1rem;font-weight:800;color:#fff;line-height:1.2;">{card['title']}</div>
                    <div style="font-size:0.68rem;color:rgba(255,255,255,0.72);margin-top:1px;">{card['sub']}</div>
                    <div style="font-size:1.8rem;font-weight:800;color:#fff;margin-top:4px;line-height:1;">{cnt}</div>
                </div>
                {_card_items_html(items_in_card)}
            </div>
            """, unsafe_allow_html=True)

    # ── 직장/항문 관련 병력 → 실손 전용 고지 안내 ──
    ANAL_RECTAL_CODES = ("K60", "K61", "K62", "K63", "K57", "K59")
    ANAL_RECTAL_NAMES = ("항문", "직장", "치루", "치핵", "치질", "항문관", "항문루", "항문직장", "치열")
    anal_rectal_items = []
    for q_title, items in summary_reports.items():
        for item in items:
            code = item.get("code", "")
            name = item.get("name", "")
            if any(code.startswith(c) for c in ANAL_RECTAL_CODES) or any(k in name for k in ANAL_RECTAL_NAMES):
                anal_rectal_items.append(item)
    if anal_rectal_items:
        names_str = ", ".join(dict.fromkeys(i["name"][:12] for i in anal_rectal_items))
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#fffbeb,#fefce8);border:1.5px solid #fde68a;
                    border-radius:12px;padding:12px 16px;margin-top:6px;margin-bottom:4px;">
            <div style="font-size:0.72rem;font-weight:700;letter-spacing:.06em;color:#92400e;margin-bottom:4px;">
                🩺 직장/항문 관련 병력 안내
            </div>
            <div style="font-size:0.83rem;font-weight:600;color:#78350f;">
                {names_str}
            </div>
            <div style="font-size:0.77rem;color:#92400e;margin-top:4px;">
                ※ 직장·항문 관련 질환은 <b>실손의료보험 가입 시에만</b> 고지 대상입니다.<br>
                일반 사망/암/건강보험 설계 시에는 고지 불필요 — 설계 매니저에게 실손 포함 여부를 확인하세요.
            </div>
        </div>
        """, unsafe_allow_html=True)

    if analysis_product_type == "건강체/표준체 (일반심사)" and flagged_count >= 5:
        st.markdown(f"""
        <div class="switch-banner" style="margin-top:10px;">
            🔄 고지 대상 질환 <b>{flagged_count}개</b> — 심사 기준을 간편심사로 변경하면 청약 가능성이 높아질 수 있습니다.
        </div>
        """, unsafe_allow_html=True)

    # 처방 종료일 배너
    if prescription_end_details:
        active_prescs    = [p for p in prescription_end_details if not p["already_ok"]]
        completed_prescs = [p for p in prescription_end_details if p["already_ok"]]
        if active_prescs:
            latest_avail = max(active_prescs, key=lambda x: x["available"])
            rows_html = "".join([
                f'<tr><td style="padding:4px 8px;font-size:0.79rem;">{p["name"]}</td>'
                f'<td style="padding:4px 8px;font-size:0.79rem;">{p["presc_date"]}</td>'
                f'<td style="padding:4px 8px;font-size:0.79rem;">{p["m_days"]}일</td>'
                f'<td style="padding:4px 8px;font-size:0.79rem;font-weight:700;color:#dc2626;">{p["end_date"]}</td>'
                f'<td style="padding:4px 8px;font-size:0.79rem;font-weight:700;color:#6366f1;">{p["available"]}</td></tr>'
                for p in active_prescs
            ])
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#fef2f2,#fff);border:1.5px solid #fca5a5;
                        border-radius:12px;padding:14px 16px;margin-bottom:10px;">
                <div style="font-size:0.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
                            color:#dc2626;margin-bottom:6px;">💊 복약 중 — 처방 종료 후 가입 가능</div>
                <div style="font-size:0.88rem;font-weight:800;color:#991b1b;margin-bottom:10px;">
                    최소 가입 가능 날짜: <span style="color:#6366f1;">{latest_avail["available"]}</span>
                </div>
                <table style="width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;">
                    <tr style="background:#fef2f2;font-size:0.72rem;font-weight:700;color:#6b7280;">
                        <td style="padding:5px 8px;">질환명</td><td style="padding:5px 8px;">처방일</td>
                        <td style="padding:5px 8px;">투약일수</td><td style="padding:5px 8px;">복약 종료일</td>
                        <td style="padding:5px 8px;">가입 가능일</td>
                    </tr>
                    {rows_html}
                </table>
                <div style="margin-top:8px;font-size:0.74rem;color:#7f1d1d;">
                    ※ 처방일 + 투약일수 = 복약 종료일. 다음날부터 해당 약 관련 Q1 면제
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif completed_prescs:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#f0fdf4,#fff);border:1px solid #86efac;
                        border-radius:12px;padding:10px 16px;margin-bottom:10px;">
                <div style="font-size:0.8rem;font-weight:700;color:#15803d;">
                    ✅ 3개월 이내 처방 {len(completed_prescs)}건 — 모두 복약 완료 (투약 관련 Q1 면제 가능)
                </div>
                <div style="font-size:0.75rem;color:#166534;margin-top:3px;">
                    단, 진단/소견 자체가 3개월 이내이면 Q1은 별도 판단됩니다.
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── 고지 판정 리포트 (한 페이지) ──
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

        if analysis_product_type == "간편심사 (유병자 3-5-5 기준)" and drug_change_summary:
            if ai_res.get("drug_change_hit"):
                drug_reason = ai_res.get("drug_change_reason", "")
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#fef2f2,#fee2e2);border:1.5px solid #fca5a5;
                            border-radius:12px;padding:12px 16px;margin-bottom:12px;">
                    <div style="font-size:0.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#dc2626;margin-bottom:4px;">
                        💊 처방약 변경 감지 — 간편심사 Q1 해당
                    </div>
                    <div style="font-size:0.84rem;font-weight:700;color:#991b1b;margin-bottom:4px;">
                        3개월 이내 처방약 변경/추가 → 가입 불가
                    </div>
                    <div style="font-size:0.79rem;color:#7f1d1d;line-height:1.7;">{drug_reason}</div>
                    <div style="margin-top:7px;font-size:0.73rem;color:#991b1b;background:#fff5f5;border-radius:8px;padding:6px 10px;">
                        ✅ 가입가능: 동일 약 지속 / 용량 감소 / 약 중단 &nbsp;|&nbsp; ❌ 가입불가: 약 종류 변경 / 새 약 추가 / 용량 증가
                    </div>
                </div>
                """, unsafe_allow_html=True)

        for q_title in sorted(summary_reports.keys()):
            items   = summary_reports[q_title]
            q_badge = re.sub(r"\].*", "]", q_title).strip("[]").strip()
            q_label = re.sub(r"^\[.*?\]\s*", "", q_title)
            full_header = f"{q_badge} {q_label}"
            st.markdown(
                f'<div class="duty-card"><div class="duty-card-head">'
                f'<span class="duty-q-title">{_html.escape(full_header)}</span>'
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
                max_med   = item["med_days"]
                med       = item["med_days"]
                pills = ""
                if med > 0:       pills += f'<span class="stat-pill">💊 투약 {med}일</span>'
                if inpatient > 0: pills += f'<span class="stat-pill red">🏥 입원 {inpatient}일</span>'
                if n_surg > 0:    pills += f'<span class="stat-pill red">🔪 수술 {n_surg}건</span>'
                if max_med >= 30: pills += f'<span class="stat-pill purple">📋 최대처방 {max_med}일</span>'
                st.markdown(
                    f'<div class="duty-item">'
                    f'  <div class="duty-disease">{name}<span class="duty-code">{code}</span></div>'
                    f'  <div class="duty-meta">📅 {fd} ~ {ld} &nbsp;·&nbsp; 🏥 {hosp}</div>'
                    f'  <div class="duty-reason">↳ {detail}</div>'
                    f'  <div class="duty-stats-row">{pills}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)


    # ── 하단 카카오 전달 미리보기 ──
    st.markdown('<div class="section-head" style="margin-top:18px;">💬 카카오톡 전달 메시지 미리보기</div>', unsafe_allow_html=True)
    with st.expander("메시지 내용 펼치기"):
        st.text(kakao_msg)