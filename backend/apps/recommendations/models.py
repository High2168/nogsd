"""
推荐系统模型定义
包含用户交互记录和推荐结果缓存
"""

from django.db import models
from django.conf import settings


class UserJobInteraction(models.Model):
    """
    用户-职位交互记录模型
    记录用户对职位的各种行为

    这是协同过滤算法的核心数据来源:
    - 浏览行为：隐式反馈，权重较低
    - 收藏行为：显式正向反馈
    - 投递行为：强正向反馈
    - 评分行为：显式反馈，最直接的偏好表达
    """

    # 交互类型
    INTERACTION_TYPES = [
        ('view', '浏览'),           # 查看职位详情
        ('favorite', '收藏'),       # 收藏职位
        ('unfavorite', '取消收藏'), # 取消收藏
        ('apply', '投递'),          # 投递简历
        ('rating', '评分'),         # 对职位评分
    ]

    # 关联用户
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interactions',
        verbose_name='用户'
    )

    # 关联职位
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='interactions',
        verbose_name='职位'
    )

    # 交互类型
    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPES,
        verbose_name='交互类型'
    )

    # 评分（1-5分，仅rating类型使用）
    rating = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='评分',
        help_text='1-5分，分数越高表示越满意'
    )

    # 交互时长（秒，仅view类型使用）
    duration = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='浏览时长',
        help_text='浏览时长，单位：秒'
    )

    # 用户来源（记录用户是从哪里看到这个职位的）
    source = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='来源',
        help_text='如：推荐、搜索、首页等'
    )

    # 设备信息
    device = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='设备',
        help_text='如：PC、Mobile、App'
    )

    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'user_job_interactions'
        verbose_name = '用户交互记录'
        verbose_name_plural = '用户交互记录'
        # 索引优化查询性能
        indexes = [
            models.Index(fields=['user', 'job']),
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['job', 'interaction_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} {self.get_interaction_type_display()} {self.job.title}"

    def get_rating_value(self):
        """
        获取交互的数值化价值
        用于协同过滤算法计算

        价值映射:
        - 浏览: 1.0 (基础)
        - 收藏: 3.0
        - 投递: 4.0
        - 评分: 按评分值
        """
        interaction_values = {
            'view': 1.0,
            'favorite': 3.0,
            'unfavorite': -1.0,
            'apply': 4.0,
        }

        if self.interaction_type == 'rating' and self.rating:
            return float(self.rating)
        return interaction_values.get(self.interaction_type, 0.0)


class Recommendation(models.Model):
    """
    推荐结果缓存模型
    存储系统为用户生成的推荐结果

    这样设计的好处:
    1. 避免重复计算
    2. 可以追溯推荐历史
    3. 支持A/B测试不同算法
    """

    # 关联用户
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name='用户'
    )

    # 关联职位
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='recommended_to',
        verbose_name='推荐职位'
    )

    # 推荐分数（0-1之间）
    score = models.FloatField(
        verbose_name='推荐分数',
        help_text='推荐算法计算的分数，范围0-1'
    )

    # 推荐理由（JSON格式）
    # 示例: [
    #     {"type": "skill_match", "desc": "技能匹配：Python", "score": 0.9},
    #     {"type": "salary_match", "desc": "薪资符合期望", "score": 0.8}
    # ]
    reasons = models.JSONField(
        default=list,
        blank=True,
        verbose_name='推荐理由',
        help_text='推荐的详细理由列表'
    )

    # 使用的推荐算法
    ALGORITHM_CHOICES = [
        ('user_cf', 'User-based协同过滤'),
        ('item_cf', 'Item-based协同过滤'),
        ('hybrid', '混合推荐'),
        ('cold_start', '冷启动推荐'),
        ('content', '基于内容推荐'),
    ]
    algorithm = models.CharField(
        max_length=50,
        choices=ALGORITHM_CHOICES,
        verbose_name='推荐算法'
    )

    # 是否已被用户查看
    is_viewed = models.BooleanField(
        default=False,
        verbose_name='是否已查看'
    )

    # 用户是否对推荐进行了操作（点击、收藏等）
    is_interacted = models.BooleanField(
        default=False,
        verbose_name='是否已交互'
    )

    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'recommendations'
        verbose_name = '推荐结果'
        verbose_name_plural = '推荐结果缓存'
        # 同一用户同一职位同一天只保留一条推荐
        unique_together = [['user', 'job', 'created_at']]
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['user', 'algorithm']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"为{self.user.username}推荐 {self.job.title} (分数:{self.score:.2f})"


class UserSimilarity(models.Model):
    """
    用户相似度模型
    缓存用户之间的相似度计算结果

    用于User-based协同过滤:
    - 避免重复计算
    - 加速推荐生成
    """

    # 用户1
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='similarities_as_user1',
        verbose_name='用户1'
    )

    # 用户2
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='similarities_as_user2',
        verbose_name='用户2'
    )

    # 相似度（-1到1之间，余弦相似度）
    similarity = models.FloatField(
        verbose_name='相似度',
        help_text='余弦相似度，范围-1到1'
    )

    # 计算时间
    calculated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='计算时间'
    )

    class Meta:
        db_table = 'user_similarities'
        verbose_name = '用户相似度'
        verbose_name_plural = '用户相似度'
        unique_together = [['user1', 'user2']]
        indexes = [
            models.Index(fields=['user1', '-similarity']),
        ]

    def __str__(self):
        return f"{self.user1.username} <-> {self.user2.username}: {self.similarity:.3f}"


class JobSimilarity(models.Model):
    """
    职位相似度模型
    缓存职位之间的相似度计算结果

    用于Item-based协同过滤:
    - 基于用户行为计算职位相似度
    - 推荐相似职位
    """

    # 职位1
    job1 = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='similarities_as_job1',
        verbose_name='职位1'
    )

    # 职位2
    job2 = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='similarities_as_job2',
        verbose_name='职位2'
    )

    # 相似度（0到1之间）
    similarity = models.FloatField(
        verbose_name='相似度',
        help_text='相似度，范围0到1'
    )

    # 计算时间
    calculated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='计算时间'
    )

    class Meta:
        db_table = 'job_similarities'
        verbose_name = '职位相似度'
        verbose_name_plural = '职位相似度'
        unique_together = [['job1', 'job2']]
        indexes = [
            models.Index(fields=['job1', '-similarity']),
        ]

    def __str__(self):
        return f"{self.job1.title} <-> {self.job2.title}: {self.similarity:.3f}"
