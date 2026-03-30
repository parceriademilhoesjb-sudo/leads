"""
pages/data.py — Command Center Dashboard
Acessível em /data · NÃO afeta o app principal
Design: CyberX-inspired dark CRM · Dados reais do SQLite
"""

import streamlit as st
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from storage import load_leads

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Command Center — Avestra CRM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Oculta todo o chrome do Streamlit ────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, header, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stSidebarNav"],
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stApp { background: #0a0b14 !important; }
.block-container { padding: 0 !important; margin: 0 !important;
  max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# ── Carrega e normaliza dados ─────────────────────────────────────────────────
_raw = load_leads()

def _temp(score):
    s = int(score or 0)
    if s >= 70: return "Quente"
    if s >= 45: return "Morno"
    return "Frio"

leads_data = []
for l in _raw:
    leads_data.append({
        "username":      l.get("username", ""),
        "full_name":     (l.get("full_name") or l.get("username") or "").strip(),
        "score":         int(l.get("score") or 0),
        "temperatura":   _temp(l.get("score")),
        "closer":        (l.get("closer") or ""),
        "nicho":         (l.get("nicho") or "Geral"),
        "email":         (l.get("email") or ""),
        "phone":         (l.get("phone_full") or l.get("phone_from_bio") or ""),
        "city":          (l.get("city") or ""),
        "followers":     int(l.get("followers") or 0),
        "is_business":   str(l.get("is_business") or ""),
        "oab_encontrado": bool(l.get("oab_encontrado")),
        "oab_numero":    (l.get("oab_numero") or ""),
        "oab_seccional": (l.get("oab_seccional") or ""),
        "oab_situacao":  (l.get("oab_situacao") or ""),
        "oab_anos":      float(l.get("oab_anos_ativo") or 0),
        "site_encontrado": bool(l.get("site_encontrado")),
        "has_fb_pixel":  bool(l.get("has_fb_pixel")),
        "has_ga":        bool(l.get("has_ga")),
        "has_google_ads": bool(l.get("has_google_ads")),
        "pagespeed":     int(l.get("pagespeed_score") or 0),
        "digital_score": int(l.get("digital_score") or 0),
        "cnpj_numero":   (l.get("cnpj_numero") or ""),
        "cnpj_razao":    (l.get("cnpj_razao_social") or ""),
        "gmb_encontrado": bool(l.get("gmb_encontrado")),
        "gmb_reviews":   int(l.get("gmb_reviews") or 0),
        "has_cta":       bool(l.get("has_cta")),
        "cta_sem_link":  bool(l.get("cta_sem_link")),
        "insight":       (l.get("insight") or ""),
        "avatar_url":    (l.get("avatar_url") or ""),
        "profile_url":   (l.get("profile_url") or ""),
    })

LEADS_JSON = json.dumps(leads_data, ensure_ascii=False, default=str)
CLOSERS_JSON = json.dumps(["Matheus", "Jonas", "Giovanne", "Say"])

# ── HTML Dashboard ────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Command Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
/* ══════════════════════════════════════════════════════════
   COMMAND CENTER — Design System · CyberX-inspired dark CRM
   ══════════════════════════════════════════════════════════ */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}

:root{{
  --bg-app:       #0a0b14;
  --bg-sidebar:   #0d0e1a;
  --bg-active:    #1a1b2e;
  --bg-card:      rgba(255,255,255,0.04);
  --bg-card-h:    rgba(255,255,255,0.07);
  --bg-row:       rgba(255,255,255,0.02);
  --bg-row-alt:   rgba(255,255,255,0.04);

  --text-1: #ffffff;
  --text-2: rgba(255,255,255,.60);
  --text-3: rgba(255,255,255,.40);
  --text-4: rgba(255,255,255,.25);

  --quente:    #ef4444;
  --quente-bg: rgba(239,68,68,.15);
  --quente-gl: 0 0 18px rgba(239,68,68,.35),0 0 36px rgba(239,68,68,.18);
  --morno:     #f59e0b;
  --morno-bg:  rgba(245,158,11,.15);
  --morno-gl:  0 0 18px rgba(245,158,11,.35),0 0 36px rgba(245,158,11,.18);
  --frio:      #3b82f6;
  --frio-bg:   rgba(59,130,246,.10);
  --frio-gl:   0 0 12px rgba(59,130,246,.25);

  --accent:   #3b82f6;
  --indigo:   #6366f1;
  --success:  #10b981;
  --danger:   #ef4444;
  --warning:  #f59e0b;

  --border:   1px solid rgba(255,255,255,.06);
  --border-h: 1px solid rgba(255,255,255,.12);
  --border-a: 1px solid rgba(59,130,246,.35);

  --r-sm:4px;--r-md:10px;--r-lg:14px;--r-xl:20px;--r-full:9999px;
  --font:'DM Sans',sans-serif;
  --sidebar:240px;
  --topbar:64px;
}}

html,body{{
  font-family:var(--font);
  background:var(--bg-app);
  color:var(--text-1);
  height:100%;
  overflow:hidden;
}}

/* ── Atmospheric gradient ── */
body::before{{
  content:'';
  position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse 70% 50% at 80% 0%,rgba(79,70,229,.13) 0%,transparent 55%),
    radial-gradient(ellipse 50% 40% at 20% 100%,rgba(59,130,246,.07) 0%,transparent 45%),
    radial-gradient(ellipse 40% 30% at 50% 50%,rgba(99,102,241,.04) 0%,transparent 60%);
}}

/* ── Stars ── */
@keyframes starFloat{{
  from{{transform:translateY(0)}}
  to{{transform:translateY(-800px)}}
}}
.stars{{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}}
.stars span{{
  position:absolute;width:1px;height:1px;background:#fff;border-radius:50%;
  animation:starFloat linear infinite;opacity:.4;
}}

/* ── Layout ── */
#app{{
  display:grid;
  grid-template-columns:var(--sidebar) 1fr;
  grid-template-rows:var(--topbar) 1fr;
  height:100vh;
  position:relative;z-index:1;
}}

/* ── Sidebar ── */
#sidebar{{
  grid-row:1/-1;
  background:var(--bg-sidebar);
  border-right:var(--border);
  display:flex;flex-direction:column;
  padding:24px 16px;
  gap:4px;
  overflow-y:auto;
}}

