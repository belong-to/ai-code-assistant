import logging
import time
import re
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """代码分析器类，用于分析代码质量、复杂度和提供改进建议"""
    
    def __init__(self, max_workers=4):
        """初始化代码分析器
        
        Args:
            max_workers (int): 并行分析的最大工作线程数
        """
        logger.info("初始化代码分析器")
        self.max_workers = max_workers
        self.language_patterns = {
            'python': {
                'comment': '#.*?$|"""[\\s\\S]*?"""|' + "'''[\\s\\S]*?'''",
                'function': r'\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                'class': r'\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\:]',
                'import': r'\s*import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)|\.\s*from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import',
                'exception': r'\s*except\s+|\s*try\s*:|\s*finally\s*:'
            },
            'javascript': {
                'comment': r'\/\/.*?$|\/\*[\s\S]*?\*\/',
                'function': r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(|const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\([^\)]*\)\s*=>|([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*function',
                'class': r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\{\extends]',
                'import': 'import\\s+.*?from\\s+["\'](.+?)["\']|require\\s*\\(["\'](.+?)["\']\\)',
                'exception': r'try\s*{|catch\s*\(|finally\s*{'
            },
            # 可以添加更多语言的模式
        }
    
    def analyze(self, code, language='python', context=''):
        """分析代码并提供反馈
        
        Args:
            code (str): 要分析的代码
            language (str): 代码语言，默认为python
            context (str): 代码上下文信息
            
        Returns:
            dict: 包含代码质量、建议、潜在问题和最佳实践的分析结果
        """
        start_time = time.time()
        logger.info(f"开始分析{language}代码，长度：{len(code)}字符")
        
        try:
            # 使用线程池并行执行多个分析任务
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交各种分析任务
                complexity_future = executor.submit(self._analyze_complexity, code, language)
                structure_future = executor.submit(self._analyze_structure, code, language)
                quality_future = executor.submit(self._analyze_quality, code, language)
                security_future = executor.submit(self._analyze_security, code, language)
                
                # 获取各个分析结果
                complexity_result = complexity_future.result()
                structure_result = structure_future.result()
                quality_result = quality_future.result()
                security_result = security_future.result()
            
            # 整合分析结果
            result = {
                'code_quality': quality_result,
                'complexity': complexity_result,
                'suggestions': self._generate_suggestions(code, language, quality_result, complexity_result),
                'potential_issues': security_result.get('issues', []),
                'best_practices': self._get_best_practices(language),
                'structure': structure_result
            }
            
            elapsed_time = time.time() - start_time
            logger.info(f"代码分析完成，耗时：{elapsed_time:.2f}秒")
            
            return result
            
        except Exception as e:
            logger.error(f"代码分析过程中发生错误: {str(e)}")
            # 返回基本分析结果和错误信息
            return {
                'code_quality': {
                    'maintainability': 'unknown',
                    'readability': 'unknown',
                    'efficiency': 'unknown'
                },
                'error': str(e),
                'suggestions': ['代码分析过程中发生错误，请检查代码格式是否正确'],
                'potential_issues': ['无法完成完整分析'],
                'best_practices': self._get_best_practices(language)
            }
    
    def _analyze_structure(self, code, language):
        """分析代码结构
        
        Args:
            code (str): 要分析的代码
            language (str): 代码语言
            
        Returns:
            dict: 代码结构分析结果
        """
        patterns = self.language_patterns.get(language, self.language_patterns['python'])
        
        # 提取函数和类
        functions = re.findall(patterns['function'], code, re.MULTILINE)
        classes = re.findall(patterns['class'], code, re.MULTILINE)
        imports = re.findall(patterns['import'], code, re.MULTILINE)
        
        # 计算代码行数和注释行数
        total_lines = len(code.split('\n'))
        comments = re.findall(patterns['comment'], code, re.MULTILINE)
        comment_lines = sum(c.count('\n') + 1 for c in comments)
        
        # 计算注释比例
        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
        
        return {
            'total_lines': total_lines,
            'comment_lines': comment_lines,
            'comment_ratio': comment_ratio,
            'function_count': len(functions),
            'class_count': len(classes),
            'import_count': len(imports),
            'functions': functions[:10],  # 限制返回数量
            'classes': classes[:5]        # 限制返回数量
        }
    
    def _analyze_quality(self, code, language):
        """分析代码质量
        
        Args:
            code (str): 要分析的代码
            language (str): 代码语言
            
        Returns:
            dict: 代码质量分析结果
        """
        patterns = self.language_patterns.get(language, self.language_patterns['python'])
        
        # 分析注释比例
        structure = self._analyze_structure(code, language)
        comment_ratio = structure['comment_ratio']
        
        # 分析异常处理
        exceptions = re.findall(patterns['exception'], code, re.MULTILINE)
        has_exception_handling = len(exceptions) > 0
        
        # 分析代码行长度
        lines = code.split('\n')
        long_lines = sum(1 for line in lines if len(line.strip()) > 100)
        long_line_ratio = long_lines / len(lines) if lines else 0
        
        # 评估可维护性
        if comment_ratio >= 0.2 and has_exception_handling and long_line_ratio < 0.1:
            maintainability = 'excellent'
        elif comment_ratio >= 0.1 and has_exception_handling and long_line_ratio < 0.2:
            maintainability = 'good'
        elif comment_ratio >= 0.05 and long_line_ratio < 0.3:
            maintainability = 'medium'
        else:
            maintainability = 'needs_improvement'
        
        # 评估可读性
        if comment_ratio >= 0.15 and long_line_ratio < 0.1:
            readability = 'excellent'
        elif comment_ratio >= 0.1 and long_line_ratio < 0.15:
            readability = 'good'
        elif comment_ratio >= 0.05 and long_line_ratio < 0.25:
            readability = 'medium'
        else:
            readability = 'needs_improvement'
        
        # 评估效率（简化版）
        efficiency = 'good'  # 默认值，实际应用中需要更复杂的分析
        
        return {
            'maintainability': maintainability,
            'readability': readability,
            'efficiency': efficiency,
            'metrics': {
                'comment_ratio': comment_ratio,
                'has_exception_handling': has_exception_handling,
                'long_line_ratio': long_line_ratio
            }
        }
    
    def _analyze_security(self, code, language):
        """分析代码安全性
        
        Args:
            code (str): 要分析的代码
            language (str): 代码语言
            
        Returns:
            dict: 代码安全性分析结果
        """
        issues = []
        
        # 检查常见安全问题（示例）
        if language == 'python':
            # 检查硬编码密码
            if re.search(r'password\s*=\s*["\'][^"\'\']+["\']', code, re.IGNORECASE):
                issues.append('可能存在硬编码的密码')
            
            # 检查SQL注入风险
            if re.search(r'execute\(["\']\s*SELECT.*?\%s', code, re.IGNORECASE):
                issues.append('可能存在SQL注入风险')
                
            # 检查不安全的反序列化
            if 'pickle.loads' in code or 'yaml.load(' in code:
                issues.append('使用了可能不安全的反序列化方法')
        
        elif language == 'javascript':
            # 检查eval使用
            if 'eval(' in code:
                issues.append('使用了不安全的eval()函数')
                
            # 检查XSS风险
            if 'innerHTML' in code or 'document.write(' in code:
                issues.append('可能存在XSS风险')
                
            # 检查不安全的正则表达式
            if re.search(r'RegExp\([^)]+\+', code):
                issues.append('使用了可能导致ReDoS攻击的正则表达式')
        
        return {
            'issues': issues,
            'risk_level': 'high' if len(issues) > 2 else 'medium' if len(issues) > 0 else 'low'
        }
    
    def _generate_suggestions(self, code, language, quality_result, complexity_result):
        """生成代码改进建议
        
        Args:
            code (str): 要分析的代码
            language (str): 代码语言
            quality_result (dict): 质量分析结果
            complexity_result (dict): 复杂度分析结果
            
        Returns:
            list: 改进建议列表
        """
        suggestions = []
        
        # 基于代码质量指标生成建议
        metrics = quality_result.get('metrics', {})
        
        if metrics.get('comment_ratio', 0) < 0.1:
            suggestions.append('增加代码注释以提高可读性和可维护性')
            
        if not metrics.get('has_exception_handling', False):
            suggestions.append('添加适当的异常处理机制以提高代码健壮性')
            
        if metrics.get('long_line_ratio', 0) > 0.2:
            suggestions.append('减少过长的代码行，每行保持在100个字符以内')
        
        # 基于复杂度指标生成建议
        if complexity_result.get('cyclomatic_complexity', 0) > 10:
            suggestions.append('降低函数的复杂度，考虑将复杂函数拆分为多个小函数')
            
        if complexity_result.get('max_nesting_depth', 0) > 3:
            suggestions.append('减少代码嵌套层级，过深的嵌套会降低代码可读性')
        
        # 语言特定建议
        if language == 'python':
            if 'except:' in code or 'except Exception:' in code:
                suggestions.append('避免捕获所有异常，应该捕获特定类型的异常')
                
            if not re.search(r'def\s+\w+\([^)]*\)\s*->\s*\w+:', code):
                suggestions.append('考虑使用类型提示增强代码可读性和可维护性')
        
        elif language == 'javascript':
            if 'var ' in code:
                suggestions.append('使用let和const替代var以避免变量提升问题')
                
            if not re.search(r'\s+async\s+', code) and ('then(' in code or 'catch(' in code):
                suggestions.append('考虑使用async/await替代Promise链以提高代码可读性')
        
        return suggestions
    
    def _get_best_practices(self, language):
        """获取语言特定的最佳实践
        
        Args:
            language (str): 代码语言
            
        Returns:
            list: 最佳实践列表
        """
        common_practices = [
            '编写清晰的文档和注释',
            '遵循一致的代码风格',
            '编写单元测试确保代码质量'
        ]
        
        language_specific = {
            'python': [
                '遵循PEP 8风格指南',
                '使用类型提示增强代码可读性',
                '使用虚拟环境管理依赖',
                '使用列表推导式提高代码简洁性'
            ],
            'javascript': [
                '使用ESLint保持代码质量',
                '优先使用const和let替代var',
                '使用解构赋值简化代码',
                '使用模块化设计提高可维护性'
            ],
            'java': [
                '遵循Java编码规范',
                '使用设计模式解决常见问题',
                '避免过度工程化',
                '使用Stream API处理集合操作'
            ]
        }
        
        return common_practices + language_specific.get(language, [])
    
    def _analyze_complexity(self, code, language='python'):
        """分析代码复杂度
        
        Args:
            code (str): 要分析的代码
            language (str): 代码语言
            
        Returns:
            dict: 代码复杂度分析结果
        """
        # 计算圈复杂度（简化版）
        patterns = self.language_patterns.get(language, self.language_patterns['python'])
        
        # 分析条件语句和循环
        if language == 'python':
            # 计算条件分支和循环
            if_count = len(re.findall(r'\s+if\s+|\s+elif\s+|\s+else\s*:', code, re.MULTILINE))
            loop_count = len(re.findall(r'\s+for\s+|\s+while\s+', code, re.MULTILINE))
            try_count = len(re.findall(r'\s+try\s*:', code, re.MULTILINE))
            
            # 计算函数数量
            function_count = len(re.findall(patterns['function'], code, re.MULTILINE))
            
            # 估算圈复杂度
            cyclomatic_complexity = 1 + if_count + loop_count + try_count
            
        elif language == 'javascript':
            # 计算条件分支和循环
            if_count = len(re.findall(r'\s+if\s*\(|\s+else\s+|\s+else\s+if\s*\(|\?', code, re.MULTILINE))
            loop_count = len(re.findall(r'\s+for\s*\(|\s+while\s*\(|\s+do\s*\{', code, re.MULTILINE))
            try_count = len(re.findall(r'\s+try\s*\{', code, re.MULTILINE))
            
            # 计算函数数量
            function_count = len(re.findall(patterns['function'], code, re.MULTILINE))
            
            # 估算圈复杂度
            cyclomatic_complexity = 1 + if_count + loop_count + try_count
            
        else:
            # 默认简单估算
            if_count = len(re.findall(r'if|else', code, re.IGNORECASE))
            loop_count = len(re.findall(r'for|while|do', code, re.IGNORECASE))
            cyclomatic_complexity = 1 + if_count + loop_count
            function_count = 0
        
        # 计算嵌套深度
        lines = code.split('\n')
        max_indent = 0
        current_indent = 0
        
        for line in lines:
            if line.strip() == '':
                continue
                
            # 计算缩进级别
            indent = len(line) - len(line.lstrip())
            if language == 'python':
                # Python使用缩进表示代码块
                current_indent = indent // 4  # 假设使用4个空格的缩进
            else:
                # 其他语言通过花括号计数
                current_indent += line.count('{') - line.count('}')
                
            max_indent = max(max_indent, current_indent)
        
        # 评估复杂度级别
        if cyclomatic_complexity <= 5:
            complexity_level = 'low'
        elif cyclomatic_complexity <= 10:
            complexity_level = 'medium'
        else:
            complexity_level = 'high'
            
        return {
            'cyclomatic_complexity': cyclomatic_complexity,
            'complexity_level': complexity_level,
            'max_nesting_depth': max_indent,
            'condition_count': if_count,
            'loop_count': loop_count,
            'function_count': function_count
        }
        
    def analyze_complexity(self, code, language='python'):
        """分析代码复杂度（公共API方法）
        
        Args:
            code (str): 要分析的代码
            language (str): 代码语言，默认为python
            
        Returns:
            dict: 包含循环复杂度、认知复杂度等指标的分析结果
        """
        logger.info(f"分析{language}代码复杂度")
        
        # 这里实现代码复杂度分析逻辑
        # 实际项目中可能会使用专门的复杂度分析工具
        
        # 示例返回结果
        return {
            'cyclomatic_complexity': 5,
            'cognitive_complexity': 7,
            'lines_of_code': len(code.split('\n')),
            'complexity_rating': 'medium',
            'recommendations': [
                '考虑将复杂的函数拆分为更小的函数',
                '减少嵌套层级以降低认知复杂度'
            ]
        }