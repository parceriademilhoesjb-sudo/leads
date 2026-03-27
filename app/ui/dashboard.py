"""
dashboard.py — Tela 3: Dashboard interativo com tabela de leads filtráveis.
"""

import io
import json
import pandas as pd
import streamlit as st
from ui.lead_card import render_lead_card


def _color_cls(val: str) -> str:
    if "Quente" in str(val):
        return "color: #90c0e0; font-weight: 800; text-shadow: 0 0 10px rgba(144, 192, 224, 0.4)"
    if "Morno" in str(val):
        return "color: #5070b0; font-weight: 700"
    return "color: #306090; font-weight: 600"


def render_dashboard(leads: list[dict]):
    """Renderiza o dashboard principal com leads disponíveis (sem closer atribuído)."""

    # Apenas leads não atribuídos
    disponiveis = [l for l in leads if not l.get("closer")]

    st.markdown(
        "<div class='manrope' style='margin-bottom:32px'>"
        "<h2 style='color:#ffffff;margin-bottom:4px;font-weight:800;letter-spacing:-1px'>"
        "📊 Dashboard <span class='accent-text'>Principal</span></h2>"
        "<p style='color:#b0c0d0;font-size:1.1rem'>Leads qualificados prontos para abordagem estratégica.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    if not disponiveis:
        st.markdown(
            "<div style='text-align:center;padding:60px 20px;color:#64748B'>"
            "<div style='font-size:3rem;margin-bottom:12px'>✅</div>"
            "<h3 style='color:#94A3B8;margin-bottom:8px'>Todos os leads foram atribuídos!</h3>"
            "<p>Acesse o painel de cada closer na barra lateral.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(disponiveis)

    # ── Métricas resumo ───────────────────────────────────────────────────────
    total = len(disponiveis)
    quentes = df["classificacao"].str.contains("Quente").sum() if "classificacao" in df else 0
    mornos = df["classificacao"].str.contains("Morno").sum() if "classificacao" in df else 0
    frios = df["classificacao"].str.contains("Frio").sum() if "classificacao" in df else 0
    com_contato = df.apply(
        lambda r: bool(r.get("phone_full") or r.get("phone_from_bio") or r.get("email")),
        axis=1,
    ).sum()

    # Custom HTML Metrics for Pulse look
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 24px;">
        <div style="background: rgba(80, 112, 176, 0.1); border: 1px solid rgba(80, 112, 176, 0.2); padding: 20px; border-radius: 16px; text-align: center;">
            <div style="color: #ffffff; font-size: 2rem; font-weight: 800; font-family: 'Manrope';">{total}</div>
            <div style="color: #b0c0d0; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Total</div>
        </div>
        <div style="background: rgba(144, 192, 224, 0.1); border: 1px solid rgba(144, 192, 224, 0.2); padding: 20px; border-radius: 16px; text-align: center;">
            <div style="color: #90c0e0; font-size: 2rem; font-weight: 800; font-family: 'Manrope'; text-shadow: 0 0 15px rgba(144, 192, 224, 0.4);">{quentes}</div>
            <div style="color: #b0c0d0; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">🔥 Quentes</div>
        </div>
        <div style="background: rgba(80, 112, 176, 0.1); border: 1px solid rgba(80, 112, 176, 0.2); padding: 20px; border-radius: 16px; text-align: center;">
            <div style="color: #5070b0; font-size: 2rem; font-weight: 800; font-family: 'Manrope';">{mornos}</div>
            <div style="color: #b0c0d0; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">🟡 Mornos</div>
        </div>
        <div style="background: rgba(80, 112, 176, 0.1); border: 1px solid rgba(80, 112, 176, 0.2); padding: 20px; border-radius: 16px; text-align: center;">
            <div style="color: #306090; font-size: 2rem; font-weight: 800; font-family: 'Manrope';">{frios}</div>
            <div style="color: #b0c0d0; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">❄️ Frios</div>
        </div>
        <div style="background: rgba(80, 112, 176, 0.1); border: 1px solid rgba(80, 112, 176, 0.2); padding: 20px; border-radius: 16px; text-align: center;">
            <div style="color: #ffffff; font-size: 2rem; font-weight: 800; font-family: 'Manrope';">{com_contato}</div>
            <div style="color: #b0c0d0; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">📱 Contato</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Filtros ───────────────────────────────────────────────────────────────
    f1, f2, f3, f4, f5 = st.columns(5)

    with f1:
        opcoes_cls = ["Todos"] + sorted(df["classificacao"].unique().tolist()) if "classificacao" in df else ["Todos"]
        filtro_cls = st.selectbox("Classificação", opcoes_cls)

    with f2:
        nichos = ["Todos"] + sorted(df["nicho"].unique().tolist()) if "nicho" in df else ["Todos"]
        filtro_nicho = st.selectbox("Nicho", nichos)

    with f3:
        filtro_email = st.checkbox("Com email")

    with f4:
        filtro_fone = st.checkbox("Com telefone")

    with f5:
        filtro_site = st.checkbox("Com site")

    # Aplicar filtros
    mask = pd.Series([True] * len(df), index=df.index)

    if filtro_cls != "Todos":
        mask &= df["classificacao"].str.contains(filtro_cls.replace("🔥 ", "").replace("🟡 ", "").replace("❄️ ", ""))

    if filtro_nicho != "Todos":
        mask &= df["nicho"] == filtro_nicho

    if filtro_email:
        mask &= df["email"].fillna("").astype(str).str.strip().ne("")

    if filtro_fone:
        mask &= (
            df.get("phone_full", pd.Series("")).fillna("").astype(str).str.strip().ne("") |
            df.get("phone_from_bio", pd.Series("")).fillna("").astype(str).str.strip().ne("")
        )

    if filtro_site:
        mask &= df.get("site_encontrado", pd.Series(False)).fillna(False)

    df_filtered = df[mask].copy()

    st.caption(f"Exibindo {len(df_filtered)} de {total} leads")

    # ── Exportar ──────────────────────────────────────────────────────────────
    if len(df_filtered) > 0:
        exp1, exp2 = st.columns([1, 1])

        csv_buf = io.StringIO()
        export_cols = [
            "username", "full_name", "nicho", "score", "classificacao",
            "oab_numero", "oab_seccional", "oab_situacao", "oab_anos_ativo",
            "cnpj_numero", "cnpj_razao_social",
            "site_url", "has_fb_pixel", "has_ga",
            "email", "phone_full", "phone_from_bio",
            "followers", "profile_url", "insight",
        ]
        export_cols = [c for c in export_cols if c in df_filtered.columns]
        df_filtered[export_cols].to_csv(csv_buf, index=False, encoding="utf-8-sig")
        with exp1:
            st.download_button(
                "⬇️ Exportar CSV filtrado",
                csv_buf.getvalue().encode("utf-8-sig"),
                file_name="leads_qualificados.csv",
                mime="text/csv",
            )

        # Export JSON completo (inclui closer e todos os dados — para sincronizar com local)
        with exp2:
            json_bytes = json.dumps(
                df_filtered.to_dict("records"),
                ensure_ascii=False,
                default=str,
            ).encode("utf-8")
            st.download_button(
                "📦 Exportar JSON completo",
                json_bytes,
                file_name="leads_backup.json",
                mime="application/json",
                help="Exporta todos os dados + closers atribuídos. Use para importar no app local.",
            )

    st.divider()

    # ── Cards de leads ────────────────────────────────────────────────────────
    if len(df_filtered) == 0:
        st.info("Nenhum lead encontrado com os filtros selecionados.")
        return

    # Ordenar por score desc + paginação (20 por página)
    df_sorted  = df_filtered.sort_values("score", ascending=False)
    total_filt = len(df_sorted)
    PAGE_SIZE  = 20

    page_key = "dash_page"
    # Reset página quando filtros mudam
    filtro_sig = (filtro_cls, filtro_nicho, filtro_email, filtro_fone, filtro_site)
    if st.session_state.get("_dash_filtro_sig") != filtro_sig:
        st.session_state[page_key] = 0
        st.session_state["_dash_filtro_sig"] = filtro_sig

    pagina_atual = st.session_state.get(page_key, 0)
    inicio  = pagina_atual * PAGE_SIZE
    fim     = min(inicio + PAGE_SIZE, total_filt)
    pagina_leads = df_sorted.iloc[inicio:fim].to_dict("records")

    for lead in pagina_leads:
        render_lead_card(lead, show_assign=True)

    # Navegação de página
    if total_filt > PAGE_SIZE:
        total_paginas = (total_filt + PAGE_SIZE - 1) // PAGE_SIZE
        st.markdown(
            f"<p style='text-align:center;color:#64748b;font-size:12px;margin-top:8px'>"
            f"Página {pagina_atual + 1} de {total_paginas} · {total_filt} leads</p>",
            unsafe_allow_html=True,
        )
        nav1, nav2, nav3 = st.columns([1, 2, 1])
        with nav1:
            if pagina_atual > 0:
                if st.button("← Anterior", use_container_width=True):
                    st.session_state[page_key] = pagina_atual - 1
                    st.rerun()
        with nav3:
            if fim < total_filt:
                if st.button("Próxima →", use_container_width=True):
                    st.session_state[page_key] = pagina_atual + 1
                    st.rerun()