.brand{{
  display:flex;align-items:center;gap:10px;
  padding:0 8px 24px;
  border-bottom:var(--border);margin-bottom:16px;
}}
.brand-icon{{
  width:36px;height:36px;border-radius:10px;
  background:linear-gradient(135deg,#4f46e5,#3b82f6);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;flex-shrink:0;
}}
.brand-name{{font-size:15px;font-weight:700;color:var(--text-1);letter-spacing:-.02em}}
.brand-sub{{font-size:11px;color:var(--text-3);margin-top:1px}}

.nav-section{{font-size:10px;font-weight:600;text-transform:uppercase;
  letter-spacing:.08em;color:var(--text-4);padding:12px 8px 4px;}}

.nav-item{{
  display:flex;align-items:center;gap:10px;
  padding:10px 12px;border-radius:var(--r-md);
  cursor:pointer;transition:all .18s;
  color:var(--text-2);font-size:14px;font-weight:500;
  border:1px solid transparent;
}}
.nav-item:hover{{background:rgba(255,255,255,.04);color:var(--text-1)}}
.nav-item.active{{
  background:var(--bg-active);color:var(--text-1);
  border:var(--border-a);
}}
.nav-item .nav-icon{{font-size:16px;opacity:.8;width:20px;text-align:center}}
.nav-item .nav-badge{{
  margin-left:auto;font-size:11px;font-weight:700;
  background:rgba(59,130,246,.2);color:var(--accent);
  padding:2px 8px;border-radius:var(--r-full);
}}
.nav-divider{{height:1px;background:rgba(255,255,255,.05);margin:12px 0}}

.sidebar-footer{{
  margin-top:auto;padding-top:16px;border-top:var(--border);
  display:flex;align-items:center;gap:10px;
}}
.avatar-circle{{
  width:34px;height:34px;border-radius:50%;
  background:linear-gradient(135deg,var(--indigo),var(--accent));
  display:flex;align-items:center;justify-content:center;
  font-size:14px;font-weight:700;flex-shrink:0;
}}
.sidebar-user-name{{font-size:13px;font-weight:600;color:var(--text-1)}}
.sidebar-user-role{{font-size:11px;color:var(--text-3)}}

/* ── Top bar ── */
#topbar{{
  background:rgba(13,14,26,.8);backdrop-filter:blur(12px);
  border-bottom:var(--border);
  display:flex;align-items:center;gap:16px;padding:0 32px;
  position:sticky;top:0;z-index:10;
}}
.breadcrumb{{display:flex;align-items:center;gap:6px;color:var(--text-3);font-size:13px}}
.breadcrumb .sep{{opacity:.4}}
.breadcrumb .current{{color:var(--text-1)}}
.topbar-right{{margin-left:auto;display:flex;align-items:center;gap:12px}}
.topbar-btn{{
  width:36px;height:36px;border-radius:var(--r-md);
  background:var(--bg-card);border:var(--border);
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;color:var(--text-2);font-size:16px;
  transition:all .18s;
}}
.topbar-btn:hover{{background:var(--bg-card-h);color:var(--text-1)}}
.live-badge{{
  display:flex;align-items:center;gap:6px;
  background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.2);
  color:#10b981;font-size:12px;font-weight:600;
  padding:5px 12px;border-radius:var(--r-full);
}}
.live-dot{{width:7px;height:7px;border-radius:50%;background:#10b981;
  animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}

/* ── Content ── */
#content{{
  overflow-y:auto;padding:32px 40px;
  scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.1) transparent;
}}

.view{{display:none}}
.view.active{{display:block}}

/* ── Page header ── */
.page-title{{font-size:30px;font-weight:400;color:var(--text-1);margin-bottom:4px}}
.page-sub{{font-size:14px;color:var(--text-3);margin-bottom:28px}}

/* ── Stat cards ── */
.stat-grid{{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:16px;margin-bottom:24px;
}}
@media(max-width:1100px){{.stat-grid{{grid-template-columns:repeat(2,1fr)}}}}

.stat-card{{
  background:var(--bg-card);
  backdrop-filter:blur(12px);
  border:var(--border);border-radius:var(--r-lg);
  padding:20px 24px;
  transition:all .2s;
  position:relative;overflow:hidden;
}}
.stat-card::after{{
  content:'';position:absolute;top:0;right:0;
  width:80px;height:80px;border-radius:50%;
  filter:blur(40px);opacity:.5;
}}
.stat-card.quente{{border-left:3px solid var(--quente)}}
.stat-card.quente::after{{background:var(--quente)}}
.stat-card.morno{{border-left:3px solid var(--morno)}}
.stat-card.morno::after{{background:var(--morno)}}
.stat-card.frio{{border-left:3px solid var(--frio)}}
.stat-card.frio::after{{background:var(--frio)}}
.stat-card.total{{border-left:3px solid var(--indigo)}}
.stat-card.total::after{{background:var(--indigo)}}
.stat-card:hover{{background:var(--bg-card-h);border:var(--border-h)}}

.stat-label{{font-size:12px;font-weight:500;text-transform:uppercase;
  letter-spacing:.06em;color:var(--text-3);margin-bottom:10px}}
.stat-value{{font-size:38px;font-weight:400;color:var(--text-1);
  font-variant-numeric:tabular-nums;line-height:1}}
.stat-change{{
  font-size:12px;font-weight:600;margin-top:8px;
  display:flex;align-items:center;gap:4px;
}}
.stat-change.up{{color:var(--success)}}
.stat-change.dn{{color:var(--danger)}}

/* ── Cards de conteúdo ── */
.card{{
  background:var(--bg-card);backdrop-filter:blur(12px);
  border:var(--border);border-radius:var(--r-lg);padding:24px;
  transition:border .2s;
}}
.card:hover{{border:var(--border-h)}}
.card-title{{font-size:15px;font-weight:600;color:var(--text-1);margin-bottom:16px;
  display:flex;align-items:center;gap:8px}}
.card-title .card-icon{{font-size:16px;opacity:.7}}

/* ── Two-column grid ── */
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}}
.three-col{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:24px}}

/* ── Funnel items ── */
.funnel-item{{
  display:flex;align-items:center;gap:14px;
  padding:12px 0;border-bottom:var(--border);
}}
.funnel-item:last-child{{border-bottom:none}}
.funnel-label{{font-size:13px;color:var(--text-2);width:100px;flex-shrink:0}}
.funnel-bar-wrap{{flex:1;height:6px;background:rgba(255,255,255,.08);border-radius:3px;overflow:hidden}}
.funnel-bar{{height:100%;border-radius:3px;transition:width .6s cubic-bezier(.4,0,.2,1)}}
.funnel-count{{font-size:14px;font-weight:600;color:var(--text-1);
  width:40px;text-align:right;font-variant-numeric:tabular-nums}}

/* ── Temperature badge ── */
.temp-badge{{
  display:inline-flex;align-items:center;gap:5px;
  padding:4px 10px;border-radius:var(--r-full);
  font-size:11px;font-weight:700;letter-spacing:.03em;
}}
.temp-badge.Quente{{
  background:var(--quente-bg);color:var(--quente);
  box-shadow:var(--quente-gl);
}}
.temp-badge.Morno{{background:var(--morno-bg);color:var(--morno)}}
.temp-badge.Frio{{background:var(--frio-bg);color:var(--frio)}}

/* ── Score bar (CyberX style) ── */
.score-wrap{{display:flex;align-items:center;gap:10px}}
.score-bars{{
  display:flex;align-items:flex-end;gap:1.5px;height:20px;
}}
.score-bars .bar{{
  width:3px;border-radius:1px;
  transition:opacity .3s;
}}
.score-num{{font-size:13px;font-weight:600;color:var(--text-2);
  font-variant-numeric:tabular-nums;min-width:28px}}

/* ── Tabela de leads ── */
.table-wrap{{overflow-x:auto;}}
.leads-table{{width:100%;border-collapse:collapse;font-size:13px}}
.leads-table th{{
  font-size:11px;font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;color:var(--text-3);
  padding:10px 14px;text-align:left;
  border-bottom:var(--border);white-space:nowrap;cursor:pointer;
}}
.leads-table th:hover{{color:var(--text-1)}}
.leads-table td{{
  padding:12px 14px;border-bottom:var(--border);
  color:var(--text-2);vertical-align:middle;
}}
.leads-table tr:hover td{{background:rgba(255,255,255,.03);color:var(--text-1)}}
.leads-table tr:nth-child(even) td{{background:var(--bg-row-alt)}}

.lead-name{{font-weight:600;color:var(--text-1);font-size:13px}}
.lead-handle{{font-size:11px;color:var(--text-4);margin-top:1px}}

.oab-badge{{
  display:inline-flex;align-items:center;gap:4px;
  padding:2px 8px;border-radius:var(--r-sm);font-size:11px;font-weight:600;
  background:rgba(16,185,129,.12);color:#10b981;
}}
.no-badge{{
  padding:2px 8px;border-radius:var(--r-sm);font-size:11px;
  background:rgba(255,255,255,.05);color:var(--text-4);
}}

