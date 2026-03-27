"""
lead_card.py — Card expandido de cada lead no dashboard.
"""

import streamlit as st


def _classificacao_color(cls: str) -> str:
    if "Quente" in cls:
        return "#90c0e0"
    if "Morno" in cls:
        return "#5070b0"
    return "#306090"


def render_lead_card(lead: dict, show_assign: bool = False):
    """Renderiza o card expandido de um lead dentro de um st.expander."""
    cls   = lead.get("classificacao", "")
    score = lead.get("score", 0)

    with st.expander(
        f"{cls}  ·  Score {score}/100  ·  @{lead.get('username', '')}  —  {lead.get('full_name', '')}",
        expanded=False,
    ):
        username  = lead.get("username", "")
        full_name = lead.get("full_name", "")
        initial   = (full_name or username or "?")[0].upper()
        closer    = lead.get("closer", "")
        color     = _classificacao_color(cls)

        closer_badge = (
            f"<span style='background:rgba(144,192,224,0.1);color:#90c0e0;padding:2px 10px;"
            f"border-radius:99px;font-size:11px;font-weight:800;margin-left:8px;"
            f"border:1px solid rgba(144,192,224,0.2)'>👤 {closer.capitalize()}</span>"
            if closer else ""
        )

        # ── Header: avatar + nome ──────────────────────────────────────────────
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:20px;margin-bottom:16px">
  <div style="width:72px;height:72px;border-radius:50%;background:#0a1628;flex-shrink:0;
    border:2px solid rgba(80,112,176,0.5);display:flex;align-items:center;justify-content:center;
    font-size:26px;font-weight:800;color:#90c0e0;font-family:'Manrope',sans-serif">
    {initial}
  </div>
  <div>
    <div style="font-size:1.3rem;font-weight:800;color:#fff;font-family:'Manrope',sans-serif">
      {full_name}{closer_badge}
    </div>
    <div style="color:#b0c0d0;font-size:0.875rem;margin-top:2px">
      @{username} · <span style="color:#90c0e0">⚖️ {lead.get('nicho','Geral')}</span>
      · {lead.get('followers',0):,} seguidores
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        st.divider()

        # ── OAB / CNPJ / Site — uma única chamada st.markdown ─────────────────
        oab_html = ""
        if lead.get("oab_encontrado"):
            anos = lead.get("oab_anos_ativo")
            anos_txt = f"<br><small style='color:#64748b'>Inscrito há {anos:.0f} ano(s)</small>" if anos is not None else ""
            oab_html = (
                f"<strong style='color:#e2e8f0'>{lead.get('oab_numero','')} "
                f"{lead.get('oab_seccional','')}</strong> — {lead.get('oab_situacao','')}{anos_txt}"
            )
        else:
            oab_html = "<span style='color:#64748b;font-size:12px'>Não encontrado</span>"

        cnpj_html = ""
        if lead.get("cnpj_numero"):
            cnpj_html = (
                f"<span style='color:#e2e8f0'>{lead.get('cnpj_razao_social', lead.get('cnpj_numero',''))}</span>"
                f"<br><small style='color:#64748b'>{lead.get('cnpj_situacao','')}</small>"
            )
        else:
            cnpj_html = "<span style='color:#64748b;font-size:12px'>Não encontrado</span>"

        site_html = ""
        if lead.get("site_encontrado"):
            site_url = lead.get("site_url", "")
            pixels = []
            if lead.get("has_fb_pixel"):  pixels.append("Pixel FB")
            if lead.get("has_ga"):        pixels.append("GA/GTM")
            if lead.get("has_google_ads"): pixels.append("Google Ads")
            pixel_txt = (
                f"<br><small style='color:#64748b'>✓ {' · '.join(pixels)}</small>"
                if pixels else "<br><small style='color:#64748b'>⚠️ Sem rastreamento</small>"
            )
            disp = site_url[:38] + "…" if len(site_url) > 38 else site_url
            site_html = f"<a href='{site_url}' target='_blank' style='color:#90c0e0'>{disp}</a>{pixel_txt}"
        else:
            site_html = "<span style='color:#64748b;font-size:12px'>Não encontrado +20pts</span>"

        label_style = "color:#94a3b8;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px"
        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;margin:8px 0">
  <div><div style="{label_style}">OAB</div>{oab_html}</div>
  <div><div style="{label_style}">CNPJ</div>{cnpj_html}</div>
  <div><div style="{label_style}">Site</div>{site_html}</div>
