"""
数据处理程序 - 处理开源职位数据集
将英文职位数据转换为中文格式并导入系统

数据来源: data job posts.csv
处理流程:
    1. 读取CSV数据
    2. 清洗和转换数据
    3. 翻译关键字段为中文
    4. 提取技能标签
    5. 标准化薪资格式
    6. 导入数据库

运行方式:
    python manage.py shell
    >>> from scripts.import_job_data import import_data
    >>> import_data(r"C:\Users\qingd\Downloads\data job posts.csv\data job posts.csv")

作者: 刘怀仁
"""

import pandas as pd
import re
import random
from datetime import datetime
from django.contrib.auth import get_user_model

from apps.jobs.models import JobCategory, JobTag, Company, Job
from apps.users.models import UserProfile
from apps.recommendations.models import UserJobInteraction

User = get_user_model()


# ==================== 翻译映射 ====================

# 职位标题翻译
TITLE_TRANSLATIONS = {
    'Chief Financial Officer': '财务总监',
    'Financial Analyst': '财务分析师',
    'Accountant': '会计',
    'Software Developer': '软件开发工程师',
    'Software Engineer': '软件工程师',
    'Web Developer': 'Web开发工程师',
    'Front-end Developer': '前端开发工程师',
    'Back-end Developer': '后端开发工程师',
    'Full Stack Developer': '全栈开发工程师',
    'Data Analyst': '数据分析师',
    'Data Scientist': '数据科学家',
    'Project Manager': '项目经理',
    'Product Manager': '产品经理',
    'Marketing Manager': '市场经理',
    'Sales Manager': '销售经理',
    'HR Manager': '人力资源经理',
    'Graphic Designer': '平面设计师',
    'UI/UX Designer': 'UI/UX设计师',
    'Network Administrator': '网络管理员',
    'System Administrator': '系统管理员',
    'Database Administrator': '数据库管理员',
    'DevOps Engineer': '运维工程师',
    'QA Engineer': '测试工程师',
    'Business Analyst': '业务分析师',
    'Consultant': '顾问',
    'Administrative Assistant': '行政助理',
    'Executive Assistant': '执行助理',
    'Office Manager': '办公室经理',
    'Receptionist': '前台接待',
    'Customer Service': '客服专员',
    'Technical Support': '技术支持',
    'Java Developer': 'Java开发工程师',
    'Python Developer': 'Python开发工程师',
    '.NET Developer': '.NET开发工程师',
    'PHP Developer': 'PHP开发工程师',
    'Mobile Developer': '移动开发工程师',
    'iOS Developer': 'iOS开发工程师',
    'Android Developer': 'Android开发工程师',
    'Security Engineer': '安全工程师',
    'IT Manager': 'IT经理',
    'Technical Lead': '技术负责人',
    'Architect': '架构师',
    'Director': '总监',
    'VP': '副总裁',
    'CEO': '首席执行官',
    'CFO': '首席财务官',
    'CTO': '首席技术官',
}

# 城市翻译
CITY_TRANSLATIONS = {
    'Yerevan': '埃里温',
    'Armenia': '亚美尼亚',
    'New York': '纽约',
    'San Francisco': '旧金山',
    'Los Angeles': '洛杉矶',
    'Seattle': '西雅图',
    'Boston': '波士顿',
    'Chicago': '芝加哥',
    'Austin': '奥斯汀',
    'Denver': '丹佛',
    'London': '伦敦',
    'Berlin': '柏林',
    'Paris': '巴黎',
    'Tokyo': '东京',
    'Singapore': '新加坡',
    'Sydney': '悉尼',
    'Toronto': '多伦多',
    'Vancouver': '温哥华',
    'Beijing': '北京',
    'Shanghai': '上海',
    'Shenzhen': '深圳',
    'Guangzhou': '广州',
    'Hangzhou': '杭州',
    'Remote': '远程',
}

