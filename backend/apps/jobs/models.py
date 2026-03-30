"""
职位模型定义
包含职位分类、职位标签、职位信息等模型
"""

from django.db import models
from django.db.models import F


class JobCategory(models.Model):
    """
    职位分类模型
    用于对职位进行分类管理

    示例:
        - 技术开发
            - 后端开发
            - 前端开发
            - 移动开发
        - 产品设计
            - 产品经理
            - UI设计
    """

    # 分类名称
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='分类名称'
    )

    # 父分类（支持多级分类）
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父分类'
    )

    # 排序权重
    sort_order = models.IntegerField(
        default=0,
        verbose_name='排序',
        help_text='数字越小越靠前'
    )

    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'job_categories'
        verbose_name = '职位分类'
        verbose_name_plural = '职位分类'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def get_full_path(self):
        """获取完整的分类路径"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class JobTag(models.Model):
    """
    职位标签模型
    用于标记职位的技术栈、福利等属性

    标签分类:
        - skill: 技术栈（Python, Java, Vue等）
        - benefit: 福利（五险一金, 年假等）
        - industry: 行业（互联网, 金融等）
        - other: 其他
    """

    # 标签分类
    TAG_CATEGORIES = [
        ('skill', '技术栈'),
        ('benefit', '福利待遇'),
        ('industry', '行业'),
        ('other', '其他'),
    ]

    # 标签名称
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='标签名称'
    )

    # 标签分类
    category = models.CharField(
        max_length=20,
        choices=TAG_CATEGORIES,
        default='skill',
        verbose_name='标签分类'
    )

    # 标签颜色（用于前端展示）
    color = models.CharField(
        max_length=20,
        blank=True,
        default='#409EFF',
        verbose_name='标签颜色',
        help_text='十六进制颜色代码'
    )

    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'job_tags'
        verbose_name = '职位标签'
        verbose_name_plural = '职位标签'
        ordering = ['category', 'name']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"


class Company(models.Model):
    """
    公司模型
    存储公司信息，避免在职位表中重复存储

    这样设计的好处:
    1. 减少数据冗余
    2. 方便管理公司信息
    3. 可以统计公司发布的职位数量
    """

    # 公司名称
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='公司名称'
    )

    # 公司Logo
    logo = models.URLField(
        blank=True,
        verbose_name='公司Logo'
    )

    # 公司规模
    SIZE_CHOICES = [
        ('0-20', '0-20人'),
        ('20-99', '20-99人'),
        ('100-499', '100-499人'),
        ('500-999', '500-999人'),
        ('1000-9999', '1000-9999人'),
        ('10000+', '10000人以上'),
    ]
    size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES,
        blank=True,
        verbose_name='公司规模'
    )

    # 所属行业
    industry = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='所属行业'
    )

    # 公司简介
    description = models.TextField(
        blank=True,
        verbose_name='公司简介'
    )

    # 公司地址
    address = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='公司地址'
    )

    # 公司官网
    website = models.URLField(
        blank=True,
        verbose_name='公司官网'
    )

    # 融资阶段
    FINANCING_CHOICES = [
        ('unfinanced', '未融资'),
        ('angel', '天使轮'),
        ('a', 'A轮'),
        ('b', 'B轮'),
        ('c', 'C轮'),
        ('d', 'D轮及以上'),
        ('listed', '已上市'),
        ('acquired', '被收购'),
    ]
    financing_stage = models.CharField(
        max_length=20,
        choices=FINANCING_CHOICES,
        blank=True,
        verbose_name='融资阶段'
    )

    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'companies'
        verbose_name = '公司'
        verbose_name_plural = '公司信息'

    def __str__(self):
        return self.name


class Job(models.Model):
    """
    职位信息模型
    存储职位的完整信息

    这是推荐系统的核心数据，用于:
    1. 推荐算法的物品特征
    2. 用户搜索和筛选
    3. 职位详情展示
    """

    # ==================== 基本信息 ====================
    # 职位标题
    title = models.CharField(
        max_length=200,
        verbose_name='职位标题',
        help_text='如：高级Python开发工程师'
    )

    # 关联公司
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs',
        verbose_name='所属公司'
    )

    # ==================== 薪资信息 ====================
    # 最低薪资（元/月）
    salary_min = models.IntegerField(
        verbose_name='最低薪资',
        help_text='单位：元/月'
    )

    # 最高薪资（元/月）
    salary_max = models.IntegerField(
        verbose_name='最高薪资',
        help_text='单位：元/月'
    )

    # 薪资说明（如"14薪"、"年底双薪"等）
    salary_note = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='薪资说明'
    )

    # ==================== 职位要求 ====================
    # 工作地点
    location = models.CharField(
        max_length=100,
        verbose_name='工作地点'
    )

    # 详细地址
    address = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='详细地址'
    )

    # 学历要求
    EDUCATION_CHOICES = [
        ('unlimited', '不限'),
        ('high_school', '高中'),
        ('college', '大专'),
        ('bachelor', '本科'),
        ('master', '硕士'),
        ('doctor', '博士'),
    ]
    education_required = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        default='unlimited',
        verbose_name='学历要求'
    )

    # 经验要求
    EXPERIENCE_CHOICES = [
        ('unlimited', '不限'),
        ('0-1', '应届生/0-1年'),
        ('1-3', '1-3年'),
        ('3-5', '3-5年'),
        ('5-10', '5-10年'),
        ('10+', '10年以上'),
    ]
    experience_required = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='unlimited',
        verbose_name='经验要求'
    )

    # ==================== 职位描述 ====================
    # 职位描述
    description = models.TextField(
        verbose_name='职位描述',
        help_text='职位的详细描述'
    )

    # 任职要求
    requirements = models.TextField(
        blank=True,
        verbose_name='任职要求',
        help_text='对候选人的要求'
    )

    # ==================== 分类和标签 ====================
    # 职位分类
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs',
        verbose_name='职位分类'
    )

    # 职位标签（多对多关系）
    tags = models.ManyToManyField(
        JobTag,
        blank=True,
        related_name='jobs',
        verbose_name='职位标签'
    )

    # ==================== 状态和统计 ====================
    # 是否有效（软删除）
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否有效'
    )

    # 是否紧急招聘
    is_urgent = models.BooleanField(
        default=False,
        verbose_name='紧急招聘'
    )

    # 是否热门
    is_hot = models.BooleanField(
        default=False,
        verbose_name='热门职位'
    )

    # 浏览次数
    view_count = models.IntegerField(
        default=0,
        verbose_name='浏览次数'
    )

    # 投递次数
    apply_count = models.IntegerField(
        default=0,
        verbose_name='投递次数'
    )

    # 收藏次数
    favorite_count = models.IntegerField(
        default=0,
        verbose_name='收藏次数'
    )

    # ==================== 时间戳 ====================
    # 发布时间
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='发布时间'
    )

    # 截止时间
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='截止时间'
    )

    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'jobs'
        verbose_name = '职位'
        verbose_name_plural = '职位信息'
        ordering = ['-created_at']  # 按创建时间倒序
        # 添加索引以优化常用查询
        indexes = [
            models.Index(fields=['is_active', '-created_at'], name='job_active_created_idx'),
            models.Index(fields=['location'], name='job_location_idx'),
            models.Index(fields=['salary_min', 'salary_max'], name='job_salary_range_idx'),
            models.Index(fields=['education_required'], name='job_education_idx'),
            models.Index(fields=['experience_required'], name='job_experience_idx'),
            models.Index(fields=['is_hot', 'is_active'], name='job_hot_active_idx'),
            models.Index(fields=['is_urgent', 'is_active'], name='job_urgent_active_idx'),
        ]

    def __str__(self):
        return f"{self.title} - {self.company.name}"

    def get_salary_range(self):
        """获取薪资范围字符串"""
        min_k = self.salary_min // 1000
        max_k = self.salary_max // 1000
        return f"{min_k}K-{max_k}K"

    def get_skill_tags(self):
        """获取技术栈标签列表"""
        return self.tags.filter(category='skill')

    def get_benefit_tags(self):
        """获取福利标签列表"""
        return self.tags.filter(category='benefit')

    def increment_view_count(self) -> None:
        """
        增加浏览次数（使用 F() 表达式避免竞态条件）

        使用 update() 而非 save() 确保原子性操作
        """
        Job.objects.filter(pk=self.pk).update(
            view_count=F('view_count') + 1
        )

    def increment_apply_count(self) -> None:
        """
        增加投递次数（使用 F() 表达式避免竞态条件）

        使用 update() 而非 save() 确保原子性操作
        """
        Job.objects.filter(pk=self.pk).update(
            apply_count=F('apply_count') + 1
        )
