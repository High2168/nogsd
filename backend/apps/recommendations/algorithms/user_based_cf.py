"""
基于用户的协同过滤算法 (User-based Collaborative Filtering)

核心思想:
    找到与目标用户兴趣相似的其他用户，推荐这些相似用户喜欢但目标用户未接触过的职位

算法步骤:
    1. 构建用户-职位评分矩阵
    2. 计算用户之间的相似度
    3. 找到目标用户的K个最近邻
    4. 聚合最近邻用户喜欢的职位，生成推荐
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, lil_matrix
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import logging

logger = logging.getLogger(__name__)


class UserBasedCF:
    """
    基于用户的协同过滤推荐算法

    使用余弦相似度计算用户之间的相似性

    参数:
        k: 最近邻用户数量，默认20
        min_similarity: 最小相似度阈值，默认0.1
    """

    def __init__(self, k: int = 20, min_similarity: float = 0.1):
        """
        初始化算法

        Args:
            k: 最近邻用户数量
            min_similarity: 用户之间的最小相似度阈值
        """
        self.k = k
        self.min_similarity = min_similarity

        # 用户-职位评分矩阵（稀疏矩阵）
        self.user_item_matrix = None

        # 用户相似度矩阵
        self.user_similarity = None

        # 用户和职位的映射字典
        self.user_mapping = {}   # {user_id: matrix_index}
        self.item_mapping = {}   # {job_id: matrix_index}
        self.reverse_user_mapping = {}  # {matrix_index: user_id}
        self.reverse_item_mapping = {}  # {matrix_index: job_id}

        # 交互数据
        self.interactions = None

    def fit(self, interactions: List[Dict]) -> 'UserBasedCF':
        """
        训练模型，构建用户-职位矩阵并计算用户相似度

        Args:
            interactions: 交互记录列表，每个元素包含:
                - user_id: 用户ID
                - job_id: 职位ID
                - rating: 评分或交互价值

        Returns:
            self，支持链式调用
        """
        logger.info(f"开始训练User-based CF模型，交互记录数: {len(interactions)}")

        # 存储交互数据
        self.interactions = interactions

        # 获取所有用户和职位
        unique_users = sorted(set(i['user_id'] for i in interactions))
        unique_items = sorted(set(i['job_id'] for i in interactions))

        # 创建映射
        self.user_mapping = {uid: idx for idx, uid in enumerate(unique_users)}
        self.item_mapping = {iid: idx for idx, iid in enumerate(unique_items)}
        self.reverse_user_mapping = {idx: uid for uid, idx in self.user_mapping.items()}
        self.reverse_item_mapping = {idx: iid for iid, idx in self.item_mapping.items()}

        n_users = len(unique_users)
        n_items = len(unique_items)

        logger.info(f"用户数: {n_users}, 职位数: {n_items}")

        # 构建用户-职位评分矩阵
        # 使用稀疏矩阵节省内存
        matrix = lil_matrix((n_users, n_items))

        for interaction in interactions:
            user_idx = self.user_mapping.get(interaction['user_id'])
            item_idx = self.item_mapping.get(interaction['job_id'])
            rating = interaction.get('rating', 1.0)

            if user_idx is not None and item_idx is not None:
                matrix[user_idx, item_idx] = rating

        # 转换为CSR格式（更适合矩阵运算）
        self.user_item_matrix = matrix.tocsr()

        # 计算用户相似度矩阵（使用余弦相似度）
        logger.info("计算用户相似度矩阵...")
        self.user_similarity = cosine_similarity(self.user_item_matrix)

        # 将对角线设为0（用户与自己的相似度不考虑）
        np.fill_diagonal(self.user_similarity, 0)

        logger.info("模型训练完成")
        return self

    def _get_k_nearest_neighbors(self, user_idx: int) -> List[Tuple[int, float]]:
        """
        获取用户的K个最近邻

        Args:
            user_idx: 用户在矩阵中的索引

        Returns:
            最近邻列表，每个元素为(邻居索引, 相似度)
        """
        # 获取该用户与其他所有用户的相似度
        similarities = self.user_similarity[user_idx]

        # 找到相似度大于阈值的用户
        valid_neighbors = [
            (idx, sim) for idx, sim in enumerate(similarities)
            if sim >= self.min_similarity and idx != user_idx
        ]

        # 按相似度降序排序，取前K个
        valid_neighbors.sort(key=lambda x: x[1], reverse=True)

        return valid_neighbors[:self.k]

    def recommend(self, user_id: int, n: int = 10, exclude_items: Set[int] = None) -> List[Dict]:
        """
        为指定用户生成推荐

        Args:
            user_id: 用户ID
            n: 推荐数量，默认10
            exclude_items: 需要排除的职位ID集合（如用户已交互的职位）

        Returns:
            推荐列表，每个元素包含:
                - job_id: 职位ID
                - score: 推荐分数
                - reason: 推荐理由
        """
        # 检查用户是否存在
        if user_id not in self.user_mapping:
            logger.warning(f"用户 {user_id} 不在训练数据中，可能是冷启动用户")
            return []

        user_idx = self.user_mapping[user_id]

        # 获取用户已交互的职位
        user_items = set()
        if exclude_items:
            user_items = exclude_items

        # 也排除训练数据中用户已交互的职位
        user_row = self.user_item_matrix[user_idx].toarray().flatten()
        for item_idx, rating in enumerate(user_row):
            if rating > 0:
                user_items.add(self.reverse_item_mapping[item_idx])

        # 获取最近邻用户
        neighbors = self._get_k_nearest_neighbors(user_idx)

        if not neighbors:
            logger.warning(f"用户 {user_id} 没有找到相似用户")
            return []

        # 聚合邻居用户的偏好
        item_scores = defaultdict(float)
        neighbor_contributions = defaultdict(list)

        for neighbor_idx, similarity in neighbors:
            neighbor_row = self.user_item_matrix[neighbor_idx].toarray().flatten()

            for item_idx, rating in enumerate(neighbor_row):
                if rating > 0:
                    item_id = self.reverse_item_mapping[item_idx]

                    # 排除用户已交互的职位
                    if item_id in user_items:
                        continue

                    # 加权评分 = 相似度 * 评分
                    weighted_score = similarity * rating
                    item_scores[item_id] += weighted_score

                    # 记录贡献来源（用于推荐理由）
                    neighbor_id = self.reverse_user_mapping[neighbor_idx]
                    neighbor_contributions[item_id].append({
                        'user_id': neighbor_id,
                        'similarity': similarity,
                        'rating': rating
                    })

        # 按分数排序
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)

        # 生成推荐结果
        recommendations = []
        for job_id, score in sorted_items[:n]:
            # 归一化分数（0-1之间）
            max_score = sorted_items[0][1] if sorted_items else 1
            normalized_score = score / max_score if max_score > 0 else 0

            # 生成推荐理由
            top_contributors = neighbor_contributions[job_id][:3]
            reason = f"与您兴趣相似的用户也关注了此职位（相似用户数: {len(neighbor_contributions[job_id])}）"

            recommendations.append({
                'job_id': job_id,
                'score': round(normalized_score, 4),
                'reason': reason,
                'contributors': top_contributors,
                'algorithm': 'user_cf'
            })

        return recommendations

    def get_similar_users(self, user_id: int, n: int = 5) -> List[Dict]:
        """
        获取与指定用户最相似的用户

        Args:
            user_id: 用户ID
            n: 返回数量

        Returns:
            相似用户列表
        """
        if user_id not in self.user_mapping:
            return []

        user_idx = self.user_mapping[user_id]
        neighbors = self._get_k_nearest_neighbors(user_idx)

        return [
            {
                'user_id': self.reverse_user_mapping[idx],
                'similarity': round(sim, 4)
            }
            for idx, sim in neighbors[:n]
        ]

    def get_user_interactions(self, user_id: int) -> List[Dict]:
        """
        获取用户的交互记录

        Args:
            user_id: 用户ID

        Returns:
            交互记录列表
        """
        if user_id not in self.user_mapping:
            return []

        user_idx = self.user_mapping[user_id]
        user_row = self.user_item_matrix[user_idx].toarray().flatten()

        interactions = []
        for item_idx, rating in enumerate(user_row):
            if rating > 0:
                interactions.append({
                    'job_id': self.reverse_item_mapping[item_idx],
                    'rating': rating
                })

        return interactions