</div>
""", unsafe_allow_html=True)

        # ── Contatos ──────────────────────────────────────────────────────────
        phone = lead.get("phone_full", "") or lead.get("phone_from_bio", "")
        email = lead.get("email", "")

        st.divider()
        contact_cols = st.columns(3)
        with contact_cols[0]:
            if phone:
                st.markdown(f"📱 `{phone}`")
                st.link_button("WhatsApp", f"https://wa.me/{phone.lstrip('+')}", use_container_width=True)
        with contact_cols[1]:
            if email:
                st.markdown(f"✉️ `{email}`")
                st.link_button("Email", f"mailto:{email}", use_container_width=True)
        with contact_cols[2]:
            ig_url = lead.get("profile_url", f"https://instagram.com/{username}")
            st.link_button("Ver Instagram", ig_url, use_container_width=True)

        # ── Insight ───────────────────────────────────────────────────────────
        insight = lead.get("insight", "")
        if insight:
            st.divider()
            st.info(f"💡 {insight}")

        # ── Atribuir para closer ──────────────────────────────────────────────
        if show_assign:
            st.divider()
            st.markdown(
                "<p style='color:#b0c0d0;font-size:11px;font-weight:700;"
                "text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px'>"
                "Atribuir para closer</p>",
                unsafe_allow_html=True,
            )
            a1, a2 = st.columns([3, 1])
            with a1:
                closer_choice = st.selectbox(
                    "Closer",
                    options=["", "Matheus", "Jonas", "Giovanne"],
                    key=f"closer_sel_{username}",
                    label_visibility="collapsed",
                    format_func=lambda x: "Selecione o closer..." if x == "" else x,
                )
            with a2:
                if st.button(
                    "Atribuir →",
                    key=f"assign_btn_{username}",
                    use_container_width=True,
                    disabled=not closer_choice,
                ):
                    st.session_state["assign_action"] = {
                        "username": username,
                        "closer": closer_choice.lower(),
                    }
                    st.rerun()

        # ── Proposta ──────────────────────────────────────────────────────────
        st.divider()
        proposta = lead.get("proposta") or {}
        tem_proposta = bool(proposta.get("valor") or proposta.get("texto"))

        if tem_proposta:
            st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(80,112,176,0.12) 0%,rgba(5,10,21,0.6) 100%);
  border:1px solid rgba(80,112,176,0.3);border-radius:16px;padding:20px 24px;margin-bottom:12px">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
    <span style="font-size:1.1rem">📋</span>
    <span style="color:#90c0e0;font-size:11px;font-weight:800;text-transform:uppercase;
      letter-spacing:1.5px">Proposta Enviada</span>
    {"<span style='background:rgba(144,192,224,0.15);color:#90c0e0;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:700;margin-left:auto;border:1px solid rgba(144,192,224,0.25)'>" + proposta.get('status','') + "</span>" if proposta.get('status') else ""}
  </div>
  {"<div style='font-size:2rem;font-weight:800;color:#fff;font-family:Manrope;margin-bottom:8px'>R$ " + proposta.get('valor','') + "</div>" if proposta.get('valor') else ""}
  {"<div style='color:#b0c0d0;font-size:0.9rem;line-height:1.6;white-space:pre-wrap'>" + proposta.get('texto','') + "</div>" if proposta.get('texto') else ""}
</div>
""", unsafe_allow_html=True)

        # Formulário de proposta (toggle)
        form_key = f"show_proposta_{username}"
        if not st.session_state.get(form_key):
            label = "✏️ Editar Proposta" if tem_proposta else "📋 Adicionar Proposta"
            if st.button(label, key=f"btn_proposta_{username}", use_container_width=False):
                st.session_state[form_key] = True
                st.rerun()
        else:
            st.markdown(
                "<p style='color:#90c0e0;font-size:11px;font-weight:800;text-transform:uppercase;"
                "letter-spacing:1px;margin-bottom:10px'>Nova Proposta</p>",
                unsafe_allow_html=True,
            )
            p1, p2 = st.columns([1, 2])
            with p1:
                valor_input = st.text_input(
                    "Valor (R$)",
                    value=proposta.get("valor", ""),
                    key=f"prop_valor_{username}",
                    placeholder="Ex: 12.000",
                )
                status_input = st.selectbox(
                    "Status",
                    options=["Em negociação", "Enviada", "Fechada", "Recusada"],
                    index=["Em negociação","Enviada","Fechada","Recusada"].index(proposta.get("status","Em negociação")) if proposta.get("status") in ["Em negociação","Enviada","Fechada","Recusada"] else 0,
                    key=f"prop_status_{username}",
                )
            with p2:
                texto_input = st.text_area(
                    "Descrição / Observações",
                    value=proposta.get("texto", ""),
                    key=f"prop_texto_{username}",
                    height=100,
                    placeholder="Descreva a proposta, serviços incluídos, condições...",
                )
            s1, s2, _ = st.columns([1, 1, 3])
            with s1:
                if st.button("💾 Salvar", key=f"prop_save_{username}", use_container_width=True):
                    st.session_state["proposta_action"] = {
                        "username": username,
                        "proposta": {
                            "valor": valor_input,
                            "texto": texto_input,
                            "status": status_input,
                        },
                    }
                    st.session_state.pop(form_key, None)
                    st.rerun()
            with s2:
                if st.button("Cancelar", key=f"prop_cancel_{username}", use_container_width=True):
                    st.session_state.pop(form_key, None)
                    st.rerun()

        # ── Excluir lead ──────────────────────────────────────────────────────
        st.divider()
        col_del, _ = st.columns([1, 5])
        with col_del:
            if st.button("🗑️ Excluir lead", key=f"del_btn_{username}", use_container_width=True):
                st.session_state["delete_action"] = {"username": username}
                st.rerun()

        # ── Score breakdown ───────────────────────────────────────────────────
        criterios = lead.get("criterios_aplicados", [])
        if criterios:
            from scoring.engine import CRITERIOS
            linhas = []
            for c in criterios:
                pts = CRITERIOS.get(c, 0)
                cor = "#90c0e0" if pts > 0 else "#EF4444"
                sinal = "+" if pts > 0 else ""
                linhas.append(
                    f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
                    f"<span style='color:{cor};font-weight:800;font-size:12px;min-width:45px'>{sinal}{pts}pts</span>"
                    f"<span style='color:#b0c0d0;font-size:12px'>{c}</span></div>"
                )
            st.markdown(
                "<p style='color:#b0c0d0;font-size:10px;font-weight:800;margin-top:20px;"
                "letter-spacing:1px;text-transform:uppercase'>Detalhamento do Score</p>"
                + "".join(linhas),
                unsafe_allow_html=True,
            )
