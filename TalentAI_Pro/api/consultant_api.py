#!/usr/bin/env python3
"""
TalentAI Pro 顾问端 API 服务
基于真实数据库的REST API
"""
import sqlite3
import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import hashlib

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'talentai.db')
PORT = 8088

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    if row is None:
        return None
    return dict(zip(row.keys(), row))

def json_response(data, status=200):
    return {
        'status': status,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }

class APIHandler(BaseHTTPRequestHandler):
    """API请求处理器"""

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def parse_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            return json.loads(self.rfile.read(content_length))
        return {}

    # ========== 认证相关 ==========

    def do_POST(self):
        path = urlparse(self.path).path

        if path == '/api/login':
            self.handle_login()
        elif path == '/api/logout':
            self.send_json({'success': True})
        elif path == '/api/candidates/create':
            self.handle_candidate_create()
        elif path == '/api/jobs/create':
            self.handle_job_create()
        elif path == '/api/deals/create':
            self.handle_create_deal()
        elif path == '/api/deals/update-stage':
            self.handle_update_deal_stage()
        else:
            self.send_json({'error': 'Not found'}, 404)

    # ========== GET 请求 ==========

    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)

        # 仪表盘统计
        if path == '/api/dashboard/stats':
            self.handle_dashboard_stats()
        # 候选人列表
        elif path == '/api/candidates':
            self.handle_candidates(query)
        # 候选人详情
        elif path.startswith('/api/candidates/'):
            cid = path.split('/')[-1]
            self.handle_candidate_detail(cid)
        # 职位列表
        elif path == '/api/jobs':
            self.handle_jobs(query)
        # 职位详情
        elif path.startswith('/api/jobs/'):
            jid = path.split('/')[-1]
            self.handle_job_detail(jid)
        # 匹配列表
        elif path == '/api/matches':
            self.handle_matches(query)
        # 交易列表
        elif path == '/api/deals':
            self.handle_deals(query)
        elif path == '/api/deals/create':
            self.handle_create_deal()
        # 交易详情
        elif path.startswith('/api/deals/'):
            deal_id = path.split('/')[-1]
            if deal_id.isdigit():
                self.handle_deal_detail(int(deal_id))
            else:
                self.send_json({'error': 'Invalid deal ID'}, 400)
        # 漏斗统计
        elif path == '/api/funnel':
            self.handle_funnel()
        # 公司列表
        elif path == '/api/companies':
            self.handle_companies()
        # 活动日志
        elif path == '/api/activities':
            self.handle_activities(query)
        else:
            self.send_json({'error': 'Not found'}, 404)

    def handle_login(self):
        """处理登录"""
        body = self.parse_body()
        username = body.get('username', '')
        password = body.get('password', '')

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT id, username, email, role, full_name, phone, avatar
            FROM users WHERE username = ? AND password_hash = ?
        ''', (username, get_password_hash(password)))
        user = c.fetchone()
        conn.close()

        if user:
            self.send_json({
                'success': True,
                'user': row_to_dict(user)
            })
        else:
            self.send_json({'success': False, 'error': '用户名或密码错误'}, 401)

    def handle_dashboard_stats(self):
        """仪表盘统计数据"""
        conn = get_db_connection()
        c = conn.cursor()

        # 候选人总数
        c.execute('SELECT COUNT(*) as count FROM candidates')
        candidates_count = c.fetchone()['count']

        # 活跃候选人（最近30天有联系）
        c.execute('''SELECT COUNT(*) as count FROM candidates
                     WHERE last_contact > datetime('now', '-30 days')''')
        active_count = c.fetchone()['count']

        # 开放职位
        c.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'open'")
        open_jobs = c.fetchone()['count']

        # 匹配成功待跟进
        c.execute("SELECT COUNT(*) as count FROM matches WHERE status = 'pending'")
        pending_matches = c.fetchone()['count']

        # 面试中
        c.execute("SELECT COUNT(*) as count FROM deals WHERE stage = 'interview'")
        in_interview = c.fetchone()['count']

        # Offer中
        c.execute("SELECT COUNT(*) as count FROM deals WHERE stage = 'offer'")
        in_offer = c.fetchone()['count']

        # 本月入职
        c.execute('''SELECT COUNT(*) as count FROM deals
                     WHERE stage = 'hired'
                     AND start_date > date('now', 'start of month')''')
        hired_this_month = c.fetchone()['count']

        # 漏斗数据
        c.execute("SELECT COUNT(*) as count FROM deals")
        total_deals = c.fetchone()['count']

        stats = {
            'candidates': candidates_count,
            'active_candidates': active_count,
            'open_jobs': open_jobs,
            'pending_matches': pending_matches,
            'in_interview': in_interview,
            'in_offer': in_offer,
            'hired_this_month': hired_this_month,
            'total_deals': total_deals
        }

        conn.close()
        self.send_json(stats)

    def handle_candidates(self, query):
        """候选人列表"""
        conn = get_db_connection()
        c = conn.cursor()

        status = query.get('status', [None])[0]
        search = query.get('search', [None])[0]
        page = int(query.get('page', ['1'])[0])
        limit = int(query.get('limit', ['20'])[0])
        offset = (page - 1) * limit

        sql = 'SELECT * FROM candidates WHERE 1=1'
        params = []

        if status:
            sql += ' AND status = ?'
            params.append(status)
        if search:
            sql += ' AND (name LIKE ? OR current_title LIKE ? OR skills LIKE ?)'
            search_pattern = f'%{search}%'
            params.extend([search_pattern, search_pattern, search_pattern])

        sql += ' ORDER BY updated_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])

        c.execute(sql, params)
        candidates = [row_to_dict(r) for r in c.fetchall()]

        # 总数
        c.execute('SELECT COUNT(*) as total FROM candidates')
        total = c.fetchone()['total']

        conn.close()
        self.send_json({
            'items': candidates,
            'total': total,
            'page': page,
            'limit': limit
        })

    def handle_candidate_detail(self, cid):
        """候选人详情"""
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('SELECT * FROM candidates WHERE id = ?', (cid,))
        candidate = c.fetchone()

        if candidate:
            # 获取相关匹配
            c.execute('''
                SELECT m.*, j.title as job_title, j.salary_min, j.salary_max
                FROM matches m
                JOIN jobs j ON m.job_id = j.id
                WHERE m.candidate_id = ?
                ORDER BY m.match_score DESC
            ''', (cid,))
            matches = [row_to_dict(r) for r in c.fetchall()]

            # 获取相关活动
            c.execute('''
                SELECT * FROM activities
                WHERE candidate_id = ?
                ORDER BY created_at DESC LIMIT 20
            ''', (cid,))
            activities = [row_to_dict(r) for r in c.fetchall()]

            data = row_to_dict(candidate)
            data['matches'] = matches
            data['activities'] = activities
            self.send_json(data)
        else:
            self.send_json({'error': 'Candidate not found'}, 404)

        conn.close()

    def handle_candidate_create(self):
        """创建新候选人"""
        body = self.parse_body()
        name = body.get('name')
        email = body.get('email', '')
        phone = body.get('phone', '')
        current_company = body.get('current_company', '')
        current_title = body.get('current_title', '')
        expected_salary = body.get('expected_salary', '')
        skills = body.get('skills', '')

        if not name:
            self.send_json({'error': '姓名不能为空'}, 400)
            return

        conn = get_db_connection()
        c = conn.cursor()

        c.execute('''
            INSERT INTO candidates (name, email, phone, current_company, current_title,
                                   expected_salary, skills, status, last_contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'new', datetime('now'))
        ''', (name, email, phone, current_company, current_title, expected_salary, skills))

        candidate_id = c.lastrowid

        # 记录活动日志
        c.execute('''
            INSERT INTO activities (candidate_id, action, content, user_name)
            VALUES (?, 'created', ?, '李明')
        ''', (candidate_id, f'新建候选人: {name}'))

        conn.commit()
        conn.close()

        self.send_json({'success': True, 'id': candidate_id, 'message': '候选人创建成功'})

    def handle_job_create(self):
        """创建新职位"""
        body = self.parse_body()
        title = body.get('title')
        company_id = body.get('company_id')
        salary_min = body.get('salary_min', 0)
        salary_max = body.get('salary_max', 0)
        location = body.get('location', '')
        department = body.get('department', '')
        headcount = body.get('headcount', 1)
        description = body.get('description', '')
        requirements = body.get('requirements', '')
        priority = body.get('priority', 'normal')

        if not title:
            self.send_json({'error': '职位名称不能为空'}, 400)
            return

        if not company_id:
            self.send_json({'error': '请选择公司'}, 400)
            return

        conn = get_db_connection()
        c = conn.cursor()

        c.execute('''
            INSERT INTO jobs (company_id, title, salary_min, salary_max, location,
                            department, headcount, description, requirements, status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)
        ''', (company_id, title, salary_min, salary_max, location, department,
              headcount, description, requirements, priority))

        job_id = c.lastrowid

        # 记录活动日志
        c.execute('''
            INSERT INTO activities (action, content, user_name)
            VALUES ('created', ?, '李明')
        ''', (f'新建职位: {title}'))

        conn.commit()
        conn.close()

        self.send_json({'success': True, 'id': job_id, 'message': '职位创建成功'})

    def handle_jobs(self, query):
        """职位列表"""
        conn = get_db_connection()
        c = conn.cursor()

        status = query.get('status', ['open'])[0]
        search = query.get('search', [None])[0]

        sql = '''SELECT j.*, c.name as company_name
                 FROM jobs j
                 JOIN companies c ON j.company_id = c.id
                 WHERE 1=1'''
        params = []

        if status:
            sql += ' AND j.status = ?'
            params.append(status)
        if search:
            sql += ' AND (j.title LIKE ? OR c.name LIKE ?)'
            search_pattern = f'%{search}%'
            params.extend([search_pattern, search_pattern])

        sql += ' ORDER BY j.priority DESC, j.created_at DESC'

        c.execute(sql, params)
        jobs = [row_to_dict(r) for r in c.fetchall()]
        conn.close()
        self.send_json({'items': jobs})

    def handle_job_detail(self, jid):
        """职位详情"""
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('''
            SELECT j.*, c.name as company_name, c.industry, c.size
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.id = ?
        ''', (jid,))
        job = c.fetchone()

        if job:
            # 获取匹配候选人
            c.execute('''
                SELECT m.*, cand.name, cand.current_title, cand.current_company, cand.skills
                FROM matches m
                JOIN candidates cand ON m.candidate_id = cand.id
                WHERE m.job_id = ? AND m.status = 'pending'
                ORDER BY m.match_score DESC
            ''', (jid,))
            matches = [row_to_dict(r) for r in c.fetchall()]

            data = row_to_dict(job)
            data['top_matches'] = matches[:5]
            self.send_json(data)
        else:
            self.send_json({'error': 'Job not found'}, 404)

        conn.close()

    def handle_matches(self, query):
        """匹配列表"""
        conn = get_db_connection()
        c = conn.cursor()

        job_id = query.get('job_id', [None])[0]
        candidate_id = query.get('candidate_id', [None])[0]
        min_score = query.get('min_score', [70])[0]

        sql = '''
            SELECT m.*,
                   cand.name as candidate_name, cand.current_title, cand.current_company, cand.skills,
                   j.title as job_title, j.salary_min, j.salary_max,
                   c.name as company_name
            FROM matches m
            JOIN candidates cand ON m.candidate_id = cand.id
            JOIN jobs j ON m.job_id = j.id
            JOIN companies c ON j.company_id = c.id
            WHERE m.match_score >= ?
        '''
        params = [min_score]

        if job_id:
            sql += ' AND m.job_id = ?'
            params.append(job_id)
        if candidate_id:
            sql += ' AND m.candidate_id = ?'
            params.append(candidate_id)

        sql += ' ORDER BY m.match_score DESC'

        c.execute(sql, params)
        matches = [row_to_dict(r) for r in c.fetchall()]
        conn.close()
        self.send_json({'items': matches})

    def handle_deals(self, query):
        """交易列表"""
        conn = get_db_connection()
        c = conn.cursor()

        stage = query.get('stage', [None])[0]

        sql = '''
            SELECT d.*,
                   cand.name as candidate_name, cand.current_title,
                   j.title as job_title,
                   c.name as company_name
            FROM deals d
            JOIN candidates cand ON d.candidate_id = cand.id
            JOIN jobs j ON d.job_id = j.id
            JOIN companies c ON d.company_id = c.id
            WHERE 1=1
        '''
        params = []

        if stage:
            sql += ' AND d.stage = ?'
            params.append(stage)

        sql += ' ORDER BY d.updated_at DESC'

        c.execute(sql, params)
        deals = [row_to_dict(r) for r in c.fetchall()]
        conn.close()
        self.send_json({'items': deals})

    def handle_create_deal(self):
        """创建新交易"""
        body = self.parse_body()
        candidate_id = body.get('candidate_id')
        job_id = body.get('job_id')
        probability = body.get('probability', 20)
        notes = body.get('notes', '')

        if not candidate_id or not job_id:
            self.send_json({'error': '缺少必要参数: candidate_id, job_id'}, 400)
            return

        conn = get_db_connection()
        c = conn.cursor()

        # 获取职位对应的公司ID
        c.execute('SELECT company_id FROM jobs WHERE id = ?', (job_id,))
        job = c.fetchone()
        if not job:
            conn.close()
            self.send_json({'error': '职位不存在'}, 404)
            return

        company_id = job['company_id']

        # 插入交易记录
        c.execute('''
            INSERT INTO deals (candidate_id, job_id, company_id, stage, probability, notes)
            VALUES (?, ?, ?, 'candidate', ?, ?)
        ''', (candidate_id, job_id, company_id, probability, notes))

        deal_id = c.lastrowid

        # 记录活动日志
        c.execute('''
            INSERT INTO activities (deal_id, candidate_id, job_id, action, content)
            VALUES (?, ?, ?, 'created', '创建招聘交易')
        ''', (deal_id, candidate_id, job_id))

        conn.commit()
        conn.close()

        self.send_json({'success': True, 'deal_id': deal_id})

    def handle_update_deal_stage(self):
        """更新交易阶段（推进）"""
        body = self.parse_body()
        deal_id = body.get('deal_id')
        next_stage = body.get('stage')  # candidate -> interview -> offer -> hired

        if not deal_id:
            self.send_json({'error': '缺少参数: deal_id'}, 400)
            return

        stage_order = ['candidate', 'interview', 'offer', 'hired']
        if next_stage not in stage_order:
            # 自动推进到下一阶段
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('SELECT stage FROM deals WHERE id = ?', (deal_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.send_json({'error': '交易不存在'}, 404)
                return
            current_stage = row['stage']
            try:
                current_idx = stage_order.index(current_stage)
                if current_idx < len(stage_order) - 1:
                    next_stage = stage_order[current_idx + 1]
                else:
                    conn.close()
                    self.send_json({'error': '已是最后阶段'}, 400)
                    return
            except ValueError:
                conn.close()
                self.send_json({'error': '无效的当前阶段'}, 400)
                return
            conn.close()

        conn = get_db_connection()
        c = conn.cursor()

        # 更新阶段
        c.execute('UPDATE deals SET stage = ? WHERE id = ?', (next_stage, deal_id))

        # 记录活动日志
        stage_name_map = {'candidate': '候选人', 'interview': '面试中', 'offer': 'Offer', 'hired': '已入职'}
        c.execute('''
            INSERT INTO activities (deal_id, action, content)
            VALUES (?, 'stage_update', ?)
        ''', (deal_id, f'交易阶段更新为: {stage_name_map.get(next_stage, next_stage)}'))

        conn.commit()
        conn.close()

        self.send_json({'success': True, 'stage': next_stage})

    def handle_deal_detail(self, deal_id):
        """获取交易详情"""
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('''
            SELECT d.*,
                   c.name as candidate_name, c.current_title as candidate_title, c.phone as candidate_phone, c.email as candidate_email,
                   j.title as job_title, j.salary_max, j.location as job_location,
                   co.name as company_name, co.industry as company_industry
            FROM deals d
            LEFT JOIN candidates c ON d.candidate_id = c.id
            LEFT JOIN jobs j ON d.job_id = j.id
            LEFT JOIN companies co ON d.company_id = co.id
            WHERE d.id = ?
        ''', (deal_id,))
        deal = c.fetchone()

        if not deal:
            conn.close()
            self.send_json({'error': '交易不存在'}, 404)
            return

        # 获取该交易的活动日志
        c.execute('''
            SELECT * FROM activities
            WHERE deal_id = ?
            ORDER BY created_at DESC
            LIMIT 20
        ''', (deal_id,))
        activities = [row_to_dict(r) for r in c.fetchall()]

        conn.close()

        result = row_to_dict(deal)
        result['activities'] = activities
        self.send_json(result)

    def handle_funnel(self):
        """招聘漏斗"""
        conn = get_db_connection()
        c = conn.cursor()

        funnel = {
            'candidate': 0,
            'interview': 0,
            'offer': 0,
            'hired': 0
        }

        for stage in funnel.keys():
            c.execute('SELECT COUNT(*) as count FROM deals WHERE stage = ?', (stage,))
            funnel[stage] = c.fetchone()['count']

        conn.close()
        self.send_json(funnel)

    def handle_companies(self):
        """公司列表"""
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM companies ORDER BY name')
        companies = [row_to_dict(r) for r in c.fetchall()]
        conn.close()
        self.send_json({'items': companies})

    def handle_activities(self, query):
        """活动日志"""
        conn = get_db_connection()
        c = conn.cursor()

        limit = int(query.get('limit', ['50'])[0])

        c.execute('''
            SELECT a.*, u.full_name as user_name
            FROM activities a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
            LIMIT ?
        ''', (limit,))
        activities = [row_to_dict(r) for r in c.fetchall()]
        conn.close()
        self.send_json({'items': activities})

def run_server():
    """启动API服务器"""
    # 确保数据库存在
    if not os.path.exists(DB_PATH):
        print("[X] 数据库不存在，正在初始化...")
        import init_database
        init_database.main()
        print()

    server = HTTPServer(('localhost', PORT), APIHandler)
    print(f"""
=================================================================
           TalentAI Pro 顾问端 API 服务
=================================================================
  [*] 地址: http://localhost:{PORT}
  [*] API文档: http://localhost:{PORT}/api/dashboard/stats
-----------------------------------------------------------------
  可用端点:
  - POST /api/login          登录
  - GET  /api/dashboard/stats  仪表盘统计
  - GET  /api/candidates     候选人列表
  - GET  /api/jobs           职位列表
  - GET  /api/matches        匹配列表
  - GET  /api/deals          交易列表
  - GET  /api/funnel         漏斗统计
  - GET  /api/activities     活动日志
=================================================================
    """)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
