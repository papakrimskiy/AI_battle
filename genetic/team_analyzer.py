import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass

@dataclass
class EvolutionTrends:
    """Класс для хранения трендов эволюции"""
    generation: int
    avg_fitness: float
    max_fitness: float
    population_size: int
    mutation_rate: float
    diversity: float
    improvement_rate: float

class TeamAnalyzer:
    def __init__(self, data_dir: str = 'genetic_data/'):
        self.data_dir = data_dir
        self.evolution_history: Dict[str, List[EvolutionTrends]] = {
            'blue': [],
            'red': []
        }
        
    def record_generation(self, team: str, population: 'Population', 
                         mutation_rate: float) -> None:
        """Запись данных о поколении"""
        if not population.individuals:
            return
            
        # Расчет метрик поколения
        fitnesses = [ind.fitness for ind in population.individuals if hasattr(ind, 'fitness')]
        if not fitnesses:
            return
            
        avg_fitness = np.mean(fitnesses)
        max_fitness = np.max(fitnesses)
        
        # Расчет разнообразия популяции
        diversity = self._calculate_diversity(population.individuals)
        
        # Расчет скорости улучшения
        improvement_rate = self._calculate_improvement_rate(team, avg_fitness)
        
        # Создание записи о поколении
        trend = EvolutionTrends(
            generation=population.generation,
            avg_fitness=avg_fitness,
            max_fitness=max_fitness,
            population_size=len(population.individuals),
            mutation_rate=mutation_rate,
            diversity=diversity,
            improvement_rate=improvement_rate
        )
        
        self.evolution_history[team].append(trend)
        
    def _calculate_diversity(self, individuals: List['RobotGenes']) -> float:
        """Расчет разнообразия в популяции"""
        if not individuals:
            return 0.0
            
        # Получаем все числовые параметры первой особи для сравнения
        numeric_fields = [
            field for field, value in individuals[0].__dict__.items()
            if isinstance(value, (int, float))
        ]
        
        if not numeric_fields:
            return 0.0
            
        # Вычисляем стандартное отклонение для каждого параметра
        diversities = []
        for field in numeric_fields:
            values = [getattr(ind, field) for ind in individuals]
            diversity = np.std(values) if len(values) > 1 else 0.0
            diversities.append(diversity)
            
        return np.mean(diversities)
        
    def _calculate_improvement_rate(self, team: str, current_fitness: float) -> float:
        """Расчет скорости улучшения фитнеса"""
        history = self.evolution_history[team]
        if not history:
            return 0.0
            
        # Берем последние 5 поколений или меньше
        recent_history = history[-5:]
        if not recent_history:
            return 0.0
            
        # Вычисляем среднее изменение фитнеса
        fitness_changes = [
            (current_fitness - h.avg_fitness) / max(h.avg_fitness, 1e-10)
            for h in recent_history
        ]
        
        return np.mean(fitness_changes)

    def analyze_trends(self, team: str) -> Dict[str, List[float]]:
        """Анализ трендов эволюции"""
        history = self.evolution_history[team]
        if not history:
            return {}
            
        return {
            'generations': [h.generation for h in history],
            'avg_fitness': [h.avg_fitness for h in history],
            'max_fitness': [h.max_fitness for h in history],
            'population_size': [h.population_size for h in history],
            'mutation_rate': [h.mutation_rate for h in history],
            'diversity': [h.diversity for h in history],
            'improvement_rate': [h.improvement_rate for h in history]
        }

    def plot_evolution_trends(self, save_dir: str = 'genetic_plots/') -> None:
        """Визуализация трендов эволюции"""
        plt.figure(figsize=(15, 10))
        
        # Создаем подграфики
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        for team in ['blue', 'red']:
            trends = self.analyze_trends(team)
            if not trends:
                continue
                
            # График фитнеса
            ax1.plot(trends['generations'], trends['avg_fitness'], 
                    label=f'{team} avg fitness')
            ax1.plot(trends['generations'], trends['max_fitness'], 
                    label=f'{team} max fitness', linestyle='--')
            ax1.set_title('Fitness Evolution')
            ax1.legend()
            
            # График размера популяции и мутации
            ax2.plot(trends['generations'], trends['population_size'], 
                    label=f'{team} population size')
            ax2_twin = ax2.twinx()
            ax2_twin.plot(trends['generations'], trends['mutation_rate'], 
                         label=f'{team} mutation rate', linestyle=':', color='red')
            ax2.set_title('Population Size and Mutation Rate')
            ax2.legend(loc='upper left')
            ax2_twin.legend(loc='upper right')
            
            # График разнообразия
            ax3.plot(trends['generations'], trends['diversity'], 
                    label=f'{team} diversity')
            ax3.set_title('Population Diversity')
            ax3.legend()
            
            # График скорости улучшения
            ax4.plot(trends['generations'], trends['improvement_rate'], 
                    label=f'{team} improvement rate')
            ax4.set_title('Improvement Rate')
            ax4.legend()
        
        plt.tight_layout()
        plt.savefig(f'{save_dir}evolution_trends.png')
        plt.close()

    def generate_report(self) -> str:
        """Генерация текстового отчета о трендах"""
        report = []
        
        for team in ['blue', 'red']:
            trends = self.analyze_trends(team)
            if not trends:
                continue
                
            report.append(f"\nTeam {team} Evolution Report:")
            
            # Анализ фитнеса
            avg_improvement = np.mean(trends['improvement_rate'])
            report.append(f"Average improvement rate: {avg_improvement:.2%}")
            
            # Анализ разнообразия
            avg_diversity = np.mean(trends['diversity'])
            report.append(f"Average population diversity: {avg_diversity:.2f}")
            
            # Анализ параметров эволюции
            avg_mutation = np.mean(trends['mutation_rate'])
            avg_population = np.mean(trends['population_size'])
            report.append(f"Average mutation rate: {avg_mutation:.3f}")
            report.append(f"Average population size: {avg_population:.1f}")
            
        return "\n".join(report)