/* ── Filtros ── */
.filters{{
  display:flex;align-items:center;gap:10px;
  margin-bottom:20px;flex-wrap:wrap;
}}
.filter-btn{{
  padding:7px 16px;border-radius:var(--r-full);
  font-size:12px;font-weight:600;cursor:pointer;
  border:var(--border);background:var(--bg-card);color:var(--text-2);
  transition:all .18s;
}}
.filter-btn:hover{{border:var(--border-h);color:var(--text-1)}}
.filter-btn.active{{
  background:rgba(59,130,246,.15);border:var(--border-a);color:var(--accent);
}}
.search-box{{
  flex:1;max-width:280px;
  background:var(--bg-card);border:var(--border);
  border-radius:var(--r-md);padding:8px 14px;
  color:var(--text-1);font-family:var(--font);font-size:13px;
  outline:none;transition:border .18s;
}}
.search-box:focus{{border:var(--border-a)}}
.search-box::placeholder{{color:var(--text-4)}}

/* ── Kanban ── */
.kanban-wrap{{
  display:grid;
  gap:16px;overflow-x:auto;padding-bottom:16px;
}}
.kanban-col{{
  background:rgba(255,255,255,.02);border:var(--border);
  border-radius:var(--r-lg);min-width:220px;
  display:flex;flex-direction:column;
}}
.kanban-header{{
  padding:14px 16px;border-bottom:var(--border);
  display:flex;align-items:center;justify-content:space-between;
}}
.kanban-col-name{{font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:.06em;color:var(--text-3)}}
.kanban-count{{
  font-size:11px;font-weight:700;
  background:rgba(255,255,255,.08);color:var(--text-2);
  padding:2px 8px;border-radius:var(--r-full);
}}
.kanban-body{{flex:1;padding:12px;display:flex;flex-direction:column;gap:8px;
  overflow-y:auto;max-height:580px}}

.kcard{{
  background:var(--bg-card);border:var(--border);
  border-radius:var(--r-md);padding:12px 14px;
  transition:all .18s;
}}
.kcard:hover{{background:var(--bg-card-h);border:var(--border-h);
  transform:translateY(-1px)}}
