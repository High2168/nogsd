"""
数据管理模块配置
"""

from django.apps import AppConfig


class DataConfig(AppConfig):
    """数据管理模块配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.data'
    verbose_name = '数据管理'
