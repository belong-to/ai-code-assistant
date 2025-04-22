from flask import Blueprint, request, jsonify
import logging
import time
from services.code_analyzer import CodeAnalyzer
from models.response import AnalysisResponse
from utils.validators import validate_code_input

logger = logging.getLogger(__name__)

code_analysis_bp = Blueprint('code_analysis', __name__)

@code_analysis_bp.route('/analyze', methods=['POST'])
def analyze_code():
    """分析代码并提供反馈"""
    request_id = f"req-{int(time.time())}"
    start_time = time.time()
    logger.info(f"[{request_id}] 收到代码分析请求")
    
    try:
        data = request.get_json()
        if not data:
            logger.warning(f"[{request_id}] 无效的请求数据格式")
            return jsonify({
                "error": "无效的请求数据格式，请提供JSON数据",
                "request_id": request_id
            }), 400
        
        # 验证输入
        validation_result = validate_code_input(data)
        if not validation_result['valid']:
            logger.warning(f"[{request_id}] 输入验证失败: {validation_result['message']}")
            return jsonify({
                "error": validation_result['message'],
                "all_errors": validation_result.get('all_errors', [validation_result['message']]),
                "request_id": request_id
            }), 400
        
        code = data.get('code')
        language = data.get('language', 'python')
        context = data.get('context', '')
        filename = data.get('filename', '')
        
        logger.info(f"[{request_id}] 分析{language}代码，长度: {len(code)}字符")
        
        # 分析代码
        analyzer = CodeAnalyzer(max_workers=4)
        analysis_result = analyzer.analyze(code, language, context)
        
        # 检查分析结果中是否有错误
        if 'error' in analysis_result:
            logger.warning(f"[{request_id}] 代码分析过程中发生错误: {analysis_result['error']}")
            return jsonify({
                "warning": "代码分析过程中发生错误，结果可能不完整",
                "error_details": analysis_result['error'],
                "partial_results": analysis_result,
                "request_id": request_id
            }), 206  # 部分内容
        
        # 构建响应
        response = AnalysisResponse(
            code_quality=analysis_result.get('code_quality'),
            suggestions=analysis_result.get('suggestions'),
            potential_issues=analysis_result.get('potential_issues'),
            best_practices=analysis_result.get('best_practices'),
            complexity=analysis_result.get('complexity'),
            structure=analysis_result.get('structure')
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"[{request_id}] 代码分析完成，耗时: {elapsed_time:.2f}秒")
        
        return jsonify({
            "result": response.to_dict(),
            "request_id": request_id,
            "processing_time": f"{elapsed_time:.2f}秒"
        }), 200
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"[{request_id}] 代码分析错误: {str(e)}", exc_info=True)
        return jsonify({
            "error": "处理请求时发生错误",
            "error_details": str(e),
            "request_id": request_id,
            "processing_time": f"{elapsed_time:.2f}秒"
        }), 500

@code_analysis_bp.route('/complexity', methods=['POST'])
def analyze_complexity():
    """分析代码复杂度"""
    try:
        data = request.get_json()
        
        # 验证输入
        validation_result = validate_code_input(data)
        if not validation_result['valid']:
            return jsonify({"error": validation_result['message']}), 400
        
        code = data.get('code')
        language = data.get('language', 'python')
        
        # 分析代码复杂度
        analyzer = CodeAnalyzer()
        complexity_result = analyzer.analyze_complexity(code, language)
        
        return jsonify(complexity_result), 200
        
    except Exception as e:
        logger.error(f"代码复杂度分析错误: {str(e)}")
        return jsonify({"error": "处理请求时发生错误"}), 500