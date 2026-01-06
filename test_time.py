from datetime import datetime, timedelta

local = datetime.now()
site = local + timedelta(hours=4)

print("="*60)
print("⏰ VERIFICAÇÃO DE CORRELAÇÃO DE HORÁRIOS")
print("="*60)
print(f"Horário LOCAL do computador: {local.strftime('%H:%M:%S')}")
print(f"Horário do SITE Bet365:      {site.strftime('%H:%M:%S')}")
print(f"Diferença:                   +4 horas")
print("="*60)
