"""
混合推荐策略 (Hybrid Recommendation)

核心思想:
    融合多种推荐算法的结果，综合生成最终推荐

策略:
    - User-based CF: 基于相似用户推荐
    - Item-based CF: 基于相似职位推荐
    - 冷启动处理: 基于内容推荐

优点:
    - 提高推荐准确率
    - 扩大推荐覆盖面
    - 解决单一算法的局限性

作者: 刘怀仁
学校: 齐鲁工业大学
"""

from typing import Dict, List, Set
from collections import defaultdict
import logging

from .user_based_cf import UserBasedCF
from .item_based_cf import ItemBasedCF
from .cold_start import ColdStartHandler

logger = logging.getLogger(__name__)


class HybridRecommender:
    """
    混合推荐器

    融合多种推荐算法的结果

    参数:
        weights: 各算法的权重，默认:
            - user_cf: 0.35
            - item_cf: 0.35
            - content: 0.30
        cold_start_threshold: 冷启动用户的最小交互次数
    """

    def __init__(
        self,
        weights: Dict[str, float] = None,
        cold_start_threshold: int = 5
    ):
        """
        初始化混合推荐器

        Args:
            weights: 算法权重字典
            cold_start_threshold: 冷启动阈值
        """
        # 默认权重
        self.weights = weights or {
            'user_cf': 0.35,
            'item_cf': 0.35,
            'content': 0.30
        }

        # 归一化权重
        total_weight = sum(self.weights.values())
        self.weights = {k: v / total_weight for k, v in self.weights.items()}

        # 初始化各算法
        self.user_cf = UserBasedCF(k=20, min_similarity=0.1)
        self.item_cf = ItemBasedCF(k=20, min_similarity=0.1)
        self.cold_start = ColdStartHandler(min_interactions=cold_start_threshold)

        # 训练数据
        self.interactions = None
        self.jobs = None
        self.user_profiles = None

        # 是否已训练
        self.is_fitted = False

    def fit(
        self,
        interactions: List[Dict],
        jobs: List[Dict] = None,
        user_profiles: List[Dict] = None
    ) -> 'HybridRecommender':
        """
        训练所有推荐模型

        Args:
            interactions: 交互记录列表
            jobs: 职位列表（用于冷启动）
            user_profiles: 用户画像列表（用于冷启动）

        Returns:
            self
        """
        logger.info("开始训练混合推荐模型...")

        self.interactions = interactions
        self.jobs = jobs or []
        self.user_profiles = user_profiles or []

        # 训练User-based CF
        if interactions:
            logger.info("训练User-based CF...")
            self.user_cf.fit(interactions)

            logger.info("训练Item-based CF...")
            self.item_cf.fit(interactions)

        self.is_fitted = True
        logger.info("混合推荐模型训练完成")

        return self

    def recommend(
        self,
        user_id: int,
        user_profile: Dict = None,
        n: int = 10,
        exclude_items: Set[int] = None
    ) -> List[Dict]:
        """
        为用户生成混合推荐

        Args:
            user_id: 用户ID
            user_profile: 用户画像（冷启动时必需）
            n: 推荐数量
            exclude_items: 需要排除的职位ID

        Returns:
            推荐列表
        """
        if not self.is_fitted:
            logger.warning("模型未训练，请先调用fit方法")
            return []

        # 检查是否为冷启动用户
        user_interactions = [i for i in self.interactions if i['user_id'] == user_id]
        is_cold_start = self.cold_start.is_cold_start_user(
            user_id,
            len(user_interactions)
        )

        # 获取用户已交互的职位
        if exclude_items is None:
            exclude_items = set()
        user_items = set(i['job_id'] for i in user_interactions)
        exclude_items.update(user_items)

        # 各算法的推荐结果
        all_recommendations = defaultdict(lambda: {'score': 0, 'reasons': [], 'algorithms': []})

        if is_cold_start:
            # 冷启动用户：主要使用基于内容的推荐
            logger.info(f"用户 {user_id} 为冷启动用户，使用基于内容推荐")

            if user_profile and self.jobs:
                content_recs = self.cold_start.recommend_for_new_user(
                    user_profile, self.jobs, n=n*2
                )

                for rec in content_recs:
                    job_id = rec['job_id']
                    all_recommendations[job_id]['score'] += rec['score'] * self.weights.get('content', 0.3)
                    all_recommendations[job_id]['reasons'] = rec.get('reasons', [])
                    all_recommendations[job_id]['algorithms'].append('content')

            # 补充热门职位
            if len(all_recommendations) < n:
                popular = self.cold_start.get_popular_jobs(self.jobs, n)
                for rec in popular:
                    if rec['job_id'] not in exclude_items:
                        job_id = rec['job_id']
                        all_recommendations[job_id]['score'] += rec['score'] * 0.3
                        all_recommendations[job_id]['reasons'].append({
                            'type': 'popular',
                            'desc': '热门职位推荐',
                            'score': rec['score']
                        })
                        all_recommendations[job_id]['algorithms'].append('popular')

        else:
            # 非冷启动用户：使用混合策略

            # 1. User-based CF推荐
            user_cf_recs = self.user_cf.recommend(user_id, n=n*2, exclude_items=exclude_items)
            for rec in user_cf_recs:
                job_id = rec['job_id']
                all_recommendations[job_id]['score'] += rec['score'] * self.weights.get('user_cf', 0.35)
                all_recommendations[job_id]['reasons'].append({
                    'type': 'similar_users',
                    'desc': rec.get('reason', '相似用户推荐'),
                    'score': rec['score']
                })
                all_recommendations[job_id]['algorithms'].append('user_cf')

            # 2. Item-based CF推荐
            item_cf_recs = self.item_cf.recommend(user_id, n=n*2, exclude_items=exclude_items)
            for rec in item_cf_recs:
                job_id = rec['job_id']
                all_recommendations[job_id]['score'] += rec['score'] * self.weights.get('item_cf', 0.35)
                all_recommendations[job_id]['reasons'].append({
                    'type': 'similar_items',
                    'desc': rec.get('reason', '相似职位推荐'),
                    'score': rec['score']
                })
                all_recommendations[job_id]['algorithms'].append('item_cf')

            # 3. 基于内容推荐（补充）
            if user_profile and self.jobs:
                content_recs = self.cold_start.recommend_for_new_user(
                    user_profile, self.jobs, n=n
                )
                for rec in content_recs:
                    job_id = rec['job_id']
                    if job_id not in exclude_items:
                        all_recommendations[job_id]['score'] += rec['score'] * self.weights.get('content', 0.3)
                        all_recommendations[job_id]['algorithms'].append('content')
                        # 合并推荐理由
                        for reason in rec.get('reasons', []):
                            if reason not in all_recommendations[job_id]['reasons']:
                                all_recommendations[job_id]['reasons'].append(reason)

        # 排序并返回Top-N
        sorted_recs = sorted(
            all_recommendations.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )

        # 构建最终推荐结果
        recommendations = []
        for job_id, data in sorted_recs[:n]:
            recommendations.append({
                'job_id': job_id,
                'score': round(data['score'], 4),
                'reasons': data['reasons'][:3],  # 最多3个推荐理由
                'algorithms': data['algorithms'],
                'is_cold_start': is_cold_start
            })

        return recommendations

    def update_weights(self, new_weights: Dict[str, float]):
        """
        更新算法权重

        Args:
            new_weights: 新的权重字典
        """
        self.weights.update(new_weights)
        # 归一化
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}

    def get_algorithm_stats(self) -> Dict:
        """
        获取算法统计信息

        Returns:
            统计信息字典
        """
        return {
            'weights': self.weights,
            'is_fitted': self.is_fitted,
            'n_interactions': len(self.interactions) if self.interactions else 0,
            'n_jobs': len(self.jobs) if self.jobs else 0,
            'n_users': len(set(i['user_id'] for i in self.interactions)) if self.interactions else 0
        }
