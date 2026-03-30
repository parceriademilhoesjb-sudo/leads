"""
main.py — OAB Lead Qualifier CRM
Upload → Enriquecer → Dashboard → Atribuir para closers
Leads acumulam no banco a cada upload. Tudo persiste automaticamente.
"""

import concurrent.futures
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from upload import parse_growman_xlsx
from enrichment.bio_parser import parse_bio
from enrichment.oab_module import lookup_oab
from enrichment.site_checker import check_site
from scoring.engine import calcular_score
from ui.dashboard import render_dashboard
from ui.closer_panel import render_closer_panel
from ui.sync_panel import render_sync_panel
from storage import add_leads, load_leads, update_closer, delete_lead, update_proposta

CLOSERS = {
    "matheus":  "Matheus",
    "jonas":    "Jonas",
    "giovanne": "Giovanne",
    "say":      "Say",
}

# ── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OAB Lead Qualifier",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Manrope:wght@200;400;600;700;800&display=swap');

/* ── Oculta nav automática de multi-página (não afeta sidebar customizado) ── */
[data-testid="stSidebarNav"] { display: none !important; }

/* ══════════════════════════════════════════════
   PULSE DESIGN SYSTEM — OAB Lead Qualifier CRM
   Inspirado no pulse.html · Agência Avestra
   ══════════════════════════════════════════════ */

/* ── Animations ── */
@keyframes animStar {
    from { transform: translateY(0px); }
    to   { transform: translateY(-2000px); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 20px rgba(80, 112, 176, 0.15); }
    50%       { box-shadow: 0 0 40px rgba(80, 112, 176, 0.35); }
}
@keyframes shimmerBorder {
    from { background-position: 0% 50%; }
    to   { background-position: 100% 50%; }
}

/* ── Base ── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    color: #e8eaf0 !important;
}

/* ── Background: deep space with stars ── */
body {
    background: #050a15 !important;
}

.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 50% 0%,   rgba(80, 112, 176, 0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 20% 60%,  rgba(32,  64, 128, 0.05) 0%, transparent 50%),
        radial-gradient(ellipse 50% 50% at 80% 80%,  rgba(80, 112, 176, 0.04) 0%, transparent 50%),
        linear-gradient(to bottom, #0a1128 0%, #050a15 100%) !important;
    min-height: 100vh;
}

/* Stars layer 1 — tiny white dots */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 1px; height: 1px;
    background: transparent;
    box-shadow:
        234px 124px #fff, 654px 345px #fff, 876px 12px #fff,
        1200px 800px #fff, 400px 1500px #fff, 1800px 200px #fff,
        100px 1000px #fff, 900px 1900px #fff, 500px 600px #fff,
        1400px 100px #fff, 300px 400px #fff, 1600px 1200px #fff,
        50px 300px #fff, 750px 1100px #fff, 1100px 1600px #fff,
        1700px 700px #fff, 200px 1800px #fff, 950px 50px #fff,
        60px 1400px #fff, 1350px 450px #fff, 780px 780px #fff,
        1050px 350px #fff, 450px 950px #fff, 1550px 650px #fff,
        320px 1250px #fff, 680px 1700px #fff, 1150px 900px #fff,
        840px 250px #fff, 1480px 1350px #fff, 120px 550px #fff;
    animation: animStar 60s linear infinite;
    z-index: 0;
    pointer-events: none;
}

/* Stars layer 2 — blue accent dots */
body::after {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 2px; height: 2px;
    background: transparent;
    box-shadow:
        123px 456px rgba(80,112,176,0.6),
        789px 234px rgba(80,112,176,0.4),
        456px 890px rgba(144,192,224,0.5),
        1100px 300px rgba(80,112,176,0.5),
        200px 1200px rgba(144,192,224,0.3),
        1500px 500px rgba(80,112,176,0.4),
        600px 1700px rgba(144,192,224,0.5),
        1300px 900px rgba(80,112,176,0.3),
        350px 750px rgba(144,192,224,0.4),
        850px 1400px rgba(80,112,176,0.6),
        1650px 1050px rgba(144,192,224,0.3),
        500px 200px rgba(80,112,176,0.5),
        1100px 1600px rgba(144,192,224,0.4),
        250px 1600px rgba(80,112,176,0.3);
    animation: animStar 90s linear infinite;
    z-index: 0;
    pointer-events: none;
}

/* Grid overlay */
.stApp > * { position: relative; z-index: 1; }
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(ellipse at center, black 30%, transparent 80%);
    z-index: 0;
    pointer-events: none;
}