# 学历翻译
EDUCATION_MAP = {
    'Bachelor': 'bachelor',
    "Bachelor's": 'bachelor',
    'Master': 'master',
    "Master's": 'master',
    'MBA': 'master',
    'PhD': 'doctor',
    'Doctorate': 'doctor',
    'High School': 'high_school',
    'College': 'college',
    'Associate': 'college',
}

# 经验翻译
EXPERIENCE_MAP = {
    'Entry level': '0-1',
    'Junior': '0-1',
    'Mid': '1-3',
    'Mid-Senior': '3-5',
    'Senior': '5-10',
    'Lead': '5-10',
    'Manager': '5-10',
    'Director': '10+',
    'Executive': '10+',
}

# 技能关键词映射
SKILL_KEYWORDS = {
    # 编程语言
    'python': 'Python',
    'java': 'Java',
    'javascript': 'JavaScript',
    'js': 'JavaScript',
    'typescript': 'TypeScript',
    'c++': 'C++',
    'c#': 'C#',
    'php': 'PHP',
    'ruby': 'Ruby',
    'go': 'Go',
    'rust': 'Rust',
    'swift': 'Swift',
    'kotlin': 'Kotlin',
    'scala': 'Scala',
    'r': 'R',
    'matlab': 'MATLAB',

    # 框架和库
    'django': 'Django',
    'flask': 'Flask',
    'spring': 'Spring',
    'react': 'React',
    'vue': 'Vue.js',
    'angular': 'Angular',
    'node': 'Node.js',
    'jquery': 'jQuery',
    'express': 'Express',

    # 数据库
    'sql': 'SQL',
    'mysql': 'MySQL',
    'postgresql': 'PostgreSQL',
    'mongodb': 'MongoDB',
    'redis': 'Redis',
    'oracle': 'Oracle',
    'elasticsearch': 'Elasticsearch',

    # 云和DevOps
    'aws': 'AWS',
    'azure': 'Azure',
    'docker': 'Docker',
    'kubernetes': 'Kubernetes',
    'linux': 'Linux',
    'git': 'Git',
    'jenkins': 'Jenkins',
    'ci/cd': 'CI/CD',

    # 数据和AI
    'machine learning': '机器学习',
    'deep learning': '深度学习',
    'tensorflow': 'TensorFlow',
    'pytorch': 'PyTorch',
    'data analysis': '数据分析',
    'big data': '大数据',
    'spark': 'Spark',
    'hadoop': 'Hadoop',

    # 其他
    'excel': 'Excel',
    'powerpoint': 'PPT',
    'word': 'Word',
    'english': '英语',
    'chinese': '中文',
    'communication': '沟通能力',
    'leadership': '领导力',
    'teamwork': '团队协作',
    'project management': '项目管理',
}


def translate_title(title):
    """翻译职位标题"""
    if not title:
        return '技术人员'

    title_lower = title.lower()

    # 精确匹配
    for eng, chn in TITLE_TRANSLATIONS.items():
        if eng.lower() in title_lower:
            return chn

    # 关键词匹配
    if 'developer' in title_lower or 'engineer' in title_lower:
        if 'senior' in title_lower or 'lead' in title_lower:
            return '高级开发工程师'
        return '开发工程师'
    if 'manager' in title_lower:
        return '经理'
    if 'analyst' in title_lower:
        return '分析师'
    if 'designer' in title_lower:
        return '设计师'
    if 'assistant' in title_lower:
        return '助理'

    return '技术人员'


def translate_location(location):
    """翻译地点"""
    if not location:
        return random.choice(['北京', '上海', '广州', '深圳', '杭州'])

    for eng, chn in CITY_TRANSLATIONS.items():
        if eng.lower() in location.lower():
            return chn

    # 如果是国外地点，随机返回一个中国城市
    return random.choice(['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉'])


