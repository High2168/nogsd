"""
推荐模块序列化器
定义API的输入输出格式
"""

from rest_framework import serializers
from .models import UserJobInteraction, Recommendation


class UserJobInteractionSerializer(serializers.ModelSerializer):
    """
    用户交互记录序列化器
    用于记录用户的交互行为
    """

    # 职位信息
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)

    class Meta:
        model = UserJobInteraction
        fields = [
            'id', 'job', 'job_title', 'company_name',
            'interaction_type', 'rating', 'duration',
            'source', 'device', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class InteractionCreateSerializer(serializers.Serializer):
    """
    交互创建序列化器
    用于创建用户交互记录
    """

    # 职位ID
    job_id = serializers.IntegerField(
        required=True,
        help_text='职位ID'
    )

    # 交互类型
    interaction_type = serializers.ChoiceField(
        choices=UserJobInteraction.INTERACTION_TYPES,
        required=True,
        help_text='交互类型'
    )

    # 评分（仅rating类型需要）
    rating = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=5,
        help_text='评分（1-5分）'
    )

    # 浏览时长（仅view类型需要）
    duration = serializers.IntegerField(
        required=False,
        min_value=0,
        help_text='浏览时长（秒）'
    )

    # 来源
    source = serializers.CharField(
        required=False,
        default='unknown',
        help_text='交互来源'
    )

    def validate(self, data):
        """验证数据"""
        interaction_type = data.get('interaction_type')

        # 评分类型必须提供评分
        if interaction_type == 'rating' and not data.get('rating'):
            raise serializers.ValidationError({
                'rating': '评分类型必须提供评分值'
            })

        return data


class RecommendationSerializer(serializers.ModelSerializer):
    """
    推荐结果序列化器
    用于展示推荐职位
    """

    # 职位信息（使用职位列表序列化器）
    from apps.jobs.serializers import JobListSerializer
    job = JobListSerializer(read_only=True)

    # 算法名称
    algorithm_name = serializers.CharField(
        source='get_algorithm_display',
        read_only=True
    )

    class Meta:
        model = Recommendation
        fields = [
            'id', 'job', 'score', 'reasons',
            'algorithm', 'algorithm_name',
            'is_viewed', 'is_interacted', 'created_at'
        ]


class RecommendationListSerializer(serializers.Serializer):
    """
    推荐列表响应序列化器
    用于返回推荐结果
    """

    # 推荐职位列表
    recommendations = serializers.ListField(
        child=serializers.DictField(),
        help_text='推荐职位列表'
    )

    # 推荐算法
    algorithm = serializers.CharField(
        help_text='使用的推荐算法'
    )

    # 是否为冷启动用户
    is_cold_start = serializers.BooleanField(
        help_text='是否为冷启动用户（新用户）'
    )

    # 推荐生成时间
    generated_at = serializers.DateTimeField(
        help_text='推荐生成时间'
    )


class UserFeedbackSerializer(serializers.Serializer):
    """
    用户反馈序列化器
    用于收集用户对推荐的反馈
    """

    # 推荐ID
    recommendation_id = serializers.IntegerField(
        required=True,
        help_text='推荐记录ID'
    )

    # 是否有帮助
    is_helpful = serializers.BooleanField(
        required=True,
        help_text='推荐是否有帮助'
    )

    # 反馈内容
    feedback = serializers.CharField(
        required=False,
        max_length=500,
        help_text='详细反馈内容'
    )
