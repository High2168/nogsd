"""
推荐模块视图
处理推荐结果获取、用户交互等API

作者: 刘怀仁
"""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from django.utils import timezone

from .models import UserJobInteraction, Recommendation
from .serializers import (
    UserJobInteractionSerializer,
    InteractionCreateSerializer,
    RecommendationSerializer
)
from apps.jobs.models import Job
from apps.jobs.serializers import JobListSerializer


class RecommendationListView(generics.ListAPIView):
    """
    推荐列表视图
    GET /api/recommendations/

    为当前用户生成个性化推荐

    返回:
        推荐职位列表，包含匹配分数和推荐理由
    """
    serializer_class = JobListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取推荐结果"""
        user = self.request.user
        n = int(self.request.query_params.get('n', 10))  # 推荐数量

        # 尝试从缓存获取推荐
        cached_recommendations = Recommendation.objects.filter(
            user=user,
            created_at__date=timezone.now().date()
        ).select_related('job', 'job__company').order_by('-score')[:n]

        if cached_recommendations.exists():
            # 返回缓存的推荐
            jobs = [r.job for r in cached_recommendations]
            # 标记为已查看
            cached_recommendations.update(is_viewed=True)
            return jobs

        # 如果没有缓存，生成新的推荐
        try:
            from .services.recommendation_service import RecommendationService
            service = RecommendationService()
            recommendations = service.get_recommendations(user.id, n=n)

            # 获取职位对象
            job_ids = [r['job_id'] for r in recommendations]
            jobs = list(Job.objects.filter(
                id__in=job_ids,
                is_active=True
            ).select_related('company', 'category').prefetch_related('tags'))

            # 按推荐分数排序
            job_score_map = {r['job_id']: r for r in recommendations}
            jobs.sort(key=lambda j: job_score_map.get(j.id, {}).get('score', 0), reverse=True)

            return jobs
        except Exception as e:
            # 推荐服务异常时返回热门职位
            return Job.objects.filter(
                is_active=True,
                is_hot=True
            ).select_related('company', 'category').prefetch_related('tags')[:n]

    def list(self, request, *args, **kwargs):
        """返回推荐结果列表"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({
            'recommendations': serializer.data,
            'algorithm': 'hybrid',
            'generated_at': timezone.now()
        })


class InteractionCreateView(generics.CreateAPIView):
    """
    创建交互记录视图
    POST /api/recommendations/interact/

    记录用户对职位的交互行为（浏览、收藏、评分等）

    请求参数:
        job_id: 职位ID
        interaction_type: 交互类型（view/favorite/unfavorite/apply/rating）
        rating: 评分（1-5，仅rating类型需要）
        duration: 浏览时长（秒，仅view类型需要）
        source: 来源
    """
    serializer_class = InteractionCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job_id = serializer.validated_data['job_id']
        interaction_type = serializer.validated_data['interaction_type']
        rating = serializer.validated_data.get('rating')
        duration = serializer.validated_data.get('duration', 0)
        source = serializer.validated_data.get('source', 'unknown')

        # 检查职位是否存在
        try:
            job = Job.objects.get(id=job_id, is_active=True)
        except Job.DoesNotExist:
            return Response(
                {'message': '职位不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 处理收藏/取消收藏（使用 F() 表达式避免竞态条件）
        if interaction_type == 'favorite':
            # 创建收藏记录
            interaction, created = UserJobInteraction.objects.get_or_create(
                user=request.user,
                job=job,
                interaction_type='favorite'
            )
            if created:
                Job.objects.filter(pk=job.pk).update(
                    favorite_count=F('favorite_count') + 1
                )

        elif interaction_type == 'unfavorite':
            # 删除收藏记录
            deleted, _ = UserJobInteraction.objects.filter(
                user=request.user,
                job=job,
                interaction_type='favorite'
            ).delete()
            if deleted:
                Job.objects.filter(pk=job.pk).update(
                    favorite_count=F('favorite_count') - 1
                )

        elif interaction_type == 'apply':
            # 创建投递记录
            UserJobInteraction.objects.get_or_create(
                user=request.user,
                job=job,
                interaction_type='apply'
            )
            Job.objects.filter(pk=job.pk).update(
                apply_count=F('apply_count') + 1
            )

        elif interaction_type == 'rating':
            # 创建或更新评分记录
            interaction, created = UserJobInteraction.objects.update_or_create(
                user=request.user,
                job=job,
                interaction_type='rating',
                defaults={'rating': rating}
            )

        elif interaction_type == 'view':
            # 记录浏览（避免重复记录）
            UserJobInteraction.objects.get_or_create(
                user=request.user,
                job=job,
                interaction_type='view',
                defaults={'duration': duration, 'source': source}
            )

        return Response({
            'message': '交互记录成功',
            'interaction_type': interaction_type
        })


class UserFavoritesView(generics.ListAPIView):
    """
    用户收藏列表视图
    GET /api/recommendations/favorites/

    返回用户收藏的职位列表
    """
    serializer_class = JobListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 获取用户收藏的职位ID
        favorite_job_ids = UserJobInteraction.objects.filter(
            user=self.request.user,
            interaction_type='favorite'
        ).values_list('job_id', flat=True)

        return Job.objects.filter(
            id__in=favorite_job_ids,
            is_active=True
        ).select_related('company', 'category').prefetch_related('tags')


class UserInteractionsView(generics.ListAPIView):
    """
    用户交互历史视图
    GET /api/recommendations/history/

    返回用户的交互历史记录
    """
    serializer_class = UserJobInteractionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserJobInteraction.objects.filter(
            user=self.request.user
        ).select_related('job', 'job__company').order_by('-created_at')[:50]
