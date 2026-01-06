import sqlite3

conn = sqlite3.connect('matches.db')
cursor = conn.cursor()

# Listar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("📋 Tabelas no banco:")
for table in tables:
    print(f"   • {table[0]}")
    
    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"     Registros: {count}")

conn.close()
