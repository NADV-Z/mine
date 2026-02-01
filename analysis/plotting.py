# analysis/plotting.py
"""Visualization and plotting functions for simulation analysis."""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from config import SimulationContext, GlobalConfig
from core.simulation import Simulator


def analyze_and_plot_details():
    """
    Analyze and plot full task timeline for Scenario C.
    Shows year-by-year breakdown of rocket launches, elevator mass, and cumulative progress.
    """
    print("\n📊 Generating full task timeline visualization...")
    
    # Run Scenario C
    ctx = SimulationContext()
    ctx.is_stochastic = False
    sim = Simulator(ctx)
    result = sim.run('C')
    
    # Extract data from history
    years = [h['year'] for h in result.history]
    rocket_launches = [h.get('rocket_launches', 0) for h in result.history]
    elevator_mass = [h.get('elevator_mass', 0) for h in result.history]
    cumulative_mass = [h.get('cumulative_mass', 0) for h in result.history]
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # Plot 1: Rocket launches per year
    axes[0].bar(years, rocket_launches, color='steelblue', alpha=0.7)
    axes[0].set_ylabel('Rocket Launches', fontsize=12)
    axes[0].set_title('Scenario C: Annual Rocket Launches', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Elevator mass delivery per year
    axes[1].bar(years, elevator_mass, color='green', alpha=0.7)
    axes[1].set_ylabel('Elevator Mass (tons)', fontsize=12)
    axes[1].set_title('Scenario C: Annual Elevator Deliveries', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Cumulative mass delivered
    axes[2].plot(years, cumulative_mass, linewidth=3, color='darkred')
    axes[2].axhline(y=GlobalConfig.GOAL_MASS_TONS, color='red', linestyle='--', 
                    linewidth=2, label='Target: 100M tons')
    axes[2].set_xlabel('Year', fontsize=12)
    axes[2].set_ylabel('Cumulative Mass (tons)', fontsize=12)
    axes[2].set_title('Scenario C: Cumulative Mass Delivered', fontsize=14, fontweight='bold')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    filename = 'scenario_comparison_full.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {filename}")
    
    return {
        'years': years,
        'rocket_launches': rocket_launches,
        'elevator_mass': elevator_mass,
        'cumulative_mass': cumulative_mass
    }


def plot_elevator_cost_breakdown():
    """
    Plot elevator cost breakdown by component for 3-port configuration.
    Shows construction costs (CNT materials) vs operational costs.
    """
    print("\n📊 Generating elevator cost breakdown...")
    
    # Run Scenario A (pure elevator)
    ctx = SimulationContext()
    ctx.is_stochastic = False
    sim = Simulator(ctx)
    result = sim.run('A')
    
    # Analyze cost components
    years = []
    construction_costs = []
    operational_costs = []
    
    for h in result.history:
        year = h['year']
        years.append(year)
        
        # Estimate construction vs operational costs
        t = year - GlobalConfig.START_YEAR
        
        if t < GlobalConfig.SE_REINFORCE_YEARS:
            # During construction period
            total_year_cost = h.get('total_cost', 0)
            
            # Rough estimate: construction is ~70% during build phase
            construction_cost = total_year_cost * 0.7
            operational_cost = total_year_cost * 0.3
        else:
            # After construction
            construction_cost = 0
            operational_cost = h.get('total_cost', 0)
        
        construction_costs.append(construction_cost)
        operational_costs.append(operational_cost)
    
    # Create stacked area chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.fill_between(years, 0, np.array(construction_costs)/1e9, 
                     label='Construction (CNT Materials)', alpha=0.7, color='orange')
    ax.fill_between(years, np.array(construction_costs)/1e9, 
                     (np.array(construction_costs) + np.array(operational_costs))/1e9,
                     label='Operational Costs', alpha=0.7, color='steelblue')
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Annual Cost (Billion $)', fontsize=12)
    ax.set_title('Space Elevator Cost Breakdown (3 Ports)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filename = 'elevator_cost_breakdown_3ports.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {filename}")
    
    return {
        'years': years,
        'construction_costs': construction_costs,
        'operational_costs': operational_costs
    }


def plot_environmental_comparison(baseline_results):
    """
    Compare environmental impact across scenarios A, B, and C.
    
    Args:
        baseline_results: dict with environmental data for each scenario
    """
    print("\n📊 Generating environmental comparison chart...")
    
    scenarios = ['A', 'B', 'C']
    durations = []
    costs = []
    env_scores = []
    
    for sc in scenarios:
        data = baseline_results[sc]
        durations.append(data['duration'])
        costs.append(data['total_cost'] / 1e9)
        env_scores.append(data.get('cumulative_S_env', 0))
    
    # Create comparison chart
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Duration comparison
    axes[0].bar(scenarios, durations, color=['green', 'steelblue', 'orange'], alpha=0.7)
    axes[0].set_ylabel('Duration (years)', fontsize=12)
    axes[0].set_title('Project Duration', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Cost comparison
    axes[1].bar(scenarios, costs, color=['green', 'steelblue', 'orange'], alpha=0.7)
    axes[1].set_ylabel('Total Cost (Billion $)', fontsize=12)
    axes[1].set_title('Total Cost', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Environmental score comparison
    axes[2].bar(scenarios, env_scores, color=['green', 'steelblue', 'orange'], alpha=0.7)
    axes[2].set_ylabel('Cumulative Environmental Score', fontsize=12)
    axes[2].set_title('Environmental Impact', fontsize=13, fontweight='bold')
    axes[2].grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Scenario Comparison (A: Elevator, B: Rocket, C: Mixed)', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    filename = 'q4_environmental_comparison.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {filename}")


def plot_env_tax_tradeoff(tax_results, baseline):
    """
    Plot environmental tax tradeoff analysis with dynamic tax curves.
    
    Args:
        tax_results: list of dicts with tax sensitivity results
        baseline: baseline scenario C results
    """
    print("\n📊 Generating environmental tax tradeoff charts...")
    
    # Extract data
    multipliers = [r['multiplier'] for r in tax_results]
    durations = [r['duration'] for r in tax_results]
    total_costs = [r['total_cost'] / 1e9 for r in tax_results]
    env_costs = [r['total_env_cost'] / 1e9 for r in tax_results]
    env_scores = [r['cumulative_S_env'] for r in tax_results]
    
    # Create multi-panel figure
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Plot 1: Duration vs Tax Multiplier
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(multipliers, durations, 'o-', linewidth=2, markersize=8, color='steelblue')
    ax1.set_xlabel('Tax Rate Multiplier', fontsize=12)
    ax1.set_ylabel('Duration (years)', fontsize=12)
    ax1.set_title('Project Duration vs Environmental Tax Rate', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Cost breakdown
    ax2 = fig.add_subplot(gs[0, 1])
    project_costs = [total - env for total, env in zip(total_costs, env_costs)]
    ax2.plot(multipliers, total_costs, 'o-', linewidth=2, markersize=8, 
             label='Total Cost', color='darkred')
    ax2.plot(multipliers, project_costs, 's--', linewidth=2, markersize=6,
             label='Project Cost', color='steelblue')
    ax2.plot(multipliers, env_costs, '^--', linewidth=2, markersize=6,
             label='Environmental Tax', color='green')
    ax2.set_xlabel('Tax Rate Multiplier', fontsize=12)
    ax2.set_ylabel('Cost (Billion $)', fontsize=12)
    ax2.set_title('Cost Breakdown vs Tax Rate', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Environmental score vs cost
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.scatter(env_scores, total_costs, s=150, c=multipliers, cmap='viridis', alpha=0.7)
    for i, mult in enumerate(multipliers):
        ax3.annotate(f'{mult}x', (env_scores[i], total_costs[i]), 
                    fontsize=9, ha='right')
    ax3.set_xlabel('Cumulative Environmental Score', fontsize=12)
    ax3.set_ylabel('Total Cost (Billion $)', fontsize=12)
    ax3.set_title('Environmental Impact vs Cost', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Dynamic tax rate curve
    ax4 = fig.add_subplot(gs[1, 1])
    years_range = range(2050, 2150)
    
    # Calculate dynamic tax rates
    from config import get_dynamic_tax_rate
    
    atm_rates_1x = [get_dynamic_tax_rate(y, GlobalConfig.ENV_TAX_ATM_BASE, 
                                         GlobalConfig.ENV_TAX_ATM_GROWTH_RATE) 
                   for y in years_range]
    atm_rates_2x = [r * 2 for r in atm_rates_1x]
    atm_rates_3x = [r * 3 for r in atm_rates_1x]
    
    ax4.plot(years_range, atm_rates_1x, linewidth=2, label='1x (Base Rate)', color='blue')
    ax4.plot(years_range, atm_rates_2x, linewidth=2, label='2x Multiplier', 
             color='orange', linestyle='--')
    ax4.plot(years_range, atm_rates_3x, linewidth=2, label='3x Multiplier', 
             color='red', linestyle=':')
    ax4.set_xlabel('Year', fontsize=12)
    ax4.set_ylabel('Tax Rate ($/unit impact)', fontsize=12)
    ax4.set_title('Dynamic Environmental Tax Rate Growth', fontsize=13, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('Q4: Environmental Tax Tradeoff Analysis (Scenario C)', 
                 fontsize=15, fontweight='bold', y=0.995)
    
    filename = 'q4_tax_tradeoff.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {filename}")


def plot_time_cost_tradeoff(results, result_a):
    """
    Plot time vs cost tradeoff for different time constraints.
    
    Args:
        results: list of result dicts from time constraint analysis
        result_a: Scenario A baseline result
    """
    print("\n📊 Generating time-cost tradeoff chart...")
    
    # Extract data
    time_limits = [r['time_limit'] for r in results]
    costs = [r['total_cost'] / 1e9 for r in results]
    actual_durations = [r['actual_duration'] for r in results]
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Cost vs Time Limit
    ax1.plot(time_limits, costs, 'o-', linewidth=2, markersize=8, color='steelblue',
             label='Scenario B (Rockets)')
    ax1.axhline(y=result_a.total_cost/1e9, color='green', linestyle='--', 
                linewidth=2, label=f'Scenario A (Elevator): ${result_a.total_cost/1e9:.2f}B')
    ax1.set_xlabel('Time Constraint (years)', fontsize=12)
    ax1.set_ylabel('Total Cost (Billion $)', fontsize=12)
    ax1.set_title('Cost vs Time Constraint', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Launch frequency
    launch_frequencies = [r['n_daily'] for r in results]
    ax2.plot(time_limits, launch_frequencies, 's-', linewidth=2, markersize=8, 
             color='darkred')
    ax2.set_xlabel('Time Constraint (years)', fontsize=12)
    ax2.set_ylabel('Daily Launches per Base', fontsize=12)
    ax2.set_title('Required Daily Launch Frequency', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filename = 'time_cost_tradeoff.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {filename}")


def plot_thickness_capacity_relationship():
    """
    Plot relationship between cable thickness and elevator capacity over time.
    Shows how reinforcement trips affect structural properties.
    """
    print("\n📊 Generating thickness-capacity relationship chart...")
    
    # Calculate thickness and capacity over reinforcement trips
    trips = np.arange(0, GlobalConfig.SE_REINFORCE_TRIPS_TOTAL + 1)
    
    # Mass growth
    masses = GlobalConfig.SE_MASS_INIT_TONS * (1 + GlobalConfig.SE_GROWTH_RATE) ** trips
    
    # Thickness estimation (assuming proportional to mass for fixed volume)
    # thickness ∝ mass^(1/2) for a cylindrical structure
    thicknesses = GlobalConfig.SE_THICKNESS_INIT_M * np.sqrt(masses / GlobalConfig.SE_MASS_INIT_TONS)
    thicknesses_um = thicknesses * 1e6  # Convert to micrometers
    
    # Capacity using logistic curve
    years = trips / (GlobalConfig.SE_REINFORCE_TRIPS_TOTAL / GlobalConfig.SE_REINFORCE_YEARS)
    capacities = []
    
    for t in years:
        K = GlobalConfig.SE_CAP_MAX_K
        A = GlobalConfig.SE_LOGISTIC_A
        r = GlobalConfig.SE_LOGISTIC_R
        capacity = K / (1 + A * np.exp(-r * t))
        capacities.append(capacity)
    
    capacities = np.array(capacities)
    
    # Create dual-axis plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    color1 = 'steelblue'
    ax1.set_xlabel('Reinforcement Trips Completed', fontsize=12)
    ax1.set_ylabel('Cable Thickness (μm)', fontsize=12, color=color1)
    ax1.plot(trips, thicknesses_um, linewidth=2.5, color=color1, label='Thickness')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3)
    
    ax2 = ax1.twinx()
    color2 = 'darkred'
    ax2.set_ylabel('Annual Capacity (tons/year/port)', fontsize=12, color=color2)
    ax2.plot(trips, capacities, linewidth=2.5, color=color2, linestyle='--', 
             label='Capacity')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Add vertical line at completion of reinforcement
    ax1.axvline(x=GlobalConfig.SE_REINFORCE_TRIPS_TOTAL, color='gray', 
                linestyle=':', linewidth=2, alpha=0.7)
    ax1.text(GlobalConfig.SE_REINFORCE_TRIPS_TOTAL, thicknesses_um.max() * 0.5, 
             'Build Complete\n(20 years)', ha='right', va='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.title('Cable Thickness & Capacity Growth During Reinforcement', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Add legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    filename = 'thickness_capacity_relationship.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {filename}")
    
    return {
        'trips': trips,
        'thicknesses_um': thicknesses_um,
        'capacities': capacities
    }