.kcard.quente{{border-left:3px solid var(--quente)}}
.kcard.morno{{border-left:3px solid var(--morno)}}
.kcard.frio{{border-left:3px solid rgba(59,130,246,.4)}}
.kcard-name{{font-size:13px;font-weight:600;color:var(--text-1);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.kcard-meta{{font-size:11px;color:var(--text-4);margin-top:2px}}
.kcard-footer{{display:flex;align-items:center;justify-content:space-between;margin-top:10px}}
.kcard-nicho{{font-size:10px;color:var(--text-3);
  background:rgba(255,255,255,.05);padding:2px 8px;border-radius:var(--r-full)}}

/* ── Closer perf ── */
.closer-grid{{
  display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px;
  margin-bottom:24px;
}}
.closer-card{{
  background:var(--bg-card);border:var(--border);border-radius:var(--r-lg);
  padding:20px;transition:all .2s;
}}
.closer-card:hover{{background:var(--bg-card-h);border:var(--border-h)}}
.closer-name{{font-size:15px;font-weight:700;color:var(--text-1);margin-bottom:4px}}
.closer-total{{font-size:32px;font-weight:400;color:var(--text-1);
  font-variant-numeric:tabular-nums;margin:8px 0 4px}}
.closer-sub{{font-size:12px;color:var(--text-3)}}
.closer-temps{{display:flex;gap:6px;margin-top:12px}}
.closer-temp-pill{{
  flex:1;text-align:center;padding:5px 0;border-radius:var(--r-sm);
  font-size:11px;font-weight:700;
}}

/* ── Nicho pills ── */
.nicho-list{{display:flex;flex-direction:column;gap:8px}}
.nicho-row{{display:flex;align-items:center;gap:10px}}
.nicho-name{{font-size:13px;color:var(--text-2);width:130px;flex-shrink:0;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.nicho-bar-wrap{{flex:1;height:6px;background:rgba(255,255,255,.07);border-radius:3px}}
.nicho-bar{{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--indigo),var(--accent))}}
.nicho-n{{font-size:12px;color:var(--text-3);width:28px;text-align:right;
  font-variant-numeric:tabular-nums}}

/* ── Empty state ── */
.empty-state{{
  text-align:center;padding:40px 20px;color:var(--text-3);
  font-size:13px;
}}

/* ── Flow SVG ── */
.flow-container{{
  width:100%;height:260px;position:relative;
  display:flex;align-items:center;
}}
#flow-svg{{width:100%;height:100%}}

/* ── Scrollbar ── */
::-webkit-scrollbar{{width:4px;height:4px}}
::-webkit-scrollbar-track{{background:transparent}}
::-webkit-scrollbar-thumb{{background:rgba(255,255,255,.1);border-radius:2px}}

/* ── Animations ── */
@keyframes fadeInUp{{
  from{{opacity:0;transform:translateY(12px)}}
  to{{opacity:1;transform:translateY(0)}}
}}
.view.active .card,.view.active .stat-card{{
  animation:fadeInUp .3s ease both;
}}
.view.active .stat-card:nth-child(1){{animation-delay:.05s}}
.view.active .stat-card:nth-child(2){{animation-delay:.10s}}
.view.active .stat-card:nth-child(3){{animation-delay:.15s}}
.view.active .stat-card:nth-child(4){{animation-delay:.20s}}

/* ── Chart canvas ── */
.chart-box{{position:relative;height:200px}}

/* ── Integration banners ── */
.integration-row{{
  display:flex;align-items:center;gap:12px;
  padding:12px 16px;border-radius:var(--r-md);
  background:rgba(255,255,255,.03);border:var(--border);
  margin-bottom:8px;
}}
.int-icon{{font-size:20px;width:32px;text-align:center}}
.int-name{{font-size:13px;font-weight:600;color:var(--text-1)}}
.int-status{{font-size:11px;color:var(--text-3);margin-top:1px}}
.int-badge{{
  margin-left:auto;padding:3px 10px;border-radius:var(--r-full);
  font-size:11px;font-weight:700;
}}
.int-badge.ok{{background:rgba(16,185,129,.15);color:#10b981}}
.int-badge.pending{{background:rgba(245,158,11,.12);color:var(--warning)}}
.int-badge.offline{{background:rgba(255,255,255,.07);color:var(--text-3)}}

/* ── Tooltip ── */
.tooltip{{
  position:relative;display:inline-block;
}}
.tooltip:hover::after{{
  content:attr(data-tip);
  position:absolute;bottom:125%;left:50%;transform:translateX(-50%);
  background:rgba(255,255,255,.95);color:#1a1b2e;
  font-size:11px;padding:5px 10px;border-radius:6px;
  white-space:nowrap;z-index:100;
}}
</style>
</head>
<body>

<!-- Stars background -->
<div class="stars" id="stars-bg"></div>

<div id="app">

  <!-- ══ SIDEBAR ══ -->
  <aside id="sidebar">
    <div class="brand">
      <div class="brand-icon">⚖️</div>
      <div>
        <div class="brand-name">Avestra CRM</div>
        <div class="brand-sub">Command Center</div>
      </div>
    </div>

    <div class="nav-section">Análise</div>
    <div class="nav-item active" data-view="dashboard">
      <span class="nav-icon">📊</span>
      Dashboard
      <span class="nav-badge" id="nb-total">0</span>
    </div>
    <div class="nav-item" data-view="pipeline">
      <span class="nav-icon">🔀</span>
      Pipeline
    </div>

    <div class="nav-section">Gestão</div>
    <div class="nav-item" data-view="leads">
      <span class="nav-icon">👥</span>
      Todos os Leads
    </div>
    <div class="nav-item" data-view="closers">
      <span class="nav-icon">🎯</span>
      Closers
    </div>

    <div class="nav-divider"></div>
    <div class="nav-section">Integrações</div>
    <div class="nav-item" data-view="integrations">
      <span class="nav-icon">🔌</span>
      Conectar APIs
    </div>

    <div class="sidebar-footer">
      <div class="avatar-circle">A</div>
      <div>
        <div class="sidebar-user-name">Avestra</div>
        <div class="sidebar-user-role">Admin</div>
      </div>
    </div>
  </aside>

  <!-- ══ TOP BAR ══ -->
  <header id="topbar">
    <div class="breadcrumb">
      <span>Avestra CRM</span>
      <span class="sep">›</span>
      <span class="current" id="bc-current">Dashboard</span>
    </div>
    <div class="topbar-right">
      <div class="live-badge">
        <span class="live-dot"></span>
        SQLite · Live
      </div>
      <div class="topbar-btn" title="Atualizar" onclick="location.reload()">↻</div>
      <div class="topbar-btn" title="Voltar ao CRM" onclick="window.parent.location.href='/'">⬅</div>
    </div>
  </header>

  <!-- ══ CONTENT ══ -->
  <main id="content">

    <!-- ════════════════════════════════ VIEW: DASHBOARD ════ -->
    <div id="view-dashboard" class="view active">
      <div class="page-title">Exposure Command Center</div>
      <div class="page-sub" id="dash-subtitle">Visão geral da pipeline de leads qualificados</div>

      <!-- Stat Cards -->
      <div class="stat-grid" id="stat-grid"></div>

      <!-- Row 1 -->
      <div class="two-col">
        <!-- Flow Visualization -->
        <div class="card">
          <div class="card-title"><span class="card-icon">〰️</span> Fluxo por Origem de Temperatura</div>
          <div class="flow-container">
            <svg id="flow-svg" viewBox="0 0 560 240"></svg>
          </div>
        </div>

        <!-- Funil -->
        <div class="card">
          <div class="card-title"><span class="card-icon">📐</span> Funil de Qualificação</div>
          <div id="funnel-view"></div>
        </div>
      </div>

      <!-- Row 2 -->
      <div class="two-col">
        <!-- Nichos -->
        <div class="card">
          <div class="card-title"><span class="card-icon">⚖️</span> Leads por Nicho Jurídico</div>
          <div class="nicho-list" id="nicho-list"></div>
        </div>

        <!-- Closers snapshot -->
        <div class="card">
          <div class="card-title"><span class="card-icon">🎯</span> Closers — Snapshot</div>
          <div class="chart-box"><canvas id="chart-closers"></canvas></div>
        </div>
      </div>

      <!-- Recentes -->
      <div class="card">
        <div class="card-title"><span class="card-icon">🕐</span> Últimos Leads — Score Mais Alto</div>
        <div class="table-wrap">
          <table class="leads-table">
            <thead>
              <tr>
                <th>Lead</th>
                <th>Score</th>
                <th>Temperatura</th>
                <th>Nicho</th>
                <th>OAB</th>
                <th>Site</th>
                <th>Pixel</th>
                <th>Closer</th>
              </tr>
            </thead>
            <tbody id="recent-tbody"></tbody>
          </table>
        </div>
      </div>
    </div><!-- /dashboard -->

    <!-- ════════════════════════════════ VIEW: PIPELINE ════ -->
    <div id="view-pipeline" class="view">
      <div class="page-title">Pipeline de Leads</div>
      <div class="page-sub">Organização por closer · Score mais alto ao topo</div>

      <div class="filters">
        <button class="filter-btn active" data-pf="all">Todos</button>
        <button class="filter-btn" data-pf="Quente">🔴 Quentes</button>
        <button class="filter-btn" data-pf="Morno">🟡 Mornos</button>
        <button class="filter-btn" data-pf="Frio">🔵 Frios</button>
      </div>

      <div class="kanban-wrap" id="kanban-board"></div>
    </div>

    <!-- ════════════════════════════════ VIEW: LEADS ════ -->
    <div id="view-leads" class="view">
      <div class="page-title">Todos os Leads</div>
      <div class="page-sub" id="leads-count-line"></div>

      <div class="filters">
        <input class="search-box" id="search-input" placeholder="🔍  Buscar por nome, @ ou nicho...">
        <button class="filter-btn active" data-tf="all">Todos</button>
        <button class="filter-btn" data-tf="Quente">🔴 Quente</button>
        <button class="filter-btn" data-tf="Morno">🟡 Morno</button>
        <button class="filter-btn" data-tf="Frio">🔵 Frio</button>
        <button class="filter-btn" id="export-btn">⬇ Exportar CSV</button>
      </div>

      <div class="card" style="padding:0">
        <div class="table-wrap">
          <table class="leads-table" id="leads-table">
            <thead>
              <tr>
                <th data-sort="full_name">Lead ↕</th>
                <th data-sort="score">Score ↕</th>
                <th>Temperatura</th>
                <th>Nicho</th>
                <th>OAB</th>
                <th>Site</th>
                <th>Pixel FB</th>
                <th>Seguidores</th>
                <th>Contato</th>
                <th>Closer</th>
                <th>Insight</th>
              </tr>
            </thead>
            <tbody id="leads-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════ VIEW: CLOSERS ════ -->
    <div id="view-closers" class="view">
      <div class="page-title">Performance dos Closers</div>
      <div class="page-sub">Distribuição de leads por consultor</div>

      <div class="closer-grid" id="closer-grid"></div>

      <div class="two-col">
        <div class="card">
          <div class="card-title"><span class="card-icon">📊</span> Score Médio por Closer</div>
          <div class="chart-box"><canvas id="chart-closer-score"></canvas></div>
        </div>
        <div class="card">
          <div class="card-title"><span class="card-icon">🌡️</span> Distribuição de Temperatura</div>
          <div class="chart-box"><canvas id="chart-closer-temp"></canvas></div>
        </div>
      </div>

      <div class="card">
        <div class="card-title"><span class="card-icon">🏆</span> Leads por Closer — Detalhado</div>
        <div class="table-wrap">
          <table class="leads-table" id="closers-leads-table">
            <thead>
              <tr>
                <th>Lead</th><th>Score</th><th>Temperatura</th>
                <th>Nicho</th><th>OAB</th><th>Closer</th>
              </tr>
            </thead>
            <tbody id="closers-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════ VIEW: INTEGRATIONS ════ -->
    <div id="view-integrations" class="view">
      <div class="page-title">Integrações &amp; APIs</div>
      <div class="page-sub">Conecte fontes externas de dados para enriquecer o dashboard</div>

      <div class="two-col">
        <div class="card">
          <div class="card-title"><span class="card-icon">🔌</span> Status das Conexões</div>

          <div class="integration-row">
            <span class="int-icon">📦</span>
            <div>
              <div class="int-name">SQLite Local</div>
              <div class="int-status">Banco principal · dados reais</div>
            </div>
            <span class="int-badge ok">✓ Ativo</span>
          </div>

          <div class="integration-row">
            <span class="int-icon">🔥</span>
            <div>
              <div class="int-name">Firebase / Firestore</div>
              <div class="int-status">Real-time listeners · pendente configuração</div>
            </div>
            <span class="int-badge pending">⚙ Config</span>
          </div>

          <div class="integration-row">
            <span class="int-icon">📘</span>
            <div>
              <div class="int-name">Meta Ads (Facebook)</div>
              <div class="int-status">Campanhas · CPL · Resultados</div>
            </div>
            <span class="int-badge offline">○ Offline</span>
          </div>

          <div class="integration-row">
            <span class="int-icon">🔎</span>
            <div>
              <div class="int-name">Google Analytics 4</div>
              <div class="int-status">Sessões · conversões · funil</div>
            </div>
            <span class="int-badge offline">○ Offline</span>
          </div>

          <div class="integration-row">
            <span class="int-icon">📈</span>
            <div>
              <div class="int-name">Google Ads</div>
              <div class="int-status">Custo por lead qualificado</div>
            </div>
            <span class="int-badge offline">○ Offline</span>
          </div>
        </div>

        <div class="card">
          <div class="card-title"><span class="card-icon">🛠️</span> Como Conectar</div>
          <div style="color:var(--text-2);font-size:13px;line-height:1.7">
            <p style="margin-bottom:12px">
              <strong style="color:var(--text-1)">Firebase:</strong><br>
              Adicione as variáveis de ambiente no Railway:<br>
              <code style="font-size:11px;color:var(--accent)">
                FIREBASE_API_KEY, FIREBASE_PROJECT_ID,<br>
                FIREBASE_APP_ID
              </code>
            </p>
            <p style="margin-bottom:12px">
              <strong style="color:var(--text-1)">Meta Ads:</strong><br>
              <code style="font-size:11px;color:var(--accent)">META_ACCESS_TOKEN, META_AD_ACCOUNT_ID</code>
            </p>
            <p>
              <strong style="color:var(--text-1)">Google Analytics 4:</strong><br>
              <code style="font-size:11px;color:var(--accent)">GA4_PROPERTY_ID, GA4_CREDENTIALS_JSON</code>
            </p>
            <div style="margin-top:16px;padding:12px;background:rgba(59,130,246,.08);
              border:1px solid rgba(59,130,246,.2);border-radius:10px;font-size:12px;
              color:var(--text-2)">
              💡 Quando as variáveis estiverem configuradas no Railway,<br>
              este painel atualizará automaticamente com dados reais.
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title"><span class="card-icon">📊</span> Preview — Dados Disponíveis (SQLite)</div>
        <div class="three-col" id="integration-stats"></div>
      </div>
    </div>

  </main>
</div>

<script>
// ═══════════════════════════════════════════════════════════════
// DATA — injetado pelo Python
// ═══════════════════════════════════════════════════════════════
const LEADS = {LEADS_JSON};
const CLOSERS = {CLOSERS_JSON};

// ═══════════════════════════════════════════════════════════════
// UTILS
// ═══════════════════════════════════════════════════════════════
const $ = id => document.getElementById(id);
const el = (tag, cls, html) => {{
  const e = document.createElement(tag);
  if(cls) e.className = cls;
  if(html) e.innerHTML = html;
  return e;
}};

function scoreColor(s) {{
  if(s >= 70) return '#ef4444';
  if(s >= 45) return '#f59e0b';
  return '#3b82f6';
}}

function renderScoreBar(score) {{
  const total = 36;
  const filled = Math.round((score/100)*total);
  let bars = '';
  for(let i=0;i<total;i++) {{
    const pct = ((i+1)/total)*100;
    let col = '#10b981'; // green
    if(pct > 70) col = '#ef4444';   // red
    else if(pct > 45) col = '#f59e0b'; // amber
    const h = 8 + Math.round(Math.random()*12);
    const op = i < filled ? '1' : '0.12';
    bars += `<span class="bar" style="height:${{h}}px;background:${{col}};opacity:${{op}}"></span>`;
  }}
  return `<div class="score-wrap">
    <div class="score-bars">${{bars}}</div>
    <span class="score-num" style="color:${{scoreColor(score)}}">${{score}}%</span>
  </div>`;
}}

function tempBadge(t) {{
  const icons = {{Quente:'🔴',Morno:'🟡',Frio:'🔵'}};
  return `<span class="temp-badge ${{t}}">${{icons[t]||''}} ${{t}}</span>`;
}}

function oabBadge(lead) {{
  if(lead.oab_encontrado && lead.oab_situacao === 'ATIVO') {{
    return `<span class="oab-badge">✓ ${{lead.oab_numero}} ${{lead.oab_seccional}}</span>`;
  }}
  return `<span class="no-badge">—</span>`;
}}

function checkBool(v) {{
  return v ? '<span style="color:#10b981;font-size:16px">✓</span>'
           : '<span style="color:rgba(255,255,255,.2);font-size:16px">—</span>';
}}

function fmt(n) {{
  if(n >= 1000000) return (n/1000000).toFixed(1)+'M';
  if(n >= 1000) return (n/1000).toFixed(1)+'k';
  return String(n);
}}

// ═══════════════════════════════════════════════════════════════
// STARS BACKGROUND
// ═══════════════════════════════════════════════════════════════
(function() {{
  const c = $('stars-bg');
  for(let i=0;i<80;i++) {{
    const s = document.createElement('span');
    s.style.cssText = `
      left:${{Math.random()*100}}%;
      top:${{Math.random()*100}}%;
      width:${{Math.random()<.3?2:1}}px;
      height:${{Math.random()<.3?2:1}}px;
      opacity:${{(.2+Math.random()*.4).toFixed(2)}};
      animation-duration:${{30+Math.random()*70}}s;
      animation-delay:${{-Math.random()*80}}s;
    `;
    c.appendChild(s);
  }}
}})();

// ═══════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════
const BREADCRUMBS = {{
  dashboard: 'Dashboard',
  pipeline: 'Pipeline',
  leads: 'Todos os Leads',
  closers: 'Closers',
  integrations: 'Integrações',
}};

let currentView = 'dashboard';

document.querySelectorAll('.nav-item[data-view]').forEach(item => {{
  item.addEventListener('click', () => {{
    const v = item.dataset.view;
    navigate(v);
  }});
}});

function navigate(v) {{
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector(`[data-view="${{v}}"]`)?.classList.add('active');
  document.querySelectorAll('.view').forEach(x => x.classList.remove('active'));
  const el = $('view-'+v);
  if(el) el.classList.add('active');
  $('bc-current').textContent = BREADCRUMBS[v] || v;
  currentView = v;
  renderView(v);
}}

function renderView(v) {{
  if(v==='dashboard') renderDashboard();
  else if(v==='pipeline') renderPipeline();
  else if(v==='leads') renderLeadsTable();
  else if(v==='closers') renderClosers();
  else if(v==='integrations') renderIntegrations();
}}

// ═══════════════════════════════════════════════════════════════
// DATA PROCESSING
// ═══════════════════════════════════════════════════════════════
const total = LEADS.length;
const quentes = LEADS.filter(l => l.temperatura==='Quente');
const mornos  = LEADS.filter(l => l.temperatura==='Morno');
const frios   = LEADS.filter(l => l.temperatura==='Frio');

const byCloser = {{}};
LEADS.forEach(l => {{
  const k = l.closer || 'Sem Closer';
  if(!byCloser[k]) byCloser[k] = [];
  byCloser[k].push(l);
}});

const byNicho = {{}};
LEADS.forEach(l => {{
  const n = l.nicho || 'Geral';
  byNicho[n] = (byNicho[n]||0)+1;
}});

// ═══════════════════════════════════════════════════════════════
// RENDER: DASHBOARD
// ═══════════════════════════════════════════════════════════════
function renderDashboard() {{
  $('nb-total').textContent = total;
  $('dash-subtitle').textContent =
    `${{total}} leads qualificados · ${{quentes.length}} prontos para fechar`;

  // Stat cards
  const sg = $('stat-grid');
  const avgScore = total ? Math.round(LEADS.reduce((a,l)=>a+l.score,0)/total) : 0;
  const withContact = LEADS.filter(l=>l.email||l.phone).length;

  sg.innerHTML = `
    ${{statCard('Total de Leads', total, 'total', '📋', null)}}
    ${{statCard('Leads Quentes', quentes.length, 'quente', '🔥',
      total ? '+'+Math.round(quentes.length/total*100)+'% do pipeline' : null)}}
    ${{statCard('Leads Mornos', mornos.length, 'morno', '🟡',
      total ? Math.round(mornos.length/total*100)+'% do pipeline' : null)}}
    ${{statCard('Score Médio', avgScore, 'frio', '📊',
      'Com contato: '+withContact+' leads')}}
  `;

  renderFlow();
  renderFunnel();
  renderNichos();
  renderClosersChart();
  renderRecentTable();
}}

function statCard(label, value, cls, icon, sub) {{
  return `
    <div class="stat-card ${{cls}}">
      <div class="stat-label">${{label}}</div>
      <div class="stat-value">${{value}}</div>
      ${{sub ? `<div class="stat-change">${{sub}}</div>` : ''}}
    </div>`;
}}

// ── Flow visualization ──────────────────────────────────────
function renderFlow() {{
  const svg = $('flow-svg');
  if(!svg) return;

  const W=560, H=240;
  const sources = [
    {{label:'Previdenciário', count: (byNicho['Previdenciário']||0)}},
    {{label:'Trabalhista',    count: (byNicho['Trabalhista']||0)}},
    {{label:'Família',       count: (byNicho['Família']||0)}},
    {{label:'Criminal',      count: (byNicho['Criminal']||0)}},
    {{label:'Empresarial',   count: (byNicho['Empresarial']||0)}},
    {{label:'Outros',        count: total - (byNicho['Previdenciário']||0)
      - (byNicho['Trabalhista']||0) - (byNicho['Família']||0)
      - (byNicho['Criminal']||0) - (byNicho['Empresarial']||0)}},
  ].filter(s=>s.count>0);

  const targets = [
    {{label:'🔴 Quente', count:quentes.length, col:'#ef4444'}},
    {{label:'🟡 Morno',  count:mornos.length,  col:'#f59e0b'}},
    {{label:'🔵 Frio',   count:frios.length,   col:'#3b82f6'}},
  ];

  const cx=W/2, cy=H/2, cr=50;
  const srcX=60, tgtX=W-60;

  let lines='', srcLabels='', tgtLabels='';
  const srcStep = H/(sources.length+1);
  const tgtStep = H/(targets.length+1);

  sources.forEach((s,i) => {{
    const y = srcStep*(i+1);
    const c = `rgba(99,102,241,${{(0.15+s.count/total*.5).toFixed(2)}})`;
    const sw = Math.max(1, Math.round(s.count/total*8));
    lines += `<path d="M${{srcX}},${{y}} C${{cx-80}},${{y}} ${{cx-80}},${{cy}} ${{cx-cr}},${{cy}}"
      fill="none" stroke="${{c}}" stroke-width="${{sw}}" opacity=".7"/>`;
    srcLabels += `<text x="${{srcX-8}}" y="${{y+4}}" text-anchor="end"
      font-family="DM Sans,sans-serif" font-size="11" fill="rgba(255,255,255,.5)"
      >${{s.label}} (${{s.count}})</text>`;
  }});

  targets.forEach((t,i) => {{
    const y = tgtStep*(i+1);
    const sw = Math.max(1, Math.round(t.count/total*10));
    lines += `<path d="M${{cx+cr}},${{cy}} C${{cx+80}},${{cy}} ${{cx+80}},${{y}} ${{tgtX}},${{y}}"
      fill="none" stroke="${{t.col}}" stroke-width="${{sw}}" opacity=".6"/>`;
    tgtLabels += `<text x="${{tgtX+8}}" y="${{y+4}}"
      font-family="DM Sans,sans-serif" font-size="11" fill="${{t.col}}"
      >${{t.label}} (${{t.count}})</text>`;
  }});

  svg.innerHTML = `
    <defs>
      <radialGradient id="cg"><stop offset="0%" stop-color="#4f46e5" stop-opacity=".5"/>
      <stop offset="100%" stop-color="#3b82f6" stop-opacity=".1"/></radialGradient>
      <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
    ${{lines}}
    <!-- Center orb -->
    <circle cx="${{cx}}" cy="${{cy}}" r="${{cr+12}}" fill="rgba(79,70,229,.08)" />
    <circle cx="${{cx}}" cy="${{cy}}" r="${{cr}}"    fill="url(#cg)" filter="url(#glow)" />
    <circle cx="${{cx}}" cy="${{cy}}" r="${{cr-8}}"  fill="rgba(79,70,229,.15)" />
    <text x="${{cx}}" y="${{cy-4}}" text-anchor="middle"
      font-family="DM Sans,sans-serif" font-size="22" font-weight="400" fill="#fff"
      >${{total}}</text>
    <text x="${{cx}}" y="${{cy+16}}" text-anchor="middle"
      font-family="DM Sans,sans-serif" font-size="10" fill="rgba(255,255,255,.5)"
      >leads</text>
    ${{srcLabels}}
    ${{tgtLabels}}
  `;
}}

// ── Funnel ──────────────────────────────────────────────────
function renderFunnel() {{
  const funnel = $('funnel-view');
  if(!funnel) return;

  const oabAtivos = LEADS.filter(l=>l.oab_encontrado && l.oab_situacao==='ATIVO').length;
  const comSite   = LEADS.filter(l=>l.site_encontrado).length;
  const comPixel  = LEADS.filter(l=>l.has_fb_pixel||l.has_ga).length;
  const comEmail  = LEADS.filter(l=>l.email).length;
  const comFone   = LEADS.filter(l=>l.phone).length;
  const comCloser = LEADS.filter(l=>l.closer).length;

  const rows = [
    {{label:'Total Leads',     n:total,     col:'#6366f1', bg:'#6366f1'}},
    {{label:'Quentes (70+)',   n:quentes.length, col:'#ef4444',bg:'#ef4444'}},
    {{label:'Mornos (45-69)', n:mornos.length,  col:'#f59e0b',bg:'#f59e0b'}},
    {{label:'Com OAB Ativo',  n:oabAtivos, col:'#10b981',bg:'#10b981'}},
    {{label:'Com E-mail',     n:comEmail,  col:'#3b82f6',bg:'#3b82f6'}},
    {{label:'Com Telefone',   n:comFone,   col:'#8b5cf6',bg:'#8b5cf6'}},
    {{label:'Atribuídos',     n:comCloser, col:'#06b6d4',bg:'#06b6d4'}},
  ];

  funnel.innerHTML = rows.map(r => `
    <div class="funnel-item">
      <span class="funnel-label">${{r.label}}</span>
      <div class="funnel-bar-wrap">
        <div class="funnel-bar" style="width:${{total?Math.round(r.n/total*100):0}}%;background:${{r.col}}"></div>
      </div>
      <span class="funnel-count">${{r.n}}</span>
    </div>
  `).join('');
}}

// ── Nichos ──────────────────────────────────────────────────
function renderNichos() {{
  const container = $('nicho-list');
  if(!container) return;
  const sorted = Object.entries(byNicho).sort((a,b)=>b[1]-a[1]).slice(0,8);
  const max = sorted[0]?.[1] || 1;
  container.innerHTML = sorted.map(([n,c]) => `
    <div class="nicho-row">
      <span class="nicho-name">${{n}}</span>
      <div class="nicho-bar-wrap">
        <div class="nicho-bar" style="width:${{Math.round(c/max*100)}}%"></div>
      </div>
      <span class="nicho-n">${{c}}</span>
    </div>
  `).join('');
}}

// ── Closers chart ────────────────────────────────────────────
let chartClosers=null, chartCloserScore=null, chartCloserTemp=null;

function renderClosersChart() {{
  const canvas = $('chart-closers');
  if(!canvas) return;
  if(chartClosers) chartClosers.destroy();
  const labels = Object.keys(byCloser);
  const data   = labels.map(k=>byCloser[k].length);
  const colors = ['#ef4444','#f59e0b','#10b981','#3b82f6','#8b5cf6','#6366f1'];

  chartClosers = new Chart(canvas, {{
    type:'bar',
    data:{{
      labels,
      datasets:[{{
        data,
        backgroundColor:colors.map(c=>c+'33'),
        borderColor:colors,
        borderWidth:2,
        borderRadius:6,
      }}]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{
        callbacks:{{label:ctx=>`${{ctx.parsed.y}} leads`}}
      }}}},
      scales:{{
        x:{{grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'rgba(255,255,255,.5)',font:{{size:11}}}}}},
        y:{{grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'rgba(255,255,255,.5)',font:{{size:11}}}},beginAtZero:true}}
      }}
    }}
  }});
}}

