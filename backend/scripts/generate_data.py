"""
测试数据生成脚本
生成职位数据、用户数据、交互数据用于系统测试

运行方式:
    python manage.py shell
    >>> from scripts.generate_data import generate_all_data
    >>> generate_all_data()
"""

import random
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

from apps.jobs.models import JobCategory, JobTag, Company, Job
from apps.users.models import UserProfile
from apps.recommendations.models import UserJobInteraction

User = get_user_model()

# ==================== 基础数据配置 ====================

# 技术标签
TECH_SKILLS = [
    'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust',
    'C++', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin',
    'React', 'Vue.js', 'Angular', 'Node.js', 'Django', 'Flask',
    'Spring', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
    'Docker', 'Kubernetes', 'AWS', 'Azure', 'Git', 'Linux'
]

# 福利标签
BENEFITS = [
    '五险一金', '年终奖', '带薪年假', '弹性工作',
    '免费三餐', '健身房', '股票期权', '节日福利',
    '定期体检', '交通补贴', '住房补贴', '加班补助'
]

# 行业标签
INDUSTRIES = [
    '互联网', '金融', '电商', '教育', '医疗健康',
    '人工智能', '游戏', '企业服务', '物流', '新能源'
]

# 城市
CITIES = [
    '北京', '上海', '广州', '深圳', '杭州', '南京',
    '成都', '武汉', '西安', '苏州', '天津', '重庆'
]

# 公司
COMPANIES = [
    {'name': '字节跳动', 'size': '10000+', 'industry': '互联网', 'financing': 'listed'},
    {'name': '阿里巴巴', 'size': '10000+', 'industry': '互联网', 'financing': 'listed'},
    {'name': '腾讯', 'size': '10000+', 'industry': '互联网', 'financing': 'listed'},
    {'name': '百度', 'size': '10000+', 'industry': '互联网', 'financing': 'listed'},
    {'name': '美团', 'size': '10000+', 'industry': '互联网', 'financing': 'listed'},
    {'name': '京东', 'size': '10000+', 'industry': '电商', 'financing': 'listed'},
    {'name': '小米', 'size': '10000+', 'industry': '互联网', 'financing': 'listed'},
    {'name': '网易', 'size': '10000+', 'industry': '互联网', 'financing': 'listed'},
    {'name': '滴滴出行', 'size': '1000-9999', 'industry': '互联网', 'financing': 'listed'},
    {'name': '快手', 'size': '10000+', 'industry': '互联网', 'financing': 'listed'},
    {'name': '小红书', 'size': '1000-9999', 'industry': '互联网', 'financing': 'd'},
    {'name': '哔哩哔哩', 'size': '1000-9999', 'industry': '互联网', 'financing': 'listed'},
    {'name': '携程', 'size': '1000-9999', 'industry': '互联网', 'financing': 'listed'},
    {'name': '蚂蚁集团', 'size': '10000+', 'industry': '金融', 'financing': 'listed'},
    {'name': '华为', 'size': '10000+', 'industry': '通信', 'financing': 'unfinanced'},
    # 中小公司
    {'name': '创新科技', 'size': '100-499', 'industry': '互联网', 'financing': 'a'},
    {'name': '数智未来', 'size': '20-99', 'industry': '人工智能', 'financing': 'b'},
    {'name': '云端网络', 'size': '100-499', 'industry': '互联网', 'financing': 'c'},
    {'name': '智慧医疗', 'size': '20-99', 'industry': '医疗健康', 'financing': 'a'},
    {'name': '在线教育科技', 'size': '100-499', 'industry': '教育', 'financing': 'b'},
]

# 职位标题模板
JOB_TITLES = [
    ('Python开发工程师', 'backend'),
    ('Java开发工程师', 'backend'),
    ('前端开发工程师', 'frontend'),
    ('全栈开发工程师', 'fullstack'),
    ('数据分析师', 'data'),
    ('算法工程师', 'algorithm'),
    ('产品经理', 'product'),
    ('UI设计师', 'design'),
    ('测试工程师', 'qa'),
    ('运维工程师', 'ops'),
    ('大数据工程师', 'bigdata'),
    ('机器学习工程师', 'ml'),
    ('架构师', 'architect'),
    ('技术经理', 'manager'),
    ('Go开发工程师', 'backend'),
]


