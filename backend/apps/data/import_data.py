"""
数据处理程序 - 处理开源职位数据集
将英文职位数据转换为中文格式并导入系统
"""

import pandas as pd
import re
import random
from django.contrib.auth import get_user_model

from apps.jobs.models import JobCategory, JobTag, Company, Job
from apps.users.models import UserProfile
from apps.recommendations.models import UserJobInteraction

User = get_user_model()

# 翻译映射（同上，简化版）
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
    'UI Designer': 'UI设计师',
    'UX Designer': 'UX设计师',
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
    'Customer Service': '客服专员',
    'Technical Support': '技术支持',
    'Java Developer': 'Java开发工程师',
    'Python Developer': 'Python开发工程师',
    'PHP Developer': 'PHP开发工程师',
    'Mobile Developer': '移动开发工程师',
    'iOS Developer': 'iOS开发工程师',
    'Android Developer': 'Android开发工程师',
    'Security Engineer': '安全工程师',
    'IT Manager': 'IT经理',
    'Technical Lead': '技术负责人',
    'Architect': '架构师',
    'Director': '总监',
}

CITY_TRANSLATIONS = {
    'Yerevan': '北京',
    'Armenia': '北京',
    'New York': '上海',
    'San Francisco': '深圳',
    'Los Angeles': '广州',
    'Seattle': '杭州',
    'Boston': '南京',
    'Chicago': '成都',
    'Remote': '远程',
}

SKILL_KEYWORDS = {
    'python': 'Python', 'java': 'Java', 'javascript': 'JavaScript',
    'js': 'JavaScript', 'typescript': 'TypeScript', 'c++': 'C++',
    'c#': 'C#', 'php': 'PHP', 'ruby': 'Ruby', 'go': 'Go',
    'django': 'Django', 'flask': 'Flask', 'spring': 'Spring',
    'react': 'React', 'vue': 'Vue.js', 'angular': 'Angular',
    'node': 'Node.js', 'sql': 'SQL', 'mysql': 'MySQL',
    'postgresql': 'PostgreSQL', 'mongodb': 'MongoDB', 'redis': 'Redis',
    'aws': 'AWS', 'azure': 'Azure', 'docker': 'Docker',
    'kubernetes': 'Kubernetes', 'linux': 'Linux', 'git': 'Git',
    'machine learning': '机器学习', 'deep learning': '深度学习',
    'data analysis': '数据分析', 'excel': 'Excel',
    'english': '英语', 'communication': '沟通能力',
}


def translate_title(title):
    """翻译职位标题"""
    if not title:
        return '技术人员'
    title_lower = title.lower()
    for eng, chn in TITLE_TRANSLATIONS.items():
        if eng.lower() in title_lower:
            return chn
    if 'developer' in title_lower or 'engineer' in title_lower:
        return '开发工程师'
    if 'manager' in title_lower:
        return '经理'
    if 'analyst' in title_lower:
        return '分析师'
    if 'designer' in title_lower:
        return '设计师'
    return '技术人员'


def translate_location(location):
    """翻译地点"""
    if not location:
        return random.choice(['北京', '上海', '广州', '深圳', '杭州'])
    for eng, chn in CITY_TRANSLATIONS.items():
        if eng.lower() in location.lower():
            return chn
    return random.choice(['北京', '上海', '广州', '深圳', '杭州'])


def extract_salary(text):
    """提取薪资"""
    if not text:
        base = random.choice([10, 15, 20, 25, 30])
        return base * 1000, (base + random.randint(5, 15)) * 1000
    numbers = re.findall(r'\$?(\d+(?:,\d+)*)', str(text))
    if not numbers:
        base = random.choice([10, 15, 20, 25, 30])
        return base * 1000, (base + random.randint(5, 15)) * 1000
    nums = [int(n.replace(',', '')) for n in numbers]
    if len(nums) >= 2:
        min_sal = min(nums[:2]) * 100
        max_sal = max(nums[:2]) * 100
        return min(max(min_sal, 8000), 50000), min(max(max_sal, 10000), 80000)
    base = nums[0]
    if base > 10000:
        base = base // 12
    return base, int(base * 1.3)


def extract_skills(text):
    """提取技能"""
    if not text:
        return []
    text_lower = text.lower()
    skills = []
    for keyword, skill_name in SKILL_KEYWORDS.items():
        if keyword in text_lower and skill_name not in skills:
            skills.append(skill_name)
    return skills[:8]


def extract_education(text):
    """提取学历"""
    if not text:
        return 'bachelor'
    text_lower = text.lower()
    if 'master' in text_lower or 'mba' in text_lower:
        return 'master'
    if 'phd' in text_lower or 'doctor' in text_lower:
        return 'doctor'
    if 'bachelor' in text_lower:
        return 'bachelor'
    return 'bachelor'


def extract_experience(text):
    """提取经验"""
    if not text:
        return '1-3'
    years = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text.lower())
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
    return '1-3'


def clean_text(text):
    """清理文本"""
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', str(text))
    return text.strip()[:2000]  # 限制长度


def create_categories_and_tags():
    """创建分类和标签"""
    categories = [
        ('技术开发', None), ('后端开发', '技术开发'), ('前端开发', '技术开发'),
        ('数据开发', '技术开发'), ('人工智能', '技术开发'),
        ('产品设计', None), ('产品经理', '产品设计'), ('UI设计', '产品设计'),
        ('运营市场', None), ('财务行政', None),
    ]
    created_cats = {}
    for name, parent_name in categories:
        parent = created_cats.get(parent_name) if parent_name else None
        cat, _ = JobCategory.objects.get_or_create(name=name, defaults={'parent': parent})
        created_cats[name] = cat

    for skill in set(SKILL_KEYWORDS.values()):
        JobTag.objects.get_or_create(name=skill, defaults={'category': 'skill', 'color': '#409EFF'})

    for benefit in ['五险一金', '年终奖', '带薪年假', '弹性工作', '节日福利']:
        JobTag.objects.get_or_create(name=benefit, defaults={'category': 'benefit', 'color': '#67C23A'})


