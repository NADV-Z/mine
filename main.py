# main.py
import numpy as np
from config import SimulationContext, GlobalConfig
from core.simulation import Simulator
from analysis.uncertainty import run_monte_carlo
from models.water import WaterModel
from analysis.plotting import analyze_and_plot_details, plot_elevator_cost_breakdown

def format_currency(val):
    return f"${val/1e9:.2f}B"

def solve_q1():
    """Q1: 确定性基准"""
    print("=== Q1: Deterministic Baseline ===")
    ctx = SimulationContext()
    ctx.is_stochastic = False
    sim = Simulator(ctx)
    
    for sc in ['A', 'B', 'C']:
        res = sim.run(sc)
        print(f"Scenario {sc}: Done in {res.final_year}, Cost: {format_currency(res.total_cost)}")
        
        years = res.final_year - GlobalConfig.START_YEAR
        avg_annual_delivery = GlobalConfig.GOAL_MASS_TONS / years
        unit_cost = res.total_cost / GlobalConfig.GOAL_MASS_TONS / 1000
        print(f"  Duration: {years} years")
        print(f"  Avg Annual Delivery: {avg_annual_delivery:,.0f} tons/year")
        print(f"  Unit Cost: ${unit_cost:.2f}/kg\n")

def solve_q2():
    """Q2: 不确定性分析"""
    print("\n=== Q2: Uncertainty & Reliability ===")
    print("🔴 启用所有不确定性因素（统一开关 is_stochastic = True）")
    
    years, costs = run_monte_carlo('C', runs=50)
    
    print(f"\nScenario C (Stochastic):")
    print(f"  Avg Year: {np.mean(years):.1f} (std: {np.std(years):.1f})")
    print(f"  Avg Cost: {format_currency(np.mean(costs))} (std: {format_currency(np.std(costs))})")
    print(f"  Worst Case Year: {max(years)}")

def solve_q3():
    """Q3: 供水分析"""
    print("\n=== Q3: Water Supply Analysis ===")
    ctx = SimulationContext()
    sim = Simulator(ctx)
    res = sim.run('C')
    built_year = res.final_year
    
    wm = WaterModel()
    water_mass, water_cost = wm.calculate_additional_needs(built_year)
    
    print(f"Colony Operational Year: {built_year}")
    print(f"Annual Water Supplement Needed: {water_mass:.2f} tons")
    print(f"Est. Logistics Cost for Water: {format_currency(water_cost)}")