def extract_salary(text):
    """从文本中提取薪资信息"""
    if not text:
        return None, None

    # 查找数字模式
    numbers = re.findall(r'\$?(\d+(?:,\d+)*)', str(text))

    if not numbers:
        # 默认薪资
        base = random.choice([10, 15, 20, 25, 30])
        return base * 1000, (base + random.randint(5, 15)) * 1000

    nums = [int(n.replace(',', '')) for n in numbers]

    if len(nums) >= 2:
        # 如果有两个数字，作为范围
        min_sal = min(nums[:2]) * 100  # 假设是年薪（万），转换为月薪
        max_sal = max(nums[:2]) * 100
        return min(max(min_sal, 8000), 50000), min(max(max_sal, 10000), 80000)

    # 单个数字
    base = nums[0]
    if base > 10000:  # 可能是年薪
        base = base // 12
    return base, int(base * 1.3)


def extract_skills(text):
    """从文本中提取技能标签"""
    if not text:
        return []

    text_lower = text.lower()
    skills = []

    for keyword, skill_name in SKILL_KEYWORDS.items():
        if keyword in text_lower and skill_name not in skills:
            skills.append(skill_name)

    # 最多返回8个技能
    return skills[:8]


def extract_education(text):
    """从文本中提取学历要求"""
    if not text:
        return 'bachelor'

    text_lower = text.lower()

    for eng, chn in EDUCATION_MAP.items():
        if eng.lower() in text_lower:
            return chn

    return 'bachelor'


def extract_experience(text):
    """从文本中提取经验要求"""
    if not text:
        return '1-3'

    text_lower = text.lower()

    # 查找年数
    years = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text_lower)
    if years:
        y = int(years[0])
        if y <= 1:
            return '0-1'
        elif y <= 3:
            return '1-3'
        elif y <= 5:
            return '3-5'
        else:
            return '5-10'

    for eng, chn in EXPERIENCE_MAP.items():
        if eng.lower() in text_lower:
            return chn

    return '1-3'


def clean_text(text):
    """清理文本"""
    if not text:
        return ''

    # 移除多余空白
    text = re.sub(r'\s+', ' ', str(text))
    # 移除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:\-\(\)]', '', text)
    return text.strip()


def create_categories_and_tags():
    """创建职位分类和标签"""
    print("创建职位分类和标签...")

    # 创建分类
    categories = [
        ('技术开发', None),
        ('后端开发', '技术开发'),
        ('前端开发', '技术开发'),
        ('移动开发', '技术开发'),
        ('数据开发', '技术开发'),
        ('人工智能', '技术开发'),
        ('产品设计', None),
        ('产品经理', '产品设计'),
        ('UI/UX设计', '产品设计'),
        ('运营市场', None),
        ('财务行政', None),
    ]

    created_categories = {}
    for name, parent_name in categories:
        parent = created_categories.get(parent_name) if parent_name else None
        cat, _ = JobCategory.objects.get_or_create(
            name=name,
            defaults={'parent': parent}
        )
        created_categories[name] = cat

    # 创建技能标签
    skill_tags = set()
    for skill in SKILL_KEYWORDS.values():
        skill_tags.add(skill)

    for skill in skill_tags:
        JobTag.objects.get_or_create(
            name=skill,
            defaults={'category': 'skill', 'color': '#409EFF'}
        )

    # 福利标签
    benefits = ['五险一金', '年终奖', '带薪年假', '弹性工作', '节日福利', '定期体检']
    for benefit in benefits:
        JobTag.objects.get_or_create(
            name=benefit,
            defaults={'category': 'benefit', 'color': '#67C23A'}
        )

    print(f"创建了 {JobCategory.objects.count()} 个分类")
    print(f"创建了 {JobTag.objects.count()} 个标签")


