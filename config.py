# config.py
import math

class GlobalConfig:
    # --- 0.1 基础常量 ---
    GOAL_MASS_TONS = 100_000_000  # 1亿吨
    START_YEAR = 2050
    MATERIAL_BASE_PRICE = 0   # $/ton (采购价)
    
    # --- 0.2 物理常量 ---
    GEO_HEIGHT_KM = 35786
    TETHER_LENGTH_KM = 100000
    
    # --- 1.1 火箭参数 ---
    ROCKET_BASES = 10
    ROCKET_FLIGHTS_PER_DAY = 4
    ROCKET_PAYLOAD_TONS = 150
    ROCKET_WEATHER_RATE_MEAN = 0.85
    ROCKET_WEATHER_RATE_STD = 0.05
    
    # 火箭成本 (学习曲线)
    ROCKET_COST_INIT = 70_000_000 # 2050年单次发射成本
    ROCKET_COST_MIN = 37_500_000  # 极限成本,根据马斯克提出的目标单次火箭成本降到每公斤250-600美元，这里取250
    ROCKET_DECAY_K = 0.05
      # ============================================================
    # 🔴 新增：时间约束分析参数
    # ============================================================
    
    # [NEW] 时间约束列表（年）
    TIME_CONSTRAINTS = [20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    # [NEW] 计算公式中的常数（用于验证）
    # n_daily = 214.89 / T
    ROCKET_DAILY_CONSTANT = 214.89  
    # 推导过程：
    # 100,000,000 / (10基地 × 365天 × 150吨 × 0.85) = 214.89
    # --- 1.2 太空电梯参数 ---
    SE_PORTS = 3
    # [NEW] 补强基础参数
    SE_REINFORCE_YEARS = 20             # 建设周期20年
    
    # [NEW] 爬升器参数
    SE_CLIMB_SPEED_KMH = 300            # 爬升速度 200 km/h
    SE_CLIMB_LENGTH_KM = 100000         # 爬升长度 100,000 km
    SE_PAYLOAD_CAPACITY = 100           # 爬升器有效载荷（吨）
    SE_VEHICLE_MASS = 50                # 爬升器自重（吨）
    
    # [MODIFIED] 最终状态参数（根据202次补强计算）
    # M_final = 6300 × (1.0115)^202 ≈ 63,315 tons
    SE_MASS_FINAL_TONS = 700000.0        # 最终质量（从20000改为63315）
    # 电梯成本
    SE_OP_COST_INIT = 100 # $/kg
    SE_OP_COST_MIN = 10   # $/kg
    SE_DECAY_K = 0.1
    
# [NEW] 缆绳建设成本参数
    # 碳纳米管(CNT)材料价格。假设量产后为 $100,000 / ton (是普通物资的20倍)
    # 这部分钱必须在前20年花掉
    SE_CABLE_MATERIAL_PRICE = 180_000_000 
    # [几何参数 - 固定不变]
    SE_LENGTH_KM = 100000          # 缆绳长度
    SE_RADIUS_M = 0.5             # 半径 0.5m
    SE_DIAMETER_KM = 0.001        # 直径 2m = 0.002 km
    
    # [碰撞面积 - 固定不变]
    # Area = Length * Diameter
    # 逻辑：无论内部怎么补强，外部轮廓永远是这个面积
    SE_COLLISION_AREA_KM2 = 100.0 
    
    # [质量参数 - 增长核心]
    SE_MASS_FINAL_TONS = 700000.0  # 最终：致密结构 (上限由你设定)
    
    # [补强参数 - 增长速率]
    # 使用 Obayashi 的逻辑：通过不断的攀爬补强，质量指数上升
    SE_REINFORCE_TRIPS_TOTAL = 413 # 总补强次数
    SE_REINFORCE_RATE = 0.0115      # 每次增加 1.15%
     # [NEW: CNT 材料价格学习曲线]
    # 2050年初期很贵，随着大规模应用(20万吨需求)，价格会跌到白菜价
    SE_CNT_COST_INIT = 180_000_000   # 初始 $500k / ton
    SE_CNT_COST_MIN = 50_000     # 最终 $5k / ton (接近普通物资)
    SE_CNT_DECAY_K = 0.15       # 衰减速度
     # [NEW] 单次补强作业导致的停运/工期占用时间 (天)
    # 逻辑：运送完材料后，需要时间进行安装。这段时间不能运殖民物资。
    # 注意：每年约25次补强。如果此值设为 14天，则 25*14=350天，导致全年几乎无法运货。
    # 建议设为 3-7 天，代表高效作业或并行作业。
    #SE_REINFORCE_WORK_DAYS = 7.0 
    
    # [运力参数]
    # 缆绳完全成熟(20万吨)后的年运力
    SE_CAP_MAX_K = 2_000_000 
     
    # [NEW] Logistic 曲线参数
    SE_CAP_MAX_K = 2_000_000            # 单港口运力上限 K（吨/年）
    SE_CAP_INIT_2050 = 179_000          # 🔴 修改：初始运力改回179,000（与题目一致）
    SE_CAP_ANCHOR_2062 = 346_200        # 锚点运力（2062年）
    # [成本与寿命]
    SE_OP_COST_INIT = 100
    SE_OP_COST_MIN = 10
    SE_DECAY_K = 0.1
    SE_REPAIR_YEARS = 5   # 断裂后重建时间
      # [COMPUTED] 根据上述参数计算 Logistic 参数 A 和 r
    # A = K / Cap_init - 1
    SE_LOGISTIC_A = SE_CAP_MAX_K / SE_CAP_INIT_2050 - 1  # ≈ 10.17
    
    # r = -1/12 × ln((K/Cap_anchor - 1) / A)
    import math
    SE_LOGISTIC_R = -1/12 * math.log((SE_CAP_MAX_K / SE_CAP_ANCHOR_2062 - 1) / SE_LOGISTIC_A)
    # 计算结果约 r ≈ 0.0833
    
    # [MODIFIED] 补强策略
    SE_GROWTH_RATE = 0.0115             # 质量增长率（保持不变）
    
    # [NEW] 持续补强（建设期后）
    SE_CONTINUOUS_REINFORCE = False      # 是否在202次后继续补强
    SE_ANNUAL_TRIPS_POST_BUILD = 5      # 202次后每年补强次数
    
    # [MODIFIED] 初始质量和厚度（保持不变）
    SE_MASS_INIT_TONS = 6300.0
    SE_THICKNESS_INIT_M = 48e-6
    
    # [COMPUTED] 最终质量（202次补强后）
   # SE_MASS_FINAL_TONS = SE_MASS_INIT_TONS * (1.0115 ** 413)  # ≈ 63,315吨
    # 风险参数 (Q2)
    SE_REPAIR_YEARS = 5   # 大碎片撞击后的重建时间
    SE_BASE_FLUX = 1e-5   # 基础通量
    
      # --- 空间碎片拟合参数 (Based on provided data points) ---
    DEBRIS_BASE_2050 = 21_633       # 拟合得出的2050年基准数量
    DEBRIS_GROWTH_RATE = 258.15     # 拟合得出的年增长率
    
    # --- 风险转化参数 ---
    # 定义：碎片数量相对于2050年每增加1倍，带来的额外影响
    DEBRIS_SE_MAINT_FACTOR = 1.5    # 碎片变多，小撞击维护费的增长倍率
    DEBRIS_ROCKET_FAIL_PENALTY = 0.005 # 碎片翻倍时，火箭故障率增加 0.5%
    # --- 4.0 环境参数 (Q4) ---
    ENV_CO2_PER_LAUNCH = 500 # tons CO2 per launch
    ENV_DEBRIS_PROB_ROCKET = 0.01 # 产生碎片概率
    
     # ============================================================
    # 🔴 新增：泊松过程参数
    # ============================================================
    
    # [电梯维护事件 - 三层泊松过程]
    SE_MAINT_LAMBDA_MINOR = 0.5      # 小故障率（次/年/港口）
    SE_MAINT_LAMBDA_MAJOR = 0.1      # 中故障率（次/年/港口）
    SE_MAINT_LAMBDA_CRITICAL = 0.02  # 大故障率（次/年/港口）
    
    # 小故障参数
    SE_MAINT_MINOR_DOWNTIME = (3, 7)      # 停运天数范围
    SE_MAINT_MINOR_COST = (100_000, 500_000)  # 成本范围（美元）
    
    # 中故障参数
    SE_MAINT_MAJOR_DOWNTIME = (30, 60)
    SE_MAINT_MAJOR_COST = (5_000_000, 20_000_000)
    
    # 大故障参数（不包括完全断裂）
    SE_MAINT_CRITICAL_DOWNTIME = (180, 365)
    SE_MAINT_CRITICAL_COST = (100_000_000, 500_000_000)
    
    # [火箭失败事件 - 泊松过程]
    ROCKET_FAIL_LAMBDA_BASE = 0.01   # 基础失败率（失败次数/发射次数）
    ROCKET_FAIL_CLUSTER_PROB = 0.15  # 聚类失败概率（连续失败）
    
    # 失败类型概率分布
    ROCKET_FAIL_TYPE_PROBS = {
        'abort': 0.60,        # 发射前中止
        'explosion': 0.30,    # 升空后爆炸
        'orbit_deviation': 0.08,  # 轨道偏离
        'pad_destruction': 0.02   # 发射台损毁
    }
    
    # 各类型失败成本
    ROCKET_FAIL_COST_ABORT = (1_000_000, 3_000_000)
    ROCKET_FAIL_COST_EXPLOSION = (60_000_000, 80_000_000)
    ROCKET_FAIL_COST_ORBIT = (8_000_000, 15_000_000)
    
    # 各类型延迟（天）
    ROCKET_FAIL_DELAY_ABORT = (1, 5)
    ROCKET_FAIL_DELAY_EXPLOSION = (20, 40)
    ROCKET_FAIL_DELAY_ORBIT = (5, 10)
    
    # ============================================================
    # 🔴 新增：稀疏事件参数
    # ============================================================
    
    # [发射台爆炸 - 稀疏事件]
    EXPLOSION_PROB_PER_LAUNCH = 0.00015  # 单次发射台爆炸概率
    EXPLOSION_REBUILD_YEARS = (2, 5)     # 重建时间范围（年）
    EXPLOSION_COST_RANGE = (500_000_000, 2_000_000_000)  # 成本范围
    
    # 重要性采样参数
    USE_IMPORTANCE_SAMPLING = True
    IS_AMPLIFICATION_FACTOR = 66         # 放大倍数：0.01 / 0.00015 ≈ 66
    
    # [连锁反应参数]
    EXPLOSION_CASCADE_THRESHOLD = 2      # 多少次爆炸触发监管审查
    EXPLOSION_CASCADE_WINDOW = 5         # 时间窗口（年）
    EXPLOSION_CASCADE_SHUTDOWN_MONTHS = 6  # 全局停运时间（月）
    EXPLOSION_CASCADE_COST = 10_000_000_000  # 监管审查额外成本
    
    # ============================================================
    # 🔴 新增���Scenario C 混合策略参数
    # ============================================================
    
    # [混合运输比例控制]
    SE_ALLOCATION_RATIO_BETA = 0.7  # 默认电梯承担比例（70%）

  # ============================================================
    # 🔴 新增：Q4 双域环境影响参数
    # ============================================================
    
    # --- 4.1 大气域参数（Atmospheric Domain）---
    # 基于 Ross & Sheaffer (2014) 的数据
    ROCKET_FUEL_MASS = 400                      # 单次发射燃料质量（吨）Falcon Heavy
    STRATOSPHERE_BURN_RATIO = 0.67              # 平流层燃烧比例（2/3规则）
    
    # 黑碳排放因子（kg BC / kg Fuel）
    BC_EMISSION_FACTOR = {
        'RP1': 0.02,        # 煤油火箭（Falcon Heavy）
        'LH2': 0.0,         # 液氢火箭（未来技术）
        'Hybrid': 0.04      # 混合动力（高污染）
    }
    
    # 黑碳辐射强迫效应
    BC_RADIATIVE_FORCING = 50000                # 相对CO2的倍数（Ross 2014, Fig 6）
    BC_RESIDENCE_TIME = 4.0                     # 平流层停留时间（年）
    
    # 燃料类型配置（用于技术路线图）
    ROCKET_FUEL_TYPE_DEFAULT = 'RP1'            # 默认燃料
    ROCKET_FUEL_COST_MULT = {                   # 成本系数
        'RP1': 1.0,
        'LH2': 2.0,         # 液氢贵2倍
        'Hybrid': 1.5
    }
    
    # --- 4.2 轨道域参数（Orbital Domain）---
    # 基于 NASA ORDEM 3.2 和 ESA 数据
    
    # 碎片产生率（pieces per launch）
    DEBRIS_ALPHA_PESSIMISTIC = 5.0              # 悲观：无回收
    DEBRIS_ALPHA_OPTIMISTIC = 0.5               # 乐观：全部一级回收
    DEBRIS_ALPHA_DEFAULT = 2.5                  # 中等：部分回收
    
    # 凯斯勒效应增长率
    KESSLER_GROWTH_RATE = 0.04                  # λ = 4%/年（NASA估算）
    
    # 分层轨道通量（ORDEM 3.2, ≥1mm 碎片）
    # 单位：impacts per m² per year
    FLUX_LEO = 1e-5         # Low Earth Orbit (0-2000 km)
    FLUX_MEO = 1e-7         # Medium Earth Orbit (2000-35000 km)
    FLUX_GEO = 1e-10        # Geostationary Orbit (35786 km)
    
    # 电梯缆绳分层参数（用于精确碰撞计算）
    SE_LAYER_CONFIG = [
        {'name': 'LEO',  'alt_range': (0, 2000),        'flux': FLUX_LEO},
        {'name': 'MEO',  'alt_range': (2000, 35786),    'flux': FLUX_MEO},
        {'name': 'GEO+', 'alt_range': (35786, 100000),  'flux': FLUX_GEO}
    ]
    
    # --- 4.3 综合环境评分参数 ---
    ENV_WEIGHT_ATM = 0.6                        # 大气域权重
    ENV_WEIGHT_ORB = 0.4                        # 轨道域权重
    
    # 环境阈值（归一化后的分数）
    ENV_THRESHOLD_WARNING = 0.6                 # 警戒线（黄色）
    ENV_THRESHOLD_CRITICAL = 0.8                # 红线（红色）
    
    # --- 4.4 环境税/碳税参数 ---
    ENV_TAX_INITIAL = 5000                      # 初始环境税（$/point）
    ENV_TAX_GROWTH_RATE = 0.05                  # 年增长率（5%）
    ENV_TAX_MAX = 50000 
    
    
    # --- 4.4 环境税/影子价格参数（Shadow Pricing） ---

    # [大气域税率参数]
    ENV_TAX_ATM_BASE = 150                      # 基础大气税率（$/单位影响，2050年）
                                                # 参考：欧盟碳价 $100-$200/吨CO2
                                                # 注意：I_atm 已包含50,000倍放大系
    ENV_TAX_ATM_GROWTH_RATE = 0.05             # 税率年增长率（5%）
                                                # 逻辑：随着环保意识提高，税率上升

    # [轨道域税率参数]
    ENV_TAX_ORB_BASE = 10_000_000              # 基础轨道税率（$/碎片，2050年）
        # [税率上限（避免数值爆炸）]
    ENV_TAX_ATM_MAX = 1e6                      # 大气税率上限（$1M/单位影响）
    ENV_TAX_ORB_MAX = 1e9                                                                  # 参考：ESA ClearSpace-1 移除成本
                                                # $10M - $50M per debris

    ENV_TAX_ORB_GROWTH_RATE = 0.05             # 税率年增长率（5%）
                                            # 逻辑：轨道越拥挤，清理成本越高                        # 税率上限                       # 税率上限
def get_dynamic_tax_rate(year, base_rate, growth_rate):
    """
    计算动态税率（指数增长）
    
    公式：λ(t) = λ_base × (1 + r)^(t - 2050)
    
    Args:
        year: 当前年份
        base_rate: 基础税率（2050年）
        growth_rate: 年增长率
    
    Returns:
        当年的税率
    
    经济学依据：
    - 反映未来社会对环境的重视程度提高
    - 模拟"环境稀缺性"随时间增加的趋势
    """
    t = year - GlobalConfig.START_YEAR
    return base_rate * ((1 + growth_rate) ** t)


# 轨道税率上限（$1B/碎片）

# 移除旧的环境税参数
# ENV_TAX_INITIAL = 5000  # 删除
# ENV_TAX_GROWTH_RATE = 0.05  # 保留但重定义
# ENV_TAX_MAX = 50000  # 删除

class SimulationContext:
    """
    仿真上下文控制类。
    通过调整这里的布尔值，可以在 Q1, Q2, Q3, Q4 模式间切换。
    """
    def __init__(self):
        self.is_stochastic = False       
        self.use_dynamic_debris = True   
        self.include_water_supply = False 
        self.calc_environmental_impact = False 
        self.env_tax_rate = 0.0          
        self.beta_elevator_ratio = None  
        
          # ✅ 统一环境总开关（唯一入口）
        self.enable_environment = False

        # 环境模块功能开关（仅在 enable_environment=True 时才生效）
        self.calc_environmental_impact = False
        self.use_progressive_tax = False
        self.env_tax_base = 0.0

        # 燃料技术路线图
        self.use_fuel_roadmap = False
        self.current_fuel_type = 'RP1'

        # 环境红线机制
        self.use_env_redline = False
        self.env_redline_threshold = 0.8

        # 碎片参数选择
        self.debris_scenario = 'default'

        # ✅ Scenario C (Monte Carlo) 环境接入开关
        self.use_monte_carlo_env = False