def create_tags():
    """创建职位标签"""
    print("创建职位标签...")

    # 技术标签
    for skill in TECH_SKILLS:
        JobTag.objects.get_or_create(
            name=skill,
            defaults={'category': 'skill', 'color': '#409EFF'}
        )

    # 福利标签
    for benefit in BENEFITS:
        JobTag.objects.get_or_create(
            name=benefit,
            defaults={'category': 'benefit', 'color': '#67C23A'}
        )

    # 行业标签
    for industry in INDUSTRIES:
        JobTag.objects.get_or_create(
            name=industry,
            defaults={'category': 'industry', 'color': '#E6A23C'}
        )

    print(f"创建了 {JobTag.objects.count()} 个标签")


def create_categories():
    """创建职位分类"""
    print("创建职位分类...")

    categories = [
        ('技术开发', None),
        ('后端开发', '技术开发'),
        ('前端开发', '技术开发'),
        ('移动开发', '技术开发'),
        ('数据开发', '技术开发'),
        ('产品设计', None),
        ('产品经理', '产品设计'),
        ('UI/UX设计', '产品设计'),
        ('运营市场', None),
    ]

    parent = None
    for name, parent_name in categories:
        if parent_name:
            try:
                parent = JobCategory.objects.get(name=parent_name)
            except JobCategory.DoesNotExist:
                parent = None

        JobCategory.objects.get_or_create(
            name=name,
            defaults={'parent': parent}
        )

    print(f"创建了 {JobCategory.objects.count()} 个分类")


def create_companies():
    """创建公司"""
    print("创建公司...")

    financing_map = {
        'unfinanced': 'unfinanced',
        'a': 'a',
        'b': 'b',
        'c': 'c',
        'd': 'd',
        'listed': 'listed',
    }

    for company_data in COMPANIES:
        Company.objects.get_or_create(
            name=company_data['name'],
            defaults={
                'size': company_data['size'],
                'industry': company_data['industry'],
                'financing_stage': financing_map.get(company_data['financing'], 'unfinanced'),
            }
        )

    print(f"创建了 {Company.objects.count()} 个公司")


def create_jobs(n=200):
    """创建职位"""
    print(f"创建 {n} 个职位...")

    companies = list(Company.objects.all())
    tags = list(JobTag.objects.all())
    categories = list(JobCategory.objects.all())

    skill_tags = [t for t in tags if t.category == 'skill']
    benefit_tags = [t for t in tags if t.category == 'benefit']

    jobs_created = 0
    for _ in range(n):
        # 随机选择职位标题
        title_template, job_type = random.choice(JOB_TITLES)
        title = title_template

        # 随机选择公司
        company = random.choice(companies)

        # 随机薪资
        salary_base = random.choice([8, 10, 12, 15, 18, 20, 25, 30, 35, 40])
        salary_min = salary_base * 1000
        salary_max = (salary_base + random.randint(3, 10)) * 1000

        # 随机城市
        location = random.choice(CITIES)

        # 随机学历和经验要求
        education = random.choice(['unlimited', 'college', 'bachelor', 'bachelor', 'master'])
        experience = random.choice(['unlimited', '0-1', '1-3', '1-3', '3-5', '3-5', '5-10'])

        # 创建职位
        job = Job.objects.create(
            title=title,
            company=company,
            salary_min=salary_min,
            salary_max=salary_max,
            location=location,
            education_required=education,
            experience_required=experience,
            description=f"我们正在寻找一位优秀的{title}加入我们的团队...",
            requirements="1. 熟悉相关技术\n2. 有良好的沟通能力\n3. 有团队合作精神",
            category=random.choice(categories) if categories else None,
            is_hot=random.random() < 0.2,
            is_urgent=random.random() < 0.1,
            view_count=random.randint(10, 1000),
            apply_count=random.randint(0, 100),
            favorite_count=random.randint(0, 50),
        )

        # 添加技术标签（2-5个）
        job_skill_tags = random.sample(skill_tags, min(random.randint(2, 5), len(skill_tags)))
        job.tags.add(*job_skill_tags)

        # 添加福利标签（2-4个）
        job_benefit_tags = random.sample(benefit_tags, min(random.randint(2, 4), len(benefit_tags)))
        job.tags.add(*job_benefit_tags)

        jobs_created += 1

    print(f"创建了 {jobs_created} 个职位")


