"""
推荐模块配置
"""

from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    """推荐模块配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.recommendations'
    verbose_name = '推荐系统'
