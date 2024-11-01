from dataclasses import dataclass, asdict
import random

@dataclass
class RobotGenes:
    """Гены робота"""
    # Базовые характеристики
    health: float
    speed: float
    damage: float
    aggression: float

    # Характеристики для MeleeRobot
    combo_multiplier: float = 1.0    # Множитель урона (1.0 - 2.0)
    lifesteal_rate: float = 0.0      # Процент восстановления здоровья (0.0 - 0.3)

    # Характеристики для RangedRobot
    accuracy: float = 0.7            # Точность стрельбы (0.5 - 1.0)
    multishot_chance: float = 0.0    # Шанс мультивыстрела (0.0 - 0.3)

    def to_dict(self) -> dict:
        """Преобразование генов в словарь"""
        return asdict(self)

    @classmethod
    def from_robot(cls, robot: 'Robot') -> 'RobotGenes':
        """Создание генов из робота"""
        base_genes = {
            'health': robot.health,
            'speed': robot.speed,
            'damage': robot.damage,
            'aggression': random.uniform(0.3, 0.8)
        }

        # Проверяем тип робота по имени класса
        robot_type = robot.__class__.__name__

        if robot_type == 'MeleeRobot':
            base_genes.update({
                'combo_multiplier': random.uniform(1.0, 2.0),
                'lifesteal_rate': random.uniform(0.0, 0.3)
            })
        elif robot_type == 'RangedRobot':
            base_genes.update({
                'accuracy': random.uniform(0.5, 1.0),
                'multishot_chance': random.uniform(0.0, 0.3)
            })

        return cls(**base_genes)

    def mutate(self, mutation_rate: float) -> None:
        """Мутация генов"""
        for field in self.__dataclass_fields__:
            if random.random() < mutation_rate:
                current_value = getattr(self, field)

                # Определяем диапазоны мутации для разных характеристик
                ranges = {
                    'health': (50, 200),
                    'speed': (2, 6),
                    'damage': (10, 30),
                    'aggression': (0.3, 0.8),
                    'combo_multiplier': (1.0, 2.0),
                    'lifesteal_rate': (0.0, 0.3),
                    'accuracy': (0.5, 1.0),
                    'multishot_chance': (0.0, 0.3)
                }

                if field in ranges:
                    min_val, max_val = ranges[field]
                    mutation = random.uniform(-0.1, 0.1) * (max_val - min_val)
                    new_value = current_value + mutation
                    new_value = max(min_val, min(max_val, new_value))
                    setattr(self, field, new_value)
