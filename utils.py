"""
Utilitários auxiliares
"""
from datetime import datetime
from typing import Dict, Any
import json


def parse_match_time(time_str: str) -> int:
    """
    Converte string de tempo para minutos
    Ex: "45'" -> 45, "90'+3" -> 93
    """
    try:
        # Remove aspas simples e caracteres extras
        time_str = time_str.replace("'", "").replace("+", ".")
        return int(float(time_str))
    except:
        return 0


def format_match_result(home_score: int, away_score: int) -> str:
    """
    Formata resultado da partida
    Ex: 2, 1 -> "2-1"
    """
    return f"{home_score}-{away_score}"


def get_match_winner(home_score: int, away_score: int) -> str:
    """
    Retorna vencedor da partida
    """
    if home_score > away_score:
        return "home"
    elif away_score > home_score:
        return "away"
    else:
        return "draw"


def calculate_total_goals(home_score: int, away_score: int) -> int:
    """
    Calcula total de gols
    """
    return home_score + away_score


def is_over_under(home_score: int, away_score: int, line: float = 2.5) -> str:
    """
    Verifica se foi Over ou Under
    """
    total = home_score + away_score
    return "over" if total > line else "under"


def both_teams_scored(home_score: int, away_score: int) -> bool:
    """
    Verifica se ambos marcaram
    """
    return home_score > 0 and away_score > 0


def clean_team_name(team_name: str) -> str:
    """
    Limpa nome do time removendo caracteres especiais
    """
    return team_name.strip().replace("\n", "").replace("\t", "")


def safe_int(value: Any, default: int = 0) -> int:
    """
    Converte para int de forma segura
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Converte para float de forma segura
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def generate_match_id(home_team: str, away_team: str, match_date: datetime) -> str:
    """
    Gera ID único para partida
    """
    timestamp = int(match_date.timestamp())
    home_clean = clean_team_name(home_team).replace(" ", "-").lower()
    away_clean = clean_team_name(away_team).replace(" ", "-").lower()
    return f"vf_{timestamp}_{home_clean}_vs_{away_clean}"


def parse_json_safely(json_str: str) -> Dict:
    """
    Parse JSON de forma segura
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formata datetime para string
    """
    return dt.strftime(format_str)


def time_ago(dt: datetime) -> str:
    """
    Retorna tempo decorrido em formato legível
    Ex: "há 5 minutos", "há 2 horas"
    """
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"há {int(seconds)} segundos"
    elif seconds < 3600:
        return f"há {int(seconds / 60)} minutos"
    elif seconds < 86400:
        return f"há {int(seconds / 3600)} horas"
    else:
        return f"há {int(seconds / 86400)} dias"
