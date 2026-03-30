"""
中文职位数据处理程序
处理G:\下载\job.csv数据集

数据清洗流程:
    1. 解析薪资格式（5千-1万 -> 5000-10000）
    2. 清洗工作地点（提取城市）
    3. 标准化学历和工作经验
    4. 提取技能标签
    5. 去除重复和无效数据
    6. 导入数据库
"""

import pandas as pd
import re
import random
from django.contrib.auth import get_user_model

from apps.jobs.models import JobCategory, JobTag, Company, Job
from apps.users.models import UserProfile
from apps.recommendations.models import UserJobInteraction

User = get_user_model()


# ==================== 数据清洗函数 ====================

def parse_salary(salary_str):
    """
    解析薪资格式
    支持格式:
        - "5千-1万" -> (5000, 10000)
        - "1万-2万" -> (10000, 20000)
        - "1.1万-2.2万" -> (11000, 22000)
        - "面议" -> 随机
        - "1万以下" -> (8000, 10000)
        - "1万以上" -> (10000, 15000)
    """
    if not salary_str or pd.isna(salary_str):
        return random.choice([8000, 10000, 12000, 15000]), random.choice([15000, 20000, 25000, 30000])

    salary_str = str(salary_str).strip()

    # 面议
    if '面议' in salary_str:
        return random.randint(8000, 15000), random.randint(20000, 35000)

    # 提取数字
    def convert_to_number(s):
        """将字符串转换为数字（单位：元）"""
        s = s.strip()
        if not s:
            return None

        # 处理"万"
        if '万' in s:
            num = float(re.search(r'[\d.]+', s).group())
            return int(num * 10000)
        # 处理"千"
        elif '千' in s:
            num = float(re.search(r'[\d.]+', s).group())
            return int(num * 1000)
        else:
            # 纯数字
            match = re.search(r'[\d.]+', s)
            if match:
                return int(float(match.group()))
        return None

    # 解析范围
    # 格式: "5千-1万" 或 "1.1万-2.2万"
    if '-' in salary_str:
        parts = salary_str.split('-')
        min_sal = convert_to_number(parts[0])
        max_sal = convert_to_number(parts[1]) if len(parts) > 1 else min_sal

        if min_sal and max_sal:
            return min(min_sal, 100000), min(max_sal, 150000)

    # 处理"以上"和"以下"
    if '以上' in salary_str:
        num = convert_to_number(salary_str)
        if num:
            return num, int(num * 1.5)
    if '以下' in salary_str:
        num = convert_to_number(salary_str)
        if num:
            return int(num * 0.6), num

    # 默认返回
    return random.randint(8000, 15000), random.randint(15000, 30000)


def extract_city(location_str):
    """
    提取城市
    格式: "天津·河北·光复道" -> "天津"
    """
    if not location_str or pd.isna(location_str):
        return random.choice(['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉'])

    location_str = str(location_str).strip()

    # 按·分割取第一部分
    if '·' in location_str:
        city = location_str.split('·')[0].strip()
        return city

    # 按空格分割
    parts = location_str.split()
    if parts:
        return parts[0].strip()

    return location_str[:2] if len(location_str) >= 2 else '北京'


def standardize_education(edu_str):
    """
    标准化学历要求
    """
    if not edu_str or pd.isna(edu_str):
        return 'unlimited'

    edu_str = str(edu_str).strip()

    education_map = {
        '学历不限': 'unlimited',
        '不限': 'unlimited',
        '中专': 'college',
        '高中': 'high_school',
        '大专': 'college',
        '本科': 'bachelor',
        '硕士': 'master',
        '博士': 'doctor',
    }

    for key, value in education_map.items():
        if key in edu_str:
            return value

    return 'unlimited'


def standardize_experience(exp_str):
    """
    标准化工作经验
    """
    if not exp_str or pd.isna(exp_str):
        return '1-3'

    exp_str = str(exp_str).strip()

    experience_map = {
        '经验不限': 'unlimited',
        '不限': 'unlimited',
        '应届生': '0-1',
        '在校生': '0-1',
        '1年以下': '0-1',
        '1-3年': '1-3',
        '3-5年': '3-5',
        '5-10年': '5-10',
        '10年以上': '10+',
    }

    for key, value in experience_map.items():
        if key in exp_str:
            return value

    # 尝试提取数字
    match = re.search(r'(\d+)-?(\d+)?', exp_str)
    if match:
        start = int(match.group(1))
        if start <= 1:
            return '0-1'
        elif start <= 3:
            return '1-3'
        elif start <= 5:
            return '3-5'
        else:
            return '5-10'

    return '1-3'


