# analysis/uncertainty.py
"""Monte Carlo uncertainty analysis module."""

import numpy as np
from config import SimulationContext
from core.simulation import Simulator


def run_monte_carlo(scenario, runs=50, enable_env=False):
    """
    Run Monte Carlo simulation with stochastic variations.
    
    Args:
        scenario: Scenario type ('A', 'B', or 'C')
        runs: Number of Monte Carlo runs
        enable_env: Whether to enable environmental tax calculations
    
    Returns:
        years: Array of completion years for each run
        costs: Array of total costs for each run
    """
    years = []
    costs = []
    
    for run in range(runs):
        # Create stochastic context
        ctx = SimulationContext()
        ctx.is_stochastic = True
        
        # Enable environmental calculations if requested
        if enable_env:
            ctx.enable_environment = True
            ctx.calc_environmental_impact = True
            ctx.use_progressive_tax = True
            ctx.env_tax_base = 1.0  # Use base tax rate
            
            # For Scenario C, enable Monte Carlo environment mode
            if scenario == 'C':
                ctx.use_monte_carlo_env = True
        
        # Run simulation
        sim = Simulator(ctx)
        result = sim.run(scenario)
        
        years.append(result.final_year)
        costs.append(result.total_cost)
    
    return np.array(years), np.array(costs)
