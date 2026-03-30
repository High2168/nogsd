"""
用户模型定义
包含自定义用户模型和用户画像模型

作者: 刘怀仁
学校: 齐鲁工业大学
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自定义用户模型
    继承Django内置的AbstractUser，扩展了手机号和头像字段

    继承字段:
        username: 用户名
        email: 邮箱
        password: 密码（加密存储）
        first_name, last_name: 姓名
        is_active: 是否激活
        is_staff: 是否员工
        is_superuser: 是否超级管理员
        date_joined: 注册时间
        last_login: 最后登录时间
    """
    # 手机号码（可选）
    phone = models.CharField(
        max_length=11,
        blank=True,
        verbose_name='手机号码',
        help_text='11位手机号码'
    )

    # 用户头像（可选）
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='头像',
        help_text='用户头像图片'
    )

    class Meta:
        db_table = 'users'  # 数据库表名
        verbose_name = '用户'
        verbose_name_plural = '用户信息'

    def __str__(self) -> str:
        """返回用户名作为字符串表示"""
        return self.username

    @property
    def profile(self) -> 'UserProfile | None':
        """获取用户画像，如果不存在返回None"""
        try:
            return self.userprofile
        except UserProfile.DoesNotExist:
            return None

    def has_complete_profile(self) -> bool:
        """检查用户是否完善了画像"""
        profile = self.profile
        if not profile:
            return False
        return bool(profile.name and profile.expected_position)


class UserProfile(models.Model):
    """
    用户画像模型
    存储用户的详细信息和求职意向

    用于:
    1. 用户画像建模
    2. 推荐算法的特征输入
    3. 冷启动问题的解决
    """

    # 性别选择
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    ]

    # 学历选择
    EDUCATION_CHOICES = [
        ('high_school', '高中'),
        ('college', '大专'),
        ('bachelor', '本科'),
        ('master', '硕士'),
        ('doctor', '博士'),
    ]

    # 工作性质选择
    JOB_TYPE_CHOICES = [
        ('fulltime', '全职'),
        ('parttime', '兼职'),
        ('intern', '实习'),
        ('remote', '远程'),
    ]

    # ==================== 关联用户 ====================
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile',
        verbose_name='用户'
    )

    # ==================== 基本信息 ====================
    # 真实姓名
    name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='姓名'
    )

    # 性别
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name='性别'
    )

    # 年龄
    age = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='年龄'
    )

    # ==================== 教育背景 ====================
    # 学历
    education = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        blank=True,
        verbose_name='学历'
    )

    # 毕业院校
    school = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='毕业院校'
    )

    # 专业
    major = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='专业'
    )

    # ==================== 求职意向 ====================
    # 期望职位
    expected_position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='期望职位'
    )

    # 期望薪资下限（元/月）
    expected_salary_min = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='期望薪资下限',
        help_text='单位：元/月'
    )

    # 期望薪资上限（元/月）
    expected_salary_max = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='期望薪资上限',
        help_text='单位：元/月'
    )

    # 期望城市列表（JSON格式存储）
    # 示例: ["北京", "上海", "深圳"]
    expected_cities = models.JSONField(
        default=list,
        blank=True,
        verbose_name='期望城市',
        help_text='期望工作的城市列表'
    )

    # 工作性质
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        blank=True,
        default='fulltime',
        verbose_name='工作性质'
    )

    # ==================== 技能标签 ====================
    # 技能列表（JSON格式存储）
    # 示例: [{"name": "Python", "level": 5, "years": 3}, ...]
    # level: 1-5级技能水平
    # years: 使用年限
    skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name='技能标签',
        help_text='技能列表，包含名称、水平、年限'
    )

    # ==================== 工作经验 ====================
    # 工作年限
    work_experience = models.IntegerField(
        default=0,
        verbose_name='工作年限',
        help_text='工作年数'
    )

    # 工作经历详情（JSON格式存储）
    # 示例: [
    #     {
    #         "company": "XX公司",
    #         "position": "前端工程师",
    #         "start_date": "2020-01",
    #         "end_date": "2023-06",
    #         "description": "负责..."
    #     }
    # ]
    experience_detail = models.JSONField(
        default=list,
        blank=True,
        verbose_name='工作经历',
        help_text='工作经历详情列表'
    )

    # ==================== 简历 ====================
    # 简历文件URL
    resume_url = models.URLField(
        blank=True,
        verbose_name='简历链接'
    )

    # 自我介绍
    introduction = models.TextField(
        blank=True,
        verbose_name='自我介绍'
    )

    # ==================== 时间戳 ====================
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'user_profiles'  # 数据库表名
        verbose_name = '用户画像'
        verbose_name_plural = '用户画像'
        # 添加索引以优化常用查询
        indexes = [
            models.Index(fields=['user_id'], name='profile_user_idx'),
            models.Index(fields=['education'], name='profile_education_idx'),
            models.Index(fields=['work_experience'], name='profile_experience_idx'),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}的画像"

    def get_skill_names(self) -> list[str]:
        """获取所有技能名称列表"""
        return [skill.get('name') for skill in self.skills if skill.get('name')]

    def get_expected_salary_range(self) -> str:
        """获取期望薪资范围字符串"""
        if self.expected_salary_min and self.expected_salary_max:
            return f"{self.expected_salary_min // 1000}K-{self.expected_salary_max // 1000}K"
        return "面议"