def process_csv_data(file_path, limit=None):
    """处理CSV数据"""
    print(f"读取数据文件: {file_path}")

    # 读取CSV
    df = pd.read_csv(file_path, low_memory=False)
    print(f"总记录数: {len(df)}")

    if limit:
        df = df.head(limit)

    # 处理数据
    jobs_data = []

    for idx, row in df.iterrows():
        try:
            # 提取标题
            title = row.get('Title', '')
            if not title or pd.isna(title):
                continue

            # 翻译标题
            cn_title = translate_title(title)

            # 公司名称
            company_name = row.get('Company', '未知公司')
            if pd.isna(company_name):
                company_name = random.choice(['科技公司', '互联网公司', '创新企业'])

            # 地点
            location = row.get('Location', '')
            cn_location = translate_location(location)

            # 职位描述和要求
            description = clean_text(row.get('JobDescription', ''))
            requirements = clean_text(row.get('JobRequirment', '') or row.get('RequiredQual', ''))

            # 提取技能
            all_text = f"{title} {description} {requirements}"
            skills = extract_skills(all_text)

            # 薪资
            salary_text = row.get('Salary', '')
            salary_min, salary_max = extract_salary(salary_text)

            # 学历和经验
            education = extract_education(requirements)
            experience = extract_experience(requirements)

            # 判断是否IT职位
            is_it = row.get('IT', False)
            if pd.isna(is_it):
                is_it = 'IT' in str(title).upper() or any(s in str(title).lower() for s in ['developer', 'engineer', 'data'])

            jobs_data.append({
                'title': cn_title,
                'original_title': title,
                'company_name': company_name,
                'location': cn_location,
                'description': description or f"我们正在寻找一位优秀的{cn_title}加入我们的团队...",
                'requirements': requirements or "1. 有相关工作经验\n2. 良好的沟通能力\n3. 团队合作精神",
                'skills': skills,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'education': education,
                'experience': experience,
                'is_it': bool(is_it),
            })

        except Exception as e:
            print(f"处理第{idx}行时出错: {e}")
            continue

    print(f"成功处理 {len(jobs_data)} 条职位数据")
    return jobs_data


def import_jobs_to_db(jobs_data):
    """将职位数据导入数据库"""
    print("导入职位数据到数据库...")

    # 获取或创建分类
    tech_cat, _ = JobCategory.objects.get_or_create(name='技术开发')
    product_cat, _ = JobCategory.objects.get_or_create(name='产品设计')

    # 获取所有标签
    tags = {t.name: t for t in JobTag.objects.all()}

    created_companies = {}
    created_count = 0

    for job_data in jobs_data:
        try:
            # 创建或获取公司
            company_name = job_data['company_name']
            if company_name not in created_companies:
                company, _ = Company.objects.get_or_create(
                    name=company_name,
                    defaults={
                        'size': random.choice(['20-99', '100-499', '100-499', '500-999']),
                        'industry': '互联网' if job_data['is_it'] else '其他',
                        'financing_stage': random.choice(['a', 'b', 'c', 'listed']),
                    }
                )
                created_companies[company_name] = company
            else:
                company = created_companies[company_name]

            # 选择分类
            category = tech_cat if job_data['is_it'] else product_cat

            # 创建职位
            job = Job.objects.create(
                title=job_data['title'],
                company=company,
                salary_min=job_data['salary_min'],
                salary_max=job_data['salary_max'],
                location=job_data['location'],
                education_required=job_data['education'],
                experience_required=job_data['experience'],
                description=job_data['description'],
                requirements=job_data['requirements'],
                category=category,
                is_hot=random.random() < 0.15,
                is_urgent=random.random() < 0.1,
                view_count=random.randint(50, 2000),
                apply_count=random.randint(0, 200),
                favorite_count=random.randint(0, 100),
            )

            # 添加技能标签
            for skill in job_data['skills']:
                if skill in tags:
                    job.tags.add(tags[skill])

            # 添加福利标签
            benefit_tags = ['五险一金', '年终奖', '带薪年假']
            for benefit in benefit_tags:
                if benefit in tags:
                    job.tags.add(tags[benefit])

            created_count += 1

            if created_count % 500 == 0:
                print(f"已导入 {created_count} 条职位...")

        except Exception as e:
            print(f"导入职位失败: {e}")
            continue

    print(f"成功导入 {created_count} 条职位")
    return created_count


