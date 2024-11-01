from dataclasses import dataclass
from typing import Dict, List
import numpy as np

@dataclass
class BattleMetrics:
    """Класс для хранения метрик боя"""
    time_alive: float
    enemies_killed: int
    base_damage: float
    damage_taken: float
    damage_dealt: float
    survival_rate: float  # Новая метрика
    kill_death_ratio: float  # Новая метрика
    objective_score: float  # Новая метрика

class FitnessCalculator:
    """Класс для расчета приспособленности с адаптивными весами"""
    def __init__(self):
        # Начальные веса для разных компонентов фитнеса
        self.weights = {
            'time_alive': 0.15,
            'enemies_killed': 0.20,
            'base_damage': 0.25,
            'damage_taken': 0.10,
            'damage_dealt': 0.15,
            'survival_rate': 0.05,
            'kill_death_ratio': 0.05,
            'objective_score': 0.05
        }

        # История весов для анализа
        self.weight_history: Dict[str, List[float]] = {
            metric: [] for metric in self.weights.keys()
        }

        # Параметры адаптации
        self.adaptation_rate = 0.05
        self.min_weight = 0.05
        self.max_weight = 0.4

        # История успешности для каждой метрики
        self.metric_success: Dict[str, List[float]] = {
            metric: [] for metric in self.weights.keys()
        }

    def _normalize_weights(self) -> None:
        """Нормализация весов, чтобы сумма равнялась 1"""
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total

    def _update_weights(self, metrics_correlation: Dict[str, float]) -> None:
        """Обновление весов на основе корреляции метрик с успехом"""
        # Обновляем веса на основе корреляции
        for metric, correlation in metrics_correlation.items():
            current_weight = self.weights[metric]
            if correlation > 0:
                # Увеличиваем вес для положительно коррелирующих метрик
                new_weight = current_weight * (1 + self.adaptation_rate * correlation)
            else:
                # Уменьшаем вес для отрицательно коррелирующих метрик
                new_weight = current_weight * (1 - self.adaptation_rate * abs(correlation))

            # Ограничиваем веса
            self.weights[metric] = np.clip(new_weight, self.min_weight, self.max_weight)

        # Нормализуем веса
        self._normalize_weights()

        # Сохраняем историю весов
        for metric, weight in self.weights.items():
            self.weight_history[metric].append(weight)

    def calculate_fitness(self, robot: 'Robot') -> float:
        """Расчет приспособленности с учетом новых характеристик"""
        base_fitness = (
            robot.kills * 100 +
            robot.base_damage_dealt * 0.5 -
            robot.damage_taken * 0.3
        )

        # Добавляем бонусы за специальные характеристики
        if hasattr(robot.genes, 'combo_multiplier'):
            base_fitness *= (1 + (robot.genes.combo_multiplier - 1) * 0.2)

        if hasattr(robot.genes, 'lifesteal_rate'):
            base_fitness *= (1 + robot.genes.lifesteal_rate * 0.3)

        if hasattr(robot.genes, 'accuracy'):
            base_fitness *= (1 + (robot.genes.accuracy - 0.5) * 0.2)

        if hasattr(robot.genes, 'multishot_chance'):
            base_fitness *= (1 + robot.genes.multishot_chance * 0.3)

        return max(0, base_fitness)

    def analyze_metrics_correlation(self, battle_history: List[Dict]) -> Dict[str, float]:
        """Анализ корреляции метрик с успехом в битвах"""
        if not battle_history:
            return {metric: 0.0 for metric in self.weights.keys()}

        # Преобразуем историю в массивы для анализа
        metrics_arrays = {metric: [] for metric in self.weights.keys()}
        success_array = []

        for battle in battle_history:
            for metric in self.weights.keys():
                metrics_arrays[metric].append(battle.get(metric, 0.0))
            success_array.append(battle.get('battle_success', 0.0))

        # Вычисляем корреляцию каждой метрики с успехом
        correlations = {}
        for metric, values in metrics_arrays.items():
            if len(values) > 1:  # Нужно минимум 2 значения для корреляции
                correlation = np.corrcoef(values, success_array)[0, 1]
                correlations[metric] = correlation if not np.isnan(correlation) else 0.0
            else:
                correlations[metric] = 0.0

        return correlations

    def update_from_battle_history(self, battle_history: List[Dict]) -> None:
        """Обновление весов на основе истории битв"""
        correlations = self.analyze_metrics_correlation(battle_history)
        self._update_weights(correlations)
