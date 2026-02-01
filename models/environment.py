# models/environment.py
from config import GlobalConfig, get_dynamic_tax_rate

class EnvironmentModel:
    """
    Environmental impact tracking model.
    Handles atmospheric and orbital debris calculations and environmental taxation.
    """
    
    def __init__(self, context):
        self.context = context
        self.debris_count = GlobalConfig.DEBRIS_BASE_2050
        self.cumulative_bc_emissions = 0.0
        
        # Fuel type configuration
        self.fuel_type = getattr(context, 'current_fuel_type', GlobalConfig.ROCKET_FUEL_TYPE_DEFAULT)
    
    def update_year(self, year, rocket_launches, scenario='C'):
        """
        Update environmental impact for a given year.
        
        Args:
            year: Current year
            rocket_launches: Number of rocket launches this year
            scenario: Scenario type ('A', 'B', or 'C')
        
        Returns:
            dict: Environmental data including impacts and taxes
        """
        if not self.context.enable_environment:
            return {
                'S_atm': 0.0,
                'S_orb': 0.0,
                'S_env': 0.0,
                'tax_atm': 0.0,
                'tax_orb': 0.0,
                'debris_count': self.debris_count
            }
        
        # Calculate atmospheric impact (black carbon emissions)
        S_atm = self._calculate_atmospheric_impact(rocket_launches)
        
        # Calculate orbital debris impact
        S_orb = self._calculate_orbital_impact(rocket_launches)
        
        # Combined environmental score
        S_env = (GlobalConfig.ENV_WEIGHT_ATM * S_atm + 
                 GlobalConfig.ENV_WEIGHT_ORB * S_orb)
        
        # Calculate environmental taxes
        tax_atm = 0.0
        tax_orb = 0.0
        
        # Only calculate taxes if progressive tax is enabled
        # For Scenario C, also check use_monte_carlo_env
        should_calc_tax = self.context.use_progressive_tax
        if scenario == 'C' and not self.context.use_monte_carlo_env:
            should_calc_tax = False
        
        if should_calc_tax:
            tax_atm = self._calculate_atmospheric_tax(year, S_atm)
            tax_orb = self._calculate_orbital_tax(year, S_orb)
        
        return {
            'S_atm': S_atm,
            'S_orb': S_orb,
            'S_env': S_env,
            'tax_atm': tax_atm,
            'tax_orb': tax_orb,
            'debris_count': self.debris_count
        }
    
    def _calculate_atmospheric_impact(self, rocket_launches):
        """
        Calculate atmospheric impact from black carbon emissions.
        
        Based on Ross & Sheaffer (2014) methodology.
        """
        if rocket_launches == 0:
            return 0.0
        
        # Fuel burned in stratosphere per launch
        fuel_per_launch = (GlobalConfig.ROCKET_FUEL_MASS * 
                          GlobalConfig.STRATOSPHERE_BURN_RATIO)
        
        # Black carbon emission factor
        bc_factor = GlobalConfig.BC_EMISSION_FACTOR.get(
            self.fuel_type, 
            GlobalConfig.BC_EMISSION_FACTOR['RP1']
        )
        
        # Total BC emissions (kg)
        bc_emissions = rocket_launches * fuel_per_launch * bc_factor
        
        # Track cumulative
        self.cumulative_bc_emissions += bc_emissions
        
        # Convert to CO2-equivalent using radiative forcing
        co2_equivalent = bc_emissions * GlobalConfig.BC_RADIATIVE_FORCING
        
        # Normalize to impact score (tons CO2-eq)
        S_atm = co2_equivalent / 1000.0
        
        return S_atm
    
    def _calculate_orbital_impact(self, rocket_launches):
        """
        Calculate orbital debris impact.
        
        Based on NASA ORDEM and Kessler syndrome models.
        """
        if rocket_launches == 0:
            return 0.0
        
        # Debris generation rate
        debris_alpha = GlobalConfig.DEBRIS_ALPHA_DEFAULT
        
        # New debris generated
        new_debris = rocket_launches * debris_alpha
        
        # Kessler effect: exponential growth
        kessler_growth = self.debris_count * GlobalConfig.KESSLER_GROWTH_RATE / 365.0
        
        # Update debris count
        self.debris_count += new_debris + kessler_growth
        
        # Impact score is proportional to debris count increase
        S_orb = new_debris + kessler_growth
        
        return S_orb
    
    def _calculate_atmospheric_tax(self, year, S_atm):
        """
        Calculate atmospheric environmental tax using dynamic tax rate.
        """
        if S_atm == 0:
            return 0.0
        
        # Get dynamic tax rate for this year
        tax_rate = get_dynamic_tax_rate(
            year,
            GlobalConfig.ENV_TAX_ATM_BASE,
            GlobalConfig.ENV_TAX_ATM_GROWTH_RATE
        )
        
        # Apply tax rate multiplier if set
        if hasattr(self.context, 'env_tax_base') and self.context.env_tax_base > 0:
            tax_rate *= self.context.env_tax_base
        
        # Cap at maximum
        tax_rate = min(tax_rate, GlobalConfig.ENV_TAX_ATM_MAX)
        
        return S_atm * tax_rate
    
    def _calculate_orbital_tax(self, year, S_orb):
        """
        Calculate orbital debris environmental tax using dynamic tax rate.
        """
        if S_orb == 0:
            return 0.0
        
        # Get dynamic tax rate for this year
        tax_rate = get_dynamic_tax_rate(
            year,
            GlobalConfig.ENV_TAX_ORB_BASE,
            GlobalConfig.ENV_TAX_ORB_GROWTH_RATE
        )
        
        # Apply tax rate multiplier if set
        if hasattr(self.context, 'env_tax_base') and self.context.env_tax_base > 0:
            tax_rate *= self.context.env_tax_base
        
        # Cap at maximum
        tax_rate = min(tax_rate, GlobalConfig.ENV_TAX_ORB_MAX)
        
        return S_orb * tax_rate
