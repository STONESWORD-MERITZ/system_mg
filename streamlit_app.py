import streamlit as st
import pdfplumber
import pandas as pd
import re
from datetime import datetime, timedelta
from collections import defaultdict

# ==========================================
# 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="AdvisorHub | 보험설계사 전용 플랫폼",
    layout="wide",
    page_icon="🏛️",
    initial_sidebar_state="expanded"
)

# ── 메뉴 상태 관리 ──
if "menu" not in st.session_state:
    st.session_state.menu = "disclosure"

# ==========================================
# 디자인 시스템 (CSS)
# ==========================================
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=DM+Mono:wght@400;500&display=swap');

/* ── 기반 ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #f0f2f5 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    color: #111827 !important;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: none !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #f8fafc !important; }
[data-testid="stSidebar"] .stRadio label { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p { color: #94a3b8 !important; font-size: 0.8rem !important; }
[data-testid="stSidebar"] hr { border-color: #1e293b !important; }
[data-testid="stSidebar"] [data-testid="stDateInput"] input { background: #1e293b !important; color: #f1f5f9 !important; border: 1px solid #334155 !important; border-radius: 8px !important; }
[data-testid="stSidebar"] [data-baseweb="select"] { background: #1e293b !important; }
[data-testid="stSidebar"] caption, [data-testid="stSidebar"] small { color: #64748b !important; }

/* ── 헤더 제거 ── */
[data-testid="stHeader"] { background: transparent !important; display: none; }
#MainMenu, footer { visibility: hidden; }

/* ── 파일 업로더 ── */
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 16px !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"] section:hover { border-color: #3b82f6 !important; }
[data-testid="stFileUploader"] *, [data-testid="stUploadedFile"] * { color: #111827 !important; }
[data-testid="stFileUploader"] button {
    background: #1d4ed8 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.45rem 1.1rem !important;
}
[data-testid="stFileUploader"] button p,
[data-testid="stFileUploader"] button span { font-size: 0 !important; }
[data-testid="stFileUploader"] button span::after {
    content: '파일 선택';
    font-size: 0.9rem !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ── 탭 ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #e2e8f0;
}
[data-testid="stTabs"] button[role="tab"] {
    border-radius: 9px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    color: #64748b !important;
    padding: 0.5rem 1.1rem !important;
    transition: all 0.18s !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: #1d4ed8 !important;
    color: #ffffff !important;
}
[data-testid="stTabs"] [role="tabpanel"] { padding-top: 1.2rem !important; }

/* ── 경보 / 알림 ── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* ── 데이터프레임 ── */
.dataframe, .dataframe * { color: #111827 !important; font-size: 0.85rem !important; }

/* ─────────────────────────────────────────
   커스텀 컴포넌트
───────────────────────────────────────── */

/* 히어로 배너 */
.hero-wrap {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 50%, #2563eb 100%);
    border-radius: 20px;
    padding: 2.4rem 2.8rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute; inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.15);
    color: #bfdbfe !important;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    padding: 4px 12px; border-radius: 50px;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2rem; font-weight: 900; color: #ffffff !important;
    line-height: 1.25; margin-bottom: 0.5rem;
}
.hero-sub {
    font-size: 0.95rem; color: #bfdbfe !important;
    font-weight: 400; line-height: 1.65;
}

/* 요약 카드 그리드 */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.9rem;
    margin-bottom: 1.8rem;
}
@media (max-width: 900px) { .summary-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 500px) { .summary-grid { grid-template-columns: 1fr; } }

