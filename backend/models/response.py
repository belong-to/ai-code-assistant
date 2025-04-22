class BaseResponse:
    """响应基类"""
    def __init__(self):
        pass
        
    def to_dict(self):
        """将响应对象转换为字典"""
        return self.__dict__

class AnalysisResponse(BaseResponse):
    """代码分析响应模型"""
    def __init__(self, code_quality=None, suggestions=None, potential_issues=None, 
                 best_practices=None, complexity=None, structure=None):
        super().__init__()
        self.code_quality = code_quality or {}
        self.suggestions = suggestions or []
        self.potential_issues = potential_issues or []
        self.best_practices = best_practices or []
        self.complexity = complexity or {}
        self.structure = structure or {}

class SuggestionResponse(BaseResponse):
    """代码建议响应"""
    def __init__(self, original_code=None, improved_code=None, explanation=None, improvement_points=None):
        super().__init__()
        self.original_code = original_code
        self.improved_code = improved_code
        self.explanation = explanation or ""
        self.improvement_points = improvement_points or []

class SolutionResponse(BaseResponse):
    """问题解决响应"""
    def __init__(self, problem=None, solution_code=None, explanation=None, additional_resources=None):
        super().__init__()
        self.problem = problem
        self.solution_code = solution_code
        self.explanation = explanation or ""
        self.additional_resources = additional_resources or []