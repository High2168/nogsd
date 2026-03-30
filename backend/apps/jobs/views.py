"""
职位模块视图
处理职位列表、详情、搜索等API
"""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from .models import Job, JobCategory, JobTag, Company
from .serializers import (
    JobListSerializer,
    JobDetailSerializer,
    JobCategorySerializer,
    JobTagSerializer,
    CompanySerializer,
    JobSearchSerializer
)
from apps.recommendations.models import UserJobInteraction


class JobPagination(PageNumberPagination):
    """职位列表分页配置"""
    page_size = 20  # 每页20条
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobListView(generics.ListAPIView):
    """
    职位列表视图
    GET /api/jobs/

    支持参数:
        keyword: 搜索关键词（职位名称、公司名称）
        location: 工作地点
        salary_min: 最低薪资
        salary_max: 最高薪资
        education: 学历要求
        experience: 经验要求
        category: 职位分类ID
        tags: 标签ID（逗号分隔）
        ordering: 排序字段（默认-created_at）

    返回:
        分页后的职位列表
    """
    serializer_class = JobListSerializer
    permission_classes = [AllowAny]
    pagination_class = JobPagination

    def get_queryset(self):
        """构建查询集"""
        queryset = Job.objects.filter(is_active=True).select_related(
            'company', 'category'
        ).prefetch_related('tags')

        # 获取查询参数
        keyword = self.request.query_params.get('keyword')
        location = self.request.query_params.get('location')
        salary_min = self.request.query_params.get('salary_min')
        salary_max = self.request.query_params.get('salary_max')
        education = self.request.query_params.get('education')
        experience = self.request.query_params.get('experience')
        category_id = self.request.query_params.get('category')
        tags = self.request.query_params.get('tags')
        ordering = self.request.query_params.get('ordering', '-created_at')

        # 关键词搜索
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(company__name__icontains=keyword) |
                Q(description__icontains=keyword)
            )

        # 地点筛选
        if location:
            queryset = queryset.filter(location__icontains=location)

        # 薪资筛选
        if salary_min:
            queryset = queryset.filter(salary_max__gte=int(salary_min))
        if salary_max:
            queryset = queryset.filter(salary_min__lte=int(salary_max))

        # 学历筛选
        if education:
            queryset = queryset.filter(education_required=education)

        # 经验筛选
        if experience:
            queryset = queryset.filter(experience_required=experience)

        # 分类筛选
        if category_id:
            queryset = queryset.filter(category_id=int(category_id))

        # 标签筛选
        if tags:
            tag_ids = [int(t) for t in tags.split(',') if t.isdigit()]
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()

        # 排序
        queryset = queryset.order_by(ordering)

        return queryset


class JobDetailView(generics.RetrieveAPIView):
    """
    职位详情视图
    GET /api/jobs/{id}/

    返回职位的完整信息，包括公司信息、标签等
    同时记录用户的浏览行为
    """
    serializer_class = JobDetailSerializer
    permission_classes = [AllowAny]
    queryset = Job.objects.filter(is_active=True).select_related(
        'company', 'category'
    ).prefetch_related('tags')

    def retrieve(self, request, *args, **kwargs):
        """获取职位详情并记录浏览"""
        instance = self.get_object()

        # 增加浏览次数
        instance.increment_view_count()

        # 记录用户浏览行为（仅登录用户）
        if request.user.is_authenticated:
            UserJobInteraction.objects.get_or_create(
                user=request.user,
                job=instance,
                interaction_type='view',
                defaults={'source': 'detail'}
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class JobCategoryListView(generics.ListAPIView):
    """
    职位分类列表视图
    GET /api/jobs/categories/

    返回所有职位分类（树形结构）
    """
    serializer_class = JobCategorySerializer
    permission_classes = [AllowAny]
    queryset = JobCategory.objects.all()


class JobTagListView(generics.ListAPIView):
    """
    职位标签列表视图
    GET /api/jobs/tags/

    返回所有职位标签

    支持参数:
        category: 标签分类（skill/benefit/industry/other）
    """
    serializer_class = JobTagSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = JobTag.objects.all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class HotJobListView(generics.ListAPIView):
    """
    热门职位列表视图
    GET /api/jobs/hot/

    返回热门职位（is_hot=True或按浏览量排序）
    """
    serializer_class = JobListSerializer
    permission_classes = [AllowAny]
    pagination_class = JobPagination

    def get_queryset(self):
        return Job.objects.filter(
            is_active=True,
            is_hot=True
        ).select_related('company', 'category').prefetch_related('tags')[:10]


class JobSearchView(APIView):
    """
    职位搜索视图
    POST /api/jobs/search/

    使用POST方法进行复杂搜索
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = JobSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 构建查询条件
        queryset = Job.objects.filter(is_active=True)

        data = serializer.validated_data

        if data.get('keyword'):
            keyword = data['keyword']
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(company__name__icontains=keyword)
            )

        if data.get('location'):
            queryset = queryset.filter(location__icontains=data['location'])

        if data.get('salary_min'):
            queryset = queryset.filter(salary_max__gte=data['salary_min'])

        if data.get('salary_max'):
            queryset = queryset.filter(salary_min__lte=data['salary_max'])

        if data.get('education'):
            queryset = queryset.filter(education_required=data['education'])

        if data.get('experience'):
            queryset = queryset.filter(experience_required=data['experience'])

        if data.get('category'):
            queryset = queryset.filter(category_id=data['category'])

        if data.get('tags'):
            tag_ids = [int(t) for t in data['tags'].split(',') if t.isdigit()]
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()

        # 排序
        ordering = data.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)

        # 分页
        paginator = JobPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = JobListSerializer(page, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)
