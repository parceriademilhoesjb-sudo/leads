import sqlite3
import os

db_path = r"c:\Users\LB-GROUP\Documents\Agência Avestra\MVP\data\crm.db"
conn = sqlite3.connect(db_path)
try:
    conn.execute("ALTER TABLE leads ADD COLUMN score INTEGER NOT NULL DEFAULT 0;")
    conn.commit()
    print("Sucesso!")
except Exception as e:
    print(f"Erro: {e}")
finally:
    conn.close()
