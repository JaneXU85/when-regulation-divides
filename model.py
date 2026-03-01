import numpy as np
import pandas as pd
import networkx as nx
from mesa import Model
from mesa.datacollection import DataCollector
from agent import PensionAgent


class PensionModel(Model):
    def __init__(self, num_agents=526, shock_step=50, shock_magnitude=0.3, seed=None, **kwargs):
        super().__init__()
        self.num_agents = num_agents
        self.shock_step = shock_step
        self.shock_magnitude = shock_magnitude
        self.current_step = 0

        if seed is not None:
            np.random.seed(seed)
            self._seed = seed

        # ==============================
        # 生成符合调查分布的代理数据
        # ==============================
        agent_data = self._generate_agent_data()

        # ==============================
        # 构建网络
        # ==============================
        network_type = kwargs.get("network_type", "small_world")
        if network_type == "small_world":
            k = kwargs.get("ws_k", 4)
            p = kwargs.get("ws_p", 0.1)
            graph = nx.watts_strogatz_graph(n=self.num_agents, k=k, p=p, seed=seed)
        elif network_type == "random":
            p_edge = 4.0 / (self.num_agents - 1) if self.num_agents > 1 else 0
            graph = nx.erdos_renyi_graph(n=self.num_agents, p=p_edge, seed=seed)
        elif network_type == "scale_free":
            m = kwargs.get("ba_m", 2)
            if self.num_agents <= m:
                raise ValueError("num_agents must be > ba_m for scale-free network")
            graph = nx.barabasi_albert_graph(n=self.num_agents, m=m, seed=seed)
        else:
            raise ValueError(f"Unsupported network type: {network_type}")
        self.G = graph

        # ==============================
        # 创建代理
        # ==============================
        self.schedule = []
        for i in range(self.num_agents):
            data = agent_data.iloc[i]
            agent = PensionAgent(
                unique_id=i,
                model=self,
                is_participant=True,
                contribution_level=1.0,
                initial_trust=data["initial_trust"],
                loss_tolerance=0.5,
                weight_strong_tie=0.3,
                weight_weak_tie=0.1,
                weight_authority=0.4,
                weight_public=0.2,
                herding_threshold=0.6,
                reg_sensitivity=data["reg_sensitivity"],
                age=40,          # 占位符
                gender="M"       # 占位符
            )
            self.schedule.append(agent)

        # ==============================
        # 数据收集器
        # ==============================
        self.datacollector = DataCollector(
            model_reporters={
                "Active_Participants": lambda m: sum(1 for a in m.schedule if a.is_active),
                "Active_Negative": lambda m: sum(1 for a in m.schedule if a.is_active and a.reg_sensitivity == "negative"),
                "Active_Positive": lambda m: sum(1 for a in m.schedule if a.is_active and a.reg_sensitivity == "positive"),
                "Count_Negative": lambda m: sum(1 for a in m.schedule if a.reg_sensitivity == "negative"),
                "Count_Positive": lambda m: sum(1 for a in m.schedule if a.reg_sensitivity == "positive"),
                "Avg_Trust": lambda m: np.mean([a.current_trust for a in m.schedule]),
                "Trust_Negative": lambda m: np.mean([a.current_trust for a in m.schedule if a.reg_sensitivity == "negative"]) if any(a.reg_sensitivity == "negative" for a in m.schedule) else 0,
                "Trust_Positive": lambda m: np.mean([a.current_trust for a in m.schedule if a.reg_sensitivity == "positive"]) if any(a.reg_sensitivity == "positive" for a in m.schedule) else 0,
            }
        )
        self.datacollector.collect(self)

    def _generate_agent_data(self):
        """生成526名代理的初始敏感性与信任"""
        n_neg, n_neu, n_pos = 218, 32, 276
        sensitivities = ["negative"] * n_neg + ["neutral"] * n_neu + ["positive"] * n_pos

        # 设置各组初始信任均值（来自您的数据）
        trust_vals = []
        rng = np.random.default_rng(seed=getattr(self, '_seed', None))
        for s in sensitivities:
            if s == "negative":
                t = rng.normal(0.585, 0.15)
            elif s == "neutral":
                t = rng.normal(0.70, 0.10)
            else:  # positive
                t = rng.normal(0.82, 0.12)
            trust_vals.append(np.clip(t, 0.0, 1.0))

        df = pd.DataFrame({
            "reg_sensitivity": sensitivities,
            "initial_trust": trust_vals
        })
        # 随机打乱顺序
        df = df.sample(frac=1, random_state=getattr(self, '_seed', None)).reset_index(drop=True)
        return df

    def step(self):
        self.current_step += 1
        # 随机激活顺序
        agents_order = np.random.permutation(self.schedule)
        for agent in agents_order:
            agent.step()

        # 应用一次性监管冲击
        if self.current_step == self.shock_step:
            for agent in self.schedule:
                if agent.reg_sensitivity == "negative":
                    agent.current_trust = max(0.0, agent.current_trust - self.shock_magnitude)
                elif agent.reg_sensitivity == "positive":
                    agent.current_trust = min(1.0, agent.current_trust + self.shock_magnitude * 0.75)

        self.datacollector.collect(self)