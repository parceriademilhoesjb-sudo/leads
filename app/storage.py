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
    # Prioridade 1: Session State (digitado na UI)
    # Prioridade 2: Environment Variables (Vercel/Local)
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

def save_leads(leads: list[dict]) -> bool:
    """Salva os leads no Supabase ou Local JSON. Retorna True se salvou na nuvem."""
    url_base, key = _get_config()
    
    # Salvar local sempre como backup (no MemFS do stlite)
    _save_json(leads)
    
    if not url_base or not key:
        return False

    url = f"{url_base.rstrip('/')}/rest/v1/leads"
    headers = _get_headers(key)

    # Preparar payload
    payload = []
    for lead in leads:
        username = lead.get("username", "")
        if not username: continue
        payload.append({
            "username": username,
            "data": lead,
            "closer": lead.get("closer", ""),
            "updated_at": "now()"
        })

    if not payload: return False

    try:
        # Upsert baseado no username
        h_upsert = {**headers, "Prefer": "resolution=merge-duplicates"}
        r = requests.post(url, json=payload, headers=h_upsert, timeout=10)
        if r.status_code in [200, 201]:
            return True
        else:
            st.error(f"Erro Supabase ({r.status_code}): {r.text}")
            return False
    except Exception as e:
        st.error(f"Erro de conexão com Nuvem: {e}")
        return False

def load_leads() -> list[dict]:
    """Carrega leads da Nuvem (Supabase) ou do arquivo local."""
    url_base, key = _get_config()
    
    # Tenta carregar local primeiro para ter algo rápido
    local_leads = _load_json()
    
    if not url_base or not key:
        return local_leads

    url = f"{url_base.rstrip('/')}/rest/v1/leads?select=data,closer&order=data->>score.desc.nullslast"
    headers = _get_headers(key)

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            rows = resp.json()
            if not rows and local_leads:
                # Se nuvem vazia mas local tem dados, sobe os dados
                save_leads(local_leads)
                return local_leads
            
            leads = []
            for row in rows:
                lead = row['data']
                lead['closer'] = row['closer']
                leads.append(lead)
            
            # Sincroniza local com nuvem (cache)
            if leads: _save_json(leads)
            return leads
        else:
            return local_leads
    except:
        return local_leads

def update_closer(username: str, closer: str) -> None:
    url_base, key = _get_config()
    
    # Atualizar local
    leads = _load_json()
    for l in leads:
        if l.get("username") == username:
            l["closer"] = closer
            break
    _save_json(leads)

    if not url_base or not key:
        return

    url = f"{url_base.rstrip('/')}/rest/v1/leads?username=eq.{username}"
    headers = _get_headers(key)

    try:
        # Primeiro ler o lead para não perder dados ao atualizar
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200 and resp.json():
            lead_data = resp.json()[0]['data']
            lead_data['closer'] = closer
            requests.patch(url, json={"closer": closer, "data": lead_data, "updated_at": "now()"}, headers=headers, timeout=5)
    except:
        pass

def total_leads() -> int:
    url_base, key = _get_config()
    if not url_base or not key: return len(_load_json())
    url = f"{url_base.rstrip('/')}/rest/v1/leads"
    try:
        h = {**_get_headers(key), "Prefer": "count=exact"}
        resp = requests.head(url, headers=h, timeout=5)
        count = resp.headers.get("Content-Range")
        return int(count.split('/')[-1]) if count else 0
    except: return len(_load_json())

def _load_json():
    if not DB_PATH_JSON.exists(): return []
    try:
        with open(DB_PATH_JSON, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: 
        return []

def _save_json(leads):
    try:
        with open(DB_PATH_JSON, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=2, default=str)
    except:
        pass