def solve_q4():
    """Q4: 环境影响评估与优化"""
    print("\n" + "=" * 80)
    print("=== Q4: Environmental Impact Assessment & Optimization ===")
    print("=" * 80)
    
    # ============================================================
    # 阶段1：基准运行（无环境约束）
    # ============================================================
    print("\n📊 PHASE 1: Baseline Environmental Assessment")
    print("-" * 80)
    
    ctx_baseline = SimulationContext()
    ctx_baseline.is_stochastic = False
    ctx_baseline.calc_environmental_impact = True
    ctx_baseline.use_progressive_tax = False  # 不使用环境税
    
    sim_baseline = Simulator(ctx_baseline)
    
    baseline_results = {}
    
    for scenario in ['A', 'B', 'C']:
        print(f"\n  Running Scenario {scenario} (baseline)...")
        result = sim_baseline.run(scenario)
        
        env_data = {
            'final_year': result.final_year,
            'total_cost': result.total_cost,
            'duration': result.final_year - GlobalConfig.START_YEAR,
            'history': result.history
        }
        
        if hasattr(sim_baseline, 'env_model') and sim_baseline.env_model:
            env_data['final_debris'] = sim_baseline.env_model.debris_count
            env_data['cumulative_S_env'] = sum(
                h.get('S_env', 0) for h in result.history
            )
        
        baseline_results[scenario] = env_data
        
        print(f"    ✅ Complete: {result.final_year}, "
              f"Cost: ${result.total_cost/1e9:.2f}B, "
              f"Env Score: {env_data.get('cumulative_S_env', 0):.2f}")
    
    # ============================================================
    # 🔴 阶段2：动态环境税优化（新逻辑）
    # ============================================================
    print("\n" + "=" * 80)
    print("📈 PHASE 2: Dynamic Environmental Tax Analysis")
    print("-" * 80)
    print("说明：使用基于影子价格理论的动态税率")
    print(f"  - 大气税率基准：${GlobalConfig.ENV_TAX_ATM_BASE}/单位影响（2050年）")
    print(f"  - 轨道税率基准：${GlobalConfig.ENV_TAX_ORB_BASE/1e6:.1f}M/碎片（2050年）")
    print(f"  - 年增长率：{GlobalConfig.ENV_TAX_ATM_GROWTH_RATE*100:.1f}%")
    print("-" * 80)
    
    # 🔴 新的扫描逻辑：扫描"税率倍数"而非绝对值
    tax_multipliers = [0, 0.5, 1.0, 1.5, 2.0, 3.0]  # 税率倍数
    tax_results = []
    
    for multiplier in tax_multipliers:
        print(f"\n  Testing tax multiplier: {multiplier}x...")
        if multiplier == 0:
            print("    (无环境税，基准情况)")
        else:
            effective_atm = GlobalConfig.ENV_TAX_ATM_BASE * multiplier
            effective_orb = GlobalConfig.ENV_TAX_ORB_BASE * multiplier / 1e6
            print(f"    大气税率：${effective_atm:.0f}/单位影响（2050年）")
            print(f"    轨道税率：${effective_orb:.1f}M/碎片（2050年）")
        
        ctx_tax = SimulationContext()
        ctx_tax.is_stochastic = False
        ctx_tax.calc_environmental_impact = True
        
        if multiplier == 0:
            ctx_tax.use_progressive_tax = False
            ctx_tax.env_tax_base = 0
        else:
            ctx_tax.use_progressive_tax = True  # 🔴 启用动态税率
            ctx_tax.env_tax_base = multiplier   # 税率倍数
        
        sim_tax = Simulator(ctx_tax)
        result = sim_tax.run('C')
        
        # 统计环境税
        total_env_cost = sum(h.get('env_cost', 0) for h in result.history)
        total_tax_atm = sum(h.get('tax_atm', 0) for h in result.history)
        total_tax_orb = sum(h.get('tax_orb', 0) for h in result.history)
        
        tax_results.append({
            'multiplier': multiplier,
            'final_year': result.final_year,
            'total_cost': result.total_cost,
            'duration': result.final_year - GlobalConfig.START_YEAR,
            'cumulative_S_env': sum(h.get('S_env', 0) for h in result.history),
            'total_env_cost': total_env_cost,
            'tax_atm': total_tax_atm,
            'tax_orb': total_tax_orb
        })
        
        print(f"    Result: {result.final_year} ({result.final_year - GlobalConfig.START_YEAR} years), "
              f"${result.total_cost/1e9:.2f}B")
        print(f"    🔍 环境税累计: ${total_env_cost/1e9:.2f}B (占比: {total_env_cost/result.total_cost*100:.2f}%)")
        print(f"       - 大气税: ${total_tax_atm/1e9:.2f}B")
        print(f"       - 轨道税: ${total_tax_orb/1e9:.2f}B")
    
    # ============================================================
    # 阶段3：可视化
    # ============================================================
    print("\n" + "=" * 80)
    print("🎨 PHASE 3: Generating Visualizations")
    print("-" * 80)
    
    from analysis.plotting import (
        plot_environmental_comparison,
        plot_env_tax_tradeoff
    )
    
    plot_environmental_comparison(baseline_results)
    plot_env_tax_tradeoff(tax_results, baseline_results['C'])
    
    # ============================================================
    # 阶段4：生成报告
    # ============================================================
    print("\n" + "=" * 80)
    print("📄 PHASE 4: Environmental Impact Report")
    print("=" * 80)
    
    print("\n🌍 BASELINE SCENARIO COMPARISON:")
    print(f"{'Scenario':<12} {'Duration':<12} {'Cost':<15} {'Env Score':<15}")
    print("-" * 54)
    
    for sc in ['A', 'B', 'C']:
        data = baseline_results[sc]
        print(f"{sc:<12} {data['duration']:<12} "
              f"${data['total_cost']/1e9:<14.2f} "
              f"{data.get('cumulative_S_env', 0):<15.2f}")
    
    print("\n💰 DYNAMIC ENVIRONMENTAL TAX ANALYSIS (Scenario C):")
    print(f"{'Tax Mult.':<12} {'Duration':<12} {'Cost':<15} {'Env Tax':<15} {'Tax %':<10}")
    print("-" * 64)
    
    for tr in tax_results:
        print(f"{tr['multiplier']:<12.1f} {tr['duration']:<12} "
              f"${tr['total_cost']/1e9:<14.2f} "
              f"${tr['total_env_cost']/1e9:<14.2f} "
              f"{tr['total_env_cost']/tr['total_cost']*100:<10.2f}%")
    
    print("\n" + "=" * 80)
    print("✅ Q4 Analysis Complete")
    print("=" * 80)
    
    return baseline_results, tax_results
def solve_visualize():
    """可视化"""
    print("\n=== Visualization: Full Task Timeline ===")
    analyze_and_plot_details()
    plot_elevator_cost_breakdown()

