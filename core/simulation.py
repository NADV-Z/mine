# core/simulation.py
import numpy as np
from config import GlobalConfig
from models.environment import EnvironmentModel
from utils import get_debris_factor

class SimulationResult:
    """Container for simulation results."""
    def __init__(self, final_year, total_cost, history):
        self.final_year = final_year
        self.total_cost = total_cost
        self.history = history

class Simulator:
    """
    Core simulation engine for space transportation scenarios.
    Supports three scenarios: A (elevator-only), B (rocket-only), C (mixed).
    """
    
    def __init__(self, context, rocket_flights_per_day=None):
        self.context = context
        self.rocket_flights_per_day = rocket_flights_per_day or GlobalConfig.ROCKET_FLIGHTS_PER_DAY
        
        # Initialize environment model if needed
        self.env_model = None
        if context.enable_environment:
            self.env_model = EnvironmentModel(context)
    
    def run(self, scenario):
        """
        Run simulation for a given scenario.
        
        Args:
            scenario: 'A' (pure elevator), 'B' (pure rocket), or 'C' (mixed)
        
        Returns:
            SimulationResult object with final_year, total_cost, and history
        """
        if scenario == 'A':
            return self._run_scenario_a()
        elif scenario == 'B':
            return self._run_scenario_b()
        elif scenario == 'C':
            return self._run_scenario_c()
        else:
            raise ValueError(f"Unknown scenario: {scenario}")
    
    def _run_scenario_a(self):
        """Scenario A: Pure space elevator."""
        year = GlobalConfig.START_YEAR
        cumulative_mass = 0.0
        total_cost = 0.0
        history = []
        
        # Track reinforcement progress
        trips_completed = 0
        
        while cumulative_mass < GlobalConfig.GOAL_MASS_TONS:
            # Calculate current capacity using logistic curve
            t = year - GlobalConfig.START_YEAR
            capacity = self._get_elevator_capacity(t, trips_completed)
            
            # Deliver mass this year
            mass_delivered = min(
                capacity * GlobalConfig.SE_PORTS,
                GlobalConfig.GOAL_MASS_TONS - cumulative_mass
            )
            
            cumulative_mass += mass_delivered
            
            # Calculate costs
            year_cost = self._calculate_elevator_cost(year, mass_delivered, trips_completed)
            total_cost += year_cost
            
            # Environmental impact (no rockets in Scenario A)
            env_data = {}
            if self.env_model:
                env_data = self.env_model.update_year(year, 0, scenario='A')
                year_cost += env_data.get('tax_atm', 0) + env_data.get('tax_orb', 0)
                total_cost = sum(h['total_cost'] for h in history) + year_cost
            
            # Update reinforcement progress
            if year - GlobalConfig.START_YEAR < GlobalConfig.SE_REINFORCE_YEARS:
                trips_per_year = GlobalConfig.SE_REINFORCE_TRIPS_TOTAL / GlobalConfig.SE_REINFORCE_YEARS
                trips_completed = min(
                    int((year - GlobalConfig.START_YEAR + 1) * trips_per_year),
                    GlobalConfig.SE_REINFORCE_TRIPS_TOTAL
                )
            
            # Record history
            history.append({
                'year': year,
                'rocket_launches': 0,
                'elevator_mass': mass_delivered,
                'cumulative_mass': cumulative_mass,
                'total_cost': year_cost,
                'elevator_capacity': capacity * GlobalConfig.SE_PORTS,
                'trips_completed': trips_completed,
                **env_data
            })
            
            year += 1
        
        return SimulationResult(year - 1, total_cost, history)
    
    def _run_scenario_b(self):
        """Scenario B: Pure rocket launches."""
        year = GlobalConfig.START_YEAR
        cumulative_mass = 0.0
        total_cost = 0.0
        history = []
        total_launches = 0
        
        while cumulative_mass < GlobalConfig.GOAL_MASS_TONS:
            # Calculate launches needed this year
            max_launches = int(
                GlobalConfig.ROCKET_BASES * 
                365 * 
                self.rocket_flights_per_day
            )
            
            # Effective launches accounting for weather
            if self.context.is_stochastic:
                weather_rate = np.random.normal(
                    GlobalConfig.ROCKET_WEATHER_RATE_MEAN,
                    GlobalConfig.ROCKET_WEATHER_RATE_STD
                )
                weather_rate = np.clip(weather_rate, 0.5, 1.0)
            else:
                weather_rate = GlobalConfig.ROCKET_WEATHER_RATE_MEAN
            
            effective_launches = int(max_launches * weather_rate)
            
            # Mass delivered
            mass_delivered = min(
                effective_launches * GlobalConfig.ROCKET_PAYLOAD_TONS,
                GlobalConfig.GOAL_MASS_TONS - cumulative_mass
            )
            
            # Actual launches needed (may be less than max if goal is near)
            actual_launches = int(np.ceil(mass_delivered / GlobalConfig.ROCKET_PAYLOAD_TONS))
            
            cumulative_mass += mass_delivered
            total_launches += actual_launches
            
            # Calculate costs with learning curve
            year_cost = self._calculate_rocket_cost(total_launches, actual_launches)
            total_cost += year_cost
            
            # Environmental impact
            env_data = {}
            if self.env_model:
                env_data = self.env_model.update_year(year, actual_launches, scenario='B')
                env_cost = env_data.get('tax_atm', 0) + env_data.get('tax_orb', 0)
                year_cost += env_cost
                total_cost = sum(h['total_cost'] for h in history) + year_cost
            
            # Record history
            history.append({
                'year': year,
                'rocket_launches': actual_launches,
                'elevator_mass': 0,
                'cumulative_mass': cumulative_mass,
                'total_cost': year_cost,
                'total_launches': total_launches,
                **env_data
            })
            
            year += 1
        
        return SimulationResult(year - 1, total_cost, history)
    
    def _run_scenario_c(self):
        """Scenario C: Mixed strategy (elevator + rocket)."""
        year = GlobalConfig.START_YEAR
        cumulative_mass = 0.0
        total_cost = 0.0
        history = []
        total_launches = 0
        trips_completed = 0
        
        while cumulative_mass < GlobalConfig.GOAL_MASS_TONS:
            # Calculate elevator capacity
            t = year - GlobalConfig.START_YEAR
            elevator_capacity = self._get_elevator_capacity(t, trips_completed)
            total_elevator_capacity = elevator_capacity * GlobalConfig.SE_PORTS
            
            # Determine allocation ratio
            beta = self.context.beta_elevator_ratio
            if beta is None:
                beta = GlobalConfig.SE_ALLOCATION_RATIO_BETA
            
            # Mass to be delivered this year
            remaining_mass = GlobalConfig.GOAL_MASS_TONS - cumulative_mass
            
            # Elevator delivery
            elevator_target = min(total_elevator_capacity, remaining_mass * beta)
            elevator_mass = min(elevator_target, remaining_mass)
            
            # Rocket delivery for the remainder
            rocket_mass = min(
                remaining_mass - elevator_mass,
                remaining_mass * (1 - beta)
            )
            
            # Calculate rocket launches needed
            rocket_launches = 0
            if rocket_mass > 0:
                # Max rockets available
                max_launches = int(
                    GlobalConfig.ROCKET_BASES * 
                    365 * 
                    self.rocket_flights_per_day
                )
                
                # Weather factor
                if self.context.is_stochastic:
                    weather_rate = np.random.normal(
                        GlobalConfig.ROCKET_WEATHER_RATE_MEAN,
                        GlobalConfig.ROCKET_WEATHER_RATE_STD
                    )
                    weather_rate = np.clip(weather_rate, 0.5, 1.0)
                else:
                    weather_rate = GlobalConfig.ROCKET_WEATHER_RATE_MEAN
                
                # Launches needed
                launches_needed = int(np.ceil(rocket_mass / GlobalConfig.ROCKET_PAYLOAD_TONS))
                rocket_launches = min(launches_needed, int(max_launches * weather_rate))
                
                # Actual mass delivered by rockets
                rocket_mass = rocket_launches * GlobalConfig.ROCKET_PAYLOAD_TONS
                rocket_mass = min(rocket_mass, remaining_mass - elevator_mass)
            
            # Total delivered
            total_delivered = elevator_mass + rocket_mass
            cumulative_mass += total_delivered
            total_launches += rocket_launches
            
            # Calculate costs
            elevator_cost = self._calculate_elevator_cost(year, elevator_mass, trips_completed)
            rocket_cost = 0
            if rocket_launches > 0:
                rocket_cost = self._calculate_rocket_cost(total_launches, rocket_launches)
            
            year_cost = elevator_cost + rocket_cost
            total_cost += year_cost
            
            # Environmental impact
            env_data = {}
            if self.env_model:
                env_data = self.env_model.update_year(year, rocket_launches, scenario='C')
                env_cost = env_data.get('tax_atm', 0) + env_data.get('tax_orb', 0)
                year_cost += env_cost
                total_cost = sum(h['total_cost'] for h in history) + year_cost
            
            # Update reinforcement progress
            if year - GlobalConfig.START_YEAR < GlobalConfig.SE_REINFORCE_YEARS:
                trips_per_year = GlobalConfig.SE_REINFORCE_TRIPS_TOTAL / GlobalConfig.SE_REINFORCE_YEARS
                trips_completed = min(
                    int((year - GlobalConfig.START_YEAR + 1) * trips_per_year),
                    GlobalConfig.SE_REINFORCE_TRIPS_TOTAL
                )
            
            # Record history
            history.append({
                'year': year,
                'rocket_launches': rocket_launches,
                'elevator_mass': elevator_mass,
                'cumulative_mass': cumulative_mass,
                'total_cost': year_cost,
                'elevator_cost': elevator_cost,
                'rocket_cost': rocket_cost,
                'elevator_capacity': total_elevator_capacity,
                'trips_completed': trips_completed,
                **env_data
            })
            
            year += 1
        
        return SimulationResult(year - 1, total_cost, history)
    
    def _get_elevator_capacity(self, t, trips_completed):
        """
        Calculate elevator capacity using logistic growth curve.
        
        Args:
            t: Years since start (year - START_YEAR)
            trips_completed: Number of reinforcement trips completed
        
        Returns:
            Capacity in tons/year for a single port
        """
        # Logistic growth formula: Cap(t) = K / (1 + A * e^(-r*t))
        K = GlobalConfig.SE_CAP_MAX_K
        A = GlobalConfig.SE_LOGISTIC_A
        r = GlobalConfig.SE_LOGISTIC_R
        
        capacity = K / (1 + A * np.exp(-r * t))
        
        return capacity
    
    def _calculate_elevator_cost(self, year, mass_delivered, trips_completed):
        """
        Calculate elevator operational cost with learning curve.
        
        Args:
            year: Current year
            mass_delivered: Mass delivered this year (tons)
            trips_completed: Number of reinforcement trips completed
        
        Returns:
            Total cost for this year ($)
        """
        if mass_delivered == 0:
            return 0.0
        
        # Operational cost per kg with learning curve
        t = year - GlobalConfig.START_YEAR
        cost_per_kg = (
            GlobalConfig.SE_OP_COST_MIN + 
            (GlobalConfig.SE_OP_COST_INIT - GlobalConfig.SE_OP_COST_MIN) * 
            np.exp(-GlobalConfig.SE_DECAY_K * t)
        )
        
        # Total operational cost
        operational_cost = mass_delivered * 1000 * cost_per_kg
        
        # Construction cost (during first 20 years)
        construction_cost = 0.0
        if year - GlobalConfig.START_YEAR < GlobalConfig.SE_REINFORCE_YEARS:
            # CNT material cost with learning curve
            cnt_cost_per_ton = (
                GlobalConfig.SE_CNT_COST_MIN +
                (GlobalConfig.SE_CNT_COST_INIT - GlobalConfig.SE_CNT_COST_MIN) *
                np.exp(-GlobalConfig.SE_CNT_DECAY_K * t)
            )
            
            # Mass increment from reinforcement
            mass_growth_rate = GlobalConfig.SE_GROWTH_RATE
            current_mass = GlobalConfig.SE_MASS_INIT_TONS * (1 + mass_growth_rate) ** trips_completed
            
            trips_this_year = GlobalConfig.SE_REINFORCE_TRIPS_TOTAL / GlobalConfig.SE_REINFORCE_YEARS
            mass_added = current_mass * mass_growth_rate * trips_this_year
            
            construction_cost = mass_added * cnt_cost_per_ton * GlobalConfig.SE_PORTS
        
        return operational_cost + construction_cost
    
    def _calculate_rocket_cost(self, total_launches, current_year_launches):
        """
        Calculate rocket cost with learning curve.
        
        Args:
            total_launches: Cumulative launches to date (used for learning curve)
            current_year_launches: Launches this year
        
        Returns:
            Total cost for this year ($)
        """
        if current_year_launches == 0:
            return 0.0
        
        # Learning curve: cost decreases with cumulative launches
        # Use average cost for launches this year
        total_cost = 0.0
        
        for i in range(current_year_launches):
            launch_number = total_launches - current_year_launches + i + 1
            
            # Cost with learning curve
            cost = (
                GlobalConfig.ROCKET_COST_MIN +
                (GlobalConfig.ROCKET_COST_INIT - GlobalConfig.ROCKET_COST_MIN) *
                np.exp(-GlobalConfig.ROCKET_DECAY_K * launch_number / 1000.0)
            )
            
            total_cost += cost
        
        return total_cost
