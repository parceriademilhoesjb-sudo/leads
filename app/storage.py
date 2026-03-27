"""
storage.py — Persistência adaptativa.
- Servidor (Railway/local): SQLite em data/crm.db
- Browser (stlite/Vercel): localStorage do browser via Pyodide JS interop
"""

import json
import sys
import sqlite3
from pathlib import Path

# Detecta se está rodando no browser (Pyodide/stlite)
_IS_PYODIDE = sys.platform == "emscripten"

DB_PATH = Path(__file__).parent.parent / "data" / "crm.db"
if not _IS_PYODIDE:
    DB_PATH.parent.mkdir(exist_ok=True, parents=True)

_LS_KEY = "oab_crm_leads"


# ── localStorage (stlite/browser) ────────────────────────────────────────────

def _ls_load() -> list[dict]:
    try:
        from js import localStorage  # type: ignore
        raw = localStorage.getItem(_LS_KEY)
        if raw:
            return json.loads(str(raw))
    except Exception:
        pass
    return []


def _ls_save(leads: list[dict]) -> None:
    try:
        from js import localStorage  # type: ignore
        localStorage.setItem(_LS_KEY, json.dumps(leads, ensure_ascii=False, default=str))
    except Exception:
        pass


# ── SQLite (servidor) ─────────────────────────────────────────────────────────

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            username   TEXT PRIMARY KEY,
            data       TEXT NOT NULL,
            closer     TEXT NOT NULL DEFAULT '',
            score      INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS avatars (
            username   TEXT PRIMARY KEY,
            data_uri   TEXT,
            fetched_at TEXT DEFAULT (datetime('now'))
        )
    """)
    c.commit()
    return c


def get_avatar(username: str) -> str | None:
    """Retorna data URI do avatar persistido no banco, ou None."""
    if _IS_PYODIDE or not username:
        return None
    try:
        c = _conn()
        row = c.execute(
            "SELECT data_uri FROM avatars WHERE username = ?", (username,)
        ).fetchone()
        c.close()
        return row[0] if row else None
    except Exception:
        return None


def save_avatar(username: str, data_uri: str | None) -> None:
    """Persiste (ou atualiza) o data URI do avatar no banco."""
    if _IS_PYODIDE or not username:
        return
    try:
        c = _conn()
        c.execute("""
            INSERT INTO avatars (username, data_uri, fetched_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(username) DO UPDATE SET
                data_uri   = excluded.data_uri,
                fetched_at = datetime('now')
        """, (username, data_uri))
        c.commit()
        c.close()
    except Exception:
        pass


# ── API pública ───────────────────────────────────────────────────────────────

def add_leads(novos: list[dict]) -> int:
    """
    Acumula leads no banco/localStorage.
    - Se username já existe: atualiza dados mas MANTÉM o closer atual.
    - Se é novo: insere com closer vazio.
    Retorna quantos leads foram adicionados/atualizados.
    """
    if _IS_PYODIDE:
        existentes = {l["username"]: l for l in _ls_load() if l.get("username")}
        count = 0
        for lead in novos:
            username = lead.get("username", "")
            if not username:
                continue
            local_closer = existentes.get(username, {}).get("closer", "")
            closer = local_closer if local_closer else lead.get("closer", "")
            existentes[username] = {**lead, "closer": closer}
            count += 1
        _ls_save(sorted(existentes.values(), key=lambda x: x.get("score", 0), reverse=True))
        return count

    # SQLite
    c = _conn()
    closer_existente = {
        row[0]: row[1]
        for row in c.execute("SELECT username, closer FROM leads")
    }
    count = 0
    for lead in novos:
        username = lead.get("username", "")
        if not username:
            continue
        # Preserva closer local se já tiver um; caso contrário usa o do lead importado
        local_closer = closer_existente.get(username, "")
        closer = local_closer if local_closer else lead.get("closer", "")
        lead_final = {**lead, "closer": closer}
        score = int(lead.get("score", 0))
        c.execute("""
            INSERT INTO leads (username, data, closer, score, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(username) DO UPDATE SET
                data       = excluded.data,
                score      = excluded.score,
                updated_at = datetime('now')
        """, (username, json.dumps(lead_final, ensure_ascii=False, default=str), closer, score))
        count += 1
    c.commit()
    c.close()
    return count


def load_leads() -> list[dict]:
    """Carrega todos os leads ordenados por score desc."""
    if _IS_PYODIDE:
        leads = _ls_load()
        if not leads:
            # Primeira visita: tenta carregar crm.json incluído pelo stlite
            try:
                json_path = Path(__file__).parent.parent / "data" / "crm.json"
                if json_path.exists():
                    with open(json_path, encoding="utf-8") as f:
                        legado = json.load(f)
                    if legado:
                        add_leads(legado)
                        leads = _ls_load()
            except Exception:
                pass
        return leads

    # SQLite
    c = _conn()
    rows = c.execute("SELECT data, closer FROM leads ORDER BY score DESC").fetchall()

    if not rows:
        json_path = DB_PATH.parent / "crm.json"
        if json_path.exists():
            try:
                with open(json_path, encoding="utf-8") as f:
                    legado = json.load(f)
                if legado:
                    c.close()
                    add_leads(legado)
                    c = _conn()
                    rows = c.execute(
                        "SELECT data, closer FROM leads ORDER BY score DESC"
                    ).fetchall()
            except Exception:
                pass

    c.close()
    leads = []
    for data_json, closer in rows:
        lead = json.loads(data_json)
        lead["closer"] = closer
        leads.append(lead)
    return leads


def update_closer(username: str, closer: str) -> None:
    """Atualiza o closer de um lead específico."""
    if _IS_PYODIDE:
        leads = _ls_load()
        for lead in leads:
            if lead.get("username") == username:
                lead["closer"] = closer
                break
        _ls_save(leads)
        return

    # SQLite
    c = _conn()
    c.execute(
        "UPDATE leads SET closer = ?, updated_at = datetime('now') WHERE username = ?",
        (closer, username),
    )
    row = c.execute("SELECT data FROM leads WHERE username = ?", (username,)).fetchone()
    if row:
        lead = json.loads(row[0])
        lead["closer"] = closer
        c.execute("UPDATE leads SET data = ? WHERE username = ?",
                  (json.dumps(lead, ensure_ascii=False, default=str), username))
    c.commit()
    c.close()


def delete_lead(username: str) -> None:
    """Remove um lead do banco permanentemente."""
    if _IS_PYODIDE:
        leads = _ls_load()
        leads = [l for l in leads if l.get("username") != username]
        _ls_save(leads)
        return
    c = _conn()
    c.execute("DELETE FROM leads WHERE username = ?", (username,))
    c.commit()
    c.close()


def total_leads() -> int:
    if _IS_PYODIDE:
        return len(_ls_load())
    c = _conn()
    n = c.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    c.close()
    return n
