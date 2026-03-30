"""
职位模块序列化器
定义API的输入输出格式

作者: 刘怀仁
"""

from rest_framework import serializers
from .models import JobCategory, JobTag, Company, Job


def _check_user_interaction(user, job_id: int, interaction_type: str) -> bool:
    """
    检查用户是否对职位有特定类型的交互

    Args:
        user: 用户对象
        job_id: 职位ID
        interaction_type: 交互类型 ('favorite', 'apply', 'rating')

    Returns:
        bool: 是否存在该交互
    """
    from apps.recommendations.models import UserJobInteraction
    return UserJobInteraction.objects.filter(
        user=user,
        job_id=job_id,
        interaction_type=interaction_type
    ).exists()


def _get_user_rating(user, job_id: int) -> int | None:
    """
    获取用户对职位的评分

    Args:
        user: 用户对象
        job_id: 职位ID

    Returns:
        int | None: 评分值（1-5），不存在则返回 None
    """
    from apps.recommendations.models import UserJobInteraction
    interaction = UserJobInteraction.objects.filter(
        user=user,
        job_id=job_id,
        interaction_type='rating'
    ).values_list('rating', flat=True).first()
    return interaction


class JobCategorySerializer(serializers.ModelSerializer):
    """职位分类序列化器"""

    # 子分类
    children = serializers.SerializerMethodField()

    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'parent', 'sort_order', 'children', 'created_at']

    def get_children(self, obj):
        """获取子分类"""
        children = obj.children.all()
        return JobCategorySerializer(children, many=True).data


class JobTagSerializer(serializers.ModelSerializer):
    """职位标签序列化器"""

    class Meta:
        model = JobTag
        fields = ['id', 'name', 'category', 'color']


class CompanySerializer(serializers.ModelSerializer):
    """公司序列化器"""

    # 公司发布的职位数量
    job_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'logo', 'size', 'industry',
            'description', 'address', 'website', 'financing_stage',
            'job_count', 'created_at'
        ]

    def get_job_count(self, obj):
        """获取公司发布的有效职位数量"""
        return obj.jobs.filter(is_active=True).count()


class JobListSerializer(serializers.ModelSerializer):
    """
    职位列表序列化器
    用于职位列表展示，包含较少字段以提高性能
    """

    # 公司信息
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.URLField(source='company.logo', read_only=True)
    company_size = serializers.CharField(source='company.size', read_only=True)
    company_industry = serializers.CharField(source='company.industry', read_only=True)

    # 薪资范围（格式化）
    salary_range = serializers.ReadOnlyField(source='get_salary_range')

    # 技术标签
    skill_tags = serializers.SerializerMethodField()

    # 匹配度（推荐时使用）
    match_score = serializers.FloatField(read_only=True, default=0)
    match_reasons = serializers.ListField(read_only=True, default=list)

    # 用户是否已收藏
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title',
            'company_name', 'company_logo', 'company_size', 'company_industry',
            'salary_min', 'salary_max', 'salary_range', 'salary_note',
            'location', 'education_required', 'experience_required',
            'skill_tags', 'is_urgent', 'is_hot',
            'view_count', 'apply_count', 'favorite_count',
            'match_score', 'match_reasons', 'is_favorite',
            'published_at', 'created_at'
        ]

    def get_skill_tags(self, obj):
        """获取技术标签"""
        tags = obj.tags.filter(category='skill')
        return JobTagSerializer(tags, many=True).data

    def get_is_favorite(self, obj) -> bool:
        """检查用户是否已收藏该职位"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return _check_user_interaction(request.user, obj.id, 'favorite')


class JobDetailSerializer(serializers.ModelSerializer):
    """
    职位详情序列化器
    用于职位详情页，包含完整信息
    """

    # 公司信息
    company = CompanySerializer(read_only=True)

    # 分类信息
    category_name = serializers.CharField(source='category.name', read_only=True)

    # 所有标签
    tags = JobTagSerializer(many=True, read_only=True)

    # 技术标签（单独提取）
    skill_tags = serializers.SerializerMethodField()
    benefit_tags = serializers.SerializerMethodField()

    # 薪资范围
    salary_range = serializers.ReadOnlyField(source='get_salary_range')

    # 用户是否已收藏/投递
    is_favorite = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title',
            'company', 'category', 'category_name',
            'salary_min', 'salary_max', 'salary_range', 'salary_note',
            'location', 'address',
            'education_required', 'experience_required',
            'description', 'requirements',
            'tags', 'skill_tags', 'benefit_tags',
            'is_urgent', 'is_hot', 'is_active',
            'view_count', 'apply_count', 'favorite_count',
            'is_favorite', 'is_applied', 'user_rating',
            'published_at', 'deadline', 'created_at', 'updated_at'
        ]

    def get_skill_tags(self, obj):
        """获取技术标签"""
        tags = obj.tags.filter(category='skill')
        return JobTagSerializer(tags, many=True).data

    def get_benefit_tags(self, obj):
        """获取福利标签"""
        tags = obj.tags.filter(category='benefit')
        return JobTagSerializer(tags, many=True).data

    def get_is_favorite(self, obj) -> bool:
        """检查用户是否已收藏"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return _check_user_interaction(request.user, obj.id, 'favorite')

    def get_is_applied(self, obj) -> bool:
        """检查用户是否已投递"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return _check_user_interaction(request.user, obj.id, 'apply')

    def get_user_rating(self, obj) -> int | None:
        """获取用户对该职位的评分"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        return _get_user_rating(request.user, obj.id)


class JobSearchSerializer(serializers.Serializer):
    """职位搜索参数序列化器"""

    # 关键词搜索
    keyword = serializers.CharField(
        required=False,
        help_text='搜索关键词'
    )

    # 城市筛选
    location = serializers.CharField(
        required=False,
        help_text='工作地点'
    )

    # 薪资范围筛选
    salary_min = serializers.IntegerField(
        required=False,
        help_text='最低薪资（元/月）'
    )
    salary_max = serializers.IntegerField(
        required=False,
        help_text='最高薪资（元/月）'
    )

    # 学历要求筛选
    education = serializers.CharField(
        required=False,
        help_text='学历要求'
    )

    # 经验要求筛选
    experience = serializers.CharField(
        required=False,
        help_text='经验要求'
    )

    # 分类筛选
    category = serializers.IntegerField(
        required=False,
        help_text='职位分类ID'
    )

    # 标签筛选
    tags = serializers.CharField(
        required=False,
        help_text='标签ID，多个用逗号分隔'
    )

    # 排序
    ordering = serializers.CharField(
        required=False,
        default='-created_at',
        help_text='排序字段，如-created_at按时间倒序'
    )
