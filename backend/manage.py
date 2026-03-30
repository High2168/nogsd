#!/usr/bin/env python
"""
Django项目管理脚本
用于运行各种Django命令

常用命令:
    python manage.py runserver     # 启动开发服务器
    python manage.py migrate       # 执行数据库迁移
    python manage.py createsuperuser  # 创建管理员账号
    python manage.py test          # 运行测试

作者: 刘怀仁
"""

import os
import sys


def main():
    """运行Django管理命令"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入Django。请确保已安装Django并且 "
            "PYTHONPATH环境变量中包含Django的安装路径。"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
