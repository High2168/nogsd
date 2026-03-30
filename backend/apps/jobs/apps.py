"""
职位模块配置
"""

from django.apps import AppConfig


class JobsConfig(AppConfig):
    """职位模块配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.jobs'
    verbose_name = '职位管理'
