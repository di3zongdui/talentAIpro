<script>
/**
 * 路由守卫 - 保护需要登录的页面
 * 使用方法：在需要保护的HTML页面</head>前引入此脚本
 */

(function() {
    // 需要登录的角色配置
    const PROTECTED_PAGES = {
        'candidate_dashboard.html': ['candidate', 'admin'],
        'consultant_dashboard.html': ['consultant', 'admin'],
        'admin_dashboard.html': ['admin'],
        'developer_dashboard.html': ['developer', 'admin'],
        'plugin_manager.html': ['admin'],
        'resume_folder_init.html': ['consultant', 'admin']
    };

    // 获取当前页面文件名
    function getCurrentPage() {
        const pathname = window.location.pathname;
        return pathname.split('/').pop() || 'consultant_dashboard.html';
    }

    // 获取会话
    function getSession() {
        try {
            return JSON.parse(localStorage.getItem('talentAI_session') || '{}');
        } catch {
            return {};
        }
    }

    // 路由守卫
    function initRouteGuard() {
        const currentPage = getCurrentPage();
        const session = getSession();

        // 检查页面是否需要保护
        if (PROTECTED_PAGES[currentPage]) {
            // 检查登录状态
            if (!session.isLoggedIn) {
                alert('请先登录');
                window.location.href = 'login.html';
                return false;
            }

            // 检查角色权限
            const allowedRoles = PROTECTED_PAGES[currentPage];
            if (!allowedRoles.includes(session.role)) {
                alert('您没有权限访问此页面');
                window.location.href = session.redirect || 'login.html';
                return false;
            }
        }
        return true;
    }

    // 退出登录
    window.logout = function() {
        localStorage.removeItem('talentAI_session');
        alert('已退出登录');
        window.location.href = 'login.html';
    };

    // 获取当前用户
    window.getCurrentUser = function() {
        return getSession();
    };

    // 检查是否有权限
    window.hasPermission = function(requiredRole) {
        const session = getSession();
        return session.role === requiredRole || session.role === 'admin';
    };

    // 获取用户显示信息
    window.getUserDisplay = function() {
        const session = getSession();
        if (!session.name) return '未登录';
        return session.name + ' (' + session.role + ')';
    };

    // 初始化
    if (!initRouteGuard()) {
        console.log('Route guard blocked access');
    }
})();
</script>
