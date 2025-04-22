from flask import Blueprint, request, jsonify
import logging
from services.qianwen_service import QianwenService
from models.response import SolutionResponse

logger = logging.getLogger(__name__)

direct_question_bp = Blueprint('direct_question', __name__)

@direct_question_bp.route('/ask', methods=['POST'])
def ask_question():
    """直接向千问API提问并获取回答"""
    try:
        data = request.get_json()
        
        question = data.get('question')
        
        if not question:
            return jsonify({"error": "缺少必要参数 'question'"}), 400
        
        # 调用千问API获取回答
        qianwen_service = QianwenService()
        response = qianwen_service.generate_response(question)
        
        if not response['success']:
            return jsonify({"error": response.get('error', '调用千问API失败')}), 500
        
        # 构建响应
        solution_response = SolutionResponse(
            problem=question,
            explanation=response.get('content', ''),
            solution_code='',  # 直接问答不需要代码
            additional_resources=[]
        )
        
        return jsonify(solution_response.to_dict()), 200
        
    except Exception as e:
        logger.error(f"处理问题时发生错误: {str(e)}")
        return jsonify({"error": "处理请求时发生错误"}), 500