/* ── Header ── */
header[data-testid="stHeader"] {
    background: rgba(5, 10, 21, 0.7) !important;
    border-bottom: 1px solid rgba(80, 112, 176, 0.15) !important;
    backdrop-filter: blur(20px) !important;
}

/* ── Main content container ── */
.block-container {
    max-width: 1320px !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(5, 10, 21, 0.85) !important;
    border-right: 1px solid rgba(80, 112, 176, 0.15) !important;
    backdrop-filter: blur(20px) !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 12px 16px !important;
    border-radius: 12px !important;
    width: 100% !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-size: 14px !important;
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: 0.2px;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(80, 112, 176, 0.1) !important;
    color: #90c0e0 !important;
    border-color: rgba(80, 112, 176, 0.25) !important;
    transform: translateX(4px) !important;
}

/* ── Metrics (Streamlit native) ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg,
        rgba(80, 112, 176, 0.08) 0%,
        rgba(5, 10, 21, 0.6) 100%) !important;
    border: 1px solid rgba(80, 112, 176, 0.2) !important;
    border-radius: 20px !important;
    padding: 24px !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    backdrop-filter: blur(12px) !important;
    animation: pulseGlow 4s ease-in-out infinite;
}

div[data-testid="metric-container"]:hover {
    border-color: rgba(144, 192, 224, 0.4) !important;
    background: linear-gradient(135deg,
        rgba(80, 112, 176, 0.18) 0%,
        rgba(5, 10, 21, 0.7) 100%) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.6),
                0 0 30px rgba(80, 112, 176, 0.15) !important;
}

div[data-testid="metric-container"] label {
    color: #64748b !important;
    font-size: 10px !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    font-family: 'Manrope', sans-serif !important;
    text-shadow: 0 0 25px rgba(144, 192, 224, 0.4) !important;
}

/* ── Expander / Lead Cards ── */
details, .stExpander {
    background: linear-gradient(135deg,
        rgba(255, 255, 255, 0.025) 0%,
        rgba(5, 10, 21, 0.4) 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 16px !important;
    margin-bottom: 16px !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    backdrop-filter: blur(8px) !important;
    overflow: hidden !important;
}

details:hover, .stExpander:hover {
    background: linear-gradient(135deg,
        rgba(80, 112, 176, 0.06) 0%,
        rgba(5, 10, 21, 0.5) 100%) !important;
    border-color: rgba(80, 112, 176, 0.25) !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4),
                0 0 20px rgba(80, 112, 176, 0.08) !important;
    transform: translateY(-2px) !important;
}

details summary {
    padding: 18px 22px !important;
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    cursor: pointer !important;
    background: transparent !important;
    letter-spacing: 0.2px;
}

