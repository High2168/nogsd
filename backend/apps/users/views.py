"""
用户模块视图
处理用户注册、登录、个人信息等API

作者: 刘怀仁
"""

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout

from .models import User, UserProfile
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserProfileCreateSerializer
)


class UserRegisterView(generics.CreateAPIView):
    """
    用户注册视图
    POST /api/auth/register/

    请求参数:
        username: 用户名
        email: 邮箱
        password: 密码
        password_confirm: 确认密码
        phone: 手机号（可选）

    响应:
        成功: 返回用户信息和JWT令牌
        失败: 返回错误信息
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]  # 允许任何人访问

    def create(self, request, *args, **kwargs):
        """创建用户并返回JWT令牌"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 创建用户
        user = serializer.save()

        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': '注册成功',
            'user': UserSerializer(user).data,
            'token': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    用户登录视图
    POST /api/auth/login/

    请求参数:
        username: 用户名
        password: 密码

    响应:
        成功: 返回用户信息和JWT令牌
        失败: 返回错误信息
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # 验证用户
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({
                'message': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'message': '账号已被禁用'
            }, status=status.HTTP_403_FORBIDDEN)

        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': '登录成功',
            'user': UserSerializer(user).data,
            'token': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })


class UserLogoutView(APIView):
    """
    用户登出视图
    POST /api/auth/logout/

    将refresh token加入黑名单，使其失效
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 获取refresh token
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                # 将token加入黑名单
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({'message': '登出成功'})
        except Exception as e:
            return Response({'message': '登出成功'})


class UserDetailView(generics.RetrieveAPIView):
    """
    用户详情视图
    GET /api/users/me/

    获取当前登录用户的信息
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    用户画像视图
    GET /api/users/profile/  获取用户画像
    PUT /api/users/profile/  更新用户画像（完整更新）
    PATCH /api/users/profile/  部分更新用户画像

    如果用户没有画像，会自动创建一个空画像
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """获取或创建用户画像"""
        user = self.request.user
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'name': user.username}
        )
        return profile

    def get_serializer_class(self):
        """根据请求方法选择序列化器"""
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileSerializer
        return UserProfileSerializer


class UserProfileCreateView(generics.CreateAPIView):
    """
    创建用户画像视图
    POST /api/users/profile/create/

    首次创建用户画像时使用
    """
    serializer_class = UserProfileCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """创建用户画像"""
        serializer.save(user=self.request.user)