// ── Recent table ─────────────────────────────────────────────
function renderRecentTable() {{
  const tbody = $('recent-tbody');
  if(!tbody) return;
  const top = [...LEADS].sort((a,b)=>b.score-a.score).slice(0,12);
  tbody.innerHTML = top.map(l => `
    <tr>
      <td>
        <div class="lead-name">${{l.full_name||l.username}}</div>
        <div class="lead-handle">@${{l.username}}</div>
      </td>
      <td>${{renderScoreBar(l.score)}}</td>
      <td>${{tempBadge(l.temperatura)}}</td>
      <td><span style="color:var(--text-2);font-size:12px">${{l.nicho}}</span></td>
      <td>${{oabBadge(l)}}</td>
      <td>${{checkBool(l.site_encontrado)}}</td>
      <td>${{checkBool(l.has_fb_pixel||l.has_ga)}}</td>
      <td><span style="color:var(--text-3);font-size:12px">${{l.closer||'—'}}</span></td>
    </tr>
  `).join('');
}}

// ═══════════════════════════════════════════════════════════════
// RENDER: PIPELINE (Kanban)
// ═══════════════════════════════════════════════════════════════
let pipelineFilter = 'all';

function renderPipeline() {{
  document.querySelectorAll('[data-pf]').forEach(btn => {{
    btn.addEventListener('click', () => {{
      document.querySelectorAll('[data-pf]').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      pipelineFilter = btn.dataset.pf;
      buildKanban();
    }});
  }});
  buildKanban();
}}

