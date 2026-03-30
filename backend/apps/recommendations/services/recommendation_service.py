"""
推荐服务层
封装推荐算法，提供统一的推荐接口
"""

from typing import Dict, List, Set
from django.conf import settings
from django.core.cache import cache
from django.db.models import F
from django.utils import timezone
import logging

from apps.recommendations.algorithms import HybridRecommender
from apps.recommendations.models import UserJobInteraction, Recommendation
from apps.jobs.models import Job
from apps.users.models import UserProfile

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    推荐服务类

    提供推荐的生成、缓存、存储等功能

    参数:
        cache_timeout: 推荐结果缓存时间（秒），默认3600
    """

    def __init__(self, cache_timeout: int = 3600):
        """
        初始化推荐服务

        Args:
            cache_timeout: 缓存超时时间
        """
        self.cache_timeout = cache_timeout
        self._recommender = None

    @property
    def recommender(self) -> HybridRecommender:
        """延迟加载推荐器"""
        if self._recommender is None:
            self._recommender = HybridRecommender()
            self._train_recommender()
        return self._recommender

    def _train_recommender(self):
        """训练推荐模型"""
        logger.info("开始训练推荐模型...")

        # 获取所有交互记录
        interactions = list(
            UserJobInteraction.objects.filter(
                job__is_active=True
            ).values('user_id', 'job_id', 'rating')
        )

        # 将交互类型转换为数值
        for interaction in interactions:
            if interaction['rating'] is None:
                interaction['rating'] = 1.0

        # 获取所有职位
        jobs = list(
            Job.objects.filter(is_active=True).values(
                'id', 'title', 'salary_min', 'salary_max',
                'location', 'education_required', 'view_count',
                'apply_count', 'favorite_count'
            )
        )

        # 批量获取标签信息（修复 N+1 查询）
        from collections import defaultdict
        from apps.jobs.models import JobTag

        job_ids = [job['id'] for job in jobs]
        job_tags_map = defaultdict(list)

        # 一次查询获取所有职位的标签
        job_tags = JobTag.objects.filter(jobs__id__in=job_ids).values(
            'jobs__id', 'name', 'category'
        )
        for tag in job_tags:
            job_tags_map[tag['jobs__id']].append({
                'name': tag['name'],
                'category': tag['category']
            })

        for job in jobs:
            job['tags'] = job_tags_map.get(job['id'], [])

        # 获取所有用户画像
        user_profiles = list(
            UserProfile.objects.values(
                'user_id', 'expected_position', 'expected_salary_min',
                'expected_salary_max', 'expected_cities', 'skills',
                'education', 'work_experience'
            )
        )

        # 训练模型
        self._recommender.fit(interactions, jobs, user_profiles)

        logger.info(f"推荐模型训练完成，交互数: {len(interactions)}, 职位数: {len(jobs)}")

    def get_recommendations(
        self,
        user_id: int,
        n: int = 10,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        获取用户推荐

        Args:
            user_id: 用户ID
            n: 推荐数量
            use_cache: 是否使用缓存

        Returns:
            推荐列表
        """
        cache_key = f'recommendations:{user_id}:{n}'

        # 尝试从缓存获取
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"从缓存获取用户 {user_id} 的推荐")
                return cached

        # 获取用户画像
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            profile_dict = {
                'expected_position': user_profile.expected_position,
                'expected_salary_min': user_profile.expected_salary_min,
                'expected_salary_max': user_profile.expected_salary_max,
                'expected_cities': user_profile.expected_cities,
                'skills': user_profile.skills,
                'education': user_profile.education,
                'work_experience': user_profile.work_experience
            }
        except UserProfile.DoesNotExist:
            profile_dict = {}

        # 获取用户已交互的职位
        exclude_items = set(
            UserJobInteraction.objects.filter(
                user_id=user_id
            ).values_list('job_id', flat=True)
        )

        # 生成推荐
        recommendations = self.recommender.recommend(
            user_id=user_id,
            user_profile=profile_dict,
            n=n,
            exclude_items=exclude_items
        )

        # 缓存结果
        if use_cache and recommendations:
            cache.set(cache_key, recommendations, self.cache_timeout)

        # 存储到数据库
        self._save_recommendations(user_id, recommendations)

        return recommendations

    def _save_recommendations(self, user_id: int, recommendations: List[Dict]):
        """
        保存推荐结果到数据库

        Args:
            user_id: 用户ID
            recommendations: 推荐列表
        """
        for rec in recommendations:
            try:
                Recommendation.objects.update_or_create(
                    user_id=user_id,
                    job_id=rec['job_id'],
                    defaults={
                        'score': rec['score'],
                        'reasons': rec.get('reasons', []),
                        'algorithm': rec.get('algorithms', ['hybrid'])[0]
                    }
                )
            except Exception as e:
                logger.error(f"保存推荐失败: {e}")

    def refresh_recommendations(self, user_id: int):
        """
        刷新用户推荐缓存

        Args:
            user_id: 用户ID
        """
        cache_key = f'recommendations:{user_id}'
        cache.delete(cache_key)

        # 删除旧的推荐记录
        Recommendation.objects.filter(user_id=user_id).delete()

        # 生成新推荐
        return self.get_recommendations(user_id, use_cache=False)

    def record_interaction(
        self,
        user_id: int,
        job_id: int,
        interaction_type: str,
        rating: int = None
    ):
        """
        记录用户交互并更新推荐

        Args:
            user_id: 用户ID
            job_id: 职位ID
            interaction_type: 交互类型
            rating: 评分（可选）
        """
        # 创建交互记录
        UserJobInteraction.objects.create(
            user_id=user_id,
            job_id=job_id,
            interaction_type=interaction_type,
            rating=rating
        )

        # 更新职位统计（使用 F() 表达式避免竞态条件）
        if interaction_type == 'favorite':
            Job.objects.filter(id=job_id).update(
                favorite_count=F('favorite_count') + 1
            )
        elif interaction_type == 'apply':
            Job.objects.filter(id=job_id).update(
                apply_count=F('apply_count') + 1
            )

        # 触发推荐更新（异步）
        # 可以使用Celery异步执行
        # self.refresh_recommendations(user_id)


# 单例模式
_recommendation_service = None


def get_recommendation_service() -> RecommendationService:
    """获取推荐服务单例"""
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service
