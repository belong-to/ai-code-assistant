from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import logging
import time
import json
from logging.handlers import RotatingFileHandler
import traceback

# 导入API路由
from api.code_analysis import code_analysis_bp
from api.code_suggestion import code_suggestion_bp
from api.problem_solving import problem_solving_bp
from api.direct_question import direct_question_bp

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 配置日志
log_file = os.path.join(log_dir, 'app.log')
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] - %(message)s')

# 文件处理器 - 使用RotatingFileHandler进行日志轮转
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用跨域资源共享

# 注册蓝图
app.register_blueprint(code_analysis_bp, url_prefix='/api/code-analysis')
app.register_blueprint(code_suggestion_bp, url_prefix='/api/code-suggestion')
app.register_blueprint(problem_solving_bp, url_prefix='/api/problem-solving')
app.register_blueprint(direct_question_bp, url_prefix='/api/direct-question')

# 请求前钩子 - 记录请求开始时间和生成请求ID
@app.before_request
def before_request():
    g.start_time = time.time()
    g.request_id = f"req-{int(time.time())}-{os.urandom(4).hex()}"
    
    # 记录请求信息
    request_data = ''
    if request.is_json:
        try:
            request_data = json.dumps(request.get_json(), ensure_ascii=False)
            if len(request_data) > 1000:  # 限制日志中请求数据的长度
                request_data = request_data[:1000] + '... [截断]'
        except Exception:
            request_data = '[无法解析JSON]'
    
    logger.info(f"[{g.request_id}] 收到请求: {request.method} {request.path} - IP: {request.remote_addr}")
    if request_data:
        logger.debug(f"[{g.request_id}] 请求数据: {request_data}")

# 请求后钩子 - 记录响应时间
@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        elapsed_time = time.time() - g.start_time
        response.headers['X-Request-ID'] = g.request_id
        response.headers['X-Response-Time'] = f"{elapsed_time:.3f}s"
        
        # 记录响应信息
        status_code = response.status_code
        log_level = logging.WARNING if status_code >= 400 else logging.INFO
        logger.log(log_level, f"[{g.request_id}] 响应: {status_code} - 耗时: {elapsed_time:.3f}秒")
    
    return response

@app.route('/', methods=['GET'])
def index():
    """根路由，提供API信息"""
    return jsonify({
        "message": "AI代码助手API服务",
        "version": "1.0",
        "endpoints": {
            "健康检查": "/api/health",
            "代码分析": "/api/code-analysis/analyze",
            "代码建议": "/api/code-suggestion/suggest",
            "问题解决": "/api/problem-solving/solve",
            "直接提问": "/api/direct-question/ask"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "ok", "message": "服务正常运行"})

@app.errorhandler(400)
def bad_request(error):
    request_id = getattr(g, 'request_id', 'unknown')
    logger.warning(f"[{request_id}] 错误的请求: {error}")
    return jsonify({
        "error": "错误的请求",
        "message": str(error),
        "request_id": request_id
    }), 400

@app.errorhandler(404)
def not_found(error):
    request_id = getattr(g, 'request_id', 'unknown')
    logger.warning(f"[{request_id}] 资源未找到: {request.path}")
    return jsonify({
        "error": "资源未找到",
        "path": request.path,
        "request_id": request_id
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    request_id = getattr(g, 'request_id', 'unknown')
    logger.warning(f"[{request_id}] 方法不允许: {request.method} {request.path}")
    return jsonify({
        "error": "方法不允许",
        "method": request.method,
        "path": request.path,
        "request_id": request_id
    }), 405

@app.errorhandler(500)
def server_error(error):
    request_id = getattr(g, 'request_id', 'unknown')
    logger.error(f"[{request_id}] 服务器错误: {error}")
    logger.error(f"[{request_id}] 错误详情: {traceback.format_exc()}")
    return jsonify({
        "error": "服务器内部错误",
        "message": str(error),
        "request_id": request_id
    }), 500

@app.errorhandler(Exception)
def unhandled_exception(error):
    request_id = getattr(g, 'request_id', 'unknown')
    logger.error(f"[{request_id}] 未处理的异常: {error}")
    logger.error(f"[{request_id}] 异常详情: {traceback.format_exc()}")
    return jsonify({
        "error": "服务器内部错误",
        "message": "发生了未处理的异常",
        "error_type": error.__class__.__name__,
        "request_id": request_id
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"启动服务器在 http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)