def process_csv_data(file_path, limit=None):
    """处理CSV数据"""
    df = pd.read_csv(file_path, low_memory=False)
    if limit:
        df = df.head(limit)

    jobs_data = []
    for _, row in df.iterrows():
        try:
            title = row.get('Title', '')
            if not title or pd.isna(title):
                continue

            company_name = row.get('Company', '科技公司')
            if pd.isna(company_name):
                company_name = random.choice(['科技公司', '互联网公司', '创新企业'])

            location = row.get('Location', '')
            description = clean_text(row.get('JobDescription', ''))
            requirements = clean_text(row.get('JobRequirment', '') or row.get('RequiredQual', ''))
            all_text = f"{title} {description} {requirements}"

            salary_text = row.get('Salary', '')
            salary_min, salary_max = extract_salary(salary_text)

            jobs_data.append({
                'title': translate_title(title),
                'company_name': company_name,
                'location': translate_location(location),
                'description': description or f"我们正在寻找一位优秀的{translate_title(title)}加入团队...",
                'requirements': requirements or "1. 有相关工作经验\n2. 良好的沟通能力",
                'skills': extract_skills(all_text),
                'salary_min': salary_min,
                'salary_max': salary_max,
                'education': extract_education(requirements),
                'experience': extract_experience(requirements),
                'is_it': 'IT' in str(title).upper() or any(s in str(title).lower() for s in ['developer', 'engineer', 'data']),
            })
        except Exception:
            continue

    return jobs_data


def import_jobs_to_db(jobs_data):
    """导入职位到数据库"""
    tech_cat, _ = JobCategory.objects.get_or_create(name='技术开发')
    product_cat, _ = JobCategory.objects.get_or_create(name='产品设计')
    tags = {t.name: t for t in JobTag.objects.all()}
    companies = {}

    for job_data in jobs_data:
        try:
            company_name = job_data['company_name']
            if company_name not in companies:
                company, _ = Company.objects.get_or_create(
                    name=company_name,
                    defaults={
                        'size': random.choice(['20-99', '100-499', '500-999']),
                        'industry': '互联网' if job_data['is_it'] else '其他',
                        'financing_stage': random.choice(['a', 'b', 'c', 'listed']),
                    }
                )
                companies[company_name] = company
            else:
                company = companies[company_name]

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
                category=tech_cat if job_data['is_it'] else product_cat,
                is_hot=random.random() < 0.15,
                view_count=random.randint(50, 2000),
                apply_count=random.randint(0, 200),
                favorite_count=random.randint(0, 100),
            )

            for skill in job_data['skills']:
                if skill in tags:
                    job.tags.add(tags[skill])
            for benefit in ['五险一金', '年终奖', '带薪年假']:
                if benefit in tags:
                    job.tags.add(tags[benefit])
        except Exception:
            continue


def create_users_and_interactions(n_users=200):
    """创建用户和交互数据"""
    jobs = list(Job.objects.all())
    if not jobs:
        return

    skill_list = list(set(SKILL_KEYWORDS.values()))
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉']

    for i in range(n_users):
        try:
            user, created = User.objects.get_or_create(
                username=f"user{i+1}",
                defaults={'email': f"user{i+1}@example.com"}
            )
            if created:
                user.set_password('123456')
                user.save()
                UserProfile.objects.create(
                    user=user,
                    name=f"用户{i+1}",
                    gender=random.choice(['male', 'female']),
                    age=random.randint(22, 38),
                    education=random.choice(['college', 'bachelor', 'master']),
                    school=random.choice(['清华大学', '北京大学', '浙江大学', '其他高校']),
                    expected_position=random.choice(['开发工程师', '产品经理', '数据分析师']),
                    expected_salary_min=random.choice([10, 15, 20]) * 1000,
                    expected_salary_max=random.choice([20, 25, 30]) * 1000,
                    expected_cities=random.sample(cities, 2),
                    skills=[{'name': s, 'level': random.randint(2, 5)} for s in random.sample(skill_list, 4)],
                    work_experience=random.randint(0, 8),
                )
        except Exception:
            continue

    users = list(User.objects.all())
    for _ in range(n_users * 15):
        try:
            user = random.choice(users)
            job = random.choice(jobs)
            interaction_type = random.choices(['view', 'favorite', 'apply', 'rating'], weights=[0.5, 0.2, 0.1, 0.2])[0]
            rating = random.choice([3, 4, 5]) if interaction_type == 'rating' else None
            UserJobInteraction.objects.get_or_create(
                user=user, job=job, interaction_type=interaction_type,
                defaults={'rating': rating}
            )
        except Exception:
            continue


def import_data(file_path, limit=2000, create_users=True):
    """完整导入流程"""
    print("创建分类和标签...")
    create_categories_and_tags()

    print(f"处理CSV数据 (限制: {limit}条)...")
    jobs_data = process_csv_data(file_path, limit=limit)
    print(f"成功处理 {len(jobs_data)} 条职位")

    print("导入职位到数据库...")
    import_jobs_to_db(jobs_data)

    if create_users:
        print("创建用户和交互数据...")
        create_users_and_interactions(n_users=300)

    print(f"\n导入完成!")
    print(f"职位数: {Job.objects.count()}")
    print(f"用户数: {User.objects.count()}")
    print(f"交互数: {UserJobInteraction.objects.count()}")
