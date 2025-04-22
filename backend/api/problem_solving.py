from flask import Blueprint, request, jsonify
import logging
from services.problem_solver import ProblemSolver
from models.response import SolutionResponse

logger = logging.getLogger(__name__)

problem_solving_bp = Blueprint('problem_solving', __name__)

@problem_solving_bp.route('/solve', methods=['POST'])
def solve_problem():
    """解决编程问题"""
    try:
        data = request.get_json()
        
        problem_description = data.get('problem_description')
        code_context = data.get('code_context', '')
        language = data.get('language', 'python')
        use_qianwen = data.get('use_qianwen', False)
        use_custom_api = data.get('use_custom_api', False)
        
        if not problem_description:
            return jsonify({"error": "缺少必要参数 'problem_description'"}), 400
        
        # 解决问题
        solver = ProblemSolver()
        solution = solver.solve(problem_description, code_context, language, use_qianwen, use_custom_api)
        
        # 构建响应
        response = SolutionResponse(
            problem=problem_description,
            solution_code=solution.get('solution_code'),
            explanation=solution.get('explanation'),
            additional_resources=solution.get('additional_resources')
        )
        
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        logger.error(f"解决问题错误: {str(e)}")
        return jsonify({"error": "处理请求时发生错误"}), 500

@problem_solving_bp.route('/explain', methods=['POST'])
def explain_concept():
    """解释编程概念"""
    try:
        data = request.get_json()
        
        concept = data.get('concept')
        language = data.get('language', 'python')
        detail_level = data.get('detail_level', 'medium')  # basic, medium, advanced
        
        if not concept:
            return jsonify({"error": "缺少必要参数 'concept'"}), 400
        
        # 解释概念
        solver = ProblemSolver()
        explanation = solver.explain_concept(concept, language, detail_level)
        
        return jsonify(explanation), 200
        
    except Exception as e:
        logger.error(f"解释概念错误: {str(e)}")
        return jsonify({"error": "处理请求时发生错误"}), 500