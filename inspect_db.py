import sqlite3
db_path = r"c:\Users\LB-GROUP\Documents\Agência Avestra\MVP\data\crm.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(f"Tabelas: {cursor.fetchall()}")

# Check columns of table 'leads'
try:
    cursor.execute("PRAGMA table_info(leads);")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Colunas de 'leads': {columns}")
except Exception as e:
    print(f"Erro ao ler leads: {e}")

conn.close()