def extract_skills(skills_str):
    """
    提取技能标签
    格式: "英语, 教育机构, 教育工作经验, 教师培训经验, 小学教育"
    """
    if not skills_str or pd.isna(skills_str):
        return []

    skills_str = str(skills_str).strip()

    # 按逗号分割
    skills = [s.strip() for s in skills_str.split(',') if s.strip()]

    # 过滤空字符串和太长的描述
    skills = [s for s in skills if 2 <= len(s) <= 20]

    # 去重
    skills = list(set(skills))

    return skills[:8]  # 最多8个


def clean_company_type(company_type):
    """清洗公司类型"""
    if not company_type or pd.isna(company_type):
        return '民营'

    company_type = str(company_type).strip()

    type_map = {
        '民营': '民营',
        '私营': '民营',
        '国企': '国企',
        '外资': '外资',
        '合资': '合资',
        '上市': '上市',
    }

    for key, value in type_map.items():
        if key in company_type:
            return value

    return company_type[:10] if len(company_type) > 10 else company_type


def clean_company_size(size_str):
    """清洗公司规模"""
    if not size_str or pd.isna(size_str):
        return '100-499'

    size_str = str(size_str).strip()

    # 标准化格式
    if '20人以下' in size_str or '少于20' in size_str:
        return '0-20'
    elif '20-99' in size_str or '20-50' in size_str or '50-99' in size_str:
        return '20-99'
    elif '100-499' in size_str or '100-299' in size_str or '300-499' in size_str:
        return '100-499'
    elif '500-999' in size_str:
        return '500-999'
    elif '1000' in size_str or '万人' in size_str:
        return '10000+'

    return '100-499'


# ==================== 数据处理主函数 ====================

def process_csv_data(file_path, limit=None):
    """处理CSV数据"""
    print(f"读取数据文件: {file_path}")

    # 读取CSV（中文编码）
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='gbk')

    print(f"总记录数: {len(df)}")

    if limit:
        df = df.head(limit)

    # 去除重复数据
    df = df.drop_duplicates(subset=['岗位名称', '企业'], keep='first')
    print(f"去重后记录数: {len(df)}")

    # 处理数据
    jobs_data = []
    skipped = 0

    for idx, row in df.iterrows():
        try:
            # 岗位名称
            title = row.get('岗位名称', '')
            if not title or pd.isna(title):
                skipped += 1
                continue

            # 企业名称
            company_name = row.get('企业', '未知公司')
            if pd.isna(company_name) or not company_name:
                company_name = '未知公司'
            company_name = str(company_name).strip()[:100]

            # 薪资
            salary_str = row.get('薪资', '')
            salary_min, salary_max = parse_salary(salary_str)

            # 验证薪资合理性
            if salary_min > salary_max:
                salary_min, salary_max = salary_max, salary_min
            if salary_min < 1000:
                salary_min = 5000
            if salary_max > 200000:
                salary_max = 50000

            # 工作地点
            location = row.get('工作地点', '')
            city = extract_city(location)

            # 工作经验
            experience = row.get('工作经验', '')
            exp_standard = standardize_experience(experience)

            # 学历要求
            education = row.get('学历要求', '')
            edu_standard = standardize_education(education)

            # 岗位需求（技能）
            skills_str = row.get('岗位需求', '')
            skills = extract_skills(skills_str)

            # 公司类型
            company_type = row.get('公司类型', '')
            company_type = clean_company_type(company_type)

            # 公司规模
            company_size = row.get('岗位需求人数', '')
            company_size = clean_company_size(company_size)

            # 企业服务/行业
            industry = row.get('企业服务', '')
            if pd.isna(industry):
                industry = '互联网'
            industry = str(industry).strip()[:50]

            jobs_data.append({
                'title': str(title).strip()[:200],
                'company_name': company_name,
                'location': city,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'education': edu_standard,
                'experience': exp_standard,
                'skills': skills,
                'company_type': company_type,
                'company_size': company_size,
                'industry': industry,
                'description': f"招聘{str(title).strip()}，工作地点：{city}",
                'requirements': f"学历要求：{education or '不限'}，经验要求：{experience or '不限'}",
            })

        except Exception as e:
            print(f"处理第{idx}行时出错: {e}")
            continue

    print(f"成功处理 {len(jobs_data)} 条职位数据，跳过 {skipped} 条无效数据")
    return jobs_data


