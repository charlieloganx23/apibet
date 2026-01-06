"""
Script para inspecionar o banco de dados SQLite
"""

import sqlite3
from database_rapidapi import engine

print("="*70)
print("📊 INFORMAÇÕES DO BANCO DE DADOS")
print("="*70)
print()

# Conectar ao banco
conn = sqlite3.connect('bet365_rapidapi.db')
cursor = conn.cursor()

# Localização
print(f"📍 Localização: {engine.url}")
print(f"📂 Arquivo: bet365_rapidapi.db")
print(f"💾 Tamanho: {conn.execute('SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()').fetchone()[0] / 1024:.2f} KB")
print()

# Tabelas
print("📋 TABELAS:")
print("-"*70)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  • {table[0]}")
print()

# Estatísticas de matches
print("📊 ESTATÍSTICAS - MATCHES:")
print("-"*70)
cursor.execute("SELECT COUNT(*) FROM matches")
total = cursor.fetchone()[0]
print(f"  Total de partidas: {total}")

cursor.execute("SELECT COUNT(*) FROM matches WHERE total_goals IS NOT NULL")
finished = cursor.fetchone()[0]
print(f"  Finalizadas: {finished}")

cursor.execute("SELECT COUNT(*) FROM matches WHERE total_goals IS NULL")
scheduled = cursor.fetchone()[0]
print(f"  Agendadas: {scheduled}")
print()

# Por liga
print("📈 POR LIGA:")
print("-"*70)
cursor.execute("""
    SELECT 
        league, 
        COUNT(*) as total,
        COUNT(CASE WHEN total_goals IS NOT NULL THEN 1 END) as finished
    FROM matches 
    GROUP BY league 
    ORDER BY total DESC
""")
for row in cursor.fetchall():
    print(f"  {row[0]:10s}: {row[1]:3d} partidas ({row[2]} finalizadas)")
print()

# Scraper logs
print("🔄 LOGS DO SCRAPER:")
print("-"*70)
cursor.execute("SELECT COUNT(*) FROM scraper_logs")
logs = cursor.fetchone()[0]
print(f"  Total de logs: {logs}")

cursor.execute("""
    SELECT 
        started_at,
        status,
        matches_found,
        matches_new
    FROM scraper_logs 
    ORDER BY id DESC 
    LIMIT 5
""")
print("  Últimas 5 execuções:")
for row in cursor.fetchall():
    print(f"    • {row[0]} - {row[1]} - {row[2]} partidas ({row[3]} novas)")
print()

# Estrutura da tabela matches
print("🏗️  ESTRUTURA DA TABELA 'matches':")
print("-"*70)
cursor.execute("PRAGMA table_info(matches)")
columns = cursor.fetchall()
print(f"  Total de colunas: {len(columns)}")
print("  Principais campos:")
print("    • id, external_id, league")
print("    • team_home, team_away")
print("    • hour, minute, scheduled_time")
print("    • goals_home, goals_away, total_goals, result")
print("    • odd_home, odd_draw, odd_away")
print("    • odd_over_25, odd_under_25")
print("    • odd_both_score_yes, odd_both_score_no")
print("    • odd_correct_* (placares exatos)")
print("    • status, scraped_at, updated_at")
print()

# Exemplos de partidas
print("⚽ EXEMPLOS DE PARTIDAS:")
print("-"*70)
cursor.execute("""
    SELECT 
        league,
        team_home || ' vs ' || team_away as match,
        hour || ':' || minute as time,
        odd_home,
        odd_draw,
        odd_away
    FROM matches 
    WHERE status = 'scheduled'
    ORDER BY hour, minute
    LIMIT 5
""")
print("  Próximas 5 partidas agendadas:")
for row in cursor.fetchall():
    print(f"    • {row[0]:8s} | {row[1]:30s} | {row[2]} | Odds: {row[3]:.2f}/{row[4]:.2f}/{row[5]:.2f}")

conn.close()

print()
print("="*70)
print("✅ Inspeção concluída!")
print("="*70)
