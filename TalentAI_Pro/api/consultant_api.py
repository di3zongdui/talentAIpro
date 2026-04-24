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
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

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
        print("❌ 数据库不存在，正在初始化...")
        import init_database
        init_database.main()
        print()

    server = HTTPServer(('localhost', PORT), APIHandler)
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║         TalentAI Pro 顾问端 API 服务                          ║
╠════════════════════════════════════════════════════════════════╣
║  🌐 地址: http://localhost:{PORT}                              ║
║  📊 API文档: http://localhost:{PORT}/api/dashboard/stats        ║
╠════════════════════════════════════════════════════════════════╣
║  可用端点:                                                     ║
║  • POST /api/login          登录                              ║
║  • GET  /api/dashboard/stats  仪表盘统计                       ║
║  • GET  /api/candidates     候选人列表                        ║
║  • GET  /api/jobs           职位列表                          ║
║  • GET  /api/matches        匹配列表                          ║
║  • GET  /api/deals          交易列表                          ║
║  • GET  /api/funnel         漏斗统计                          ║
║  • GET  /api/activities     活动日志                          ║
╚════════════════════════════════════════════════════════════════╝
    """)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
