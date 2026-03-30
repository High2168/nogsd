"""
Django管理命令 - 导入职位数据
可以直接通过命令行运行

使用方法:
    python manage.py import_data "path/to/job_posts.csv" --limit 2000
"""

from django.core.management.base import BaseCommand
from apps.data.import_data import import_data


class Command(BaseCommand):
    help = '从CSV文件导入职位数据'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='CSV文件路径')
        parser.add_argument('--limit', type=int, default=2000, help='导入职位数量限制')
        parser.add_argument('--no-users', action='store_true', help='不创建测试用户')

    def handle(self, *args, **options):
        file_path = options['file_path']
        limit = options['limit']
        create_users = not options['no_users']

        self.stdout.write(f"开始导入数据: {file_path}")
        self.stdout.write(f"职位数量限制: {limit}")

        import_data(file_path, limit=limit, create_users=create_users)

        self.stdout.write(self.style.SUCCESS('数据导入完成!'))
