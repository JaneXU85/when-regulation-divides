"""
运行多网络稳健性实验，生成 Table 1 所需数据
输出：table1_robustness.csv
"""
import os
import pandas as pd
from model import PensionModel


def run_single_experiment(network_config, num_steps=100, seed=42):
    """运行单次实验并返回最后一步的参与率"""
    print(f"  Running with seed={seed}...")
    model = PensionModel(
        num_agents=526,
        shock_step=50,
        shock_magnitude=0.3,
        seed=seed,
        **network_config["params"]
    )
    
    for _ in range(num_steps):
        model.step()
    
    # 获取最后一步数据
    df = model.datacollector.get_model_vars_dataframe()
    last_row = df.iloc[-1]
    
    total = 526
    neg_count = last_row["Count_Negative"]
    pos_count = last_row["Count_Positive"]
    
    return {
        "Network Type": network_config["label"],
        "Aggregate Participation (%)": round(last_row["Active_Participants"] / total * 100, 1),
        "Negative Group (%)": round(last_row["Active_Negative"] / neg_count * 100, 1) if neg_count > 0 else 0,
        "Positive Group (%)": round(last_row["Active_Positive"] / pos_count * 100, 1) if pos_count > 0 else 0,
    }


def main():
    # 定义网络配置（平均度 ≈ 4）
    network_configs = [
        {
            "label": "Small-world (p=0.1)",
            "params": {"network_type": "small_world", "ws_k": 4, "ws_p": 0.1}
        },
        {
            "label": "Random",
            "params": {"network_type": "random"}
        },
        {
            "label": "Scale-free (m=2)",
            "params": {"network_type": "scale_free", "ba_m": 2}
        }
    ]
    
    results = []
    os.makedirs("results", exist_ok=True)
    
    for config in network_configs:
        print(f"\nRunning {config['label']}...")
        # 可选：多次运行取平均（此处单次演示；如需平均，可循环多个 seed）
        result = run_single_experiment(config, num_steps=100, seed=42)
        results.append(result)
    
    # 保存为 CSV
    df_results = pd.DataFrame(results)
    output_path = "results/table1_robustness.csv"
    df_results.to_csv(output_path, index=False)
    print(f"\n✅ Table 1 data saved to: {output_path}")
    print(df_results.to_string(index=False))


if __name__ == "__main__":
    main()