function buildKanban() {{
  const board = $('kanban-board');
  const closerOrder = ['Sem Closer','Matheus','Jonas','Giovanne','Say'];
  const allClosers = [...new Set(['Sem Closer',...Object.keys(byCloser)])];
  const ordered = closerOrder.filter(c=>allClosers.includes(c))
    .concat(allClosers.filter(c=>!closerOrder.includes(c)));

  board.style.gridTemplateColumns = `repeat(${{ordered.length}},minmax(220px,1fr))`;

  board.innerHTML = ordered.map(closer => {{
    let leads = (byCloser[closer]||[]).sort((a,b)=>b.score-a.score);
    if(pipelineFilter!=='all') leads=leads.filter(l=>l.temperatura===pipelineFilter);
    const cards = leads.map(l => `
      <div class="kcard ${{l.temperatura.toLowerCase()}}">
        <div class="kcard-name" title="${{l.full_name}}">${{l.full_name||l.username}}</div>
        <div class="kcard-meta">@${{l.username}} · ${{fmt(l.followers)}} seg.</div>
        <div class="kcard-footer">
          <span class="kcard-nicho">${{l.nicho}}</span>
          ${{tempBadge(l.temperatura)}}
          <span style="color:${{scoreColor(l.score)}};font-size:12px;font-weight:700">${{l.score}}</span>
        </div>
      </div>
    `).join('');

    const dotColor = closer==='Sem Closer' ? 'rgba(255,255,255,.3)' :
      ['#ef4444','#f59e0b','#10b981','#3b82f6'][['Matheus','Jonas','Giovanne','Say'].indexOf(closer)%4];

    return `
      <div class="kanban-col">
        <div class="kanban-header">
          <span class="kanban-col-name">
            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
              background:${{dotColor}};margin-right:6px"></span>
            ${{closer}}
          </span>
          <span class="kanban-count">${{leads.length}}</span>
        </div>
        <div class="kanban-body">
          ${{cards || '<div class="empty-state">Nenhum lead</div>'}}
        </div>
      </div>
    `;
  }}).join('');
}}

