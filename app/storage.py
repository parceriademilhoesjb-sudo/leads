"""
storage.py — Persistência Cloud com Supabase API (HTTP Browser-safe).
Versão Corrigida: Chaves dinâmicas para Stlite.
"""

import os
import json
import requests
import streamlit as st
from pathlib import Path

# Configuração local
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)
DB_PATH_JSON = DATA_DIR / "crm.json"

def _get_config():
    """Busca as chaves de forma dinâmica (Vercel ou Campo Manual do Streamlit)."""
    url = st.session_state.get("S_URL") or os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = st.session_state.get("S_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    return url, key

def _get_headers(key):
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

def save_leads(leads: list[dict]) -> None:
    url_base, key = _get_config()
    if not url_base or not key:
        _save_json(leads)
        return

    url = f"{url_base.rstrip('/')}/rest/v1/leads"
    headers = _get_headers(key)

    # Preparar payload
    payload = []
    for lead in leads:
        username = lead.get("username", "")
        payload.append({
            "username": username,
            "data": lead,
            "closer": lead.get("closer", ""),
            "updated_at": "now()"
        })

    try:
        h_upsert = {**headers, "Prefer": "resolution=merge-duplicates"}
        r = requests.post(url, json=payload, headers=h_upsert)
        if r.status_code not in [200, 201]:
            st.error(f"Erro Supabase ({r.status_code}): {r.text}")
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        _save_json(leads)

def load_leads() -> list[dict] | None:
    url_base, key = _get_config()
    if not url_base or not key:
        return _load_json()

    url = f"{url_base.rstrip('/')}/rest/v1/leads?select=data,closer&order=data->>score.desc.nullslast"
    headers = _get_headers(key)

    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            rows = resp.json()
            if not rows:
                local = _load_json()
                if local:
                    save_leads(local)
                    return load_leads()
                return []
            
            leads = []
            for row in rows:
                lead = row['data']
                lead['closer'] = row['closer']
                leads.append(lead)
            return leads
        return _load_json()
    except:
        return _load_json()

def update_closer(username: str, closer: str) -> None:
    url_base, key = _get_config()
    if not url_base or not key:
        leads = _load_json()
        for l in leads:
            if l.get("username") == username:
                l["closer"] = closer
        _save_json(leads)
        return

    url = f"{url_base.rstrip('/')}/rest/v1/leads?username=eq.{username}"
    headers = _get_headers(key)

    try:
        # Primeiro ler o lead para não perder dados ao atualizar
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200 and resp.json():
            lead = resp.json()[0]['data']
            lead['closer'] = closer
            requests.patch(url, json={"closer": closer, "data": lead, "updated_at": "now()"}, headers=headers)
    except:
        pass

def total_leads() -> int:
    url_base, key = _get_config()
    if not url_base or not key: return len(_load_json())
    url = f"{url_base.rstrip('/')}/rest/v1/leads"
    try:
        h = {**_get_headers(key), "Prefer": "count=exact"}
        resp = requests.head(url, headers=h)
        count = resp.headers.get("Content-Range")
        return int(count.split('/')[-1]) if count else 0
    except: return 0

def _load_json():
    if not DB_PATH_JSON.exists(): return []
    try:
        with open(DB_PATH_JSON, encoding="utf-8") as f: return json.load(f)
    except: return []

def _save_json(leads):
    with open(DB_PATH_JSON, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2, default=str)
