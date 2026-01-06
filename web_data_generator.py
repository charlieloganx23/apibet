"""
Script para gerar dados JSON do banco SQLite para o dashboard web
"""

import json
import sqlite3
from datetime import datetime

def generate_web_data():
    """Gera arquivo JSON com dados do banco para o dashboard"""
    
    print("="*70)
    print("🌐 GERADOR DE DADOS WEB")
    print("="*70)
    print()
    
    # Conectar ao banco
    conn = sqlite3.connect('bet365_rapidapi.db')
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    cursor = conn.cursor()
    
    # Buscar todas as partidas
    cursor.execute("""
        SELECT 
            id, external_id, league,
            team_home, team_away,
            hour, minute, scheduled_time,
            goals_home, goals_away, total_goals, result,
            odd_home, odd_draw, odd_away,
            odd_over_25, odd_under_25,
            odd_both_score_yes, odd_both_score_no,
            odd_correct_1_0_home, odd_correct_0_0, odd_correct_1_0_away,
            odd_correct_2_0_home, odd_correct_1_1, odd_correct_2_0_away,
            odd_correct_2_1_home, odd_correct_2_2, odd_correct_2_1_away,
            status, scraped_at
        FROM matches
        ORDER BY hour, minute
    """)
    
    matches = []
    for row in cursor.fetchall():
        match = {
            'id': row['id'],
            'external_id': row['external_id'],
            'league': row['league'],
            'team_home': row['team_home'],
            'team_away': row['team_away'],
            'hour': row['hour'],
            'minute': row['minute'],
            'scheduled_time': row['scheduled_time'],
            'goals_home': row['goals_home'],
            'goals_away': row['goals_away'],
            'total_goals': row['total_goals'],
            'result': row['result'],
            'odd_home': row['odd_home'],
            'odd_draw': row['odd_draw'],
            'odd_away': row['odd_away'],
            'odd_over_25': row['odd_over_25'],
            'odd_under_25': row['odd_under_25'],
            'odd_both_score_yes': row['odd_both_score_yes'],
            'odd_both_score_no': row['odd_both_score_no'],
            'status': row['status'],
            'scraped_at': row['scraped_at']
        }
        matches.append(match)
    
    # Estatísticas
    cursor.execute("SELECT COUNT(*) as total FROM matches")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as finished FROM matches WHERE total_goals IS NOT NULL")
    finished = cursor.fetchone()['finished']
    
    scheduled = total - finished
    
    # Última execução
    cursor.execute("""
        SELECT started_at, status, matches_found, matches_new
        FROM scraper_logs
        ORDER BY id DESC
        LIMIT 1
    """)
    last_exec = cursor.fetchone()
    
    conn.close()
    
    # Montar dados
    data = {
        'generated_at': datetime.now().isoformat(),
        'stats': {
            'total': total,
            'finished': finished,
            'scheduled': scheduled
        },
        'last_execution': {
            'date': last_exec['started_at'] if last_exec else None,
            'status': last_exec['status'] if last_exec else None,
            'matches_found': last_exec['matches_found'] if last_exec else 0,
            'new_matches': last_exec['matches_new'] if last_exec else 0
        },
        'matches': matches
    }
    
    # Salvar JSON
    with open('web/data/matches.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dados gerados com sucesso!")
    print(f"📊 Total de partidas: {total}")
    print(f"   • Finalizadas: {finished}")
    print(f"   • Agendadas: {scheduled}")
    print(f"📁 Arquivo salvo: web/data/matches.json")
    print()
    print("🌐 Abra o dashboard em: web/dashboard.html")
    print("="*70)

if __name__ == '__main__':
    generate_web_data()