def create_users_and_interactions(n_users=200):
    """创建用户和交互数据"""
    print(f"创建 {n_users} 个用户...")

    jobs = list(Job.objects.all())
    if not jobs:
        print("没有职位数据，请先导入职位")
        return

    skill_list = ['Python', 'Java', 'JavaScript', 'Vue.js', 'React', 'Django', 'MySQL', 'Redis', 'Docker', 'Git']
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉']
    positions = ['开发工程师', '产品经理', '数据分析师', '设计师', '测试工程师']

    # 创建用户
    users_created = 0
    for i in range(n_users):
        username = f"user{i+1}"
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f"{username}@example.com"}
            )

            if created:
                user.set_password('123456')
                user.save()

                # 创建用户画像
                UserProfile.objects.create(
                    user=user,
                    name=f"用户{i+1}",
                    gender=random.choice(['male', 'female']),
                    age=random.randint(22, 38),
                    education=random.choice(['college', 'bachelor', 'bachelor', 'master']),
                    school=random.choice(['清华大学', '北京大学', '浙江大学', '复旦大学', '其他高校']),
                    major=random.choice(['计算机科学', '软件工程', '数据科学', '信息管理']),
                    expected_position=random.choice(positions),
                    expected_salary_min=random.choice([10, 15, 20, 25]) * 1000,
                    expected_salary_max=random.choice([20, 25, 30, 40]) * 1000,
                    expected_cities=random.sample(cities, random.randint(1, 3)),
                    job_type='fulltime',
                    skills=[{'name': s, 'level': random.randint(2, 5)} for s in random.sample(skill_list, random.randint(3, 6))],
                    work_experience=random.randint(0, 10),
                )
                users_created += 1

        except Exception as e:
            print(f"创建用户 {username} 失败: {e}")
            continue

    print(f"创建了 {users_created} 个用户")

    # 创建交互数据
    print("创建交互数据...")
    users = list(User.objects.all())
    interactions_created = 0

    for _ in range(n_users * 20):  # 每个用户平均20条交互
        user = random.choice(users)
        job = random.choice(jobs)
        interaction_type = random.choices(
            ['view', 'favorite', 'apply', 'rating'],
            weights=[0.5, 0.2, 0.1, 0.2]
        )[0]

        rating = None
        if interaction_type == 'rating':
            rating = random.choices([3, 4, 5], weights=[0.2, 0.4, 0.4])[0]

        try:
            UserJobInteraction.objects.get_or_create(
                user=user,
                job=job,
                interaction_type=interaction_type,
                defaults={'rating': rating}
            )
            interactions_created += 1
        except:
            continue

    print(f"创建了 {interactions_created} 条交互记录")


def import_data(file_path, limit=2000, create_users=True):
    """
    完整的数据导入流程

    Args:
        file_path: CSV文件路径
        limit: 导入职位数量限制
        create_users: 是否创建测试用户
    """
    print("=" * 60)
    print("开始导入数据")
    print("=" * 60)

    # 1. 创建分类和标签
    create_categories_and_tags()

    # 2. 处理CSV数据
    jobs_data = process_csv_data(file_path, limit=limit)

    # 3. 导入数据库
    import_jobs_to_db(jobs_data)

    # 4. 创建用户和交互
    if create_users:
        create_users_and_interactions(n_users=300)

    # 5. 统计结果
    print("=" * 60)
    print("数据导入完成!")
    print(f"职位数: {Job.objects.count()}")
    print(f"公司数: {Company.objects.count()}")
    print(f"用户数: {User.objects.count()}")
    print(f"交互记录数: {UserJobInteraction.objects.count()}")
    print("=" * 60)


if __name__ == '__main__':
    # 直接运行时的入口
    import sys
    if len(sys.argv) > 1:
        import_data(sys.argv[1])
    else:
        print("请提供CSV文件路径")