details summary:hover { color: #ffffff !important; }
details[open] summary { border-bottom: 1px solid rgba(80, 112, 176, 0.15) !important; }
details > div { padding: 20px 22px !important; }

/* ── Buttons — Pulse style ── */
.block-container .stButton > button {
    border-radius: 999px !important;
    background: linear-gradient(135deg, #4060a0 0%, #5070b0 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(144, 192, 224, 0.2) !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.8rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-family: 'Manrope', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-size: 12px !important;
}

.block-container .stButton > button:hover {
    background: linear-gradient(135deg, #5070b0 0%, #6090c0 100%) !important;
    border-color: rgba(144, 192, 224, 0.4) !important;
    box-shadow: 0 0 25px rgba(80, 112, 176, 0.5),
                0 8px 20px rgba(0,0,0,0.3) !important;
    transform: translateY(-2px) !important;
}

/* Download buttons */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 1px solid rgba(144, 192, 224, 0.25) !important;
    color: #90c0e0 !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background: rgba(80, 112, 176, 0.1) !important;
    border-color: rgba(144, 192, 224, 0.5) !important;
    box-shadow: 0 0 20px rgba(80, 112, 176, 0.3) !important;
}

/* Link buttons */
a[data-testid="stLinkButton"] {
    border-radius: 999px !important;
    background: rgba(80, 112, 176, 0.15) !important;
    border: 1px solid rgba(80, 112, 176, 0.25) !important;
    color: #90c0e0 !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 12px !important;
}

a[data-testid="stLinkButton"]:hover {
    background: rgba(80, 112, 176, 0.3) !important;
    border-color: rgba(144, 192, 224, 0.4) !important;
    box-shadow: 0 0 20px rgba(80, 112, 176, 0.3) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(5, 10, 21, 0.6) !important;
    border: 1px solid rgba(80, 112, 176, 0.2) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    backdrop-filter: blur(8px) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(80, 112, 176, 0.04) !important;
    border: 2px dashed rgba(80, 112, 176, 0.25) !important;
    border-radius: 20px !important;
    transition: all 0.3s ease !important;
    padding: 40px 20px !important;
    backdrop-filter: blur(8px);
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(80, 112, 176, 0.5) !important;
    background: rgba(80, 112, 176, 0.08) !important;
    box-shadow: 0 0 30px rgba(80, 112, 176, 0.1) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(5, 10, 21, 0.4) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(80, 112, 176, 0.15) !important;
    padding: 4px !important;
    backdrop-filter: blur(8px);
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #64748b !important;
    font-weight: 600 !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
}

[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(80, 112, 176, 0.2) !important;
    color: #90c0e0 !important;
    box-shadow: 0 0 15px rgba(80, 112, 176, 0.2) !important;
}

[data-testid="stTabs"] [role="tabpanel"] {
    background: transparent !important;
    border: 1px solid rgba(80, 112, 176, 0.1) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    backdrop-filter: blur(5px) !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #204080, #5070b0, #90c0e0) !important;
    height: 6px !important;
    border-radius: 3px !important;
    box-shadow: 0 0 10px rgba(80, 112, 176, 0.5) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 16px !important;
    backdrop-filter: blur(8px) !important;
    border-left-width: 4px !important;
    background: rgba(80, 112, 176, 0.08) !important;
}

/* ── Divider ── */
hr {
    border-color: rgba(80, 112, 176, 0.15) !important;
    margin: 24px 0 !important;
}

/* ── Caption / small text ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #64748b !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}

/* ── Info box ── */
div[data-testid="stInfo"] {
    background: rgba(80, 112, 176, 0.08) !important;
    border: 1px solid rgba(80, 112, 176, 0.2) !important;
    border-radius: 12px !important;
    color: #90c0e0 !important;
}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label { color: #94a3b8 !important; font-size: 13px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #050a15; }
::-webkit-scrollbar-thumb {
    background: rgba(80, 112, 176, 0.25);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: #5070b0; }

/* ── Text selection ── */
::selection {
    background: rgba(80, 112, 176, 0.4);
    color: #ffffff;
}

/* ── Utility classes ── */
.accent-text { color: #90c0e0 !important; font-weight: 700 !important; }
.glow-text { text-shadow: 0 0 30px rgba(80, 112, 176, 0.6); }
.manrope { font-family: 'Manrope', sans-serif !important; }
</style>
""", unsafe_allow_html=True)


# ── Enriquecimento ────────────────────────────────────────────────────────────
def _enrich_lead(lead_dict: dict) -> dict:
    bio          = lead_dict.get("bio", "")
    external_url = lead_dict.get("external_url", "")
    phone_full   = lead_dict.get("phone_full", "")
    username     = lead_dict.get("username", "")
    full_name    = lead_dict.get("full_name_normalizado", lead_dict.get("full_name", ""))
    city         = lead_dict.get("city", "")

    bio_data = parse_bio(bio, external_url=external_url, phone_full=phone_full, username=username)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fut_oab  = ex.submit(lookup_oab, full_name, city)
        fut_site = ex.submit(check_site, external_url, full_name, city)
        try:    oab_data  = fut_oab.result(timeout=15)
        except: oab_data  = {}
        try:    site_data = fut_site.result(timeout=15)
        except: site_data = {}

    enriched = {**lead_dict, **bio_data, **oab_data, **site_data}
    enriched.setdefault("oab_numero", "");   enriched.setdefault("oab_situacao", "")
    enriched.setdefault("oab_anos_ativo", None); enriched.setdefault("oab_encontrado", False)
    enriched.setdefault("site_encontrado", False); enriched.setdefault("has_fb_pixel", False)
    enriched.setdefault("has_ga", False);    enriched.setdefault("cnpj_numero", "")
    enriched.setdefault("cnpj_situacao", ""); enriched.setdefault("cnpj_cnae_juridico", False)
    enriched.setdefault("cnpj_razao_social", ""); enriched.setdefault("gmb_encontrado", False)
    enriched.setdefault("gmb_reviews", 0);   enriched.setdefault("closer", "")
    return calcular_score(enriched)


# ── Sidebar ───────────────────────────────────────────────────────────────────
def _nav_btn(label: str, destino: str, ativo: bool):
    if ativo:
        st.markdown(
            f"<style>[data-testid='stSidebar'] .stButton button:has(div[title='{label}']) {{ "
            f"background: rgba(80, 112, 176, 0.2) !important; color: #ffffff !important; "
            f"border-color: rgba(144, 192, 224, 0.3) !important; font-weight: 700 !important; "
            f"box-shadow: 0 4px 15px rgba(32, 64, 128, 0.2) !important; border-left: 4px solid #90c0e0 !important; }} </style>",
            unsafe_allow_html=True,
        )
    if st.button(label, use_container_width=True, key=f"nav__{destino}"):
        st.session_state["pagina"] = destino
        st.rerun()


def render_sidebar(leads: list[dict], pagina: str):
    total        = len(leads)
    disponiveis  = sum(1 for l in leads if not l.get("closer"))

    with st.sidebar:
        # Logo
        st.markdown(
            "<div style='padding:16px 8px 24px;border-bottom:1px solid rgba(80, 112, 176, 0.2);margin-bottom:24px'>"
            "<div style='font-size:1.8rem;margin-bottom:8px'>⚖️</div>"
            "<div style='font-size:1.1rem;font-weight:800;color:#ffffff;letter-spacing:-0.5px;font-family:\"Manrope\"'>"
            "AVESTRA <span style='color:#90c0e0'>CRM</span></div>"
            "<div style='font-size:12px;color:#b0c0d0;margin-top:4px'>"
            f"OAB Lead Qualifier · {total} leads</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        # Navegação principal
        _nav_btn(f"📊 Dashboard  ({disponiveis} disponíveis)", "dashboard", pagina == "dashboard")

        st.markdown(
            "<p style='color:#64748B;font-size:11px;font-weight:700;text-transform:uppercase;"
            "letter-spacing:0.8px;margin:16px 4px 6px'>Closers</p>",
            unsafe_allow_html=True,
        )
        for slug, nome in CLOSERS.items():
            count = sum(1 for l in leads if l.get("closer") == slug)
            _nav_btn(f"👤 {nome}  ({count})", f"closer_{slug}", pagina == f"closer_{slug}")

        st.divider()
        _nav_btn("⬆️ Adicionar leads", "upload", pagina == "upload")
        _nav_btn("🔄 Sincronizar dados", "sync", pagina == "sync")

        # Indicador de salvamento automático
        st.markdown(
            "<div style='margin-top:24px;padding:12px;background:rgba(144, 192, 224, 0.05);border-radius:12px;"
            "border:1px solid rgba(144, 192, 224, 0.15);text-align:center'>"
            "<span style='font-size:11px;color:#90c0e0;font-weight:600;letter-spacing:0.5px'>"
            "💾 SINCRONIZAÇÃO AUTOMÁTICA</span>"
            "</div>",
            unsafe_allow_html=True,
        )


# ── Upload ────────────────────────────────────────────────────────────────────
def tela_upload(leads: list[dict]):
    total = len(leads)

    st.markdown(
        "<h2 class='manrope' style='color:#ffffff;font-weight:800;letter-spacing:-1px;margin-bottom:8px'>"
        "⬆️ Adicionar <span class='accent-text'>Novas Oportunidades</span></h2>"
        "<p style='color:#b0c0d0;margin-bottom:32px;font-size:1.1rem'>"
        "Sistema de acumulação inteligente. Novos leads são integrados sem sobrescrever closer atual.</p>",
        unsafe_allow_html=True,
    )

    if total:
        quentes = sum(1 for l in leads if "Quente" in str(l.get("classificacao", "")))
        atrib   = sum(1 for l in leads if l.get("closer"))
        c1, c2, c3 = st.columns(3)
        c1.metric("Total no banco", total)
        c2.metric("🔥 Leads Quentes", quentes)
        c3.metric("Atribuídos a closers", atrib)
        st.divider()

    col = st.columns([1, 2, 1])[1]
    with col:
        uploaded = st.file_uploader(
            "Arraste o .xlsx do Growman aqui",
            type=["xlsx"],
            help="Exportação padrão do Growman — aba 'contacts'",
        )
        if uploaded:
            st.session_state["uploaded_file"] = uploaded
            st.session_state["pagina"] = "processando"
            st.rerun()
        st.caption("Suporta exportações do Growman IG · Filtrado automaticamente para advogados")


# ── Processando ───────────────────────────────────────────────────────────────
def tela_processando():
    uploaded = st.session_state.get("uploaded_file")
    if not uploaded:
        st.session_state["pagina"] = "upload"
        st.rerun()
        return

    st.markdown(
        "<h2 style='color:#F1F5F9;font-weight:700'>⏳ Processando leads...</h2>",
        unsafe_allow_html=True,
    )

    try:
        df, stats = parse_growman_xlsx(uploaded)
    except ValueError as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        if st.button("Voltar"):
            st.session_state["pagina"] = "upload"
            st.rerun()
        return

    st.info(
        f"📊 {stats['total_bruto']} registros · "
        f"{stats.get('apos_filtro_privado', '?')} públicos · "
        f"**{stats['advogados']} advogados detectados**"
    )

    leads_raw = df.to_dict("records")
    total = len(leads_raw)
    if total == 0:
        st.warning("Nenhum advogado encontrado. Verifique se o arquivo é do Growman.")
        if st.button("Voltar"):
            st.session_state["pagina"] = "upload"
            st.rerun()
        return

    progress    = st.progress(0, text="Iniciando...")
    status_box  = st.empty()
    preview     = st.container()
    processados = []

    for i, lead in enumerate(leads_raw):
        nome = lead.get("full_name", lead.get("username", f"Lead {i+1}"))
        progress.progress(i / total, text=f"Processando {i+1}/{total} — {nome}")
        status_box.caption(f"⚡ Enriquecendo: {nome}")
        try:
            enriched = _enrich_lead(lead)
        except Exception:
            enriched = {**lead, "score": 0, "classificacao": "❄️ Frio",
                        "insight": "Erro no processamento.", "criterios_aplicados": [],
                        "closer": ""}
        processados.append(enriched)
        if i < 5:
            with preview:
                cls   = enriched.get("classificacao", "")
                score = enriched.get("score", 0)
                nicho = enriched.get("nicho", "")
                st.markdown(f"✓ **{nome}** · {nicho} · Score **{score}** · {cls}")

    progress.progress(1.0, text="Concluído!")
    status_box.empty()

    # ACUMULAR no banco (não substitui)
    adicionados = add_leads(processados)

    # Recarregar tudo do banco (inclui leads antigos + novos)
    st.session_state["leads"] = load_leads()
    st.session_state.pop("uploaded_file", None)
    st.session_state["pagina"] = "dashboard"

    st.success(f"✅ {adicionados} leads adicionados/atualizados no banco!")
    st.rerun()


# ── Roteador ──────────────────────────────────────────────────────────────────
def main():
    # Processar atribuição antes de qualquer render
    if "assign_action" in st.session_state:
        action   = st.session_state.pop("assign_action")
        username = action["username"]
        closer   = action["closer"]
        update_closer(username, closer)
        for lead in st.session_state.get("leads", []):
            if lead.get("username") == username:
                lead["closer"] = closer
                break

    # Processar proposta
    if "proposta_action" in st.session_state:
        action   = st.session_state.pop("proposta_action")
        username = action["username"]
        proposta = action["proposta"]
        update_proposta(username, proposta)
        for lead in st.session_state.get("leads", []):
            if lead.get("username") == username:
                lead["proposta"] = proposta
                break

    # Processar exclusão
    if "delete_action" in st.session_state:
        action   = st.session_state.pop("delete_action")
        username = action["username"]
        delete_lead(username)
        st.session_state["leads"] = [
            l for l in st.session_state.get("leads", [])
            if l.get("username") != username
        ]

    # Carregar leads do banco na primeira vez
    if "leads" not in st.session_state:
        st.session_state["leads"] = load_leads()

    # Página padrão
    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "dashboard" if st.session_state["leads"] else "upload"

    leads  = st.session_state["leads"]
    pagina = st.session_state["pagina"]

    # Sidebar sempre visível (exceto processando)
    if pagina != "processando":
        render_sidebar(leads, pagina)

    # Roteamento
    if pagina == "upload":
        tela_upload(leads)
    elif pagina == "processando":
        tela_processando()
    elif pagina == "dashboard":
        render_dashboard(leads)
    elif pagina.startswith("closer_"):
        slug  = pagina.replace("closer_", "")
        nome  = CLOSERS.get(slug, slug.capitalize())
        render_closer_panel(leads, slug, nome)
    elif pagina == "sync":
        render_sync_panel(leads)


if __name__ == "__main__":
    main()
