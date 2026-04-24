#!/usr/bin/env python3
"""
TalentAI Pro 数据库初始化与数据种子脚本
"""
import sys
import os
import sqlite3
from datetime import datetime, timedelta
import hashlib
import json

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'talentai.db')

def get_password_hash(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 用户表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'consultant',
            full_name TEXT NOT NULL,
            phone TEXT,
            avatar TEXT,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')

    # 候选人表
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            gender TEXT,
            age INTEGER,
            location TEXT,
            current_company TEXT,
            current_title TEXT,
            current_salary TEXT,
            expected_salary TEXT,
            education TEXT,
            work_years INTEGER,
            skills TEXT,
            resume_path TEXT,
            source TEXT,
            status TEXT DEFAULT 'new',
            consultant_id INTEGER,
            last_contact DATETIME,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consultant_id) REFERENCES users(id)
        )
    ''')

    # 客户公司表
    c.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT,
            size TEXT,
            stage TEXT,
            description TEXT,
            website TEXT,
            address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 职位表
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company_id INTEGER NOT NULL,
            department TEXT,
            location TEXT,
            salary_min INTEGER,
            salary_max INTEGER,
            description TEXT,
            requirements TEXT,
            skills TEXT,
            headcount INTEGER DEFAULT 1,
            priority TEXT DEFAULT 'normal',
            status TEXT DEFAULT 'open',
            consultant_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (consultant_id) REFERENCES users(id)
        )
    ''')

    # 匹配表
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            match_score REAL,
            match_details TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    ''')

    # 交易/推荐表
    c.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            stage TEXT DEFAULT 'candidate',
            probability INTEGER DEFAULT 20,
            offer_salary INTEGER,
            offer_date DATE,
            start_date DATE,
            closed_reason TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')

    # 活动日志表
    c.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id INTEGER,
            candidate_id INTEGER,
            job_id INTEGER,
            user_id INTEGER,
            action TEXT NOT NULL,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (deal_id) REFERENCES deals(id),
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 简历解析记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS resume_parsed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            file_name TEXT,
            parse_result TEXT,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    return conn

def seed_users(conn):
    """种子用户数据"""
    c = conn.cursor()

    users = [
        ('admin', 'admin@cgl.com', get_password_hash('admin123'), 'admin', '郭雁冰', '13800138000', '👤'),
        ('consultant', 'li@cgl.com', get_password_hash('consultant123'), 'consultant', '李明', '13800138001', '👔'),
        ('consultant2', 'zhang@cgl.com', get_password_hash('consultant123'), 'consultant', '张华', '13800138002', '👔'),
        ('candidate', 'wang@email.com', get_password_hash('candidate123'), 'candidate', '王强', '13800138003', '👨'),
    ]

    for user in users:
        c.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, role, full_name, phone, avatar)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', user)

    conn.commit()
    print(f"✅ 用户数据已初始化 ({len(users)}条)")

def seed_companies(conn):
    """种子公司数据"""
    c = conn.cursor()

    companies = [
        ('字节跳动', '互联网', '10000+', '已上市', '全球领先的互联网科技公司', 'https://bytedance.com', '北京'),
        ('美团', '互联网', '10000+', '已上市', '中国领先的生活服务平台', 'https://meituan.com', '北京'),
        ('蔚来汽车', '新能源汽车', '5000-10000', '已上市', '高端智能电动汽车制造商', 'https://nio.com', '上海'),
        ('商汤科技', '人工智能', '2000-5000', '已上市', '人工智能算法提供商', 'https://sensetime.com', '北京'),
        ('米哈游', '游戏', '2000-5000', '未上市', '高品质游戏内容制作商', 'https://mihoyo.com', '上海'),
        ('小红书', '社交电商', '1000-2000', '未上市', '生活方式分享平台', 'https://xiaohongshu.com', '上海'),
        ('大疆创新', '无人机/硬件', '5000-10000', '未上市', '全球领先的无人机制造商', 'https://dji.com', '深圳'),
        ('SHEIN', '电商', '10000+', '未上市', '快时尚跨境电商平台', 'https://shein.com', '南京'),
    ]

    company_ids = []
    for comp in companies:
        c.execute('''
            INSERT OR IGNORE INTO companies (name, industry, size, stage, description, website, address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', comp)
        c.execute('SELECT id FROM companies WHERE name = ?', (comp[0],))
        result = c.fetchone()
        if result:
            company_ids.append(result[0])

    conn.commit()
    print(f"✅ 公司数据已初始化 ({len(companies)}条)")
    return company_ids

def seed_jobs(conn, company_ids, consultant_id=2):
    """种子职位数据"""
    c = conn.cursor()

    jobs = [
        ('高级前端工程师', company_ids[0], '前端部', '北京', 40000, 60000,
         '负责字节跳动核心产品的前端开发，使用React/Vue技术栈', '5年+前端开发经验，熟练React/Vue', 'React,Vue,TypeScript', 2, 'high'),
        ('后端资深工程师', company_ids[0], '后端部', '北京', 45000, 70000,
         '参与抖音后端架构设计与开发，处理高并发场景', '5年+后端开发，精通Go/Python', 'Go,Python,Kubernetes', 1, 'high'),
        ('产品经理', company_ids[1], '到店事业部', '北京', 35000, 55000,
         '负责美团到店业务的产品规划和设计', '3年+产品经验，有O2O经验优先', '产品设计,数据分析,用户研究', 1, 'normal'),
        ('算法工程师', company_ids[3], '研发部', '北京', 50000, 80000,
         '负责计算机视觉算法研发，落地实际业务场景', '硕士+学历，3年+算法经验', 'Python,C++,深度学习,CV', 2, 'high'),
        ('Unity3D开发工程师', company_ids[4], '游戏研发', '上海', 35000, 50000,
         '参与原神等游戏的客户端开发', '3年+Unity开发，有商业项目经验', 'Unity3D,C#,Shader', 1, 'normal'),
        ('数据分析师', company_ids[5], '数据部', '上海', 25000, 40000,
         '负责小红书数据分析和洞察，支撑业务决策', '统计学/数学背景，熟练SQL/Python', 'SQL,Python,R,Tableau', 2, 'normal'),
        ('机械工程师', company_ids[6], '研发部', '深圳', 20000, 35000,
         '负责无人机结构设计和优化', '机械相关专业，2年+经验', 'SolidWorks,CAD,材料知识', 1, 'normal'),
        ('海外运营专员', company_ids[7], '运营部', '南京', 15000, 25000,
         '负责SHEIN海外市场运营和用户增长', '英语流利，有跨境电商经验', '英语,数据分析,社媒运营', 3, 'normal'),
        ('Java高级工程师', company_ids[1], '金融部', '北京', 40000, 60000,
         '负责美团金融业务后端开发', '5年+Java开发，有金融系统经验', 'Java,Spring,Mysql,Redis', 1, 'high'),
        ('HRBP', company_ids[2], '人力资源部', '上海', 30000, 45000,
         '负责蔚来汽车研发团队的HR工作', '5年+HR经验，科技行业背景', '招聘,员工关系,组织发展', 1, 'normal'),
    ]

    job_ids = []
    for job in jobs:
        c.execute('''
            INSERT OR IGNORE INTO jobs
            (title, company_id, department, location, salary_min, salary_max, description, requirements, skills, headcount, priority, consultant_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', job)
        c.execute('SELECT id FROM jobs WHERE title = ? AND company_id = ?', (job[0], job[1]))
        result = c.fetchone()
        if result:
            job_ids.append(result[0])

    conn.commit()
    print(f"✅ 职位数据已初始化 ({len(jobs)}条)")
    return job_ids

def seed_candidates(conn, consultant_id=2):
    """种子候选人数据"""
    c = conn.cursor()

    candidates = [
        # 程序员/工程师
        ('张伟', 'zhangwei@email.com', '13600001111', '男', 30, '北京',
         '阿里巴巴', '高级前端工程师', '40K*15', '45K*15', '本科', 8,
         'React,Vue,Node.js,TypeScript', '猎聘', 'active', 1.0),
        ('李娜', 'lina@email.com', '13600002222', '女', 28, '北京',
         '腾讯', '前端开发', '35K*14', '40K*15', '硕士', 5,
         'React,Vue,JavaScript,Webpack', 'Boss直聘', 'active', 0.9),
        ('王芳', 'wangfang@email.com', '13600003333', '女', 32, '上海',
         '网易', '资深后端工程师', '50K*15', '55K*15', '本科', 9,
         'Go,Python,Kubernetes,Mysql', '猎聘', 'active', 0.85),
        ('刘强', 'liuqiang@email.com', '13600004444', '男', 29, '北京',
         '京东', 'Java开发工程师', '32K*13', '38K*14', '本科', 6,
         'Java,SpringCloud,Mysql,Redis', 'Boss直聘', 'active', 0.8),
        ('陈静', 'chenjing@email.com', '13600005555', '女', 27, '深圳',
         '华为', '算法工程师', '38K*15', '45K*15', '硕士', 4,
         'Python,深度学习,NLP, TensorFlow', '猎聘', 'active', 0.95),
        ('赵磊', 'zhaolei@email.com', '13600006666', '男', 31, '杭州',
         '蚂蚁集团', '技术专家', '60K*16', '70K*16', '硕士', 8,
         'Java,架构设计,分布式系统', '猎聘', 'passive', 0.75),
        ('孙燕', 'sunyan@email.com', '13600007777', '女', 26, '北京',
         '快手', '前端工程师', '28K*14', '32K*14', '本科', 3,
         'Vue,React,小程序开发', 'Boss直聘', 'active', 0.88),
        ('周杰', 'zhoujie@email.com', '13600008888', '男', 34, '上海',
         '携程', '技术经理', '55K*15', '65K*15', '本科', 10,
         '管理,后端架构,微服务', '猎聘', 'passive', 0.7),
        # 产品经理
        ('吴婷', 'wuting@email.com', '13600009999', '女', 29, '北京',
         '字节跳动', '产品经理', '40K*15', '45K*15', '本科', 6,
         '产品设计,数据分析,用户研究', '猎聘', 'active', 0.92),
        ('郑鑫', 'zhengxin@email.com', '13600001010', '男', 28, '上海',
         '拼多多', '高级产品经理', '45K*15', '50K*15', '硕士', 5,
         '电商产品,交易系统,增长', 'Boss直聘', 'active', 0.85),
        # 数据/运营
        ('黄丽', 'huangli@email.com', '13600001111', '女', 25, '北京',
         '滴滴', '数据分析师', '25K*14', '30K*14', '本科', 2,
         'SQL,Python,R,Tableau', 'Boss直聘', 'active', 0.9),
        ('林超', 'linchao@email.com', '13600002222', '男', 30, '上海',
         '饿了么', '数据工程师', '35K*14', '42K*14', '本科', 6,
         'Python,Hadoop,Spark,SQL', '猎聘', 'active', 0.82),
        # 游戏
        ('马媛', 'mayuan@email.com', '13600003333', '女', 27, '上海',
         '网易游戏', 'Unity开发', '30K*16', '38K*16', '本科', 4,
         'Unity3D,C#,Shader,游戏开发', '猎聘', 'active', 0.88),
        # 职能
        ('赵敏', 'zhaomin@email.com', '13600004444', '女', 33, '北京',
         '百度', 'HRBP', '35K*14', '40K*14', '本科', 8,
         '招聘,员工关系,OD', '猎聘', 'passive', 0.78),
        ('钱伟', 'qianwei@email.com', '13600005555', '男', 29, '深圳',
         '腾讯云', '解决方案专家', '40K*14', '50K*14', '硕士', 5,
         '云计算,解决方案,售前', '猎聘', 'active', 0.85),
    ]

    candidate_ids = []
    for cand in candidates:
        c.execute('''
            INSERT OR IGNORE INTO candidates
            (name, email, phone, gender, age, location, current_company, current_title, current_salary,
             expected_salary, education, work_years, skills, source, status, last_contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', cand)
        c.execute('SELECT id FROM candidates WHERE email = ?', (cand[1],))
        result = c.fetchone()
        if result:
            candidate_ids.append(result[0])

    conn.commit()
    print(f"✅ 候选人数据已初始化 ({len(candidates)}条)")
    return candidate_ids

def seed_matches(conn, candidate_ids, job_ids):
    """种子匹配数据"""
    c = conn.cursor()

    # 为每个候选人匹配合适的职位
    match_rules = [
        # (candidate_idx, job_idx, score, details)
        (0, 0, 92, 'React/Vue技能匹配度95%，8年经验符合高级要求'),
        (0, 5, 78, '技能匹配，薪资预期略高'),
        (1, 0, 88, '5年经验，React/Vue技术栈完全匹配'),
        (2, 1, 95, 'Go语言专家，高并发经验，9年后端背景'),
        (2, 8, 85, 'Java背景，架构能力强'),
        (3, 8, 90, 'Java高级工程师，6年经验完全匹配'),
        (4, 3, 94, 'NLP方向博士，算法经验4年+'),
        (5, 1, 82, '技术专家背景，可降级到资深工程师'),
        (6, 0, 86, '3年经验，Vue/React技术栈匹配'),
        (8, 2, 90, '6年产品经验，O2O背景，匹配度高'),
        (9, 2, 88, '5年电商产品，支付/交易系统经验'),
        (10, 5, 85, '2年数据分析，数据敏感度高'),
        (11, 5, 92, '数据工程师背景，分析能力强'),
        (12, 4, 89, 'Unity开发经验，游戏热情高'),
        (13, 9, 85, 'HRBP背景，大厂经验'),
        (14, 1, 80, '解决方案背景，可转向后端'),
    ]

    for rule in match_rules:
        cand_idx, job_idx, score, details = rule
        if cand_idx < len(candidate_ids) and job_idx < len(job_ids):
            c.execute('''
                INSERT OR IGNORE INTO matches (candidate_id, job_id, match_score, match_details, status)
                VALUES (?, ?, ?, ?, 'pending')
            ''', (candidate_ids[cand_idx], job_ids[job_idx], score, details))

    conn.commit()
    print(f"✅ 匹配数据已初始化 ({len(match_rules)}条)")

def seed_deals(conn, candidate_ids, job_ids):
    """种子交易数据"""
    c = conn.cursor()

    deals = [
        # stage: candidate->interview->offer->hired/rejected
        (candidate_ids[0], job_ids[0], 2, 'interview', 60, 55000, None, None, '技术一面已过，等待二面'),
        (candidate_ids[1], job_ids[0], 2, 'offer', 80, 42000, '2026-05-01', None, '已发Offer，等待入职'),
        (candidate_ids[2], job_ids[1], 2, 'candidate', 30, None, None, None, '已推荐，等待反馈'),
        (candidate_ids[8], job_ids[2], 2, 'interview', 50, None, None, None, 'HR面试完成，等待部门面试'),
        (candidate_ids[12], job_ids[4], 4, 'hired', 100, 36000, '2026-04-15', '2026-05-15', '已入职'),
    ]

    deal_ids = []
    for deal in deals:
        c.execute('''
            INSERT OR IGNORE INTO deals
            (candidate_id, job_id, company_id, stage, probability, offer_salary, offer_date, start_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', deal)
        c.execute('SELECT id FROM deals WHERE candidate_id = ? AND job_id = ?',
                  (deal[0], deal[1]))
        result = c.fetchone()
        if result:
            deal_ids.append(result[0])

    conn.commit()
    print(f"✅ 交易数据已初始化 ({len(deals)}条)")
    return deal_ids

def seed_activities(conn, deal_ids, candidate_ids):
    """种子活动日志"""
    c = conn.cursor()

    activities = [
        # Deal 1 活动
        (deal_ids[0] if len(deal_ids) > 0 else None, candidate_ids[0], job_ids[0] if 'job_ids' in dir() else None, 2,
         'created', '候选人入库，创建推荐'),
        (deal_ids[0] if len(deal_ids) > 0 else None, candidate_ids[0], job_ids[0] if 'job_ids' in dir() else None, 2,
         'matched', '匹配度92%，自动推荐到高级前端工程师'),
        (deal_ids[0] if len(deal_ids) > 0 else None, candidate_ids[0], job_ids[0] if 'job_ids' in dir() else None, 2,
         'interview_scheduled', '约到一面，5月10日14:00'),
        # Deal 2 活动
        (deal_ids[1] if len(deal_ids) > 1 else None, candidate_ids[1], job_ids[0] if 'job_ids' in dir() else None, 2,
         'created', '候选人入库'),
        (deal_ids[1] if len(deal_ids) > 1 else None, candidate_ids[1], job_ids[0] if 'job_ids' in dir() else None, 2,
         'interview_scheduled', '四面安排中'),
        (deal_ids[1] if len(deal_ids) > 1 else None, candidate_ids[1], job_ids[0] if 'job_ids' in dir() else None, 2,
         'offer_sent', '已发送Offer，42K*14'),
    ]

    # 简化版活动
    activities = [
        (deal_ids[0], candidate_ids[0], None, 2, 'created', '候选人入库，创建推荐'),
        (deal_ids[0], candidate_ids[0], None, 2, 'matched', '匹配度92%，自动推荐'),
        (deal_ids[0], candidate_ids[0], None, 2, 'interview_scheduled', '约到一面，5月10日14:00'),
        (deal_ids[1], candidate_ids[1], None, 2, 'created', '候选人入库'),
        (deal_ids[1], candidate_ids[1], None, 2, 'interview_scheduled', '四面安排中'),
        (deal_ids[1], candidate_ids[1], None, 2, 'offer_sent', '已发送Offer'),
        (deal_ids[4], candidate_ids[12], None, 2, 'created', '候选人入库'),
        (deal_ids[4], candidate_ids[12], None, 2, 'interview_scheduled', '技术面试'),
        (deal_ids[4], candidate_ids[12], None, 2, 'offer_sent', '发送Offer'),
        (deal_ids[4], candidate_ids[12], None, 2, 'hired', '入职日期5月15日'),
    ]

    for act in activities:
        c.execute('''
            INSERT INTO activities (deal_id, candidate_id, job_id, user_id, action, content)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', act)

    conn.commit()
    print(f"✅ 活动日志已初始化 ({len(activities)}条)")

def main():
    """主函数"""
    print("=" * 60)
    print("TalentAI Pro 数据库初始化")
    print("=" * 60)

    conn = init_database()
    seed_users(conn)
    company_ids = seed_companies(conn)
    job_ids = seed_jobs(conn, company_ids)
    candidate_ids = seed_candidates(conn)
    seed_matches(conn, candidate_ids, job_ids)
    deal_ids = seed_deals(conn, candidate_ids, job_ids)
    seed_activities(conn, deal_ids, candidate_ids)

    print("=" * 60)
    print("✅ 数据库初始化完成！")
    print(f"📁 数据库位置: {DB_PATH}")
    print("=" * 60)

    conn.close()

if __name__ == '__main__':
    main()
