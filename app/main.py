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
from storage import add_leads, load_leads, update_closer

CLOSERS = {
    "matheus":  "Matheus",
    "jonas":    "Jonas",
    "giovanne": "Giovanne",
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: #0D1B2A !important;
    color: #F1F5F9 !important;
}
header[data-testid="stHeader"] {
    background-color: #0A1628 !important;
    border-bottom: 1px solid #1E3050;
}
.block-container {
    max-width: 1280px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #0A1628 !important;
    border-right: 1px solid #1E3050;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
}
/* Botões da sidebar: fundo transparente por padrão */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #94A3B8 !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    width: 100% !important;
    transition: all 0.15s !important;
    font-size: 14px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #162032 !important;
    color: #F1F5F9 !important;
    border: none !important;
}

/* ── Métricas ── */
div[data-testid="metric-container"] {
    background: #162032 !important;
    border: 1px solid #2D4A6E !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    transition: border-color 0.2s;
}
div[data-testid="metric-container"]:hover { border-color: #F59E0B !important; }
div[data-testid="metric-container"] label { color: #94A3B8 !important; font-size: 13px !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #F1F5F9 !important; font-size: 2rem !important; font-weight: 700 !important;
}

/* ── Expanders ── */
details {
    background: #162032 !important;
    border: 1px solid #2D4A6E !important;
    border-radius: 10px !important;
    margin-bottom: 10px !important;
    overflow: hidden;
}
details summary {
    padding: 14px 18px !important;
    color: #F1F5F9 !important;
    font-weight: 500 !important;
    cursor: pointer;
    background: #162032 !important;
}
details summary:hover { background: #1E3050 !important; }
details[open] summary { border-bottom: 1px solid #2D4A6E; }
details > div { padding: 16px 18px !important; }

/* ── Botões gerais ── */
.block-container .stButton > button {
    border-radius: 8px !important;
    background: #1E3050 !important;
    color: #F1F5F9 !important;
    border: 1px solid #2D4A6E !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
    transition: all 0.2s !important;
}
.block-container .stButton > button:hover {
    background: #F59E0B !important;
    color: #0A1628 !important;
    border-color: #F59E0B !important;
}
a[data-testid="stLinkButton"] {
    border-radius: 8px !important;
    background: #1E3050 !important;
    border: 1px solid #2D4A6E !important;
    color: #F1F5F9 !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
a[data-testid="stLinkButton"]:hover {
    background: #F59E0B !important; border-color: #F59E0B !important; color: #0A1628 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploaderDropzone"] {
    background: #162032 !important;
    border: 2px dashed #2D4A6E !important;
    border-radius: 12px !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: #F59E0B !important; }
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small { color: #94A3B8 !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #162032 !important;
    border: 1px solid #2D4A6E !important;
    border-radius: 8px !important;
    color: #F1F5F9 !important;
}
[data-testid="stCheckbox"] label { color: #F1F5F9 !important; }

/* ── Download ── */
[data-testid="stDownloadButton"] > button {
    background: #F59E0B !important; color: #0A1628 !important;
    border: none !important; border-radius: 8px !important; font-weight: 700 !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #D97706 !important; }

/* ── Progress ── */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #F59E0B, #EF4444) !important;
    border-radius: 4px !important;
}

/* ── Alert ── */
[data-testid="stAlert"] { border-radius: 10px !important; border-left-width: 4px !important; }

/* ── Divider / Caption ── */
hr { border-color: #2D4A6E !important; margin: 16px 0 !important; }
.stCaption, [data-testid="stCaptionContainer"] { color: #64748B !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D1B2A; }
::-webkit-scrollbar-thumb { background: #2D4A6E; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #F59E0B; }
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
            f"<style>[data-testid='stSidebar'] [data-testid='baseButton-secondary'][kind='secondary']"
            f":has(+ [style*='display: none']) + div button[title='{label}']"
            f"{{background:#162032!important;color:#F59E0B!important;"
            f"border-left:3px solid #F59E0B!important;font-weight:700!important}}</style>",
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
            "<div style='padding:12px 4px 20px;border-bottom:1px solid #1E3050;margin-bottom:16px'>"
            "<div style='font-size:1.5rem;margin-bottom:4px'>⚖️</div>"
            "<div style='font-size:0.95rem;font-weight:800;color:#F1F5F9;letter-spacing:-0.3px'>"
            "OAB Lead Qualifier</div>"
            "<div style='font-size:11px;color:#64748B;margin-top:2px'>"
            f"{total} leads no banco</div>"
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

        # Indicador de salvamento automático
        st.markdown(
            "<div style='margin-top:20px;padding:8px 12px;background:#0A1628;border-radius:8px;"
            "border:1px solid #1E3050;text-align:center'>"
            "<span style='font-size:11px;color:#64748B'>💾 Dados salvos automaticamente</span>"
            "</div>",
            unsafe_allow_html=True,
        )


# ── Upload ────────────────────────────────────────────────────────────────────
def tela_upload(leads: list[dict]):
    total = len(leads)

    st.markdown(
        "<h2 style='color:#F1F5F9;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px'>"
        "⬆️ Adicionar leads</h2>"
        "<p style='color:#64748B;margin-bottom:24px'>"
        "Cada upload <strong style='color:#F59E0B'>acumula</strong> os novos leads no banco. "
        "Leads existentes são atualizados sem perder atribuições de closers.</p>",
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


if __name__ == "__main__":
    main()
