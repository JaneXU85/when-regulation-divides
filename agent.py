import numpy as np
from mesa import Agent


class PensionAgent(Agent):
    def __init__(self, unique_id, model,
                 is_participant, contribution_level, initial_trust,
                 loss_tolerance, weight_strong_tie, weight_weak_tie,
                 weight_authority, weight_public, herding_threshold,
                 reg_sensitivity, age, gender):
        super().__init__(unique_id, model)
        
        # 验证 reg_sensitivity
        if reg_sensitivity not in ["negative", "neutral", "positive"]:
            raise ValueError(f"reg_sensitivity must be 'negative', 'neutral', or 'positive', got {reg_sensitivity}")
        self.reg_sensitivity = reg_sensitivity

        # 初始状态
        self.is_active = is_participant  # True/False
        self.contribution_level = contribution_level  # 0.0–1.0
        self.current_trust = initial_trust  # 0.0–1.0
        self.loss_tolerance = loss_tolerance  # 0.0–1.0
        
        # 社会影响权重（总和不一定为1）
        self.weight_strong_tie = weight_strong_tie
        self.weight_weak_tie = weight_weak_tie
        self.weight_authority = weight_authority
        self.weight_public = weight_public
        
        self.herding_threshold = herding_threshold  # 用于从众决策
        self.age = age
        self.gender = gender

    def step(self):
        """单个时间步行为"""
        if not self.is_active:
            return

        # 获取邻居
        neighbors = list(self.model.G.neighbors(self.unique_id))
        if not neighbors:
            return

        # 计算社会影响（简化版：仅用平均信任）
        neighbor_trusts = [self.model.schedule[uid].current_trust for uid in neighbors]
        avg_neighbor_trust = np.mean(neighbor_trusts)

        # 更新信任（简单线性混合）
        social_influence = (
            self.weight_strong_tie * avg_neighbor_trust +
            self.weight_weak_tie * avg_neighbor_trust +
            self.weight_authority * 0.7 +  # 假设权威信任=0.7
            self.weight_public * 0.65      # 假设公共信任=0.65
        )
        total_weight = (self.weight_strong_tie + self.weight_weak_tie +
                        self.weight_authority + self.weight_public)
        if total_weight > 0:
            social_influence /= total_weight

        # 信任更新（保留部分自身信任）
        self.current_trust = 0.5 * self.current_trust + 0.5 * social_influence
        self.current_trust = np.clip(self.current_trust, 0.0, 1.0)

        # 决策是否继续参与
        if self.current_trust < self.loss_tolerance:
            self.is_active = False