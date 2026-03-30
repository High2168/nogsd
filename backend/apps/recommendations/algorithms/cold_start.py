"""
冷启动处理算法 (Cold Start Handler)

核心思想:
    对于新用户或新职位，由于缺少交互数据，无法使用协同过滤算法。
    本模块通过基于内容的方法解决冷启动问题。

策略:
    - 新用户: 基于用户画像（技能、期望职位、期望薪资等）匹配职位
    - 新职位: 基于职位特征（标签、描述等）找到相似职位，推荐给对相似职位感兴趣的用户
"""

from collections import defaultdict
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)


class ColdStartHandler:
    """
    冷启动处理类

    用于处理新用户和新职位的推荐问题

    参数:
        min_interactions: 判断冷启动用户的最小交互次数，默认5
    """

    def __init__(self, min_interactions: int = 5):
        """
        初始化

        Args:
            min_interactions: 交互次数少于此值视为冷启动用户
        """
        self.min_interactions = min_interactions

    def is_cold_start_user(self, user_id: int, interaction_count: int) -> bool:
        """
        判断用户是否为冷启动用户

        Args:
            user_id: 用户ID
            interaction_count: 用户交互次数

        Returns:
            是否为冷启动用户
        """
        return interaction_count < self.min_interactions

    def recommend_for_new_user(
        self,
        user_profile: Dict,
        jobs: List[Dict],
        n: int = 10
    ) -> List[Dict]:
        """
        为新用户生成推荐

        基于用户画像匹配职位特征

        Args:
            user_profile: 用户画像，包含:
                - expected_position: 期望职位
                - expected_salary_min: 期望薪资下限
                - expected_salary_max: 期望薪资上限
                - expected_cities: 期望城市列表
                - skills: 技能列表
                - education: 学历
                - work_experience: 工作经验年数
            jobs: 候选职位列表
            n: 推荐数量

        Returns:
            推荐列表
        """
        logger.info(f"为新用户生成基于内容的推荐，候选职位数: {len(jobs)}")

        # 提取用户特征
        user_skills = set(skill.get('name', '').lower() for skill in user_profile.get('skills', []))
        expected_position = user_profile.get('expected_position', '').lower()
        expected_salary_min = user_profile.get('expected_salary_min', 0)
        expected_salary_max = user_profile.get('expected_salary_max', float('inf'))
        expected_cities = set(city.lower() for city in user_profile.get('expected_cities', []))
        user_education = user_profile.get('education', '')

        # 计算每个职位的匹配分数
        scored_jobs = []

        for job in jobs:
            score = 0.0
            reasons = []

            # 1. 职位名称匹配（权重最高）
            job_title = job.get('title', '').lower()
            if expected_position and expected_position in job_title:
                score += 0.3
                reasons.append({
                    'type': 'position_match',
                    'desc': f'职位名称匹配您的期望: {expected_position}',
                    'score': 0.3
                })

            # 2. 薪资匹配
            job_salary_min = job.get('salary_min', 0)
            job_salary_max = job.get('salary_max', 0)

            if expected_salary_min <= job_salary_max and expected_salary_max >= job_salary_min:
                score += 0.2
                reasons.append({
                    'type': 'salary_match',
                    'desc': '薪资符合您的期望',
                    'score': 0.2
                })

            # 3. 城市匹配
            job_location = job.get('location', '').lower()
            if expected_cities and any(city in job_location for city in expected_cities):
                score += 0.2
                reasons.append({
                    'type': 'location_match',
                    'desc': f'工作地点在您的期望城市',
                    'score': 0.2
                })

            # 4. 技能匹配
            job_tags = job.get('tags', [])
            job_skill_tags = set(
                tag.get('name', '').lower()
                for tag in job_tags
                if tag.get('category') == 'skill'
            )

            skill_match_count = len(user_skills & job_skill_tags)
            if skill_match_count > 0:
                skill_score = min(0.3, skill_match_count * 0.1)
                score += skill_score
                matched_skills = list(user_skills & job_skill_tags)[:3]
                reasons.append({
                    'type': 'skill_match',
                    'desc': f'技能匹配: {", ".join(matched_skills)}',
                    'score': skill_score
                })

            # 5. 学历匹配（加分项）
            job_education = job.get('education_required', '')
            if user_education and job_education:
                education_levels = ['high_school', 'college', 'bachelor', 'master', 'doctor']
                user_level = education_levels.index(user_education) if user_education in education_levels else -1
                job_level = education_levels.index(job_education) if job_education in education_levels else -1

                if user_level >= job_level:
                    score += 0.1
                    reasons.append({
                        'type': 'education_match',
                        'desc': '学历符合要求',
                        'score': 0.1
                    })

            if score > 0:
                scored_jobs.append({
                    'job_id': job.get('id'),
                    'score': round(score, 4),
                    'reasons': reasons,
                    'algorithm': 'cold_start_content'
                })

        # 按分数排序
        scored_jobs.sort(key=lambda x: x['score'], reverse=True)

        return scored_jobs[:n]

    def recommend_for_new_job(
        self,
        job: Dict,
        user_profiles: List[Dict],
        n: int = 50
    ) -> List[Dict]:
        """
        为新职位找到潜在感兴趣的用户

        基于职位特征匹配用户画像

        Args:
            job: 新职位信息
            user_profiles: 用户画像列表
            n: 返回用户数量

        Returns:
            潜在用户列表及其匹配分数
        """
        logger.info(f"为新职位寻找潜在用户，用户数: {len(user_profiles)}")

        # 提取职位特征
        job_title = job.get('title', '').lower()
        job_salary_min = job.get('salary_min', 0)
        job_salary_max = job.get('salary_max', float('inf'))
        job_location = job.get('location', '').lower()
        job_tags = job.get('tags', [])
        job_skill_tags = set(
            tag.get('name', '').lower()
            for tag in job_tags
            if tag.get('category') == 'skill'
        )

        # 计算每个用户的匹配分数
        scored_users = []

        for profile in user_profiles:
            score = 0.0

            # 期望职位匹配
            expected_position = profile.get('expected_position', '').lower()
            if expected_position and expected_position in job_title:
                score += 0.3

            # 薪资匹配
            expected_salary_min = profile.get('expected_salary_min', 0)
            expected_salary_max = profile.get('expected_salary_max', float('inf'))
            if expected_salary_min <= job_salary_max and expected_salary_max >= job_salary_min:
                score += 0.2

            # 城市匹配
            expected_cities = set(city.lower() for city in profile.get('expected_cities', []))
            if expected_cities and any(city in job_location for city in expected_cities):
                score += 0.2

            # 技能匹配
            user_skills = set(
                skill.get('name', '').lower()
                for skill in profile.get('skills', [])
            )
            skill_match = len(user_skills & job_skill_tags)
            if skill_match > 0:
                score += min(0.3, skill_match * 0.1)

            if score > 0.3:  # 只推荐匹配度较高的用户
                scored_users.append({
                    'user_id': profile.get('user_id'),
                    'score': round(score, 4)
                })

        # 按分数排序
        scored_users.sort(key=lambda x: x['score'], reverse=True)

        return scored_users[:n]

    def get_popular_jobs(self, jobs: List[Dict], n: int = 10) -> List[Dict]:
        """
        获取热门职位（作为冷启动的默认推荐）

        Args:
            jobs: 职位列表
            n: 返回数量

        Returns:
            热门职位列表
        """
        # 按浏览量、投递量、收藏量综合排序
        scored_jobs = []

        for job in jobs:
            view_count = job.get('view_count', 0)
            apply_count = job.get('apply_count', 0)
            favorite_count = job.get('favorite_count', 0)

            # 综合热度分数
            score = view_count * 0.3 + apply_count * 2 + favorite_count * 1.5

            scored_jobs.append({
                'job_id': job.get('id'),
                'score': round(score / 100, 4),  # 归一化
                'reason': '热门职位推荐',
                'algorithm': 'popular'
            })

        scored_jobs.sort(key=lambda x: x['score'], reverse=True)

        return scored_jobs[:n]