def create_tags():
    """创建标签"""
    print("创建标签...")

    # 常见技能标签
    tech_skills = [
        'Python', 'Java', 'JavaScript', 'Vue.js', 'React', 'Angular',
        'Django', 'Flask', 'Spring', 'Node.js', 'TypeScript', 'Go',
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL',
        'Docker', 'Kubernetes', 'Linux', 'Git', 'AWS', 'Azure',
        'HTML', 'CSS', 'jQuery', 'Bootstrap', 'Webpack',
        '数据分析', '数据挖掘', '机器学习', '深度学习', '人工智能',
        'TensorFlow', 'PyTorch', 'Hadoop', 'Spark', 'Hive',
        'UI设计', 'UX设计', 'Photoshop', 'Sketch', 'Figma',
        '产品经理', '项目管理', '敏捷开发', 'Scrum',
        '测试', '自动化测试', '性能测试', '接口测试',
        '运维', 'DevOps', 'CI/CD', '监控', '自动化',
    ]

    for skill in tech_skills:
        JobTag.objects.get_or_create(
            name=skill,
            defaults={'category': 'skill', 'color': '#409EFF'}
        )

    # 福利标签
    benefits = ['五险一金', '年终奖', '带薪年假', '弹性工作', '节日福利',
                '定期体检', '股票期权', '加班补助', '交通补贴', '住房补贴',
                '免费三餐', '健身房', '双休', '周末双休', '绩效奖金']

    for benefit in benefits:
        JobTag.objects.get_or_create(
            name=benefit,
            defaults={'category': 'benefit', 'color': '#67C23A'}
        )

    print(f"创建了 {JobTag.objects.count()} 个标签")


def create_categories():
    """创建分类"""
    print("创建分类...")

    categories = [
        ('技术开发', None),
        ('后端开发', '技术开发'),
        ('前端开发', '技术开发'),
        ('移动开发', '技术开发'),
        ('数据开发', '技术开发'),
        ('人工智能', '技术开发'),
        ('测试运维', '技术开发'),
        ('产品设计', None),
        ('产品经理', '产品设计'),
        ('UI设计', '产品设计'),
        ('运营市场', None),
        ('运营', '运营市场'),
        ('市场', '运营市场'),
        ('销售', '运营市场'),
        ('职能支持', None),
        ('人事行政', '职能支持'),
        '财务会计',
        '客服支持',
    ]

    created = {}
    for item in categories:
        if isinstance(item, tuple):
            name, parent_name = item
            parent = created.get(parent_name) if parent_name else None
        else:
            name = item
            parent = None

        cat, _ = JobCategory.objects.get_or_create(
            name=name,
            defaults={'parent': parent}
        )
        created[name] = cat

    print(f"创建了 {JobCategory.objects.count()} 个分类")


def categorize_job(title):
    """根据职位标题判断分类"""
    title_lower = title.lower()

    if any(kw in title_lower for kw in ['python', 'java', '后端', '服务端', 'golang', 'go开发']):
        return '后端开发'
    elif any(kw in title_lower for kw in ['前端', 'vue', 'react', 'javascript', 'web开发']):
        return '前端开发'
    elif any(kw in title_lower for kw in ['ios', 'android', '移动', 'app']):
        return '移动开发'
    elif any(kw in title_lower for kw in ['数据', '大数据', 'etl', '数仓']):
        return '数据开发'
    elif any(kw in title_lower for kw in ['ai', '人工智能', '算法', '机器学习', '深度学习']):
        return '人工智能'
    elif any(kw in title_lower for kw in ['测试', 'qa', '质量']):
        return '测试运维'
    elif any(kw in title_lower for kw in ['运维', 'devops', 'sre', 'ops']):
        return '测试运维'
    elif any(kw in title_lower for kw in ['产品', 'pm']):
        return '产品经理'
    elif any(kw in title_lower for kw in ['ui', '设计', 'ux', '视觉']):
        return 'UI设计'
    elif any(kw in title_lower for kw in ['运营', '新媒体', '内容']):
        return '运营'
    elif any(kw in title_lower for kw in ['销售', 'bd', '商务', '客户']):
        return '销售'
    elif any(kw in title_lower for kw in ['人事', 'hr', '行政', '招聘']):
        return '人事行政'
    elif any(kw in title_lower for kw in ['财务', '会计', '出纳']):
        return '财务会计'
    elif any(kw in title_lower for kw in ['客服', '售后', '支持']):
        return '客服支持'
    else:
        return '技术开发'


