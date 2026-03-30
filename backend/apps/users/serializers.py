"""
用户模块序列化器
定义API的输入输出格式

作者: 刘怀仁
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    用户基础序列化器
    用于用户信息的展示
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    处理用户注册请求
    """

    # 密码确认字段
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        help_text='确认密码'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def validate(self, data):
        """验证数据"""
        # 检查两次密码是否一致
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次密码输入不一致'})

        # 检查用户名是否已存在
        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError({'username': '该用户名已被注册'})

        # 检查邮箱是否已存在
        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError({'email': '该邮箱已被注册'})

        return data

    def create(self, validated_data):
        """创建用户"""
        # 移除确认密码字段
        validated_data.pop('password_confirm')

        # 创建用户（密码会自动加密）
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    处理登录请求
    """

    username = serializers.CharField(
        required=True,
        help_text='用户名'
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text='密码'
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户画像序列化器
    用于展示和编辑用户画像
    """

    # 关联用户信息
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    # 计算字段
    salary_range = serializers.ReadOnlyField(source='get_expected_salary_range')
    skill_names = serializers.ReadOnlyField(source='get_skill_names')

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email',
            'name', 'gender', 'age',
            'education', 'school', 'major',
            'expected_position', 'expected_salary_min', 'expected_salary_max',
            'salary_range', 'expected_cities', 'job_type',
            'skills', 'skill_names',
            'work_experience', 'experience_detail',
            'resume_url', 'introduction',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_skills(self, value):
        """验证技能数据格式"""
        if not isinstance(value, list):
            raise serializers.ValidationError('技能必须是列表格式')

        for skill in value:
            if not isinstance(skill, dict):
                raise serializers.ValidationError('每个技能必须是字典格式')
            if 'name' not in skill:
                raise serializers.ValidationError('技能必须包含name字段')

        return value

    def validate_expected_cities(self, value):
        """验证期望城市数据格式"""
        if not isinstance(value, list):
            raise serializers.ValidationError('期望城市必须是列表格式')
        return value

    def validate(self, data):
        """验证薪资范围"""
        salary_min = data.get('expected_salary_min')
        salary_max = data.get('expected_salary_max')

        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError({
                'expected_salary_min': '期望薪资下限不能大于上限'
            })

        return data


class UserProfileCreateSerializer(serializers.ModelSerializer):
    """
    用户画像创建序列化器
    用于首次创建用户画像
    """

    class Meta:
        model = UserProfile
        fields = [
            'name', 'gender', 'age',
            'education', 'school', 'major',
            'expected_position', 'expected_salary_min', 'expected_salary_max',
            'expected_cities', 'job_type',
            'skills', 'work_experience', 'experience_detail',
            'resume_url', 'introduction'
        ]

    def create(self, validated_data):
        """创建用户画像"""
        user = self.context['request'].user
        # 检查是否已有画像
        if hasattr(user, 'userprofile'):
            raise serializers.ValidationError('用户画像已存在，请使用更新接口')

        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile
