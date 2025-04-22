from flask import Blueprint, request, jsonify
import logging
from services.suggestion_generator import SuggestionGenerator
from models.response import SuggestionResponse
from utils.validators import validate_code_input

logger = logging.getLogger(__name__)

code_suggestion_bp = Blueprint('code_suggestion', __name__)

@code_suggestion_bp.route('/suggest', methods=['POST'])
def suggest_improvements():
    """为代码提供改进建议"""
    try:
        data = request.get_json()
        
        # 验证输入
        validation_result = validate_code_input(data)
        if not validation_result['valid']:
            return jsonify({"error": validation_result['message']}), 400
        
        code = data.get('code')
        language = data.get('language', 'python')
        improvement_type = data.get('improvement_type', 'general')  # general, performance, readability, security
        
        # 生成建议
        generator = SuggestionGenerator()
        suggestions = generator.generate_suggestions(code, language, improvement_type)
        
        # 构建响应
        response = SuggestionResponse(
            original_code=code,
            improved_code=suggestions.get('improved_code'),
            explanation=suggestions.get('explanation'),
            improvement_points=suggestions.get('improvement_points')
        )
        
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        logger.error(f"生成代码建议错误: {str(e)}")
        return jsonify({"error": "处理请求时发生错误"}), 500

@code_suggestion_bp.route('/examples', methods=['POST'])
def provide_examples():
    """提供代码示例"""
    try:
        data = request.get_json()
        
        concept = data.get('concept')
        language = data.get('language', 'python')
        context = data.get('context', '')
        
        if not concept:
            return jsonify({"error": "缺少必要参数 'concept'"}), 400
        
        # 生成示例
        generator = SuggestionGenerator()
        examples = generator.generate_examples(concept, language, context)
        
        return jsonify(examples), 200
        
    except Exception as e:
        logger.error(f"生成代码示例错误: {str(e)}")
        return jsonify({"error": "处理请求时发生错误"}), 500