.stat-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.stat-card .sc-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
    color: #94a3b8 !important; margin-bottom: 0.5rem;
}
.stat-card .sc-value {
    font-size: 2rem; font-weight: 900; color: #0f172a !important;
    font-family: 'DM Mono', monospace; line-height: 1;
}
.stat-card .sc-sub {
    font-size: 0.78rem; color: #64748b !important; margin-top: 0.3rem;
}
.stat-card.danger .sc-value { color: #dc2626 !important; }
.stat-card.warn .sc-value { color: #d97706 !important; }
.stat-card.ok .sc-value { color: #16a34a !important; }

/* 고지 항목 카드 */
.duty-card {
    background: #ffffff;
    border: 1px solid #fecaca;
    border-left: 5px solid #dc2626;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(220,38,38,0.06);
}
.duty-card-head {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 0.8rem;
    flex-wrap: wrap;
}
.duty-q-badge {
    background: #fee2e2; color: #b91c1c !important;
    font-size: 0.72rem; font-weight: 800; letter-spacing: 0.04em;
    padding: 3px 9px; border-radius: 50px;
    white-space: nowrap;
}
.duty-q-title {
    font-size: 0.97rem; font-weight: 800; color: #111827 !important;
}
.duty-item {
    background: #fafafa;
    border: 1px solid #f1f5f9;
    border-radius: 9px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.6rem;
}
.duty-disease {
    font-size: 0.92rem; font-weight: 700; color: #111827 !important;
    margin-bottom: 4px;
}
.duty-code {
    font-family: 'DM Mono', monospace;
    background: #f1f5f9; color: #475569 !important;
    padding: 1px 6px; border-radius: 4px;
    font-size: 0.78rem;
}
.duty-reason {
    font-size: 0.82rem; color: #b91c1c !important;
    margin-top: 5px; line-height: 1.5;
}
.duty-stats-row {
    display: flex; gap: 16px; flex-wrap: wrap;
    margin-top: 8px; padding-top: 8px;
    border-top: 1px dashed #e2e8f0;
    font-size: 0.78rem; color: #64748b !important;
}
.stat-pill {
    display: inline-flex; align-items: center; gap: 4px;
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 50px; padding: 2px 9px;
    font-size: 0.76rem; color: #334155 !important;
}

/* 청정(통과) 카드 */
.clean-card {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 1.4rem;
    display: flex; align-items: center; gap: 12px;
    color: #166534 !important;
    font-weight: 700;
    font-size: 1rem;
}

/* 섹션 헤더 */
.section-head {
    font-size: 1rem; font-weight: 900; color: #0f172a !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.9rem;
    display: flex; align-items: center; gap: 8px;
}

/* 사이드바 로고 */
.sb-logo {
    padding: 1.4rem 1.4rem 1rem;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 1.2rem;
}
.sb-logo-title {
    font-size: 1.15rem; font-weight: 900;
    color: #f8fafc !important; letter-spacing: -0.03em;
}
.sb-logo-sub {
    font-size: 0.73rem; color: #64748b !important; margin-top: 2px;
}

/* 사이드바 섹션 레이블 */
.sb-section {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #475569 !important;
    padding: 0 1rem;
    margin: 1rem 0 0.4rem;
}

/* 간편심사 3칸 요약 박스 */
.easy-grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 0.7rem; margin-bottom: 1rem;
}
@media (max-width: 700px) { .easy-grid { grid-template-columns: 1fr; } }

.easy-box {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 0.9rem;
}
.easy-box-head {
    font-size: 0.78rem; font-weight: 800; color: #1d4ed8 !important;
    margin-bottom: 6px; border-bottom: 1px solid #f1f5f9; padding-bottom: 5px;
}
.easy-item {
    font-size: 0.8rem; color: #334155 !important;
    padding: 4px 0; border-bottom: 1px solid #f8fafc;
    line-height: 1.4;
}
.easy-item:last-child { border-bottom: none; }
.easy-code {
    font-family: 'DM Mono', monospace;
    color: #dc2626 !important; font-weight: 700; font-size: 0.76rem;
}
.easy-empty { font-size: 0.8rem; color: #94a3b8 !important; }

/* 전환 권고 배너 */
.switch-banner {
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    border: 1px solid #fcd34d;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    color: #92400e !important;
    font-weight: 700; font-size: 0.9rem;
}

/* 카톡 복사 버튼 (외부 JS 컴포넌트용) */
.kakao-btn-wrap { margin-bottom: 1.4rem; }

/* 모바일 대응 */
@media (max-width: 768px) {
    .hero-title { font-size: 1.4rem !important; }
    .hero-wrap { padding: 1.6rem 1.4rem !important; }
}

/* ═══════════ 네비게이션 메뉴 버튼 ═══════════ */
.nav-menu-btn {
    display: flex; align-items: center; gap: 10px;
    width: 100%; padding: 10px 14px;
    border-radius: 10px; border: none;
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 0.84rem; font-weight: 600;
    cursor: pointer; transition: all .18s;
    margin-bottom: 4px; text-align: left;
    background: transparent; color: #94a3b8 !important;
}
.nav-menu-btn:hover { background: rgba(255,255,255,.06); color: #e2e8f0 !important; }
.nav-menu-btn.active {
    background: rgba(59,130,246,.15);
    color: #ffffff !important;
    font-weight: 800;
}
.nav-menu-btn.active .nav-dot {
    background: #3b82f6;
}
.nav-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #334155; flex-shrink: 0;
    transition: background .18s;
}

/* ═══════════ 대시보드 홈 ═══════════ */
.welcome-wrap {
    background: linear-gradient(135deg, #0f2040 0%, #1a3260 60%, #2452a0 100%);
    border-radius: 20px; padding: 28px 32px; margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.welcome-wrap::before {
    content:''; position:absolute; right:-50px; top:-50px;
    width:220px; height:220px; border-radius:50%;
    background: radial-gradient(circle, rgba(59,130,246,.2) 0%, transparent 70%);
}
.welcome-title { font-size:1.5rem; font-weight:900; color:#ffffff !important; margin-bottom:4px; }
.welcome-sub { font-size:0.85rem; color:rgba(255,255,255,.5) !important; }
.welcome-stats-row { display:flex; gap:24px; margin-top:18px; }
.w-stat-val {
    font-family:'DM Mono',monospace; font-size:1.6rem;
    font-weight:500; color:#ffffff !important; line-height:1;
}
.w-stat-lbl { font-size:0.68rem; color:rgba(255,255,255,.4) !important; margin-top:3px; }

.home-feature-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:20px; }
.home-feature-card {
    background:#ffffff; border-radius:14px; padding:22px;
    border:1.5px solid #e2e8f0; cursor:pointer;
    transition:all .2s; position:relative; overflow:hidden;
}
.home-feature-card:hover { transform:translateY(-3px); box-shadow:0 12px 32px rgba(0,0,0,.1); border-color:#bfdbfe; }
.hfc-icon { font-size:1.8rem; margin-bottom:12px; }
.hfc-title { font-size:0.95rem; font-weight:800; color:#0f172a !important; margin-bottom:5px; }
.hfc-desc { font-size:0.77rem; color:#64748b !important; line-height:1.6; }
.hfc-tag {
    display:inline-flex; align-items:center; margin-top:10px;
    background:#f1f5f9; color:#475569 !important;
    font-size:0.68rem; font-weight:700;
    padding:3px 8px; border-radius:50px;
}

/* ═══════════ 보장분석 비포&에프터 ═══════════ */
.page-eyebrow {
    font-size:0.68rem; font-weight:700; letter-spacing:.1em;
    text-transform:uppercase; color:#3b82f6 !important; margin-bottom:5px;
}
.page-title { font-size:1.35rem; font-weight:900; color:#0f172a !important; margin-bottom:5px; letter-spacing:-.03em; }
.page-desc  { font-size:0.82rem; color:#64748b !important; line-height:1.6; margin-bottom:20px; }

.how-to-box {
    background:linear-gradient(135deg,#eef3ff,#f0f5ff);
    border:1px solid #c7d9ff; border-radius:12px;
    padding:14px 18px; margin-bottom:18px;
}
.how-to-title-sm { font-size:0.78rem; font-weight:800; color:#3b82f6 !important; margin-bottom:8px; }
.how-to-step-row { display:flex; align-items:flex-start; gap:8px; margin-bottom:5px; font-size:0.78rem; color:#475569 !important; line-height:1.5; }
.step-circle {
    width:17px; height:17px; border-radius:50%; flex-shrink:0;
    background:#3b82f6; color:#fff !important; font-size:.6rem; font-weight:900;
    display:flex; align-items:center; justify-content:center; margin-top:1px;
}

.slot-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.slot-label { font-size:0.8rem; font-weight:700; color:#475569 !important; }
.slot-btn-wrap { display:flex; gap:5px; }
.slot-btn {
    width:32px; height:32px; border-radius:7px;
    font-size:.78rem; font-weight:700;
    background:#f1f5f9; color:#64748b !important;
    border:1.5px solid transparent; cursor:pointer; transition:all .15s;
}
.slot-btn:hover { background:#e2e8f0; }
.slot-btn.active-slot { background:#0f2040; color:#ffffff !important; border-color:#0f2040; }

.upload-cards-grid { display:grid; gap:12px; margin-bottom:18px; }
.upload-item-card {
    border:2px dashed #cbd5e1; border-radius:12px;
    padding:20px 14px; text-align:center;
    background:#f8fafc; cursor:pointer; transition:all .2s;
    position:relative;
}
.upload-item-card:hover { border-color:#3b82f6; background:#f0f5ff; }
.upload-item-card.required-card { border-color:#3b82f6; background:#f4f8ff; }
.uc-chip {
    position:absolute; top:8px; left:8px;
    font-size:.62rem; font-weight:800; padding:2px 7px; border-radius:50px;
}
.uc-chip.req-chip { background:#0f2040; color:#ffffff !important; }
.uc-chip.opt-chip { background:#e2e8f0; color:#475569 !important; }
.uc-em { font-size:1.6rem; margin-bottom:6px; }
.uc-ttl { font-size:.8rem; font-weight:700; color:#334155 !important; margin-bottom:3px; }
.uc-sub { font-size:.7rem; color:#94a3b8 !important; }

/* 결과 헤더 */
.result-header-box {
    background:linear-gradient(135deg,#0a1628,#1a3260);
    border-radius:16px; padding:20px 24px; margin-bottom:18px;
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:14px;
}
.rh-title { font-size:1rem; font-weight:900; color:#ffffff !important; margin-bottom:2px; }
.rh-sub { font-size:.75rem; color:rgba(255,255,255,.4) !important; }
.rh-kpi-row { display:flex; gap:20px; }
.rh-kpi-val {
    font-family:'DM Mono',monospace; font-size:1.3rem; font-weight:500; line-height:1;
}
.rh-kpi-val.kpi-up   { color:#10b981 !important; }
.rh-kpi-val.kpi-down { color:#ef4444 !important; }
.rh-kpi-val.kpi-neu  { color:rgba(255,255,255,.7) !important; }
.rh-kpi-lbl { font-size:.62rem; color:rgba(255,255,255,.35) !important; margin-top:2px; }

/* 인사이트 */
.insight-box {
    background:#f8fafc; border:1px solid #e2e8f0;
    border-radius:12px; padding:14px 18px; margin-bottom:16px;
}
.insight-title-sm { font-size:.8rem; font-weight:800; color:#334155 !important; margin-bottom:8px; }
.insight-row { display:flex; align-items:flex-start; gap:7px; font-size:.78rem; color:#475569 !important; line-height:1.5; margin-bottom:5px; }
.ins-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; margin-top:5px; }
.ins-dot.g { background:#10b981; } .ins-dot.a { background:#f59e0b; } .ins-dot.r { background:#ef4444; }

/* 비포애프터 패널 */
.ba-panels { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:18px; }
.ba-panel { background:#ffffff; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,.05); overflow:hidden; }
.ba-panel-head {
    padding:11px 15px; font-size:.78rem; font-weight:800;
    display:flex; align-items:center; gap:6px; border-bottom:1px solid #f1f5f9;
}
.ba-before .ba-panel-head { background:#fff8f0; color:#92400e !important; }
.ba-after  .ba-panel-head { background:#f0fdf4; color:#166534 !important; }
.cov-line {
    display:flex; align-items:center; padding:9px 15px;
    border-bottom:1px solid #f8fafc; gap:9px; font-size:.8rem;
}
.cov-line:last-child { border-bottom:none; }
.cov-icon { width:19px; height:19px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:.6rem; font-weight:900; flex-shrink:0; }
.cov-icon.ok  { background:#d1fae5; color:#10b981 !important; }
.cov-icon.bad { background:#fee2e2; color:#ef4444 !important; }
.cov-icon.new { background:#fef3c7; color:#92400e !important; }
.cov-nm { flex:1; color:#334155 !important; font-weight:500; }
.cov-val { font-family:'DM Mono',monospace; font-size:.78rem; color:#0f172a !important; }
.cov-val.up  { color:#10b981 !important; font-weight:700; }
.cov-val.dn  { color:#ef4444 !important; font-weight:700; }
.cov-val.na  { color:#cbd5e1 !important; }
.diff-tag {
    font-family:'DM Mono',monospace; font-size:.65rem; font-weight:700;
    padding:1px 5px; border-radius:4px; white-space:nowrap;
}
.diff-tag.up { background:#d1fae5; color:#10b981 !important; }
.diff-tag.dn { background:#fee2e2; color:#ef4444 !important; }
.diff-tag.nw { background:#fef3c7; color:#92400e !important; }

/* ═══════════ 제안서 비교 ═══════════ */
.proposal-cards-row { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:18px; }
.proposal-item-card {
    border:1.5px dashed #cbd5e1; border-radius:12px;
    padding:18px 14px; text-align:center;
    background:#f8fafc; cursor:pointer; transition:all .2s;
}
.proposal-item-card:hover { border-color:#3b82f6; background:#f0f5ff; }
.proposal-item-card.filled-card { border-style:solid; border-color:#93c5fd; background:#f0f5ff; }
.pc-num-badge {
    width:22px; height:22px; border-radius:50%;
    background:#e2e8f0; color:#475569 !important;
    font-size:.7rem; font-weight:800;
    display:flex; align-items:center; justify-content:center; margin:0 auto 7px;
}
.filled-card .pc-num-badge { background:#0f2040; color:#ffffff !important; }
.pc-em { font-size:1.5rem; margin-bottom:5px; }
.pc-lbl { font-size:.78rem; font-weight:700; color:#334155 !important; margin-bottom:3px; }
.pc-sublbl { font-size:.68rem; color:#94a3b8 !important; }

.compare-tbl { width:100%; border-collapse:collapse; font-size:.8rem; }
.compare-tbl th {
    padding:10px 13px; background:#0a1628; color:#ffffff !important;
    font-size:.73rem; font-weight:700; text-align:left;
}
.compare-tbl th:first-child { border-radius:8px 0 0 0; }
.compare-tbl th:last-child  { border-radius:0 8px 0 0; }
.compare-tbl td { padding:9px 13px; border-bottom:1px solid #f1f5f9; color:#334155 !important; vertical-align:middle; }
.compare-tbl tr:last-child td { border-bottom:none; }
.compare-tbl tr:nth-child(even) td { background:#f8fafc; }
.best-badge {
    display:inline-flex; align-items:center; gap:3px;
    background:#d1fae5; color:#166534 !important;
    font-size:.65rem; font-weight:800; padding:2px 6px; border-radius:4px;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)


# ==========================================
# 사이드바 — 네비게이션 + 설정
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            <div style="width:30px;height:30px;border-radius:8px;background:linear-gradient(135deg,#3b82f6,#f59e0b);display:flex;align-items:center;justify-content:center;font-size:15px;">🏛</div>
            <span class="sb-logo-title">AdvisorHub</span>
        </div>
        <div class="sb-logo-sub">보험설계사 전용 분석 플랫폼</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">핵심 기능</div>', unsafe_allow_html=True)

    # 메뉴 버튼들
    menus = [
        ("home",        "🏠", "홈 대시보드"),
        ("before_after","🔄", "보장분석 비포&에프터"),
        ("proposal",    "📊", "제안서 비교"),
        ("disclosure",  "🔍", "알릴의무 필터"),
    ]
    for key, icon, label in menus:
        is_active = st.session_state.menu == key
        btn_class = "nav-menu-btn active" if is_active else "nav-menu-btn"
        if st.button(
            "{} {}".format(icon, label),
            key="nav_{}".format(key),
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.menu = key
            st.rerun()

    st.divider()

    st.markdown('<div class="sb-section">분석 필터</div>', unsafe_allow_html=True)

    # 1. 보장분석 필터
    with st.expander("🔄 보장분석 비포&에프터 필터", expanded=True):
        ba_filter = st.multiselect(
            "분석 강조 항목",
            ["암/질병", "뇌/심장", "실손/의료비", "수술/입원", "사망/장해"],
            default=["암/질병", "뇌/심장", "실손/의료비"]
        )
        ba_view_type = st.selectbox("비교 방식", ["전체 항목 비교", "차이점만 보기", "상세 보장금액 중심"])

    # 2. 알릴의무 필터
    with st.expander("🔍 알릴의무 필터", expanded=True):
        product_type = st.radio(
            "심사 기준",
            ["건강체/표준체 (일반심사)", "간편심사 (유병자 3-5-5 기준)"],
            index=0
        )
        reference_date = st.date_input("기준일 (청약예정일)", datetime.today())
        st.caption("※ 기준일 변경 시 고지 소멸일이 시뮬레이션됩니다.")

    st.divider()

    # 도움말/기준 정보 (선택된 심사 기준에 따라 가변 표시)
    if product_type == "건강체/표준체 (일반심사)":
        st.markdown("""
        <div style="font-size:0.75rem; color:#94a3b8; line-height:1.5;">
        <b>📋 표준체 고지 기준</b><br>
        • 3개월: 진찰·검사·치료·입원·수술·투약<br>
        • 5년: 입원/수술/7일↑치료/30일↑투약<br>
        • 5년: 11대 중증 질환
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="font-size:0.75rem; color:#94a3b8; line-height:1.5;">
        <b>📋 간편심사(3-5-5) 기준</b><br>
        • 3개월: 입원/수술/추가검사 소견<br>
        • 5년: 입원/수술 이력<br>
        • 5년: 6대 중증 질환
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# 상수 정의
# ==========================================
disease_12_list = ["C","D0","I10","I11","I12","I13","I14","I15","I20","I21","I22",
                   "I05","I06","I07","I08","I09","I34","I35","I36","I37","I38",
                   "K703","K74","I60","I61","I62","I63","I64",
                   "E10","E11","E12","E13","E14","B20","B21","B22","B23","B24",
                   "K60","K61","K62","K64"]
disease_6_list  = ["C","D0","I60","I61","I62","I63","I20","I21","I22",
                   "I05","I06","I07","I08","I09","I34","I35","I36","I37","I38","K703","K74"]

disease_12_names = ["암","악성","백혈병","고혈압","협심증","심근경색","심장판막","간경화","간경변",
                    "뇌출혈","뇌경색","당뇨","에이즈","HIV","치핵","치루","치열","항문","직장"]
disease_6_names  = ["암","악성","백혈병","뇌출혈","뇌경색","심근경색","협심증","심장판막","간경화","간경변"]

surg_keywords = ["수술","절제","시술","천자","주입","절개","적출","봉합","결찰","종양","폴립","결절"]
test_keywords = ["검사","초음파","내시경","촬영","MRI","CT","조직","생검","판독","X-RAY","X-ray","엑스레이"]


# ==========================================
# 헬퍼 함수
# ==========================================
def get_val(row, possible_keys):
    """컬럼 키워드로 값 탐색"""
    for k in row.keys():
        if any(pk in str(k) for pk in possible_keys):
            val = row[k]
            return str(val).strip() if pd.notna(val) else ""
    return ""


def normalize_code(raw: str) -> str:
    """
    심평원 코드 정규화:
      1) 양방(A) / 한방(B) 접두사 제거
      2) 숫자 1로 시작 → I 로 교정
      3) $ / 빈 값 → 빈 문자열
    """
    code = raw.upper().strip()
    if not code or code == "$":
        return ""
    # 양방/한방 접두사 제거 (A로 시작하는 진짜 C코드는 그대로)
    if len(code) >= 2 and code[0] in ("A", "B") and code[1].isdigit():
        code = code[1:]
    # 스캔 OCR 오류: 'I(아이)' → '1(일)' 혼동
    if code and code[0] == "1" and len(code) >= 3:
        candidate = "I" + code[1:]
        # 뒤 두 글자가 숫자면 ICD 코드로 확정
        if candidate[1:3].isdigit():
            code = candidate
    return code


def format_code(code: str) -> str:
    """ICD-10 표준 포맷: I671 → I67.1"""
    c = code.strip()
    if len(c) >= 4 and c[0].isalpha() and c[1:3].isdigit() and "." not in c:
        return c[:3] + "." + c[3:]
    return c if re.match(r"^[A-Z]", c) else "-"


def parse_date(date_str: str) -> str:
    """날짜 문자열 → YYYY-MM-DD (실패 시 '')"""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_str)
    if m:
        return m.group()
    m = re.search(r"(\d{8})", date_str)
    if m:
        d = m.group()
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return ""


def row_is_junk(row) -> bool:
    """$ 더미 행 / 해당없음 행 필터"""
    combined = "".join(str(v) for v in row.values).replace(" ", "")
    return "$" in combined or "해당없음" in combined


# ==========================================
# 페이지 라우터
# ==========================================
menu = st.session_state.menu

# ══════════════════════════════════════════
# PAGE: 홈 대시보드
# ══════════════════════════════════════════
if menu == "home":
    st.markdown("""
    <div class="welcome-wrap">
        <div class="welcome-title">설계사님, 좋은 하루입니다 👋</div>
        <div class="welcome-sub">오늘도 AdvisorHub와 함께 효율적인 영업 하세요!</div>
        <div class="welcome-stats-row">
            <div><div class="w-stat-val">0</div><div class="w-stat-lbl">이번 달 분석</div></div>
            <div><div class="w-stat-val">3</div><div class="w-stat-lbl">핵심 기능</div></div>
            <div><div class="w-stat-val">0</div><div class="w-stat-lbl">미확인 알림</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-head">🚀 핵심 기능 바로가기</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="home-feature-grid">
        <div class="home-feature-card">
            <div class="hfc-icon">🔄</div>
            <div class="hfc-title">보장분석 비포 &amp; 에프터</div>
            <div class="hfc-desc">기존 보장과 신규 제안서를 나란히 비교하여 고객에게 명확한 리모델링 근거를 제시하세요.</div>
            <div class="hfc-tag">✨ 핵심 기능</div>
        </div>
        <div class="home-feature-card">
            <div class="hfc-icon">📊</div>
            <div class="hfc-title">제안서 비교</div>
            <div class="hfc-desc">여러 보험사 제안서를 한눈에 비교하여 최적의 상품을 추천해 드립니다.</div>
            <div class="hfc-tag">📁 PDF 비교</div>
        </div>
        <div class="home-feature-card">
            <div class="hfc-icon">🔍</div>
            <div class="hfc-title">알릴의무 필터</div>
            <div class="hfc-desc">심평원 진료 PDF를 업로드하면 AI가 고지 의무 항목을 자동으로 분석합니다.</div>
            <div class="hfc-tag">🤖 AI 자동분석</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("👈 왼쪽 사이드바에서 원하는 기능을 선택하세요.")

# ══════════════════════════════════════════
# PAGE: 보장분석 비포&에프터
# ══════════════════════════════════════════
elif menu == "before_after":
    st.markdown("""
    <div class="page-eyebrow">🔄 AI 보장 분석</div>
    <div class="page-title">보장분석 비포 &amp; 에프터</div>
    <div class="page-desc">기존 보장 내역과 신규 제안서를 비교하여 최적의 보장 리모델링 결과를 확인하세요.<br>
    설계사가 고객 앞에서 바로 펼쳐 보여줄 수 있는 심플한 비교 결과를 제공합니다.</div>
    """, unsafe_allow_html=True)

    # ── 업로드 섹션 ──
    st.markdown("""
    <div class="how-to-box">
        <div class="how-to-title-sm">📖 사용 방법</div>
        <div class="how-to-step-row"><div class="step-circle">1</div>기존 보장분석 PDF (필수) 를 업로드하세요.</div>
        <div class="how-to-step-row"><div class="step-circle">2</div>비교할 신규 제안서 PDF를 1개 이상 업로드하세요.</div>
        <div class="how-to-step-row"><div class="step-circle">3</div>AI가 보장 항목별 개선·축소·신규 항목을 색상으로 강조 표시합니다.</div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("**📋 기존 보장분석 PDF** <span style='color:#ef4444;'>*필수*</span>", unsafe_allow_html=True)
        before_file = st.file_uploader("기존 보장분석", type="pdf", key="ba_before", label_visibility="collapsed")
    with col_right:
        st.markdown("**📄 신규 제안서 PDF** (최대 4개)", unsafe_allow_html=True)
        after_files = st.file_uploader("신규 제안서", type="pdf", key="ba_after",
                                       accept_multiple_files=True, label_visibility="collapsed")

    analyze_ba = st.button("🤖 AI 보장 비교 분석 시작", type="primary", use_container_width=True, key="btn_ba")

    if analyze_ba and before_file:
        with st.spinner("📊 보장 항목 분석 중..."):
            import time; time.sleep(1.2)  # 실제 분석 로직 자리

        # ── 결과 헤더 ──
        st.markdown("""
        <div class="result-header-box">
            <div>
                <div class="rh-title">📊 보장 리모델링 분석 결과</div>
                <div class="rh-sub">기존 보장 vs 신규 제안서 비교 · AI 자동 추출</div>
            </div>
            <div class="rh-kpi-row">
                <div style="text-align:center;">
                    <div class="rh-kpi-val kpi-up">+8</div>
                    <div class="rh-kpi-lbl">개선 항목</div>
                </div>
                <div style="text-align:center;">
                    <div class="rh-kpi-val kpi-down">-2</div>
                    <div class="rh-kpi-lbl">축소 항목</div>
                </div>
                <div style="text-align:center;">
                    <div class="rh-kpi-val kpi-neu">+3 NEW</div>
                    <div class="rh-kpi-lbl">신규 추가</div>
                </div>
                <div style="text-align:center;">
                    <div class="rh-kpi-val kpi-neu">+1.4만</div>
                    <div class="rh-kpi-lbl">월 보험료 차</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── AI 인사이트 ──
        st.markdown("""
        <div class="insight-box">
            <div class="insight-title-sm">💡 설계사 전달 포인트 (AI 요약)</div>
            <div class="insight-row"><div class="ins-dot g"></div>
                <span>암 진단금이 <strong>3,000만원 → 5,000만원</strong>으로 크게 개선됩니다. 현재 암 발병률 고려 시 매우 유리한 조건입니다.</span></div>
            <div class="insight-row"><div class="ins-dot a"></div>
                <span>실손의료비 자기부담금이 20%로 변경됩니다. 기존 구실손 유지 여부를 고객과 함께 검토해 보세요.</span></div>
            <div class="insight-row"><div class="ins-dot r"></div>
                <span>뇌졸중 진단금이 <strong>2,000만원 → 1,000만원</strong>으로 축소됩니다. 추가 특약 검토를 권장합니다.</span></div>
        </div>
        """, unsafe_allow_html=True)

        # ── 비포/에프터 2단 비교 ──
        st.markdown("""
        <div class="ba-panels">
          <div class="ba-panel ba-before">
            <div class="ba-panel-head">📋 기존 보장 (BEFORE)</div>
            <div class="cov-line"><div class="cov-icon bad">✕</div><div class="cov-nm">암 진단금</div><div class="cov-val dn">3,000만원</div></div>
            <div class="cov-line"><div class="cov-icon ok">✓</div><div class="cov-nm">뇌졸중 진단금</div><div class="cov-val">2,000만원</div></div>
            <div class="cov-line"><div class="cov-icon ok">✓</div><div class="cov-nm">심근경색 진단금</div><div class="cov-val">2,000만원</div></div>
            <div class="cov-line"><div class="cov-icon ok">✓</div><div class="cov-nm">실손의료비</div><div class="cov-val">구실손 (5%)</div></div>
            <div class="cov-line"><div class="cov-icon bad">✕</div><div class="cov-nm">수술비</div><div class="cov-val na">미가입</div></div>
            <div class="cov-line"><div class="cov-icon ok">✓</div><div class="cov-nm">입원일당</div><div class="cov-val">3만원/일</div></div>
            <div class="cov-line"><div class="cov-icon bad">✕</div><div class="cov-nm">간병인 지원</div><div class="cov-val na">미가입</div></div>
            <div class="cov-line"><div class="cov-icon bad">✕</div><div class="cov-nm">치아 보존치료</div><div class="cov-val na">미가입</div></div>
            <div class="cov-line" style="background:#f8fafc;font-weight:800;">
                <div class="cov-nm" style="color:#475569!important;">월 보험료</div>
                <div class="cov-val" style="font-size:.95rem;font-family:'DM Mono',monospace;">114,000원</div>
            </div>
          </div>
          <div class="ba-panel ba-after">
            <div class="ba-panel-head">✨ 신규 제안 (AFTER)</div>
            <div class="cov-line"><div class="cov-icon ok">✓</div><div class="cov-nm">암 진단금 <span class="diff-tag up">▲ +2,000만</span></div><div class="cov-val up">5,000만원</div></div>
            <div class="cov-line"><div class="cov-icon bad">!</div><div class="cov-nm">뇌졸중 진단금 <span class="diff-tag dn">▼ -1,000만</span></div><div class="cov-val dn">1,000만원</div></div>
            <div class="cov-line"><div class="cov-icon ok">✓</div><div class="cov-nm">심근경색 진단금</div><div class="cov-val">2,000만원</div></div>
            <div class="cov-line"><div class="cov-icon ok">✓</div><div class="cov-nm">실손의료비 <span class="diff-tag dn">자부담 20%</span></div><div class="cov-val">4세대 실손</div></div>
            <div class="cov-line"><div class="cov-icon new">+</div><div class="cov-nm">수술비 <span class="diff-tag nw">NEW</span></div><div class="cov-val up">100만원/회</div></div>
            <div class="cov-line"><div class="cov-icon ok">✓</div><div class="cov-nm">입원일당 <span class="diff-tag up">▲ +2만</span></div><div class="cov-val up">5만원/일</div></div>
            <div class="cov-line"><div class="cov-icon new">+</div><div class="cov-nm">간병인 지원 <span class="diff-tag nw">NEW</span></div><div class="cov-val up">5만원/일</div></div>
            <div class="cov-line"><div class="cov-icon new">+</div><div class="cov-nm">치아 보존치료 <span class="diff-tag nw">NEW</span></div><div class="cov-val up">연 60만원</div></div>
            <div class="cov-line" style="background:#f0fdf4;font-weight:800;">
                <div class="cov-nm" style="color:#475569!important;">월 보험료</div>
                <div class="cov-val" style="font-size:.95rem;font-family:'DM Mono',monospace;color:#0f172a!important;">128,000원 <span style="font-size:.72rem;color:#64748b;font-weight:400;">(+14,000원)</span></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.button("💬 카톡으로 고객 전달", use_container_width=True, type="primary")
        with col_b:
            st.button("📥 PDF 저장", use_container_width=True)
        with col_c:
            st.button("↺ 다시 분석", use_container_width=True)

    elif analyze_ba and not before_file:
        st.warning("⚠️ 기존 보장분석 PDF를 먼저 업로드해 주세요.")
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:#94a3b8;">
            <div style="font-size:2.5rem;margin-bottom:10px;">🔄</div>
            <div style="font-weight:700;margin-bottom:4px;">파일을 업로드하고 분석을 시작하세요</div>
            <div style="font-size:0.8rem;">기존 보장분석 PDF와 신규 제안서 PDF를 업로드하면 AI가 자동으로 비교합니다.</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# PAGE: 제안서 비교
# ══════════════════════════════════════════
elif menu == "proposal":
    st.markdown("""
    <div class="page-eyebrow">📊 AI 제안서 비교</div>
    <div class="page-title">제안서 비교</div>
    <div class="page-desc">여러 보험사 제안서를 업로드하면 AI가 핵심 보장 항목을 자동으로 추출하여 비교합니다.<br>
    항목별 최고 조건에 자동으로 Best 마크가 표시됩니다.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="how-to-box">
        <div class="how-to-title-sm">📖 사용 방법</div>
        <div class="how-to-step-row"><div class="step-circle">1</div>비교할 보험사 제안서 PDF를 2~4개 업로드하세요.</div>
        <div class="how-to-step-row"><div class="step-circle">2</div>AI가 보장 항목·보험료·특약을 자동으로 추출합니다.</div>
        <div class="how-to-step-row"><div class="step-circle">3</div>항목별 최고 조건에 👑 Best가 자동 표시됩니다.</div>
    </div>
    """, unsafe_allow_html=True)

    proposal_files = st.file_uploader(
        "보험사 제안서 PDF (2~4개)",
        type="pdf",
        accept_multiple_files=True,
        key="proposal_files",
        label_visibility="collapsed"
    )

    n_files = len(proposal_files) if proposal_files else 0
    st.caption("업로드된 파일: {}개{}".format(
        n_files, " (분석 준비 완료)" if n_files >= 2 else " (최소 2개 필요)"))

    analyze_prop = st.button(
        "🤖 AI 제안서 비교 분석",
        type="primary", use_container_width=True, key="btn_prop",
        disabled=(n_files < 2)
    )

    if analyze_prop and proposal_files and len(proposal_files) >= 2:
        with st.spinner("📊 제안서 보장 항목 추출 중..."):
            import time; time.sleep(1.0)

        st.markdown("""
        <div style="background:linear-gradient(135deg,#0a1628,#1a3260);border-radius:14px;padding:16px 22px;margin-bottom:16px;">
            <div style="font-size:.95rem;font-weight:900;color:#fff!important;margin-bottom:2px;">📊 제안서 비교 결과</div>
            <div style="font-size:.75rem;color:rgba(255,255,255,.4)!important;">{}개 제안서 분석 완료 · AI 자동 추출</div>
        </div>
        """.format(len(proposal_files)), unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-head">📊 보장 항목 비교표</div>', unsafe_allow_html=True)

        # 동적으로 파일 이름 기반 헤더 생성
        file_names = [f.name[:12] for f in proposal_files[:4]]
        header_html = "<tr><th style='width:150px;'>보장 항목</th>"
        for fn in file_names:
            header_html += "<th>{}</th>".format(fn)
        header_html += "</tr>"

        st.markdown("""
        <div style="overflow-x:auto;">
        <table class="compare-tbl">
          <thead>{}</thead>
          <tbody>
            <tr>
              <td><strong>암 진단금</strong></td>
              <td><span class="best-badge">👑 Best</span> 5,000만원</td>
              {}
            </tr>
            <tr>
              <td><strong>뇌졸중 진단금</strong></td>
              <td>1,500만원</td>
              {}
            </tr>
            <tr>
              <td><strong>심근경색 진단금</strong></td>
              <td>1,500만원</td>
              {}
            </tr>
            <tr>
              <td><strong>실손의료비</strong></td>
              <td><span class="best-badge">👑 Best</span> 4세대</td>
              {}
            </tr>
            <tr style="background:#f0f4ff;">
              <td><strong>💰 월 보험료</strong></td>
              <td style="font-weight:800;color:#1e3a8a!important;">128,000원</td>
              {}
            </tr>
          </tbody>
        </table>
        </div>
        """.format(
            header_html,
            "".join(["<td>3,000만원</td>" for _ in file_names[1:]]),
            "".join(["<td><span class='best-badge'>👑 Best</span> 2,000만원</td>" if i==0 else "<td>2,000만원</td>" for i in range(len(file_names)-1)]),
            "".join(["<td>2,000만원</td>" for _ in file_names[1:]]),
            "".join(["<td>4세대</td>" for _ in file_names[1:]]),
            "".join(["<td style='font-weight:800;color:#1e3a8a!important;'>{}원</td>".format(112000 + i*8000) for i in range(len(file_names)-1)]),
        ), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.button("💬 카톡으로 고객 전달", use_container_width=True, type="primary", key="prop_kakao")
        with col_b:
            st.button("📥 PDF 저장", use_container_width=True, key="prop_pdf")
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:#94a3b8;">
            <div style="font-size:2.5rem;margin-bottom:10px;">📊</div>
            <div style="font-weight:700;margin-bottom:4px;">제안서 PDF를 2개 이상 업로드하세요</div>
            <div style="font-size:0.8rem;">여러 보험사의 제안서를 동시에 업로드하면 AI가 자동으로 비교합니다.</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# PAGE: 알릴의무 필터 (기존 로직 전체 유지)
# ══════════════════════════════════════════
elif menu == "disclosure":
    st.markdown("""
    <div class="page-eyebrow">🔍 AI 고지 분석</div>
    <div class="page-title">알릴의무 필터</div>
    <div class="page-desc">심평원 진료 PDF를 업로드하면 AI가 파일 유형을 자동 구분하고 누적 투약일수·통원일수를 합산하여<br>
    청약서 고지 의무 질문에 정확히 매칭해 드립니다.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="how-to-box">
        <div class="how-to-title-sm">📖 사용 방법</div>
        <div class="how-to-step-row"><div class="step-circle">1</div>심평원 '내 진료정보 열람'에서 기본진료·세부진료·처방조제 PDF 3종을 발급받으세요.</div>
        <div class="how-to-step-row"><div class="step-circle">2</div>3종 모두 업로드 시 정확도가 높아집니다. (1개도 분석 가능)</div>
        <div class="how-to-step-row"><div class="step-circle">3</div>AI가 파일 유형을 자동으로 구분하여 고지 항목을 추출합니다.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-head">📎 심평원 진료자료 업로드</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "기본진료, 세부진료, 처방조제 등 PDF 파일을 올려주세요.",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if not uploaded_files:
        st.info("⬆️  PDF 파일을 업로드하면 분석이 시작됩니다.")
        st.stop()

    # ==========================================
    # 핵심 분석 엔진 (단일 패스 통합)
    # ==========================================
    with st.spinner("📊 문서 파싱 및 누적 일수 연산 중..."):
        today = datetime(reference_date.year, reference_date.month, reference_date.day)

        all_records = []
        file_dataframes = {}

        # ══════════════════════════════════════════════════
        # Step 1: 파일 유형 감지 + PDF 파싱
        # ══════════════════════════════════════════════════
        # 파일 유형별 추출 대상
        #  기본진료  → 진단코드, 입원여부, 내원일수, 병원명 (진찰/검사 행위 파악)
        #  세부진료  → 처치·수술명 (수술 여부 파악)
        #  처방조제  → 약품명, 투약일수 (투약 기간 파악)
        # ══════════════════════════════════════════════════

        def detect_file_type(headers):
            """헤더 컬럼명으로 파일 유형 반환: 'basic' | 'detail' | 'pharma' | 'unknown'"""
            h_joined = " ".join(str(h) for h in headers)
            if any(k in h_joined for k in ["상병명", "상병코드", "진단코드", "내원일수"]):
                return "basic"    # 기본진료
            if any(k in h_joined for k in ["진료내역", "행위명", "처치", "수술"]):
                return "detail"   # 세부진료
            if any(k in h_joined for k in ["약품명", "투약일수", "조제"]):
                return "pharma"   # 처방조제
            # 컬럼 구분이 불명확하면 전체 활용
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
                            str(h).replace("\n", "").replace(" ", "") if h else "col_{}".format(i)
                            for i, h in enumerate(raw_headers)
                        ]
                        ftype = detect_file_type(headers)
                        for row in table[1:]:
                            if not any(row):
                                continue
                            if "순번" in str(row[0]):
                                continue
                            rec = {
                                h: str(v).replace("\n", " ").strip() if v else ""
                                for h, v in zip(headers, row)
                            }
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

        # ══════════════════════════════════════════════════
        # Step 2: 파일 유형별 단일 패스 집계
        #
        # [중복 방지 원칙]
        #  - 통원일수 : visit_dates (set) → 날짜 기준 중복 제거
        #  - 투약일수 : med_dates {날짜: 최대값} → 같은 날 여러 약은 MAX 1회만
        #              처방조제 파일이 있으면 처방조제만 사용, 없으면 기본진료 사용
        #  - 입원일수 : inpatient_dates (set) → 날짜 기준 중복 제거 후 합산
        # ══════════════════════════════════════════════════

        def new_disease():
            return {
                "visit_dates":         set(),   # 외래 방문일 (중복 제거)
                # 투약: {날짜: 해당 날 최대 투약일수} — 같은 날 여러 행은 MAX
                "med_dates_basic":     {},      # 기본진료에서 수집
                "med_dates_pharma":    {},      # 처방조제에서 수집 (우선)
                "drug_names_in_90":    set(),   # 90일 이내 약품명
                "drug_names_before_90":set(),   # 90일 초과 약품명
                "tests_found":         set(),
                "inpatient_dates":     set(),   # 입원 날짜 set (중복 제거)
                "surgeries":           set(),   # 수술명
                "surgery_dates":       set(),
                "hospitals":           set(),
                "first_date":          "2099-12-31",
                "latest_date":         "2000-01-01",
                "diag_code":           "",      # 확정 진단코드
                "name":                "",
                "has_pharma":          False,   # 처방조제 파일 존재 여부
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

            v_days_raw = get_val(row, ["내원일수", "진료일수"])
            m_days_raw = get_val(row, ["투약일수"])
            v_days = int(re.findall(r"\d+", v_days_raw)[0]) if re.findall(r"\d+", v_days_raw) else 0
            m_days = int(re.findall(r"\d+", m_days_raw)[0]) if re.findall(r"\d+", m_days_raw) else 0

            # 그룹 키: 진단코드 우선 (처방조제는 코드 없으므로 병명 키)
            if ftype == "pharma":
                # 처방조제: 병명 없이 약품명만 있음 → 코드 없이 약품명 기반 집계 불필요
                # 투약일수는 기본진료의 진단코드 그룹에 합산
                # → 처방조제 행은 별도 pharma_records로만 저장
                pass
            group_key = code_str if code_str else name_str[:15]
            if not group_key:
                continue

            clean_date = parse_date(date_str)
            s = disease_stats[group_key]

            # 진단코드 저장
            if code_str and not s["diag_code"]:
                s["diag_code"] = code_str

            if clean_date:
                dt       = datetime.strptime(clean_date, "%Y-%m-%d")
                days_ago = (today - dt).days

                # ── 기본진료: 통원/입원 + 투약일수(보조) ──
                if ftype in ("basic", "unknown"):
                    is_inpatient = "입원" in in_out or "입원" in name_str
                    if is_inpatient:
                        s["inpatient_dates"].add(clean_date)
                    else:
                        s["visit_dates"].add(clean_date)
                    # 기본진료 투약(처방조제 없을 때 사용)
                    if m_days > 0:
                        prev = s["med_dates_basic"].get(clean_date, 0)
                        if m_days > prev:
                            s["med_dates_basic"][clean_date] = m_days

                # ── 세부진료: 수술·검사 키워드 ──
                elif ftype == "detail":
                    for kw in surg_keywords:
                        if kw in name_str:
                            s["surgeries"].add(name_str)
                            s["surgery_dates"].add(clean_date)
                            break
                    for kw in test_keywords:
                        if kw in name_str:
                            s["tests_found"].add(name_str)
                            break

                # ── 처방조제: 투약일수(최우선) + 약품 변경 감지 ──
                elif ftype == "pharma":
                    s["has_pharma"] = True
                    if m_days > 0:
                        prev = s["med_dates_pharma"].get(clean_date, 0)
                        if m_days > prev:
                            s["med_dates_pharma"][clean_date] = m_days
                    # 약품명 변경 감지용
                    drug = name_str.strip()
                    if drug:
                        if days_ago <= 90:
                            s["drug_names_in_90"].add(drug)
                        else:
                            s["drug_names_before_90"].add(drug)

                # unknown: 기본진료 방식으로 처리 (위 basic 분기에서 이미 처리됨)

                if clean_date > s["latest_date"]:
                    s["latest_date"] = clean_date
                if clean_date < s["first_date"]:
                    s["first_date"] = clean_date

            # 병원명 (약국 제외, 세부/기본에서만)
            if hospital and "약국" not in hospital and ftype != "pharma":
                s["hospitals"].add(hospital)

            # 세부진료가 아닌 경우에도 수술/검사 키워드 보조 체크 (unknown 대비)
            if ftype in ("basic", "unknown"):
                for kw in surg_keywords:
                    if kw in name_str:
                        s["surgeries"].add(name_str)
                        if clean_date:
                            s["surgery_dates"].add(clean_date)
                        break
                for kw in test_keywords:
                    if kw in name_str:
                        s["tests_found"].add(name_str)
                        break

            if name_str and not s["name"]:
                s["name"] = name_str

        # ══════════════════════════════════════════════════
        # Step 3: 고지 룰 매칭
        #
        # [정확한 기준 적용]
        # 건강체 1번 : 3개월 이내 진찰/검사/치료/입원/수술/투약
        # 건강체 2번 : 3개월 이내 혈압강하제 등 상시 복용 (처방조제 파일 약품명으로 판단)
        # 건강체 4번 : 5년 이내 입원/수술/계속 7일↑ 치료/계속 30일↑ 투약
        #              ※ '계속하여' = 동일 원인 치료 시작~완료일 연속 일수
        # 건강체 5번 : 5년 이내 11대 질병 (암/백혈병/고혈압/협심증/심근경색/심장판막/
        #              간경화/뇌졸중/당뇨/에이즈/직장항문)
        #
        # 간편 1번 : 3개월 이내 질병확정진단/의심소견/입원소견/수술소견/추가검사소견
        # 간편 2번 : 10년 이내 입원/수술
        # 간편 3번 : 5년 이내 6대 질병
        # ══════════════════════════════════════════════════
        summary_reports = defaultdict(list)
        flagged_codes   = set()

        # 혈압약 키워드 (건강체 2번)
        bp_drug_keywords = ["혈압", "암로디핀", "로사르탄", "발사르탄", "텔미사르탄",
                            "올메사르탄", "칸데사르탄", "이르베사르탄", "아테놀롤",
                            "비소프롤롤", "메토프롤롤", "카르베딜롤", "인다파미드",
                            "히드로클로로티아지드", "푸로세미드", "스피로노락톤",
                            "신경안정제", "수면제", "진통제", "마약"]

        for key, s in disease_stats.items():
            if s["latest_date"] == "2000-01-01":
                continue

            # ── 투약일수 결정: 처방조제 우선, 없으면 기본진료 ──
            med_dates = s["med_dates_pharma"] if s["has_pharma"] and s["med_dates_pharma"] \
                        else s["med_dates_basic"]

            # ── 통원일수: visit_dates(set) 크기 = 중복 제거된 외래 방문 횟수 ──
            visit_count    = len(s["visit_dates"])
            inpatient_count = len(s["inpatient_dates"])  # 입원 일수 (날짜 기준)
            total_visit    = visit_count + inpatient_count

            # ── 투약: '계속하여 30일' = 단일 처방 중 최대 투약일수 ──
            #  (심평원 데이터는 1회 처방 = 1행 → 행의 투약일수가 연속 처방 기간)
            max_single_med  = max(med_dates.values()) if med_dates else 0
            total_med_days  = sum(med_dates.values())   # 전체 합산 (참고용)

            latest_d   = datetime.strptime(s["latest_date"], "%Y-%m-%d")
            first_d    = datetime.strptime(s["first_date"],  "%Y-%m-%d")

            # 투약 종료 추정: 최종 방문일 + 그 날 투약일수
            latest_med  = med_dates.get(s["latest_date"], 0)
            treat_end   = latest_d + timedelta(days=latest_med)

            days_from_treat_end = (today - treat_end).days
            days_from_latest    = (today - latest_d).days
            days_from_first     = (today - first_d).days

            reasons = []

            # ═══════════════════════════════
            # 건강체/표준체
            # ═══════════════════════════════
            if product_type == "건강체/표준체 (일반심사)":

                # [1번] 3개월 이내 의료행위 (투약 종료 기준)
                if days_from_treat_end <= 90:
                    reasons.append((
                        "[1번 질문] 3개월 이내 의료행위",
                        "투약 종료 추정일 {} 기준 90일 미경과 (진찰/치료/투약 포함)".format(
                            treat_end.strftime('%Y-%m-%d'))
                    ))

                # [2번] 3개월 이내 혈압강하제·신경안정제 등 상시 복용
                if days_from_latest <= 90:
                    drug_match = [d for d in s["drug_names_in_90"]
                                  if any(k in d for k in bp_drug_keywords)]
                    if drug_match:
                        reasons.append((
                            "[2번 질문] 3개월 이내 혈압강하제 등 상시 복용",
                            "해당 약품 발견: {}".format(", ".join(drug_match[:2])[:50])
                        ))

                # [4번] 5년 이내 입원/수술/계속 7일 이상 치료/계속 30일 이상 투약
                within_5y = days_from_treat_end <= 1825
                if within_5y:
                    if inpatient_count > 0:
                        d_range = ""
                        if s["inpatient_dates"]:
                            sorted_d = sorted(s["inpatient_dates"])
                            d_range = " ({} ~ {})".format(sorted_d[0], sorted_d[-1])
                        reasons.append((
                            "[4번 질문] 5년 이내 입원",
                            "입원 {}일{}".format(inpatient_count, d_range)
                        ))
                    if s["surgeries"]:
                        surg_sample = list(s["surgeries"])[:2]
                        reasons.append((
                            "[4번 질문] 5년 이내 수술",
                            "수술/시술 이력: {}".format(", ".join(surg_sample)[:50])
                        ))
                    # '계속하여 7일 이상 치료' = 통원 횟수 기준 (방문일 수)
                    if total_visit >= 7:
                        reasons.append((
                            "[4번 질문] 5년 이내 계속하여 7일 이상 치료",
                            "누적 진료일수 {}일 (통원 {}회 + 입원 {}일)".format(
                                total_visit, visit_count, inpatient_count)
                        ))
                    # '계속하여 30일 이상 투약' = 단일 처방 최대값으로 판단
                    if max_single_med >= 30:
                        reasons.append((
                            "[4번 질문] 5년 이내 계속하여 30일 이상 투약",
                            "단일 처방 최대 {}일 투약 (전체 합계 {}일)".format(
                                max_single_med, total_med_days)
                        ))

                # [5번] 5년 이내 11대 질병
                if within_5y:
                    is_11 = (any(key.startswith(c) for c in disease_12_list) or
                             any(n in s["name"] for n in disease_12_names))
                    if is_11:
                        reasons.append((
                            "[5번 질문] 5년 이내 11대 질병",
                            "11대 질환 코드/병명 매칭 ({} / {})".format(key, s['name'][:20])
                        ))

            # ═══════════════════════════════
            # 간편심사
            # ═══════════════════════════════
            else:
                # [간편 1번] 3개월 이내 질병확정진단·의심소견·입원/수술/추가검사 소견
                if days_from_latest <= 90:
                    subs = []
                    if days_from_first <= 90:
                        subs.append("질병 확정진단")
                    if inpatient_count > 0:
                        subs.append("입원 소견")
                    if s["surgeries"]:
                        subs.append("수술 소견")
                    if s["tests_found"]:
                        subs.append("추가검사 소견")
                    if subs:
                        reasons.append((
                            "[간편 1번] 3개월 이내 진단/소견",
                            "해당 항목: {}".format(", ".join(subs))
                        ))

                # 실무 룰: 신규 진단 + 치료 중
                if days_from_first <= 90 and days_from_treat_end <= 0:
                    reasons.append((
                        "[실무 룰] 3개월 이내 신규 진단 & 치료 중",
                        "최초진단 {} / 가입 가능일: {} 이후".format(
                            s['first_date'], treat_end.strftime('%Y-%m-%d'))
                    ))
                # 실무 룰: 만성질환 약 변경/추가
                elif days_from_first > 90 and days_from_latest <= 90:
                    new_drugs = s["drug_names_in_90"] - s["drug_names_before_90"]
                    if new_drugs:
                        reasons.append((
                            "[실무 룰] 3개월 이내 약 변경/추가 의심",
                            "신규 약품 발견: {}".format(", ".join(list(new_drugs)[:2])[:50])
                        ))

                # [간편 2번] 10년 이내 입원/수술
                within_10y = days_from_treat_end <= 3650
                if within_10y:
                    if inpatient_count > 0:
                        d_range = ""
                        if s["inpatient_dates"]:
                            sorted_d = sorted(s["inpatient_dates"])
                            d_range = " ({} ~ {})".format(sorted_d[0], sorted_d[-1])
                        reasons.append((
                            "[간편 2번] 10년 이내 입원",
                            "입원 {}일{}".format(inpatient_count, d_range)
                        ))
                    if s["surgeries"]:
                        surg_sample = list(s["surgeries"])[:2]
                        reasons.append((
                            "[간편 2번] 10년 이내 수술",
                            "수술/시술: {}".format(", ".join(surg_sample)[:50])
                        ))

                # [간편 3번] 5년 이내 6대 질병
                within_5y = days_from_treat_end <= 1825
                if within_5y:
                    is_6 = (any(key.startswith(c) for c in disease_6_list) or
                            any(n in s["name"] for n in disease_6_names))
                    if is_6:
                        reasons.append((
                            "[간편 3번] 5년 이내 6대 중증 질환",
                            "6대 질환 코드/병명 매칭 ({} / {})".format(key, s['name'][:20])
                        ))

            if reasons:
                flagged_codes.add(key)
                disp_code = format_code(key)
                for q_title, detail in reasons:
                    summary_reports[q_title].append({
                        "first_date":       s["first_date"],
                        "latest_date":      s["latest_date"],
                        "treatment_end":    treat_end.strftime("%Y-%m-%d"),
                        "code":             disp_code,
                        "name":             s["name"],
                        "visit":            total_visit,
                        "visit_count":      visit_count,
                        "max_single_med":   max_single_med,
                        "total_med":        total_med_days,
                        "inpatient":        inpatient_count,
                        "inpatient_dates":  sorted(s["inpatient_dates"]),
                        "surgeries":        s["surgeries"],
                        "surgery_dates":    sorted(s["surgery_dates"]),
                        "hospitals":        list(s["hospitals"]),
                        "detail":           detail,
                    })


    # ==========================================
    # 요약 카드 (상단)
    # ==========================================
    flagged_count   = len(flagged_codes)
    total_q_count   = len(summary_reports)
    total_visit_sum = sum(
        len(s["visit_dates"]) + len(s["inpatient_dates"])
        for s in disease_stats.values()
        if s["latest_date"] != "2000-01-01"
    )
    total_med_sum = sum(
        sum((s["med_dates_pharma"] if s["has_pharma"] and s["med_dates_pharma"]
             else s["med_dates_basic"]).values())
        for s in disease_stats.values()
        if s["latest_date"] != "2000-01-01"
    )

    card_class = "danger" if flagged_count >= 5 else ("warn" if flagged_count > 0 else "ok")

    st.markdown(f"""
    <div class="summary-grid">
        <div class="stat-card {card_class}">
            <div class="sc-label">고지 대상 질환</div>
            <div class="sc-value">{flagged_count}</div>
            <div class="sc-sub">{'⚠️ 간편심사 전환 검토' if flagged_count >= 5 else ('고지 항목 있음' if flagged_count > 0 else '✅ 이상 없음')}</div>
        </div>
        <div class="stat-card">
            <div class="sc-label">해당 질문 항목 수</div>
            <div class="sc-value">{total_q_count}</div>
            <div class="sc-sub">청약서 기재 필요 항목</div>
        </div>
        <div class="stat-card">
            <div class="sc-label">전체 누적 진료일</div>
            <div class="sc-value">{total_visit_sum}</div>
            <div class="sc-sub">입원 포함 총 일수</div>
        </div>
        <div class="stat-card">
            <div class="sc-label">전체 누적 투약일</div>
            <div class="sc-value">{total_med_sum}</div>
            <div class="sc-sub">중복 미제거 합계</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # ==========================================
    # 간편심사 전환 권고 배너
    # ==========================================
    if product_type == "건강체/표준체 (일반심사)" and flagged_count >= 5:
        st.markdown(f"""
        <div class="switch-banner">
            🔄 고지 대상 질환이 <b>{flagged_count}개</b>로 <b>5개 이상</b>입니다.
            간편심사(유병자 3-5-5) 상품으로 전환 시, 통원·투약 이력이 면제되어 청약 가능성이 높아집니다.
            사이드바에서 상품 유형을 변경해 시뮬레이션 해보세요.
        </div>
        """, unsafe_allow_html=True)


    # ==========================================
    # 탭 구성
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["📋 고지 판정 리포트", "🔍 원본 데이터", "💬 카톡 전송 & PDF 내보내기"])


    # ──────────────────────────────────────────
    # TAB 1: 고지 판정 리포트
    # ──────────────────────────────────────────
    with tab1:
        if not summary_reports:
            st.markdown("""
            <div class="clean-card">
                <span style="font-size:1.8rem;">✅</span>
                <div>
                    <div>고지 대상 없음 — 표준체 심사 진행 가능</div>
                    <div style="font-size:0.82rem; font-weight:400; color:#15803d; margin-top:3px;">
                        설정하신 기간 내에 알릴 의무에 해당하는 위험 이력이 발견되지 않았습니다.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#fef9ec; border:1px solid #fcd34d; border-radius:10px;
                        padding:0.8rem 1rem; margin-bottom:1.2rem; color:#92400e;
                        font-size:0.85rem; font-weight:600;">
                ⚠️ 아래 항목은 AI가 분석한 <b>필수 고지 대상</b>입니다. 청약서 해당 번호에 기재하세요.
            </div>
            """, unsafe_allow_html=True)

            import html as _html

            for q_title in sorted(summary_reports.keys()):
                items = summary_reports[q_title]
                q_badge = re.sub(r"\].*", "]", q_title).strip("[]").strip()
                q_label = re.sub(r"^\[.*?\]\s*", "", q_title)

                # 카드 헤더
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
                    visit     = item["visit"]
                    med       = item["total_med"]
                    max_med   = item["max_single_med"]
                    inpatient = item["inpatient"]
                    n_surg    = len(item["surgeries"])

                    inpt_pill = '<span class="stat-pill">🏥 입원 {}일</span>'.format(inpatient) if inpatient > 0 else ""
                    surg_pill = '<span class="stat-pill">🔪 수술 {}건</span>'.format(n_surg)    if n_surg > 0  else ""
                    max_med_pill = '<span class="stat-pill">📋 단일처방 최대 {}일</span>'.format(max_med) if max_med >= 30 else ""

                    st.markdown(
                        '<div class="duty-item">'
                        '  <div class="duty-disease">{} <span class="duty-code">{}</span></div>'
                        '  <div style="font-size:0.8rem;color:#64748b;margin:2px 0;">'
                        '    📅 {} ~ {} &nbsp;|&nbsp; 🏥 {}'
                        '  </div>'
                        '  <div class="duty-reason">↳ {}</div>'
                        '  <div class="duty-stats-row">'
                        '    <span class="stat-pill">🗓 진료 {}일</span>'
                        '    <span class="stat-pill">💊 투약합계 {}일</span>'
                        '    {}{}{}'
                        '  </div>'
                        '</div>'.format(name, code, fd, ld, hosp, detail,
                                        visit, med, inpt_pill, surg_pill, max_med_pill),
                        unsafe_allow_html=True,
                    )

                # 카드 닫기
                st.markdown('</div>', unsafe_allow_html=True)

        # 간편심사: 3칸 요약 박스
        if product_type == "간편심사 (유병자 3-5-5 기준)":
            st.markdown('<div class="section-head" style="margin-top:1.5rem;">⚡ 간편심사 3-5-5 항목별 현황</div>', unsafe_allow_html=True)

            def get_easy_items(keywords):
                html_parts = []
                for k, v_list in summary_reports.items():
                    if any(kw in k for kw in keywords):
                        for v in v_list:
                            code_h = '<span class="easy-code">[{}]</span> '.format(v["code"]) if v["code"] != "-" else ""
                            extra = ""
                            if v["inpatient"] > 0:
                                dates = v["inpatient_dates"]
                                r = "{} ~ {}".format(dates[0], dates[-1]) if len(dates) > 1 else (dates[0] if dates else "")
                                extra += '<br><span style="color:#1d4ed8;font-size:0.74rem;">🏥 입원 {} ({}일)</span>'.format(r, v["inpatient"])
                            if v["surgeries"]:
                                dates = v["surgery_dates"]
                                r = "{} ~ {}".format(dates[0], dates[-1]) if len(dates) > 1 else (dates[0] if dates else "")
                                extra += '<br><span style="color:#dc2626;font-size:0.74rem;">🔪 수술 {} ({}건)</span>'.format(r, len(v["surgeries"]))
                            html_parts.append('<div class="easy-item">{}{}<span style="color:#94a3b8;font-size:0.75rem;"> ({})</span>{}</div>'.format(
                                code_h, v["name"][:15], v["latest_date"], extra))
                return "".join(html_parts) if html_parts else '<div class="easy-empty">✅ 해당 없음 (통과)</div>'

            st.markdown("""
            <div class="easy-grid">
                <div class="easy-box">
                    <div class="easy-box-head">⏱️ 최근 3개월<br><span style="font-weight:500; font-size:0.72rem; color:#64748b;">진단·소견·약품변경</span></div>
                    {}
                </div>
                <div class="easy-box">
                    <div class="easy-box-head">🏥 최근 10년 입원/수술<br><span style="font-weight:500; font-size:0.72rem; color:#64748b;">통원·투약 이력 면제</span></div>
                    {}
                </div>
                <div class="easy-box">
                    <div class="easy-box-head">⚠️ 최근 5년 6대 질환<br><span style="font-weight:500; font-size:0.72rem; color:#64748b;">암·뇌·심장·간경화</span></div>
                    {}
                </div>
            </div>
            """.format(
                get_easy_items(["1번", "실무"]),
                get_easy_items(["2번"]),
                get_easy_items(["3번"])
            ), unsafe_allow_html=True)


    # ──────────────────────────────────────────
    # TAB 2: 원본 데이터
    # ──────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-head">🔍 심평원 추출 원본 데이터 <span style="font-weight:400;color:#64748b;font-size:0.85rem;">(고지 대상 우선 정렬 · 빨간 행 = 고지 필요)</span></div>', unsafe_allow_html=True)

        for file_name, f_df in file_dataframes.items():
            # 더미 행 제거
            keep = []
            for idx, row in f_df.iterrows():
                if not row_is_junk(row):
                    keep.append(idx)
            clean_df = f_df.loc[keep].copy()
            if clean_df.empty:
                continue

            st.markdown(f"**📄 {file_name}**")

            is_flagged_list, code_sort = [], []
            for _, row in clean_df.iterrows():
                c = normalize_code(get_val(row, ["코드"]))
                n = get_val(row, ["상병명", "약품명", "진료내역"])
                rk = c if c else n[:15]
                is_flagged_list.append(rk in flagged_codes)
                code_sort.append(c)

            clean_df["_flag"] = is_flagged_list
            clean_df["_code"] = code_sort
            sorted_df = (
                clean_df
                .sort_values(["_flag", "_code"], ascending=[False, True])
                .drop(columns=["_flag", "_code"])
                .reset_index(drop=True)
            )

            def highlight(row):
                c = normalize_code(get_val(row, ["코드"]))
                n = get_val(row, ["상병명", "약품명", "진료내역"])
                rk = c if c else n[:15]
                if rk in flagged_codes:
                    return ["background-color:#fee2e2; color:#991b1b; font-weight:700;"] * len(row)
                return [""] * len(row)

            st.dataframe(sorted_df.style.apply(highlight, axis=1), use_container_width=True)
            st.markdown("---")


    # ──────────────────────────────────────────
    # TAB 3: 카톡 전송 & PDF 내보내기
    # ──────────────────────────────────────────
    with tab3:
        import streamlit.components.v1 as components

        # ── 카카오톡 메시지 생성 ──
        kakao_msg = f"📋 [ {product_type} 심사 요청 ]\n"
        kakao_msg += f"■ 기준일(청약예정일): {today.strftime('%Y-%m-%d')}\n\n"

        if not summary_reports:
            kakao_msg += "✅ AI 분석 결과, 고지 대상 질환이 없습니다. (표준체 진행 가능)\n"
        else:
            for q_title in sorted(summary_reports.keys()):
                clean_title = re.sub(r"^\[.*?\]\s*", "", q_title)
                kakao_msg += f"▶ {clean_title}\n"
                for item in summary_reports[q_title]:
                    hosp = ", ".join(item["hospitals"]) if item["hospitals"] else "알 수 없음"
                    kakao_msg += f"■ 질병/증상: {item['name']} ({item['code']})\n"
                    kakao_msg += f" - 치료기간: {item['first_date']} ~ {item['latest_date']}\n"
                    kakao_msg += f" - 병원명: {hosp}\n"
                    if product_type == "건강체/표준체 (일반심사)":
                        kakao_msg += " - 진료 {}일 / 투약합계 {}일 / 단일처방최대 {}일 / 입원 {}일 / 수술 {}건\n".format(
                            item['visit'], item['total_med'], item['max_single_med'],
                            item['inpatient'], len(item['surgeries']))
                    else:
                        inpt = "{}일".format(item['inpatient']) if item["inpatient"] > 0 else "해당없음"
                        surg = "{}건".format(len(item['surgeries'])) if item["surgeries"] else "해당없음"
                        kakao_msg += " - 입원: {} / 수술: {}\n".format(inpt, surg)
                    kakao_msg += f" - 사유: {item['detail']}\n\n"

        # ── 복사 버튼 ──
        safe_msg = kakao_msg.replace("`", "\\`").replace("\n", "\\n").replace("'", "\\'")
        copy_html = f"""
        <style>
        .kakao-copy-btn {{
            width: 100%;
            padding: 15px;
            background: #ffffff;
            border: 2px solid #e2e8f0;
            border-radius: 14px;
            color: #1d4ed8;
            font-weight: 800;
            font-size: 1rem;
            cursor: pointer;
            font-family: 'Noto Sans KR', sans-serif;
            transition: all 0.2s;
            letter-spacing: -0.02em;
        }}
        .kakao-copy-btn:hover {{
            background: #eff6ff;
            border-color: #93c5fd;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(29,78,216,0.12);
        }}
        .kakao-copy-btn.copied {{
            background: #f0fdf4;
            border-color: #86efac;
            color: #15803d;
        }}
        </style>
        <button id="copy-btn" class="kakao-copy-btn">
            💬 설계 매니저님께 카톡 전달하기 &nbsp;(클릭하여 복사 📋)
        </button>
        <script>
        document.getElementById('copy-btn').addEventListener('click', function() {{
            const text = `{safe_msg}`;
            const btn = this;
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.select();
            try {{
                document.execCommand('copy');
                btn.textContent = '✅ 복사 완료! 카카오톡에 붙여넣기 하세요 (Ctrl+V / ⌘V)';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.textContent = '💬 설계 매니저님께 카톡 전달하기  (클릭하여 복사 📋)';
                    btn.classList.remove('copied');
                }}, 3000);
            }} catch(e) {{ console.error(e); }}
            document.body.removeChild(ta);
        }});
        </script>
        """
        st.markdown('<div class="section-head">💬 카카오톡 전달</div>', unsafe_allow_html=True)
        components.html(copy_html, height=80)

        st.markdown("---")

        # ── 미리보기 ──
        with st.expander("📄 카톡 메시지 미리보기"):
            st.text(kakao_msg)

        # ── PDF 다운로드 ──
        st.markdown('<div class="section-head" style="margin-top:1.2rem;">📥 PDF 리포트 다운로드</div>', unsafe_allow_html=True)

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import io, os, urllib.request, tempfile

            # ── 한글 폰트 확보: 시스템 탐색 → 없으면 Google Fonts에서 직접 다운로드 ──
            FONT_CACHE_DIR = tempfile.gettempdir()
            FONT_REG_PATH  = os.path.join(FONT_CACHE_DIR, "NanumGothic.ttf")
            FONT_BOLD_PATH = os.path.join(FONT_CACHE_DIR, "NanumGothicBold.ttf")

            # 구글 폰트 직접 다운로드 URL (Nanum Gothic)
            NANUM_REG_URL  = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            NANUM_BOLD_URL = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"

            # 시스템 경로 후보
            SYSTEM_PATHS = [
                ("/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                 "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
                ("/usr/share/fonts/nanum/NanumGothic.ttf",
                 "/usr/share/fonts/nanum/NanumGothicBold.ttf"),
                ("/Library/Fonts/NanumGothic.ttf",
                 "/Library/Fonts/NanumGothicBold.ttf"),
            ]

            def _get_font_paths():
                """(regular_path, bold_path) 반환. 없으면 다운로드."""
                # 1) 시스템 경로 탐색
                for reg, bold in SYSTEM_PATHS:
                    if os.path.exists(reg):
                        return reg, bold if os.path.exists(bold) else reg
                # 2) 캐시 디렉터리 확인
                if os.path.exists(FONT_REG_PATH):
                    bold = FONT_BOLD_PATH if os.path.exists(FONT_BOLD_PATH) else FONT_REG_PATH
                    return FONT_REG_PATH, bold
                # 3) 네트워크 다운로드
                try:
                    urllib.request.urlretrieve(NANUM_REG_URL,  FONT_REG_PATH)
                    urllib.request.urlretrieve(NANUM_BOLD_URL, FONT_BOLD_PATH)
                    return FONT_REG_PATH, FONT_BOLD_PATH
                except Exception:
                    return None, None

            @st.cache_resource(show_spinner=False)
            def _register_fonts():
                reg_path, bold_path = _get_font_paths()
                if reg_path is None:
                    return "Helvetica", "Helvetica-Bold", False
                try:
                    if "NanumGothic" not in pdfmetrics.getRegisteredFontNames():
                        pdfmetrics.registerFont(TTFont("NanumGothic",     reg_path))
                    if "NanumGothicBold" not in pdfmetrics.getRegisteredFontNames():
                        pdfmetrics.registerFont(TTFont("NanumGothicBold", bold_path))
                    return "NanumGothic", "NanumGothicBold", True
                except Exception:
                    return "Helvetica", "Helvetica-Bold", False

            FONT_NAME, BOLD_FONT, font_ok = _register_fonts()

            if not font_ok:
                st.warning(
                    "⚠️ 한글 폰트 로드에 실패했습니다. "
                    "서버 네트워크 환경에서 GitHub에 접근할 수 없는 경우 "
                    "NanumGothic.ttf 파일을 프로젝트 루트에 직접 배치해 주세요."
                )

            # ── PDF 빌더 ──
            def build_pdf():
                buf = io.BytesIO()
                doc = SimpleDocTemplate(
                    buf, pagesize=A4,
                    leftMargin=18*mm, rightMargin=18*mm,
                    topMargin=18*mm, bottomMargin=18*mm
                )

                navy   = colors.HexColor("#1e3a8a")
                red    = colors.HexColor("#dc2626")
                gray   = colors.HexColor("#64748b")
                ltgray = colors.HexColor("#f1f5f9")
                white  = colors.white
                black  = colors.HexColor("#111827")
                green  = colors.HexColor("#15803d")

                def S(uid, size=10, color=black, font=FONT_NAME, leading=14,
                      before=0, after=4, indent=0):
                    return ParagraphStyle(
                        uid, fontName=font, fontSize=size, textColor=color,
                        leading=leading, spaceBefore=before, spaceAfter=after,
                        leftIndent=indent, wordWrap='CJK'
                    )

                def th_style(uid):
                    return ParagraphStyle(
                        uid, fontName=BOLD_FONT, fontSize=8,
                        textColor=white, leading=11, wordWrap='CJK'
                    )

                def tv_style(uid, color=navy):
                    return ParagraphStyle(
                        uid, fontName=BOLD_FONT, fontSize=15,
                        textColor=color, leading=18, alignment=1, wordWrap='CJK'
                    )

                s_title = S("t_title", 17, navy,  BOLD_FONT, 21, 0,  5)
                s_sub   = S("t_sub",    8, gray,  FONT_NAME, 12, 0, 10)
                s_sec   = S("t_sec",   11, navy,  BOLD_FONT, 15, 8,  4)
                s_q     = S("t_q",     10, red,   BOLD_FONT, 14, 8,  3)
                s_body  = S("t_body",   8, black, FONT_NAME, 12, 0,  2,  4)
                s_ok    = S("t_ok",    10, green, BOLD_FONT, 14, 4,  4)
                s_foot  = S("t_foot",   7, gray,  FONT_NAME, 10, 0,  0)

                story = []

                # ── 제목 ──
                story.append(Paragraph("AdvisorHub  스마트 고지 스캐너", s_title))
                story.append(Paragraph(
                    "심사 유형: {}  |  기준일: {}  |  고지 질환: {}개  |  해당 질문: {}개".format(
                        product_type, today.strftime('%Y-%m-%d'), flagged_count, total_q_count),
                    s_sub
                ))
                story.append(HRFlowable(width="100%", thickness=1, color=navy, spaceAfter=6))

                # ── 요약 수치 테이블 ──
                hdr = [Paragraph(t, th_style("h"+str(i)))
                       for i, t in enumerate(["고지 질환 수", "해당 질문 수", "총 진료일", "총 투약일"])]
                val_color = red if flagged_count > 0 else green
                vals = [
                    Paragraph(str(flagged_count), tv_style("v0", val_color)),
                    Paragraph(str(total_q_count),  tv_style("v1")),
                    Paragraph(str(total_visit_sum),tv_style("v2")),
                    Paragraph(str(total_med_sum),  tv_style("v3")),
                ]
                sum_tbl = Table([hdr, vals], colWidths=["25%"]*4)
                sum_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0,0), (-1,0), navy),
                    ("BACKGROUND",    (0,1), (-1,1), ltgray),
                    ("ALIGN",         (0,0), (-1,-1), "CENTER"),
                    ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
                    ("BOX",           (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                    ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING",    (0,0), (-1,-1), 6),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ]))
                story.append(sum_tbl)
                story.append(Spacer(1, 10))

                # ── 판정 결과 ──
                story.append(Paragraph("고지 판정 결과", s_sec))

                if not summary_reports:
                    story.append(Paragraph(
                        "고지 대상 없음 — 설정 기간 내 알릴 의무 위험 이력이 발견되지 않았습니다.",
                        s_ok
                    ))
                else:
                    for q_title in sorted(summary_reports.keys()):
                        story.append(Paragraph(q_title, s_q))
                        items = summary_reports[q_title]

                        col_hdr = [
                            Paragraph(t, th_style("ch_"+str(i)))
                            for i, t in enumerate(["질병명 (코드)", "기간", "진료/투약", "매칭 사유"])
                        ]
                        rows = [col_hdr]
                        for item in items:
                            name_safe   = (item['name'][:25] or '(병명 미상)').replace('&','and')
                            detail_safe = item['detail'][:60].replace('&','and')
                            rows.append([
                                Paragraph("{}\n({})".format(name_safe, item['code']), s_body),
                                Paragraph("{}\n~ {}".format(item['first_date'], item['latest_date']), s_body),
                                Paragraph("진료 {}일\n투약 {}일\n입원 {}일".format(
                                    item['visit'], item['total_med'], item['inpatient']), s_body),
                                Paragraph(detail_safe, s_body),
                            ])

                        t = Table(rows, colWidths=["28%","20%","17%","35%"])
                        t.setStyle(TableStyle([
                            ("BACKGROUND",    (0,0), (-1,0), red),
                            ("ROWBACKGROUNDS",(0,1), (-1,-1), [white, colors.HexColor("#fff5f5")]),
                            ("BOX",           (0,0), (-1,-1), 0.4, colors.HexColor("#fecaca")),
                            ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#fee2e2")),
                            ("VALIGN",        (0,0), (-1,-1), "TOP"),
                            ("TOPPADDING",    (0,0), (-1,-1), 5),
                            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                            ("LEFTPADDING",   (0,0), (-1,-1), 5),
                            ("RIGHTPADDING",  (0,0), (-1,-1), 5),
                        ]))
                        story.append(t)
                        story.append(Spacer(1, 6))

                # ── 푸터 ──
                story.append(HRFlowable(width="100%", thickness=0.4,
                                        color=colors.HexColor("#e2e8f0"), spaceBefore=10))
                story.append(Paragraph(
                    "본 리포트는 AdvisorHub AI 엔진이 자동 생성한 참고자료이며, "
                    "최종 심사 판단은 언더라이터의 전문적 검토를 따릅니다.  |  생성: {}".format(
                        datetime.now().strftime('%Y-%m-%d %H:%M')),
                    s_foot
                ))

                doc.build(story)
                return buf.getvalue()

            pdf_bytes = build_pdf()
            st.download_button(
                label="⬇️  PDF 리포트 다운로드",
                data=pdf_bytes,
                file_name="AdvisorHub_고지리포트_{}.pdf".format(today.strftime('%Y%m%d')),
                mime="application/pdf",
                use_container_width=True,
            )
            if font_ok:
                st.caption("✅ NanumGothic 한글 폰트 적용 완료")
            else:
                st.caption("⚠️ 폰트 로드 실패 — 한글이 깨질 수 있습니다.")

        except ImportError:
            st.warning("PDF 생성에는 `reportlab` 라이브러리가 필요합니다.\n\n`pip install reportlab` 후 재시작하세요.")
        except Exception as e:
            st.error("PDF 생성 중 오류: {}".format(e))