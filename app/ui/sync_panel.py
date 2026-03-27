"""
sync_panel.py — Tela de sincronização de dados entre produção e local.
Permite exportar todos os leads (com closers) em JSON e importar de outro ambiente.
"""

import json
import streamlit as st
from storage import add_leads, load_leads


def render_sync_panel(leads: list[dict]):
    st.markdown(
        "<h2 style='color:#F1F5F9;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px'>"
        "🔄 Sincronizar dados</h2>"
        "<p style='color:#64748B;margin-bottom:24px'>"
        "Exporte todos os leads desta instância ou importe dados de outra (ex: produção → local).</p>",
        unsafe_allow_html=True,
    )

    tab_export, tab_import = st.tabs(["📦 Exportar (esta instância)", "⬇️ Importar (de outra instância)"])

    # ── EXPORTAR ──────────────────────────────────────────────────────────────
    with tab_export:
        total = len(leads)
        atrib = sum(1 for l in leads if l.get("closer"))

        st.markdown(
            f"<div style='background:rgba(32,64,128,0.2);border:1px solid rgba(80,112,176,0.3);"
            f"border-radius:12px;padding:16px 20px;margin-bottom:20px'>"
            f"<b style='color:#F1F5F9'>{total} leads</b> "
            f"<span style='color:#64748B'>({atrib} com closer atribuído)</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if total == 0:
            st.info("Nenhum lead no banco para exportar.")
        else:
            json_bytes = json.dumps(
                leads,
                ensure_ascii=False,
                indent=2,
                default=str,
            ).encode("utf-8")

            st.download_button(
                "📦 Baixar leads_backup.json",
                json_bytes,
                file_name="leads_backup.json",
                mime="application/json",
                use_container_width=True,
            )
            st.caption(
                "O arquivo inclui todos os dados enriquecidos + closers atribuídos. "
                "Use-o para importar no app local via a aba 'Importar'."
            )

    # ── IMPORTAR ──────────────────────────────────────────────────────────────
    with tab_import:
        st.markdown(
            "<p style='color:#94A3B8;margin-bottom:16px'>"
            "Faça upload do <code>leads_backup.json</code> exportado de outra instância. "
            "Os dados serão <strong>mesclados</strong>: leads novos são adicionados, "
            "existentes são atualizados mas <strong>closers locais são preservados</strong>.</p>",
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Selecione o leads_backup.json",
            type=["json"],
            key="sync_import_json",
        )

        if uploaded:
            try:
                raw = json.loads(uploaded.read().decode("utf-8"))
            except Exception as e:
                st.error(f"Erro ao ler JSON: {e}")
                return

            if not isinstance(raw, list):
                st.error("Formato inválido — o JSON deve ser uma lista de leads.")
                return

            st.info(f"📋 {len(raw)} leads encontrados no arquivo.")

            col_imp, _ = st.columns([1, 3])
            with col_imp:
                if st.button("✅ Importar agora", use_container_width=True, type="primary"):
                    adicionados = add_leads(raw)
                    st.session_state["leads"] = load_leads()
                    st.success(f"✅ {adicionados} leads importados/atualizados!")
                    st.rerun()
