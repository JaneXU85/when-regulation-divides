"""
批量运行 PensionModel 100 次，汇总分组统计结果。
兼容你现有的 model.py 和 agent.py。
修复了 KeyError: 'Step' 问题（通过 reset_index）。
"""
import os
import pandas as pd
from tqdm import tqdm
from model import PensionModel  # 直接导入你的模型

# ==============================
# 配置参数
# ==============================
NUM_REPS = 100
TOTAL_STEPS = 100
SHOCK_STEP = 50
SHOCK_MAGNITUDE = 0.3  # 与你之前的 paperA_stratified_shock_30pct.csv 一致
SEED_BASE = 42

OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================
# 运行多次仿真
# ==============================
all_results = []

for rep in tqdm(range(NUM_REPS), desc="Running replications"):
    seed = SEED_BASE + rep
    
    # 初始化模型（使用你 model.py 中定义的 PensionModel）
    model = PensionModel(
        num_agents=526,
        shock_step=SHOCK_STEP,
        shock_magnitude=SHOCK_MAGNITUDE,
        seed=seed
    )
    
    # 运行 TOTAL_STEPS 步
    for _ in range(TOTAL_STEPS):
        model.step()
    
    # 从 DataCollector 提取数据
    df_run = model.datacollector.get_model_vars_dataframe()
    
    # ✅ 关键修复：Mesa 的 DataFrame 以 Step 为索引，需转为列
    df_run = df_run.reset_index().rename(columns={"index": "Step"})
    
    # 标记 replication ID
    df_run["Replication"] = rep
    all_results.append(df_run)

# ==============================
# 合并所有 replication 数据
# ==============================
df_all = pd.concat(all_results, ignore_index=True)

# 按 Step 分组计算均值和标准差
summary_stats = df_all.groupby("Step").agg(["mean", "std"]).reset_index()

# 扁平化列名: (col, stat) -> col_stat
summary_stats.columns = [
    "_".join(col).strip("_") if col[1] else col[0]
    for col in summary_stats.columns.values
]

# 保存汇总结果
output_path = os.path.join(OUTPUT_DIR, f"paperA_{int(SHOCK_MAGNITUDE*100)}pct_{NUM_REPS}reps_summary.csv")
summary_stats.to_csv(output_path, index=False)
print(f"\n✅ 汇总结果已保存至: {output_path}")

# 可选：保存原始长格式数据（含 Replication 列）
long_path = os.path.join(OUTPUT_DIR, f"paperA_{int(SHOCK_MAGNITUDE*100)}pct_{NUM_REPS}reps_long.csv")
df_all.to_csv(long_path, index=False)
print(f"✅ 原始长格式数据已保存至: {long_path}")