// ═══════════════════════════════════════════════════════════════
// RENDER: LEADS TABLE
// ═══════════════════════════════════════════════════════════════
let leadsFilter='all', leadsSearch='', leadsSort={{col:'score',asc:false}};

function renderLeadsTable() {{
  $('leads-count-line').textContent = `${{total}} leads no banco · filtre e exporte`;

  const si = $('search-input');
  si?.addEventListener('input', e => {{ leadsSearch=e.target.value.toLowerCase(); buildLeadsTable(); }});

  document.querySelectorAll('[data-tf]').forEach(btn => {{
    btn.addEventListener('click', () => {{
      document.querySelectorAll('[data-tf]').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      leadsFilter = btn.dataset.tf;
      buildLeadsTable();
    }});
  }});

  document.querySelectorAll('#leads-table th[data-sort]').forEach(th => {{
    th.addEventListener('click', () => {{
      const col = th.dataset.sort;
      leadsSort = leadsSort.col===col
        ? {{col, asc:!leadsSort.asc}}
        : {{col, asc:false}};
      buildLeadsTable();
    }});
  }});

  $('export-btn')?.addEventListener('click', exportCSV);
  buildLeadsTable();
}}

function buildLeadsTable() {{
  let data = [...LEADS];
  if(leadsFilter!=='all') data = data.filter(l=>l.temperatura===leadsFilter);
  if(leadsSearch) data = data.filter(l =>
    (l.full_name+l.username+l.nicho).toLowerCase().includes(leadsSearch));

  data.sort((a,b) => {{
    const va = a[leadsSort.col]||'', vb = b[leadsSort.col]||'';
    return leadsSort.asc ? (va>vb?1:-1) : (va<vb?1:-1);
  }});

  const tbody = $('leads-tbody');
  tbody.innerHTML = data.map(l => `
    <tr>
      <td>
        <div class="lead-name">${{l.full_name||l.username}}</div>
        <div class="lead-handle">@${{l.username}}</div>
      </td>
      <td>${{renderScoreBar(l.score)}}</td>
      <td>${{tempBadge(l.temperatura)}}</td>
      <td style="color:var(--text-2);font-size:12px">${{l.nicho}}</td>
      <td>${{oabBadge(l)}}</td>
      <td>${{checkBool(l.site_encontrado)}}</td>
      <td>${{checkBool(l.has_fb_pixel)}}</td>
      <td style="color:var(--text-3);font-size:12px;font-variant-numeric:tabular-nums">${{fmt(l.followers)}}</td>
      <td>
        ${{l.email ? `<a href="mailto:${{l.email}}" style="color:var(--accent);font-size:12px;text-decoration:none">✉ email</a>` : ''}}
        ${{l.phone ? `<a href="https://wa.me/${{l.phone.replace(/\\D/g,'')}}" style="color:#10b981;font-size:12px;text-decoration:none;margin-left:6px">📱 wa</a>` : ''}}
        ${{!l.email&&!l.phone ? '<span class="no-badge">—</span>' : ''}}
      </td>
      <td style="color:var(--text-3);font-size:12px">${{l.closer||'—'}}</td>
      <td style="color:var(--text-3);font-size:11px;max-width:200px;overflow:hidden;
        text-overflow:ellipsis;white-space:nowrap" title="${{l.insight}}">${{l.insight||'—'}}</td>
    </tr>
  `).join('');
}}

