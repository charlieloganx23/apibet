"""
Modelo de Machine Learning Melhorado para Predição de Resultados
Aprende com os padrões dos resultados reais
"""
import sys
sys.path.insert(0, r'c:\Users\darkf\OneDrive\Documentos\apibet')

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
from database_rapidapi import get_db
from models_rapidapi import Match
from datetime import datetime

print("=" * 70)
print("🤖 MODELO DE MACHINE LEARNING - PREDIÇÃO DE RESULTADOS")
print("=" * 70)

try:
    # ETAPA 1: Carregar dados
    print("\n📊 ETAPA 1: Carregando dados do banco...")
    
    data = []
    
    with get_db() as db:
        finished_matches = db.query(Match).filter(
            Match.status == 'finished',
            Match.result.isnot(None)
        ).all()
        
        print(f"   ✅ {len(finished_matches)} partidas finalizadas carregadas")
        
        if len(finished_matches) < 50:
            print("   ⚠️  Poucos dados para treinar. Mínimo: 50 partidas")
            sys.exit(1)
        
        # ETAPA 2: Preparar features (dentro da sessão)
        print("\n🔧 ETAPA 2: Preparando features...")
        
        for match in finished_matches:
            if all([match.odd_home, match.odd_draw, match.odd_away]):
                # Features baseadas em odds
                features = {
                    # Odds básicas
                    'odd_home': match.odd_home,
                    'odd_draw': match.odd_draw,
                'odd_away': match.odd_away,
                
                # Probabilidades implícitas
                'prob_home': 1 / match.odd_home,
                'prob_draw': 1 / match.odd_draw,
                'prob_away': 1 / match.odd_away,
                
                # Odds diferenciais
                'odd_diff_home_away': match.odd_home - match.odd_away,
                'odd_ratio_home_away': match.odd_home / match.odd_away,
                
                # Favorito
                'is_home_favorite': 1 if match.odd_home < match.odd_away else 0,
                'favorite_odd': min(match.odd_home, match.odd_away),
                
                # Over/Under odds (se disponível)
                'odd_over_25': match.odd_over_25 if match.odd_over_25 else 2.0,
                'odd_under_25': match.odd_under_25 if match.odd_under_25 else 2.0,
                
                # Both teams to score (se disponível)
                'odd_both_score_yes': match.odd_both_score_yes if match.odd_both_score_yes else 2.0,
                
                # Liga (encoding)
                'league': match.league,
                
                # Target
                'result': match.result
            }
            
            data.append(features)
    
    # ETAPA 3: Criar DataFrame (fora da sessão)
    df = pd.DataFrame(data)
    print(f"   ✅ {len(df)} registros preparados")
    print(f"   📋 Features: {len(df.columns) - 1}")
    
    # Encoding da liga
    le_league = LabelEncoder()
    df['league_encoded'] = le_league.fit_transform(df['league'])
    
    # ETAPA 3: Treinar modelo
    print("\n🎓 ETAPA 3: Treinando modelo...")
    
    # Features e target
    X = df.drop(['result', 'league'], axis=1)
    y = df['result']
    
    print(f"   Features utilizadas: {list(X.columns)}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    print(f"   Treino: {len(X_train)} | Teste: {len(X_test)}")
    
    # Modelo 1: Random Forest
    print("\n   🌲 Treinando Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    
    print(f"      Acurácia: {rf_accuracy * 100:.2f}%")
    
    # Modelo 2: Gradient Boosting
    print("\n   🚀 Treinando Gradient Boosting...")
    gb_model = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    gb_model.fit(X_train, y_train)
    gb_pred = gb_model.predict(X_test)
    gb_accuracy = accuracy_score(y_test, gb_pred)
    
    print(f"      Acurácia: {gb_accuracy * 100:.2f}%")
    
    # Escolhe melhor modelo
    if gb_accuracy > rf_accuracy:
        print(f"\n   ✅ Gradient Boosting escolhido (melhor performance)")
        best_model = gb_model
        best_accuracy = gb_accuracy
        model_name = "GradientBoosting"
    else:
        print(f"\n   ✅ Random Forest escolhido (melhor performance)")
        best_model = rf_model
        best_accuracy = rf_accuracy
        model_name = "RandomForest"
    
    # ETAPA 4: Validação cruzada
    print("\n🔄 ETAPA 4: Validação cruzada...")
    cv_scores = cross_val_score(best_model, X, y, cv=5)
    print(f"   Scores: {[f'{s*100:.1f}%' for s in cv_scores]}")
    print(f"   Média: {cv_scores.mean() * 100:.2f}% (±{cv_scores.std() * 100:.2f}%)")
    
    # ETAPA 5: Feature Importance
    print("\n📊 ETAPA 5: Importância das features...")
    if hasattr(best_model, 'feature_importances_'):
        importances = pd.DataFrame({
            'feature': X.columns,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n   Top 10 features mais importantes:")
        for idx, row in importances.head(10).iterrows():
            print(f"      {row['feature']}: {row['importance']:.4f}")
    
    # ETAPA 6: Relatório de classificação
    print("\n📋 ETAPA 6: Relatório de classificação...")
    y_pred_full = best_model.predict(X_test)
    print("\n" + classification_report(y_test, y_pred_full, target_names=['away', 'draw', 'home']))
    
    # ETAPA 7: Salvar modelo
    print("\n💾 ETAPA 7: Salvando modelo...")
    
    model_data = {
        'model': best_model,
        'model_name': model_name,
        'feature_names': list(X.columns),
        'league_encoder': le_league,
        'accuracy': best_accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'trained_at': datetime.now(),
        'n_samples': len(df)
    }
    
    joblib.dump(model_data, 'ml_model_trained.pkl')
    print(f"   ✅ Modelo salvo: ml_model_trained.pkl")
    
    # ETAPA 8: Teste de predição
    print("\n🎯 ETAPA 8: Teste de predição...")
    
    # Carrega partida agendada para testar
    with get_db() as db:
        upcoming = db.query(Match).filter(Match.status == 'scheduled').first()
        
        if upcoming and all([upcoming.odd_home, upcoming.odd_draw, upcoming.odd_away]):
            test_features = {
                'odd_home': upcoming.odd_home,
                'odd_draw': upcoming.odd_draw,
                'odd_away': upcoming.odd_away,
                'prob_home': 1 / upcoming.odd_home,
                'prob_draw': 1 / upcoming.odd_draw,
                'prob_away': 1 / upcoming.odd_away,
                'odd_diff_home_away': upcoming.odd_home - upcoming.odd_away,
                'odd_ratio_home_away': upcoming.odd_home / upcoming.odd_away,
                'is_home_favorite': 1 if upcoming.odd_home < upcoming.odd_away else 0,
                'favorite_odd': min(upcoming.odd_home, upcoming.odd_away),
                'odd_over_25': upcoming.odd_over_25 if upcoming.odd_over_25 else 2.0,
                'odd_under_25': upcoming.odd_under_25 if upcoming.odd_under_25 else 2.0,
                'odd_both_score_yes': upcoming.odd_both_score_yes if upcoming.odd_both_score_yes else 2.0,
                'league_encoded': le_league.transform([upcoming.league])[0]
            }
            
            team_home = upcoming.team_home
            team_away = upcoming.team_away
            league = upcoming.league
            odd_home = upcoming.odd_home
            odd_draw = upcoming.odd_draw
            odd_away = upcoming.odd_away
            
            X_test_single = pd.DataFrame([test_features])
            prediction = best_model.predict(X_test_single)[0]
            proba = best_model.predict_proba(X_test_single)[0]
            
            print(f"\n   🎮 Partida teste: {team_home} vs {team_away}")
            print(f"   Liga: {league}")
            print(f"   Odds: Casa={odd_home} | Empate={odd_draw} | Fora={odd_away}")
            print(f"\n   🔮 Predição: {prediction}")
            print(f"   📊 Probabilidades:")
            classes = best_model.classes_
            for i, cls in enumerate(classes):
                print(f"      {cls}: {proba[i] * 100:.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ MODELO ML TREINADO E SALVO COM SUCESSO!")
    print(f"🎯 Acurácia final: {best_accuracy * 100:.2f}%")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
