from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import csv
from datetime import datetime
import pygame
from entities.robot import Robot, MeleeRobot, RangedRobot, TankRobot

@dataclass
class SquadMetrics:
    """Метрики эффективности отряда"""
    task_completion: float = 0.0    # Процент выполнения задачи
    squad_losses: float = 0.0       # Процент потерь состава
    damage_dealt: float = 0.0       # Общий нанесенный урон
    timestamp: float = 0.0          # Время замера

class Squad:
    """Класс отряда роботов"""
    def __init__(self, squad_id: str, task_type: str):
        self.id = squad_id
        self.task_type = task_type
        self.robots: List[Robot] = []
        self.metrics = SquadMetrics()
        self.initial_size = 0
        self.last_update_time = pygame.time.get_ticks()

    def add_robot(self, robot: Robot) -> None:
        """Добавление робота в отряд"""
        self.robots.append(robot)
        if self.initial_size == 0:
            self.initial_size = len(self.robots)

    def update_metrics(self) -> None:
        """Обновление метрик отряда"""
        if not self.robots:
            return

        # Обновляем потери состава
        self.metrics.squad_losses = 1 - (len(self.robots) / self.initial_size)

        # Обновляем общий урон
        total_damage = sum(robot.base_damage_dealt for robot in self.robots)
        self.metrics.damage_dealt = total_damage

        # Обновляем выполнение задачи в зависимости от типа
        if self.task_type == 'attack':
            self.metrics.task_completion = min(1.0, total_damage / 1000)  # Пример порога
        elif self.task_type == 'defense':
            # Процент выживших роботов как показатель успешной защиты
            self.metrics.task_completion = 1 - self.metrics.squad_losses
        else:  # base
            self.metrics.task_completion = len(self.robots) / self.initial_size

        self.metrics.timestamp = pygame.time.get_ticks()

class SquadManager:
    """Менеджер управления отрядами"""
    def __init__(self):
        self.squads: Dict[str, Squad] = {}
        self.last_check_time = pygame.time.get_ticks()
        self.check_interval = 45000  # 45 секунд
        self.csv_logger = CSVLogger()

    def create_squad(self, team: str, generation: int, task_type: str, number: int) -> Squad:
        """Создание нового отряда"""
        squad_id = f"{team}_gen{generation}_{task_type}{number}"
        squad = Squad(squad_id, task_type)
        self.squads[squad_id] = squad
        return squad

    def update(self, base_health: float, enemy_count: int, ally_count: int) -> None:
        """Обновление состояния отрядов"""
        current_time = pygame.time.get_ticks()

        # Обновляем метрики всех отрядов
        for squad in self.squads.values():
            squad.update_metrics()

        # Проверяем необходимость переформирования каждые 45 секунд
        if current_time - self.last_check_time >= self.check_interval:
            self._check_reformation_conditions(base_health, enemy_count, ally_count)
            self.last_check_time = current_time

        # Логирование метрик
        self._log_metrics()

    def _check_reformation_conditions(self, base_health: float, enemy_count: int, ally_count: int) -> None:
        """Проверка условий для переформирования отрядов"""
        force_ratio = ally_count / max(enemy_count, 1)

        for squad in self.squads.values():
            needs_reformation = False

            # Проверяем условия
            if base_health <= 20:  # Критическое здоровье базы
                needs_reformation = True
            elif force_ratio < 0.7 or force_ratio > 1.5:  # Неблагоприятное соотношение сил
                needs_reformation = True
            elif squad.metrics.squad_losses >= 0.4:  # Большие потери в отряде
                needs_reformation = True

            if needs_reformation:
                self._reform_squad(squad)

    def _reform_squad(self, squad: Squad) -> None:
        """Переформирование отряда"""
        # Здесь будет логика переформирования отряда
        pass

    def _log_metrics(self) -> None:
        """Логирование метрик отрядов"""
        for squad in self.squads.values():
            self.csv_logger.log_squad_metrics(squad)

class CSVLogger:
    """Класс для логирования метрик отрядов"""
    def __init__(self):
        self.filename = f"logs/squad_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self._initialize_csv()

    def _initialize_csv(self) -> None:
        """Инициализация CSV файла"""
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'timestamp',
                'squad_id',
                'task_type',
                'robots_count',
                'task_completion',
                'squad_losses',
                'damage_dealt'
            ])

    def log_squad_metrics(self, squad: Squad) -> None:
        """Запись метрик отряда в CSV"""
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                squad.metrics.timestamp,
                squad.id,
                squad.task_type,
                len(squad.robots),
                squad.metrics.task_completion,
                squad.metrics.squad_losses,
                squad.metrics.damage_dealt
            ])
