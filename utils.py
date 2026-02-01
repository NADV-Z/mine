# utils.py
from config import GlobalConfig

def get_debris_factor(year, context):
    """
    计算当年的碎片风险倍数 (Risk Factor)。
    相对于 2050 年基准 (Factor = 1.0)。
    
    ✅ 保持不变
    """
    if not context.use_dynamic_debris:
        return 1.0
        
    if year < 2050:
        return 1.0
        
    # 线性拟合公式: N(t) = N_base + k * (t - 2050)
    delta_t = year - 2050
    current_count = GlobalConfig.DEBRIS_BASE_2050 + (GlobalConfig.DEBRIS_GROWTH_RATE * delta_t)
    
    # 风险因子 = 当前数量 / 2050基准数量
    factor = current_count / GlobalConfig.DEBRIS_BASE_2050
    return factor


# ============================================================
# 🔴 可选新增：辅助函数（提升代码可读性）
# 如果不需要可以不添加
# ============================================================

def calculate_reinforcement_progress(year, start_year=2050, total_trips=202, total_years=20):
    """
    🔴 可选新增：计算某年应该完成的累计补强次数
    
    Args:
        year: 当前年份
        start_year: 开始年份
        total_trips: 总补强次数
        total_years: 建设周期
    
    Returns:
        该年应完成的累计次数
    """
    year_index = year - start_year + 1
    target_cumulative = int(year_index * total_trips / total_years)
    return min(target_cumulative, total_trips)


def calculate_climb_time_days(length_km=100000, speed_kmh=200):
    """
    🔴 可选新增：计算单趟爬升时间（天）
    
    Args:
        length_km: 爬升长度（km）
        speed_kmh: 爬升速度（km/h）
    
    Returns:
        单趟时间（天，向上取整）
    """
    import math
    hours = length_km / speed_kmh
    days = hours / 24
    return math.ceil(days)  # 21天