"""
Modelo de Machine Learning para prever total de gols
Usa Random Forest Classifier com dados de odds
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import joblib
import logging
from datetime import datetime
from typing import Dict, List, Tuple

from database_rapidapi import get_db
from models_rapidapi import Match, PredictionModel, Prediction

logger = logging.getLogger(__name__)


class GoalsPredictionModel:
    """Modelo para prever total de gols em partidas de futebol virtual"""
    
    def __init__(self):
        self.model_goals = None  # Predição de total de gols
        self.model_result = None  # Predição de resultado (home/draw/away)
        self.label_encoder_league = LabelEncoder()
        self.label_encoder_result = LabelEncoder()
        self.feature_columns = []
        self.is_trained = False
    
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para o modelo
        
        Args:
            df: DataFrame com dados das partidas
        
        Returns:
            DataFrame com features preparadas
        """
        # Copia para não modificar original
        df = df.copy()
        
        # Encode liga
        df['league_encoded'] = self.label_encoder_league.fit_transform(df['league'])
        
        # Features baseadas em odds
        features = [
            'league_encoded',
            'odd_home',
            'odd_draw', 
            'odd_away',
            'odd_over_25',
            'odd_under_25',
            'odd_both_score_yes',
            'odd_both_score_no',
            'odd_exact_goals_0',
            'odd_exact_goals_1',
            'odd_exact_goals_2',
            'odd_exact_goals_3',
        ]
        
        # Features derivadas (probabilidades implícitas)
        df['prob_home'] = 1 / df['odd_home']
        df['prob_draw'] = 1 / df['odd_draw']
        df['prob_away'] = 1 / df['odd_away']
        df['prob_over_25'] = 1 / df['odd_over_25']
        df['prob_under_25'] = 1 / df['odd_under_25']
        df['prob_both_score'] = 1 / df['odd_both_score_yes']
        
        # Diferença de odds (indica favorito)
        df['odd_diff'] = df['odd_home'] - df['odd_away']
        df['prob_diff'] = df['prob_home'] - df['prob_away']
        
        # Features de gols esperados baseadas em odds exatas
        df['expected_goals_low'] = (
            0 * (1/df['odd_exact_goals_0']) + 
            1 * (1/df['odd_exact_goals_1']) +
            2 * (1/df['odd_exact_goals_2'])
        ) / 3  # Média ponderada simplificada
        
        features_derived = [
            'prob_home', 'prob_draw', 'prob_away',
            'prob_over_25', 'prob_under_25', 'prob_both_score',
            'odd_diff', 'prob_diff', 'expected_goals_low'
        ]
        
        self.feature_columns = features + features_derived
        
        return df[self.feature_columns]
    
    def load_data(self, min_samples: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Carrega dados de partidas finalizadas do banco
        
        Args:
            min_samples: Mínimo de partidas finalizadas necessárias
        
        Returns:
            Tupla (X, y) com features e targets
        """
        with get_db() as db:
            # Busca apenas partidas finalizadas (com resultado)
            matches = db.query(Match).filter(
                Match.status == "finished",
                Match.total_goals.isnot(None)
            ).all()
            
            if len(matches) < min_samples:
                raise ValueError(
                    f"Dados insuficientes! Encontradas {len(matches)} partidas finalizadas. "
                    f"Mínimo necessário: {min_samples}. "
                    f"Execute 'python main_rapidapi.py continuous' para coletar mais dados."
                )
            
            logger.info(f"✅ {len(matches)} partidas finalizadas carregadas do banco")
            
            # Converte para DataFrame
            data = []
            for m in matches:
                data.append({
                    'id': m.id,
                    'external_id': m.external_id,
                    'league': m.league,
                    'team_home': m.team_home,
                    'team_away': m.team_away,
                    'odd_home': m.odd_home,
                    'odd_draw': m.odd_draw,
                    'odd_away': m.odd_away,
                    'odd_over_25': m.odd_over_25,
                    'odd_under_25': m.odd_under_25,
                    'odd_both_score_yes': m.odd_both_score_yes,
                    'odd_both_score_no': m.odd_both_score_no,
                    'odd_exact_goals_0': m.odd_exact_goals_0,
                    'odd_exact_goals_1': m.odd_exact_goals_1,
                    'odd_exact_goals_2': m.odd_exact_goals_2,
                    'odd_exact_goals_3': m.odd_exact_goals_3,
                    'total_goals': m.total_goals,
                    'result': m.result
                })
            
            df = pd.DataFrame(data)
            
            # Remove linhas com valores nulos nas features importantes
            df = df.dropna(subset=[
                'odd_home', 'odd_draw', 'odd_away', 
                'odd_over_25', 'odd_under_25',
                'total_goals', 'result'
            ])
            
            logger.info(f"✅ {len(df)} partidas válidas após limpeza")
            
            # Prepara features
            X = self._prepare_features(df)
            
            # Targets
            y_goals = df['total_goals']
            y_result = df['result']
            
            return X, y_goals, y_result, df
    
    def train(self, test_size: float = 0.2, random_state: int = 42):
        """
        Treina modelos de predição
        
        Args:
            test_size: Proporção dos dados para teste
            random_state: Seed para reprodutibilidade
        """
        logger.info("\n" + "="*60)
        logger.info("🤖 TREINANDO MODELO DE MACHINE LEARNING")
        logger.info("="*60 + "\n")
        
        # Carrega dados
        X, y_goals, y_result, df_original = self.load_data()
        
        # Split treino/teste
        X_train, X_test, y_goals_train, y_goals_test = train_test_split(
            X, y_goals, test_size=test_size, random_state=random_state
        )
        
        _, _, y_result_train, y_result_test = train_test_split(
            X, y_result, test_size=test_size, random_state=random_state
        )
        
        logger.info(f"📊 Dados divididos:")
        logger.info(f"   Treino: {len(X_train)} partidas")
        logger.info(f"   Teste: {len(X_test)} partidas\n")
        
        # ===== MODELO 1: Predição de Total de Gols =====
        logger.info("🎯 Treinando modelo de TOTAL DE GOLS...")
        
        self.model_goals = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.model_goals.fit(X_train, y_goals_train)
        
        # Avaliação
        y_goals_pred = self.model_goals.predict(X_test)
        y_goals_pred_rounded = np.round(y_goals_pred).astype(int)
        
        mae = mean_absolute_error(y_goals_test, y_goals_pred)
        accuracy_goals = accuracy_score(y_goals_test, y_goals_pred_rounded)
        
        logger.info(f"   MAE (Erro Médio Absoluto): {mae:.2f} gols")
        logger.info(f"   Acurácia (gols exatos): {accuracy_goals:.2%}\n")
        
        # ===== MODELO 2: Predição de Resultado =====
        logger.info("🎯 Treinando modelo de RESULTADO (Casa/Empate/Fora)...")
        
        self.label_encoder_result.fit(y_result)
        y_result_train_encoded = self.label_encoder_result.transform(y_result_train)
        y_result_test_encoded = self.label_encoder_result.transform(y_result_test)
        
        self.model_result = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.model_result.fit(X_train, y_result_train_encoded)
        
        # Avaliação
        y_result_pred = self.model_result.predict(X_test)
        accuracy_result = accuracy_score(y_result_test_encoded, y_result_pred)
        
        logger.info(f"   Acurácia: {accuracy_result:.2%}\n")
        
        # Feature importance
        logger.info("📊 Features mais importantes (Total de Gols):")
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model_goals.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.head(10).iterrows():
            logger.info(f"   {row['feature']:25s}: {row['importance']:.4f}")
        
        self.is_trained = True
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ MODELOS TREINADOS COM SUCESSO!")
        logger.info(f"{'='*60}\n")
        
        return {
            'mae_goals': mae,
            'accuracy_goals': accuracy_goals,
            'accuracy_result': accuracy_result,
            'feature_importance': feature_importance
        }
    
    def predict(self, match_data: Dict) -> Dict:
        """
        Faz predição para uma partida
        
        Args:
            match_data: Dicionário com dados da partida
        
        Returns:
            Dicionário com predições
        """
        if not self.is_trained:
            raise ValueError("Modelo não treinado! Execute .train() primeiro.")
        
        # Prepara features
        df = pd.DataFrame([match_data])
        X = self._prepare_features(df)
        
        # Predição de gols
        goals_pred = self.model_goals.predict(X)[0]
        goals_rounded = int(np.round(goals_pred))
        
        # Predição de resultado
        result_pred_encoded = self.model_result.predict(X)[0]
        result_pred_proba = self.model_result.predict_proba(X)[0]
        result_pred = self.label_encoder_result.inverse_transform([result_pred_encoded])[0]
        
        # Confiança (probabilidade máxima)
        confidence = result_pred_proba.max()
        
        return {
            'predicted_total_goals': goals_rounded,
            'predicted_total_goals_float': goals_pred,
            'predicted_result': result_pred,
            'confidence': confidence,
            'result_probabilities': {
                label: prob 
                for label, prob in zip(
                    self.label_encoder_result.classes_, 
                    result_pred_proba
                )
            }
        }
    
    def save(self, filepath: str = "models/goals_prediction_model.pkl"):
        """Salva modelo treinado"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model_goals': self.model_goals,
            'model_result': self.model_result,
            'label_encoder_league': self.label_encoder_league,
            'label_encoder_result': self.label_encoder_result,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"💾 Modelo salvo em: {filepath}")
    
    def load(self, filepath: str = "models/goals_prediction_model.pkl"):
        """Carrega modelo treinado"""
        model_data = joblib.load(filepath)
        
        self.model_goals = model_data['model_goals']
        self.model_result = model_data['model_result']
        self.label_encoder_league = model_data['label_encoder_league']
        self.label_encoder_result = model_data['label_encoder_result']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"✅ Modelo carregado de: {filepath}")