def create_users(n=100):
    """创建测试用户"""
    print(f"创建 {n} 个测试用户...")

    users_created = 0
    for i in range(n):
        username = f"testuser{i+1}"
        email = f"testuser{i+1}@example.com"

        # 创建用户
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
            }
        )

        if created:
            user.set_password('password123')
            user.save()

            # 创建用户画像
            UserProfile.objects.create(
                user=user,
                name=f"测试用户{i+1}",
                gender=random.choice(['male', 'female']),
                age=random.randint(22, 35),
                education=random.choice(['college', 'bachelor', 'bachelor', 'master']),
                school=random.choice(['清华大学', '北京大学', '浙江大学', '复旦大学', '上海交通大学', '其他高校']),
                major=random.choice(['计算机科学', '软件工程', '数据科学', '人工智能', '信息管理']),
                expected_position=random.choice([t[0] for t in JOB_TITLES]),
                expected_salary_min=random.choice([10, 15, 20, 25]) * 1000,
                expected_salary_max=random.choice([20, 25, 30, 35, 40]) * 1000,
                expected_cities=random.sample(CITIES, random.randint(1, 3)),
                job_type='fulltime',
                skills=[
                    {'name': skill, 'level': random.randint(1, 5)}
                    for skill in random.sample(TECH_SKILLS, random.randint(3, 6))
                ],
                work_experience=random.randint(0, 10),
            )

            users_created += 1

    print(f"创建了 {users_created} 个用户")


def create_interactions(n=5000):
    """创建用户交互数据"""
    print(f"创建 {n} 条交互数据...")

    users = list(User.objects.all())
    jobs = list(Job.objects.filter(is_active=True))

    if not users or not jobs:
        print("请先创建用户和职位")
        return

    interactions_created = 0
    for _ in range(n):
        user = random.choice(users)
        job = random.choice(jobs)
        interaction_type = random.choices(
            ['view', 'favorite', 'apply', 'rating'],
            weights=[0.5, 0.2, 0.1, 0.2]
        )[0]

        rating = None
        if interaction_type == 'rating':
            rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.2, 0.35, 0.3])[0]

        # 避免重复
        _, created = UserJobInteraction.objects.get_or_create(
            user=user,
            job=job,
            interaction_type=interaction_type,
            defaults={'rating': rating}
        )

        if created:
            interactions_created += 1

    print(f"创建了 {interactions_created} 条交互记录")


def generate_all_data(users=100, jobs=200, interactions=5000):
    """
    生成所有测试数据

    Args:
        users: 用户数量
        jobs: 职位数量
        interactions: 交互记录数量
    """
    print("=" * 50)
    print("开始生成测试数据")
    print("=" * 50)

    # 清除现有数据（可选）
    # UserJobInteraction.objects.all().delete()
    # Job.objects.all().delete()
    # Company.objects.all().delete()
    # UserProfile.objects.all().delete()
    # User.objects.filter(username__startswith='testuser').delete()

    # 创建基础数据
    create_categories()
    create_tags()
    create_companies()

    # 创建职位和用户
    create_jobs(jobs)
    create_users(users)

    # 创建交互数据
    create_interactions(interactions)

    print("=" * 50)
    print("测试数据生成完成!")
    print(f"用户数: {User.objects.count()}")
    print(f"职位数: {Job.objects.count()}")
    print(f"公司数: {Company.objects.count()}")
    print(f"交互记录数: {UserJobInteraction.objects.count()}")
    print("=" * 50)


if __name__ == '__main__':
    generate_all_data()
