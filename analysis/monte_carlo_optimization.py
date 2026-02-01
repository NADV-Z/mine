# analysis/monte_carlo_optimization.py
"""Monte Carlo optimization for Scenario C beta parameter."""

import numpy as np
import pandas as pd
import time
from config import SimulationContext, GlobalConfig
from core.simulation import Simulator


def solve_monte_carlo_parallel():
    """
    Run Monte Carlo optimization for different beta values (elevator ratio in Scenario C).
    
    Tests beta values: [0.5, 0.6, 0.7, 0.8, 0.9]
    For each beta, runs Monte Carlo with environmental tax enabled
    
    Returns:
        summary_df: DataFrame with results for each beta
        optimal: dict with best beta configuration
        variance_stats: dict with variance statistics
    """
    # Configuration
    MONTE_CARLO_RUNS = 100  # Number of runs per beta value
    
    print("\n" + "=" * 80)
    print("MONTE CARLO BETA OPTIMIZATION")
    print("=" * 80)
    print(f"Runs per beta: {MONTE_CARLO_RUNS}")
    print(f"Environmental tax: ENABLED")
    print("-" * 80)
    
    beta_values = [0.5, 0.6, 0.7, 0.8, 0.9]
    results = []
    
    for beta in beta_values:
        print(f"\n🔄 Testing β = {beta:.1f}...")
        
        years = []
        costs = []
        env_taxes = []
        durations = []
        
        for run in range(MONTE_CARLO_RUNS):
            # Create context with environmental tax enabled
            ctx = SimulationContext()
            ctx.is_stochastic = True
            ctx.enable_environment = True
            ctx.calc_environmental_impact = True
            ctx.use_progressive_tax = True
            ctx.use_monte_carlo_env = True
            ctx.env_tax_base = 1.0  # Use base tax rate
            ctx.beta_elevator_ratio = beta
            
            # Run simulation
            sim = Simulator(ctx)
            result = sim.run('C')
            
            # Collect results
            years.append(result.final_year)
            costs.append(result.total_cost)
            durations.append(result.final_year - GlobalConfig.START_YEAR)
            
            # Calculate total environmental tax
            total_env_tax = sum(
                h.get('tax_atm', 0) + h.get('tax_orb', 0) 
                for h in result.history
            )
            env_taxes.append(total_env_tax)
        
        # Calculate statistics
        years_arr = np.array(years)
        costs_arr = np.array(costs)
        env_taxes_arr = np.array(env_taxes)
        durations_arr = np.array(durations)
        
        mean_year = np.mean(years_arr)
        std_year = np.std(years_arr)
        mean_cost = np.mean(costs_arr)
        std_cost = np.std(costs_arr)
        mean_env_tax = np.mean(env_taxes_arr)
        mean_duration = np.mean(durations_arr)
        
        # Calculate cost including environmental tax
        mean_total_cost = mean_cost  # Already includes env tax
        
        results.append({
            'beta': beta,
            'mean_year': mean_year,
            'std_year': std_year,
            'mean_duration': mean_duration,
            'mean_cost': mean_cost,
            'std_cost': std_cost,
            'mean_env_tax': mean_env_tax,
            'env_tax_pct': (mean_env_tax / mean_cost) * 100 if mean_cost > 0 else 0,
            'cv_year': std_year / mean_year if mean_year > 0 else 0,
            'cv_cost': std_cost / mean_cost if mean_cost > 0 else 0
        })
        
        print(f"  ✅ Complete:")
        print(f"     Mean completion: {mean_year:.1f} ({mean_duration:.1f} years)")
        print(f"     Mean cost: ${mean_cost/1e9:.2f}B (std: ${std_cost/1e9:.2f}B)")
        print(f"     Mean env tax: ${mean_env_tax/1e9:.2f}B ({(mean_env_tax/mean_cost)*100:.2f}%)")
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(results)
    
    # Find optimal beta (minimize mean cost including env tax)
    optimal_idx = summary_df['mean_cost'].idxmin()
    optimal_beta = summary_df.loc[optimal_idx]
    
    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS")
    print("=" * 80)
    print(f"\n📊 SUMMARY TABLE:")
    print(f"{'Beta':<8} {'Duration':<12} {'Cost (B$)':<15} {'Env Tax (B$)':<15} {'Tax %':<10}")
    print("-" * 70)
    
    for _, row in summary_df.iterrows():
        print(f"{row['beta']:<8.1f} {row['mean_duration']:<12.1f} "
              f"${row['mean_cost']/1e9:<14.2f} "
              f"${row['mean_env_tax']/1e9:<14.2f} "
              f"{row['env_tax_pct']:<10.2f}%")
    
    print("\n🎯 OPTIMAL CONFIGURATION:")
    print(f"  Beta: {optimal_beta['beta']:.1f}")
    print(f"  Duration: {optimal_beta['mean_duration']:.1f} years")
    print(f"  Cost: ${optimal_beta['mean_cost']/1e9:.2f}B")
    print(f"  Env Tax: ${optimal_beta['mean_env_tax']/1e9:.2f}B ({optimal_beta['env_tax_pct']:.2f}%)")
    
    # Variance statistics
    variance_stats = {
        'min_cv_year': summary_df['cv_year'].min(),
        'max_cv_year': summary_df['cv_year'].max(),
        'min_cv_cost': summary_df['cv_cost'].min(),
        'max_cv_cost': summary_df['cv_cost'].max(),
        'mean_env_tax_pct': summary_df['env_tax_pct'].mean()
    }
    
    # Save results to CSV with timestamp
    timestamp = int(time.time())
    summary_filename = f'monte_carlo_results_{timestamp}.csv'
    summary_df.to_csv(summary_filename, index=False)
    print(f"\n💾 Results saved to: {summary_filename}")
    
    # Generate detailed history for optimal beta only (to save computation time)
    print(f"\n📝 Generating detailed history for optimal beta = {optimal_beta['beta']:.1f}...")
    detailed_filename = f'monte_carlo_detailed_{timestamp}.csv'
    detailed_data = []
    
    # Run deterministic simulation for optimal beta only
    ctx = SimulationContext()
    ctx.is_stochastic = False
    ctx.enable_environment = True
    ctx.calc_environmental_impact = True
    ctx.use_progressive_tax = True
    ctx.use_monte_carlo_env = True
    ctx.env_tax_base = 1.0
    ctx.beta_elevator_ratio = optimal_beta['beta']
    
    sim = Simulator(ctx)
    result = sim.run('C')
    
    for h in result.history:
        detailed_data.append({
            'beta': optimal_beta['beta'],
            'year': h['year'],
            'rocket_launches': h.get('rocket_launches', 0),
            'elevator_mass': h.get('elevator_mass', 0),
            'cumulative_mass': h.get('cumulative_mass', 0),
            'total_cost': h.get('total_cost', 0),
            'S_env': h.get('S_env', 0),
            'tax_atm': h.get('tax_atm', 0),
            'tax_orb': h.get('tax_orb', 0),
            'env_cost': h.get('tax_atm', 0) + h.get('tax_orb', 0)
        })
    
    detailed_df = pd.DataFrame(detailed_data)
    detailed_df.to_csv(detailed_filename, index=False)
    print(f"💾 Detailed history saved to: {detailed_filename}")
    
    # Create visualization
    _plot_beta_optimization(summary_df, timestamp)
    
    return summary_df, optimal_beta.to_dict(), variance_stats


