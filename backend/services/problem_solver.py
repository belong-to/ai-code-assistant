import logging
from services.qianwen_service import QianwenService
from services.custom_api_service import CustomAPIService

logger = logging.getLogger(__name__)

class ProblemSolver:
    """问题解决器类，用于解决编程问题和解释编程概念"""
    
    def __init__(self):
        """初始化问题解决器"""
        logger.info("初始化问题解决器")
        self.qianwen_service = QianwenService()
        self.custom_api_service = CustomAPIService()
    
    def solve(self, problem_description, code_context='', language='python', use_qianwen=False, use_custom_api=False):
        """解决编程问题
        
        Args:
            problem_description (str): 问题描述
            code_context (str): 代码上下文，默认为空
            language (str): 代码语言，默认为python
            use_qianwen (bool): 是否使用千问API，默认为False
            use_custom_api (bool): 是否使用自定义API，默认为False
            
        Returns:
            dict: 包含解决方案代码、解释和额外资源的结果
        """
        logger.info(f"解决{language}编程问题，使用千问API: {use_qianwen}，使用自定义API: {use_custom_api}")
        
        # 如果选择使用千问API
        if use_qianwen:
            return self.qianwen_service.solve_problem(problem_description, code_context, language)
            
        # 如果选择使用自定义API
        if use_custom_api:
            return self.custom_api_service.solve_problem(problem_description, code_context, language)
        
        # 默认解决方案逻辑
        return {
            'solution_code': f"# {problem_description}的解决方案\n# 这里是解决方案代码",
            'explanation': f"这个解决方案通过以下步骤解决了问题：\n1. 分析问题\n2. 设计解决方案\n3. 实现代码",
            'additional_resources': [
                f'{language}官方文档',
                '相关教程链接'
            ]
        }
    
    def explain(self, concept, language='python', detail_level='medium'):
        """解释编程概念
        
        Args:
            concept (str): 编程概念
            language (str): 代码语言，默认为python
            detail_level (str): 详细程度，可选值：basic, medium, advanced
            
        Returns:
            dict: 包含概念解释、示例和资源的结果
        """
        logger.info(f"解释{concept}概念，详细程度为{detail_level}")
        
        # 这里实现概念解释逻辑
        # 实际项目中可能会有预定义的解释库或使用AI生成
        
        # 根据详细程度提供不同级别的解释
        explanation = ""
        examples = []
        
        if detail_level == 'basic':
            explanation = f"{concept}是一个基础编程概念，它的基本用途是..."
            examples = [f"# 简单的{concept}示例\n# 基础代码示例"]
            
        elif detail_level == 'medium':
            explanation = f"{concept}是一个重要的编程概念，它可以用于...\n它的工作原理是..."
            examples = [
                f"# {concept}的常见用法\n# 中级代码示例",
                f"# {concept}的另一种用法\n# 另一个中级代码示例"
            ]
            
        elif detail_level == 'advanced':
            explanation = f"{concept}是一个高级编程概念，它在复杂系统中的应用包括...\n它的内部实现机制是...\n高级使用技巧包括..."
            examples = [
                f"# {concept}的高级用法\n# 高级代码示例",
                f"# {concept}在实际项目中的应用\n# 复杂代码示例"
            ]
        
        # 示例返回结果
        return {
            'explanation': explanation,
            'examples': examples,
            'resources': [
                f'{language}官方文档关于{concept}的章节',
                f'关于{concept}的深入教程'
            ]
        }