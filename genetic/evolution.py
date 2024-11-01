from typing import List, Optional, Dict
import numpy as np
from .chromosome import RobotGenes
from .population import Population
from .fitness import FitnessCalculator

class Evolution:
    """Класс управления эволюционным процессом"""
    def __init__(self, initial_population_size: int = 10, mutation_rate: float = 0.1):
        self.min_population_size = 6
        self.max_population_size = 20
        self.current_population_size = initial_population_size
        self.base_mutation_rate = mutation_rate
        
        # Инициализация популяций с текущим размером
        self.populations = {
            'blue': Population(self.current_population_size),
            'red': Population(self.current_population_size)
        }
        
        self.fitness_calculator = FitnessCalculator()
        
        # История фитнеса для адаптивной мутации
        self.fitness_history: Dict[str, List[float]] = {
            'blue': [],
            'red': []
        }
        
        # Параметры адаптивной мутации
        self.mutation_rates = {
            'blue': mutation_rate,
            'red': mutation_rate
        }
        self.adaptation_rate = 0.1
        self.min_mutation_rate = 0.01
        self.max_mutation_rate = 0.3
        
        # Параметры для динамического размера популяции
        self.stagnation_threshold = 3  # Количество поколений без улучшения
        self.improvement_threshold = 0.05  # Минимальное улучшение фитнеса
        self.size_change_rate = 2  # Количество особей для изменения размера

    def _update_mutation_rate(self, team: str) -> None:
        """Обновление скорости мутации на основе истории фитнеса"""
        if len(self.fitness_history[team]) < 2:
            return
            
        # Получаем последние значения фитнеса
        current_fitness = self.fitness_history[team][-1]
        prev_fitness = self.fitness_history[team][-2]
        
        # Вычисляем относительное изменение
        fitness_change = (current_fitness - prev_fitness) / max(abs(prev_fitness), 1e-10)
        
        current_rate = self.mutation_rates[team]
        
        if fitness_change > 0:
            # Если фитнес улучшается, уменьшаем мутацию
            new_rate = current_rate * (1 - self.adaptation_rate)
        else:
            # Если фитнес ухудшается или стагнирует, увеличиваем мутацию
            new_rate = current_rate * (1 + self.adaptation_rate)
            
        # Ограничиваем значение
        self.mutation_rates[team] = np.clip(new_rate, 
                                          self.min_mutation_rate, 
                                          self.max_mutation_rate)

    def _update_fitness_history(self, team: str, population: Population) -> None:
        """Обновление истории фитнеса"""
        if not population.individuals:
            return
            
        # Вычисляем средний фитнес популяции
        avg_fitness = np.mean([
            ind.fitness for ind in population.individuals 
            if hasattr(ind, 'fitness')
        ])
        
        self.fitness_history[team].append(avg_fitness)
        
        # Ограничиваем историю последними 10 поколениями
        if len(self.fitness_history[team]) > 10:
            self.fitness_history[team] = self.fitness_history[team][-10:]

    def _crossover(self, parent1: RobotGenes, parent2: RobotGenes) -> RobotGenes:
        """Равномерный кроссовер между двумя родителями"""
        child_genes = {}
        
        for field in parent1.__dataclass_fields__:
            val1 = getattr(parent1, field)
            val2 = getattr(parent2, field)
            
            if isinstance(val1, (int, float)):
                if np.random.random() < 0.5:
                    mean_val = (val1 + val2) / 2
                    deviation = abs(val1 - val2) * 0.1
                    child_genes[field] = mean_val + np.random.uniform(-deviation, deviation)
                else:
                    child_genes[field] = val1 if np.random.random() < 0.5 else val2
            else:
                child_genes[field] = val1 if np.random.random() < 0.5 else val2
        
        return RobotGenes(**child_genes)

    def initialize_population(self, robot_type: str, base_robot: 'Robot') -> None:
        """Инициализация популяции для определенного типа робота"""
        population = self.populations[robot_type]
        base_genes = RobotGenes.from_robot(base_robot)

        for _ in range(self.current_population_size):
            new_genes = RobotGenes(**base_genes.to_dict())
            new_genes.mutate(mutation_rate=1.0)
            population.individuals.append(new_genes)

    def _adjust_population_size(self, team: str) -> None:
        """Корректировка размера популяции на основе прогресса эволюции"""
        if len(self.fitness_history[team]) < self.stagnation_threshold:
            return
            
        # Получаем последние значения фитнеса
        recent_fitness = self.fitness_history[team][-self.stagnation_threshold:]
        
        # Проверяем наличие улучшения
        is_improving = all(
            recent_fitness[i] > recent_fitness[i-1] * (1 + self.improvement_threshold)
            for i in range(1, len(recent_fitness))
        )
        
        # Проверяем стагнацию
        is_stagnating = all(
            abs(recent_fitness[i] - recent_fitness[i-1]) < self.improvement_threshold * recent_fitness[i-1]
            for i in range(1, len(recent_fitness))
        )
        
        if is_improving and self.current_population_size < self.max_population_size:
            # Увеличиваем размер популяции при устойчивом улучшении
            self.current_population_size = min(
                self.current_population_size + self.size_change_rate,
                self.max_population_size
            )
        elif is_stagnating and self.current_population_size > self.min_population_size:
            # Уменьшаем размер популяции при стагнации
            self.current_population_size = max(
                self.current_population_size - self.size_change_rate,
                self.min_population_size
            )

    def evolve_population(self, robot_type: str) -> None:
        """Эволюция популяции одного типа роботов"""
        population = self.populations[robot_type]
        
        # Обновляем историю фитнеса и адаптируем параметры
        self._update_fitness_history(robot_type, population)
        self._update_mutation_rate(robot_type)
        self._adjust_population_size(robot_type)
        
        new_individuals = []

        # Элитизм - сохраняем лучших особей (10% популяции)
        elite_count = max(1, int(self.current_population_size * 0.1))
        sorted_individuals = sorted(
            population.individuals,
            key=lambda x: x.fitness if hasattr(x, 'fitness') else 0,
            reverse=True
        )
        
        new_individuals.extend([
            RobotGenes(**ind.to_dict()) 
            for ind in sorted_individuals[:elite_count]
        ])

        # Создаем новое поколение
        while len(new_individuals) < self.current_population_size:
            parent1 = population.select_tournament()
            parent2 = population.select_tournament()
            
            child = self._crossover(parent1, parent2)
            child.mutate(self.mutation_rates[robot_type])
            
            new_individuals.append(child)

        population.individuals = new_individuals
        population.generation += 1
        
        # Обновляем размер популяции в классе Population
        population.size = self.current_population_size