def import_jobs_to_db(jobs_data):
    """导入职位到数据库"""
    print("导入职位到数据库...")

    tags = {t.name: t for t in JobTag.objects.all()}
    categories = {c.name: c for c in JobCategory.objects.all()}
    companies = {}

    created_count = 0
    total = len(jobs_data)

    for i, job_data in enumerate(jobs_data):
        try:
            # 创建或获取公司
            company_name = job_data['company_name']
            if company_name not in companies:
                company, _ = Company.objects.get_or_create(
                    name=company_name,
                    defaults={
                        'size': job_data.get('company_size', '100-499'),
                        'industry': job_data.get('industry', '互联网'),
                        'financing_stage': 'b' if job_data.get('company_type') == '民营' else 'unfinanced',
                    }
                )
                companies[company_name] = company
            else:
                company = companies[company_name]

            # 确定分类
            cat_name = categorize_job(job_data['title'])
            category = categories.get(cat_name)

            # 创建职位
            job = Job.objects.create(
                title=job_data['title'],
                company=company,
                salary_min=job_data['salary_min'],
                salary_max=job_data['salary_max'],
                location=job_data['location'],
                education_required=job_data['education'],
                experience_required=job_data['experience'],
                description=job_data.get('description', ''),
                requirements=job_data.get('requirements', ''),
                category=category,
                is_hot=random.random() < 0.1,
                is_urgent=random.random() < 0.05,
                view_count=random.randint(100, 5000),
                apply_count=random.randint(0, 300),
                favorite_count=random.randint(0, 150),
            )

            # 添加技能标签
            for skill in job_data['skills']:
                # 如果标签不存在，创建新的
                if skill not in tags:
                    tag, _ = JobTag.objects.get_or_create(
                        name=skill,
                        defaults={'category': 'skill', 'color': '#409EFF'}
                    )
                    tags[skill] = tag
                job.tags.add(tags[skill])

            # 添加福利标签
            for benefit in ['五险一金', '年终奖', '带薪年假']:
                if benefit in tags:
                    job.tags.add(tags[benefit])

            created_count += 1

            if (i + 1) % 500 == 0:
                print(f"进度: {i+1}/{total} ({(i+1)*100//total}%)")

        except Exception as e:
            print(f"导入职位失败 ({job_data.get('title', 'unknown')}): {e}")
            continue

    print(f"成功导入 {created_count} 条职位")
    return created_count


def create_test_users(n_users=100):
    """创建测试用户"""
    print(f"创建 {n_users} 个测试用户...")

    jobs = list(Job.objects.all())
    if not jobs:
        print("没有职位数据")
        return

    skill_list = ['Python', 'Java', 'JavaScript', 'Vue.js', 'React', 'MySQL', 'Redis', 'Docker', 'Git']
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '天津', '苏州']

    created = 0
    for i in range(n_users):
        username = f"test{i+1}"
        try:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password='123456',
                    email=f'{username}@test.com'
                )
                UserProfile.objects.create(
                    user=user,
                    name=f"用户{i+1}",
                    gender=random.choice(['male', 'female']),
                    age=random.randint(22, 38),
                    education=random.choice(['college', 'bachelor', 'master']),
                    school=random.choice(['清华大学', '北京大学', '浙江大学', '复旦大学', '上海交通大学', '其他高校']),
                    expected_position=random.choice(['开发工程师', '产品经理', '数据分析师', '设计师']),
                    expected_salary_min=random.choice([10, 15, 20]) * 1000,
                    expected_salary_max=random.choice([20, 25, 30, 35]) * 1000,
                    expected_cities=random.sample(cities, 2),
                    skills=[{'name': s, 'level': random.randint(2, 5)} for s in random.sample(skill_list, 4)],
                    work_experience=random.randint(0, 8),
                )
                created += 1
        except Exception as e:
            continue

    print(f"创建了 {created} 个新用户")


def create_interactions():
    """创建交互数据"""
    print("创建交互数据...")

    users = list(User.objects.filter(username__startswith='test'))
    jobs = list(Job.objects.all())

    if not users or not jobs:
        print("缺少用户或职位数据")
        return

    created = 0
    for _ in range(len(users) * 15):
        try:
            user = random.choice(users)
            job = random.choice(jobs)
            interaction_type = random.choices(
                ['view', 'favorite', 'apply', 'rating'],
                weights=[0.5, 0.2, 0.1, 0.2]
            )[0]
            rating = random.choices([3, 4, 5], weights=[0.2, 0.4, 0.4])[0] if interaction_type == 'rating' else None

            UserJobInteraction.objects.get_or_create(
                user=user,
                job=job,
                interaction_type=interaction_type,
                defaults={'rating': rating}
            )
            created += 1
        except Exception:
            continue

    print(f"创建了 {created} 条交互记录")


def import_chinese_jobs(file_path, limit=None, create_users=True):
    """
    完整的中文数据导入流程

    Args:
        file_path: CSV文件路径
        limit: 导入职位数量限制
        create_users: 是否创建测试用户
    """
    print("=" * 60)
    print("开始导入中文职位数据")
    print("=" * 60)

    # 1. 创建分类和标签
    create_categories()
    create_tags()

    # 2. 处理CSV数据
    jobs_data = process_csv_data(file_path, limit=limit)

    # 3. 导入数据库
    import_jobs_to_db(jobs_data)

    # 4. 创建用户和交互
    if create_users:
        create_test_users(100)
        create_interactions()

    # 5. 统计结果
    print("=" * 60)
    print("数据导入完成!")
    print(f"职位数: {Job.objects.count()}")
    print(f"公司数: {Company.objects.count()}")
    print(f"用户数: {User.objects.count()}")
    print(f"交互记录数: {UserJobInteraction.objects.count()}")
    print("=" * 60)