function exportCSV() {{
  const headers = ['username','full_name','score','temperatura','nicho','oab_numero',
    'oab_seccional','oab_situacao','email','phone','city','site_encontrado',
    'has_fb_pixel','has_ga','followers','closer','insight'];
  const rows = LEADS.map(l => headers.map(h => `"${{String(l[h]||'').replace(/"/g,'""')}}"`).join(','));
  const csv = [headers.join(','),...rows].join('\\n');
  const blob = new Blob([csv],{{type:'text/csv;charset=utf-8;'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'leads_avestra.csv';
  a.click();
}}

// ═══════════════════════════════════════════════════════════════
// RENDER: CLOSERS
// ═══════════════════════════════════════════════════════════════
function renderClosers() {{
  const grid = $('closer-grid');
  const allCloserKeys = Object.keys(byCloser);

  const accentColors = ['#ef4444','#f59e0b','#10b981','#3b82f6','#8b5cf6','#6366f1'];

  grid.innerHTML = allCloserKeys.map((closer,idx) => {{
    const leads = byCloser[closer];
    const q = leads.filter(l=>l.temperatura==='Quente').length;
    const m = leads.filter(l=>l.temperatura==='Morno').length;
    const f = leads.filter(l=>l.temperatura==='Frio').length;
    const avg = leads.length ? Math.round(leads.reduce((a,l)=>a+l.score,0)/leads.length) : 0;
    const col = accentColors[idx%accentColors.length];
    return `
      <div class="closer-card" style="border-left:3px solid ${{col}}">
        <div class="closer-name">${{closer}}</div>
        <div class="closer-total" style="color:${{col}}">${{leads.length}}</div>
        <div class="closer-sub">leads · score médio ${{avg}}</div>
        <div class="closer-temps">
          <div class="closer-temp-pill" style="background:rgba(239,68,68,.15);color:#ef4444">🔴 ${{q}}</div>
          <div class="closer-temp-pill" style="background:rgba(245,158,11,.15);color:#f59e0b">🟡 ${{m}}</div>
          <div class="closer-temp-pill" style="background:rgba(59,130,246,.12);color:#3b82f6">🔵 ${{f}}</div>
        </div>
      </div>
    `;
  }}).join('');

  // Chart: score médio por closer
  setTimeout(() => {{
    const c1 = $('chart-closer-score');
    if(c1) {{
      if(chartCloserScore) chartCloserScore.destroy();
      const labels = allCloserKeys;
      const avgs = labels.map(k => {{
        const ls = byCloser[k];
        return ls.length ? Math.round(ls.reduce((a,l)=>a+l.score,0)/ls.length) : 0;
      }});
      chartCloserScore = new Chart(c1, {{
        type:'bar',
        data:{{labels, datasets:[{{
          data:avgs,label:'Score Médio',
          backgroundColor:'rgba(99,102,241,.25)',
          borderColor:'#6366f1',borderWidth:2,borderRadius:8,
        }}]}},
        options:{{
          responsive:true,maintainAspectRatio:false,
          plugins:{{legend:{{display:false}}}},
          scales:{{
            x:{{grid:{{color:'rgba(255,255,255,.04)'}},ticks:{{color:'rgba(255,255,255,.5)',font:{{size:11}}}}}},
            y:{{grid:{{color:'rgba(255,255,255,.04)'}},ticks:{{color:'rgba(255,255,255,.5)',font:{{size:11}}}},beginAtZero:true,max:100}}
          }}
        }}
      }});
    }}

    // Chart: temp distribution
    const c2 = $('chart-closer-temp');
    if(c2) {{
      if(chartCloserTemp) chartCloserTemp.destroy();
      const labels = allCloserKeys;
      chartCloserTemp = new Chart(c2, {{
        type:'bar',
        data:{{
          labels,
          datasets:[
            {{label:'Quente',data:labels.map(k=>byCloser[k].filter(l=>l.temperatura==='Quente').length),
              backgroundColor:'rgba(239,68,68,.3)',borderColor:'#ef4444',borderWidth:2,borderRadius:4}},
            {{label:'Morno',data:labels.map(k=>byCloser[k].filter(l=>l.temperatura==='Morno').length),
              backgroundColor:'rgba(245,158,11,.25)',borderColor:'#f59e0b',borderWidth:2,borderRadius:4}},
            {{label:'Frio',data:labels.map(k=>byCloser[k].filter(l=>l.temperatura==='Frio').length),
              backgroundColor:'rgba(59,130,246,.2)',borderColor:'#3b82f6',borderWidth:2,borderRadius:4}},
          ]
        }},
        options:{{
          responsive:true,maintainAspectRatio:false,
          plugins:{{legend:{{labels:{{color:'rgba(255,255,255,.6)',font:{{size:11}}}}}}}},
          scales:{{
            x:{{stacked:true,grid:{{color:'rgba(255,255,255,.04)'}},ticks:{{color:'rgba(255,255,255,.5)',font:{{size:11}}}}}},
            y:{{stacked:true,grid:{{color:'rgba(255,255,255,.04)'}},ticks:{{color:'rgba(255,255,255,.5)',font:{{size:11}}}},beginAtZero:true}}
          }}
        }}
      }});
    }}
  }}, 100);

  // Leads table by closer
  const tbody = $('closers-tbody');
  const sorted = [...LEADS].sort((a,b)=>b.score-a.score);
  tbody.innerHTML = sorted.map(l => `
    <tr>
      <td>
        <div class="lead-name">${{l.full_name||l.username}}</div>
        <div class="lead-handle">@${{l.username}}</div>
      </td>
      <td>${{renderScoreBar(l.score)}}</td>
      <td>${{tempBadge(l.temperatura)}}</td>
      <td style="color:var(--text-2);font-size:12px">${{l.nicho}}</td>
      <td>${{oabBadge(l)}}</td>
      <td style="color:var(--text-2);font-size:12px">${{l.closer||'—'}}</td>
    </tr>
  `).join('');
}}

// ═══════════════════════════════════════════════════════════════
// RENDER: INTEGRATIONS
// ═══════════════════════════════════════════════════════════════
function renderIntegrations() {{
  const box = $('integration-stats');
  if(!box) return;
  const stats = [
    {{label:'Total Leads',   value:total,       icon:'📋'}},
    {{label:'Com OAB Ativo', value:LEADS.filter(l=>l.oab_encontrado&&l.oab_situacao==='ATIVO').length, icon:'⚖️'}},
    {{label:'Com Site',      value:LEADS.filter(l=>l.site_encontrado).length, icon:'🌐'}},
    {{label:'Com Pixel',     value:LEADS.filter(l=>l.has_fb_pixel||l.has_ga).length, icon:'📡'}},
    {{label:'Com E-mail',    value:LEADS.filter(l=>l.email).length, icon:'✉️'}},
    {{label:'Com Telefone',  value:LEADS.filter(l=>l.phone).length, icon:'📱'}},
  ];
  box.innerHTML = stats.map(s => `
    <div class="stat-card total" style="padding:16px 20px">
      <div class="stat-label">${{s.icon}} ${{s.label}}</div>
      <div class="stat-value">${{s.value}}</div>
    </div>
  `).join('');
}}

// ═══════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════
renderDashboard();
</script>
</body>
</html>"""

# ── Render ────────────────────────────────────────────────────────────────────
st.components.v1.html(HTML, height=920, scrolling=False)