def _plot_beta_optimization(summary_df, timestamp):
    """Create visualization of beta optimization results."""
    import matplotlib.pyplot as plt
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Duration vs Beta
    ax1.plot(summary_df['beta'], summary_df['mean_duration'], 'o-', linewidth=2, markersize=8)
    ax1.fill_between(
        summary_df['beta'],
        summary_df['mean_duration'] - summary_df['std_year'],
        summary_df['mean_duration'] + summary_df['std_year'],
        alpha=0.3
    )
    ax1.set_xlabel('Beta (Elevator Ratio)', fontsize=12)
    ax1.set_ylabel('Duration (years)', fontsize=12)
    ax1.set_title('Project Duration vs Beta', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Cost vs Beta
    ax2.plot(summary_df['beta'], summary_df['mean_cost']/1e9, 'o-', 
             linewidth=2, markersize=8, label='Total Cost')
    ax2.plot(summary_df['beta'], summary_df['mean_env_tax']/1e9, 's--', 
             linewidth=2, markersize=6, label='Env Tax', alpha=0.7)
    ax2.fill_between(
        summary_df['beta'],
        (summary_df['mean_cost'] - summary_df['std_cost'])/1e9,
        (summary_df['mean_cost'] + summary_df['std_cost'])/1e9,
        alpha=0.2
    )
    ax2.set_xlabel('Beta (Elevator Ratio)', fontsize=12)
    ax2.set_ylabel('Cost (Billion $)', fontsize=12)
    ax2.set_title('Total Cost vs Beta (with Environmental Tax)', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filename = f'beta_optimization_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Visualization saved to: {filename}")
