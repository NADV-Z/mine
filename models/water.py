# models/water.py
from config import GlobalConfig

class WaterModel:
    """
    Water supply model for colony sustainability.
    Calculates additional water needs based on colony build timeline.
    """
    
    def __init__(self):
        # Water consumption parameters
        self.per_capita_water = 50  # tons/person/year
        self.colony_population = 10_000  # initial population
        
        # Water logistics cost ($/ton delivered to Mars)
        self.water_delivery_cost = 5000  # $/ton
    
    def calculate_additional_needs(self, built_year):
        """
        Calculate annual water supplement needs and logistics cost.
        
        Args:
            built_year: Year when colony construction completes
        
        Returns:
            tuple: (water_mass in tons, water_cost in $)
        """
        # Annual water requirement
        water_mass = self.colony_population * self.per_capita_water
        
        # Total logistics cost for water delivery
        water_cost = water_mass * self.water_delivery_cost
        
        return water_mass, water_cost
