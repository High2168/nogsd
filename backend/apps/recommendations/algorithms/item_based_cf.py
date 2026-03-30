"""
基于物品的协同过滤算法 (Item-based Collaborative Filtering)

核心思想:
    基于用户的历史行为，推荐与用户喜欢的职位相似的其他职位

算法步骤:
    1. 构建用户-职位评分矩阵
    2. 计算职位之间的相似度
    3. 根据用户历史喜欢的职位，找到相似的职位
    4. 加权聚合生成推荐

优点:
    - 职位相似度相对稳定，可以预计算
    - 推荐结果可解释性强
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, lil_matrix
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import logging

logger = logging.getLogger(__name__)


class ItemBasedCF:
    """
    基于物品的协同过滤推荐算法

    使用余弦相似度计算职位之间的相似性

    参数:
        k: 每个职位考虑的相似职位数量，默认20
        min_similarity: 最小相似度阈值，默认0.1
    """

    def __init__(self, k: int = 20, min_similarity: float = 0.1):
        """
        初始化算法

        Args:
            k: 相似职位数量
            min_similarity: 职位之间的最小相似度阈值
        """
        self.k = k
        self.min_similarity = min_similarity

        # 用户-职位评分矩阵
        self.user_item_matrix = None

        # 职位相似度矩阵
        self.item_similarity = None

        # 用户和职位的映射
        self.user_mapping = {}
        self.item_mapping = {}
        self.reverse_user_mapping = {}
        self.reverse_item_mapping = {}

        # 交互数据
        self.interactions = None

        # 预计算的职位相似度缓存
        self._item_neighbors_cache = {}

    def fit(self, interactions: List[Dict]) -> 'ItemBasedCF':
        """
        训练模型，构建矩阵并计算职位相似度

        Args:
            interactions: 交互记录列表

        Returns:
            self
        """
        logger.info(f"开始训练Item-based CF模型，交互记录数: {len(interactions)}")

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
        matrix = lil_matrix((n_users, n_items))

        for interaction in interactions:
            user_idx = self.user_mapping.get(interaction['user_id'])
            item_idx = self.item_mapping.get(interaction['job_id'])
            rating = interaction.get('rating', 1.0)

            if user_idx is not None and item_idx is not None:
                matrix[user_idx, item_idx] = rating

        self.user_item_matrix = matrix.tocsr()

        # 计算职位相似度矩阵
        # 注意：职位相似度是基于用户对职位的评分向量计算的
        # 即：如果很多用户同时对职位A和职位B评分，则A和B相似
        logger.info("计算职位相似度矩阵...")

        # 转置矩阵，每行代表一个职位，每列代表一个用户
        item_user_matrix = self.user_item_matrix.T

        # 计算职位之间的余弦相似度
        self.item_similarity = cosine_similarity(item_user_matrix)

        # 对角线设为0
        np.fill_diagonal(self.item_similarity, 0)

        # 预计算每个职位的相似职位
        self._precompute_item_neighbors()

        logger.info("模型训练完成")
        return self

    def _precompute_item_neighbors(self):
        """预计算每个职位的相似职位列表"""
        n_items = self.item_similarity.shape[0]

        for item_idx in range(n_items):
            similarities = self.item_similarity[item_idx]

            # 找到相似度大于阈值的职位
            neighbors = [
                (idx, sim) for idx, sim in enumerate(similarities)
                if sim >= self.min_similarity and idx != item_idx
            ]

            # 按相似度排序
            neighbors.sort(key=lambda x: x[1], reverse=True)

            self._item_neighbors_cache[item_idx] = neighbors[:self.k]

    def recommend(self, user_id: int, n: int = 10, exclude_items: Set[int] = None) -> List[Dict]:
        """
        为指定用户生成推荐

        Args:
            user_id: 用户ID
            n: 推荐数量
            exclude_items: 需要排除的职位ID

        Returns:
            推荐列表
        """
        # 检查用户是否存在
        if user_id not in self.user_mapping:
            logger.warning(f"用户 {user_id} 不在训练数据中")
            return []

        user_idx = self.user_mapping[user_id]

        # 获取用户已交互的职位
        user_items = set()
        user_row = self.user_item_matrix[user_idx].toarray().flatten()

        # 用户喜欢的职位（评分>0）
        liked_items = []
        for item_idx, rating in enumerate(user_row):
            if rating > 0:
                item_id = self.reverse_item_mapping[item_idx]
                user_items.add(item_id)
                liked_items.append((item_idx, rating))

        if exclude_items:
            user_items.update(exclude_items)

        if not liked_items:
            logger.warning(f"用户 {user_id} 没有交互记录")
            return []

        # 基于用户喜欢的职位，找到相似的职位
        item_scores = defaultdict(float)
        item_similarity_sources = defaultdict(list)

        for liked_item_idx, liked_rating in liked_items:
            # 获取该职位的相似职位
            similar_items = self._item_neighbors_cache.get(liked_item_idx, [])

            for similar_item_idx, similarity in similar_items:
                similar_item_id = self.reverse_item_mapping[similar_item_idx]

                # 排除已交互的职位
                if similar_item_id in user_items:
                    continue

                # 加权评分 = 用户对该职位的评分 * 职位相似度
                weighted_score = liked_rating * similarity
                item_scores[similar_item_id] += weighted_score

                # 记录来源（用于推荐理由）
                liked_item_id = self.reverse_item_mapping[liked_item_idx]
                item_similarity_sources[similar_item_id].append({
                    'source_item_id': liked_item_id,
                    'similarity': similarity,
                    'user_rating': liked_rating
                })

        # 按分数排序
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)

        # 生成推荐结果
        recommendations = []
        for job_id, score in sorted_items[:n]:
            # 归一化分数
            max_score = sorted_items[0][1] if sorted_items else 1
            normalized_score = score / max_score if max_score > 0 else 0

            # 生成推荐理由
            sources = item_similarity_sources[job_id][:3]
            source_items = [s['source_item_id'] for s in sources]

            reason = f"与您浏览过的职位相似（相似职位数: {len(item_similarity_sources[job_id])}）"

            recommendations.append({
                'job_id': job_id,
                'score': round(normalized_score, 4),
                'reason': reason,
                'similar_to': source_items,
                'algorithm': 'item_cf'
            })

        return recommendations

    def get_similar_items(self, job_id: int, n: int = 10) -> List[Dict]:
        """
        获取与指定职位最相似的职位

        Args:
            job_id: 职位ID
            n: 返回数量

        Returns:
            相似职位列表
        """
        if job_id not in self.item_mapping:
            return []

        item_idx = self.item_mapping[job_id]
        neighbors = self._item_neighbors_cache.get(item_idx, [])

        return [
            {
                'job_id': self.reverse_item_mapping[idx],
                'similarity': round(sim, 4)
            }
            for idx, sim in neighbors[:n]
        ]

    def get_item_features(self, job_id: int) -> Dict:
        """
        获取职位的特征信息

        Args:
            job_id: 职位ID

        Returns:
            职位特征信息
        """
        if job_id not in self.item_mapping:
            return {}

        item_idx = self.item_mapping[job_id]
        item_vector = self.user_item_matrix.T[item_idx].toarray().flatten()

        return {
            'job_id': job_id,
            'interaction_count': int(np.sum(item_vector > 0)),
            'total_rating': float(np.sum(item_vector)),
            'avg_rating': float(np.mean(item_vector[item_vector > 0])) if np.any(item_vector > 0) else 0
        }