def solve_time_constraint_analysis():
    """时间约束分析"""
    print("\n=== Time Constraint Analysis: Rocket Launch Frequency ===")
    print(f"Target: {GlobalConfig.GOAL_MASS_TONS:,} tons")
    print(f"Scenario: Pure Rocket (Scenario B)\n")
    
    print(f"{'Time':<8} {'Daily':<10} {'Annual':<12} {'Annual':<12} "
          f"{'Capacity':<15} {'Total':<12} {'Cost':<12} {'Unit':<10}")
    print(f"{'(years)':<8} {'Launches':<10} {'(Theory)':<12} {'(Actual)':<12} "
          f"{'(tons/year)':<15} {'(tons)':<12} {'(B$)':<12} {'($/kg)':<10}")
    print("-" * 105)
    
    results = []
    
    for time_limit in GlobalConfig.TIME_CONSTRAINTS:
        n_daily = GlobalConfig.ROCKET_DAILY_CONSTANT / time_limit
        n_annual_theory = (GlobalConfig.ROCKET_BASES * 365 * n_daily * 
                          GlobalConfig.ROCKET_WEATHER_RATE_MEAN)
        
        import math
        n_annual_actual = math.ceil(n_annual_theory)
        annual_capacity = n_annual_actual * GlobalConfig.ROCKET_PAYLOAD_TONS
        total_capacity = annual_capacity * time_limit
        
        ctx = SimulationContext()
        ctx.is_stochastic = False
        sim = Simulator(ctx, rocket_flights_per_day=n_daily)
        
        result = sim.run('B')
        total_cost = result.total_cost
        unit_cost = total_cost / GlobalConfig.GOAL_MASS_TONS / 1000
        completion_year = result.final_year
        actual_duration = completion_year - GlobalConfig.START_YEAR
        
        results.append({
            'time_limit': time_limit,
            'n_daily': n_daily,
            'n_annual_theory': n_annual_theory,
            'n_annual_actual': n_annual_actual,
            'annual_capacity': annual_capacity,
            'total_capacity': total_capacity,
            'total_cost': total_cost,
            'unit_cost': unit_cost,
            'completion_year': completion_year,
            'actual_duration': actual_duration
        })
        
        print(f"{time_limit:<8} {n_daily:<10.3f} {n_annual_theory:<12.2f} "
              f"{n_annual_actual:<12,} {annual_capacity:<15,} "
              f"{total_capacity:<12,} {total_cost/1e9:<12.2f} {unit_cost:<10.2f}")
    
    print("-" * 105)
    print("\n✅ 分析完成")
    
    print("\n正在运行 Scenario A（纯电梯）以获取对比基准...")
    ctx_a = SimulationContext()
    ctx_a.is_stochastic = False
    sim_a = Simulator(ctx_a)
    result_a = sim_a.run('A')
    
    print(f"Scenario A 完成年份: {result_a.final_year}")
    print(f"Scenario A 总成本: ${result_a.total_cost/1e9:.2f}B")
    
    from analysis.plotting import plot_time_cost_tradeoff
    plot_time_cost_tradeoff(results, result_a)
    
    return results

def solve_elevator_physics_analysis():
    """电梯物理分析"""
    print("\n=== Elevator Physics Analysis ===")
    from analysis.plotting import plot_thickness_capacity_relationship
    data = plot_thickness_capacity_relationship()
    
    print("\nKey Data Points:")
    print(f"Initial (0 trips):")
    print(f"  Thickness: {data['thicknesses_um'][0]:.2f} μm")
    print(f"  Capacity: {data['capacities'][0]:,.0f} tons/year")
    print(f"\nMid-point (101 trips):")
    print(f"  Thickness: {data['thicknesses_um'][101]:.2f} μm")
    print(f"  Capacity: {data['capacities'][101]:,.0f} tons/year")
    print(f"\nFinal (202 trips):")
    print(f"  Thickness: {data['thicknesses_um'][202]:.2f} μm")
    print(f"  Capacity: {data['capacities'][202]:,.0f} tons/year")
    
    return data

# ✅ 新函数
def solve_monte_carlo_optimization():
    """
    蒙特卡洛并行优化
    """
    print("\n" + "=" * 80)
    print("MONTE CARLO OPTIMIZATION")
    print("=" * 80)
    
    # ✅ 新导入
    from analysis.monte_carlo_optimization import solve_monte_carlo_parallel
    
    summary_df, optimal, variance_stats = solve_monte_carlo_parallel()
    
    return summary_df, optimal, variance_stats


if __name__ == "__main__":
    # 基础分析
    solve_q1()
    solve_q2()
    solve_q3()
    baseline_env, tax_sensitivity = solve_q4()
    
    # 可视化
    solve_visualize()
    solve_time_constraint_analysis()
    solve_elevator_physics_analysis()
    
    # 🔴 蒙特卡洛优化（1000次迭代）
    #solve_monte_carlo_optimization()

   