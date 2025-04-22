import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.code_analyzer import CodeAnalyzer

class TestCodeAnalyzer(unittest.TestCase):
    """代码分析器测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.analyzer = CodeAnalyzer(max_workers=2)
        
        # 测试用Python代码
        self.python_code = """
        def calculate_sum(a, b):
            # 计算两个数的和
            return a + b
            
        def process_data(data_list):
            result = []
            for item in data_list:
                try:
                    processed = item * 2
                    result.append(processed)
                except Exception as e:
                    print(f"处理数据时出错: {e}")
            return result
        """
        
        # 测试用JavaScript代码
        self.js_code = """
        function calculateSum(a, b) {
            // 计算两个数的和
            return a + b;
        }
        
        function processData(dataList) {
            const result = [];
            for (let i = 0; i < dataList.length; i++) {
                try {
                    const processed = dataList[i] * 2;
                    result.push(processed);
                } catch (error) {
                    console.error(`处理数据时出错: ${error}`);
                }
            }
            return result;
        }
        """
    
    def test_analyze_python(self):
        """测试Python代码分析"""
        result = self.analyzer.analyze(self.python_code, 'python')
        
        # 验证结果包含预期的键
        self.assertIn('code_quality', result)
        self.assertIn('suggestions', result)
        self.assertIn('potential_issues', result)
        self.assertIn('best_practices', result)
        self.assertIn('complexity', result)
        self.assertIn('structure', result)
        
        # 验证结构分析
        structure = result['structure']
        self.assertGreater(structure['total_lines'], 0)
        self.assertGreater(structure['function_count'], 0)
        self.assertEqual(len(structure['functions']), 2)  # 应该检测到两个函数
        
        # 验证复杂度分析
        complexity = result['complexity']
        self.assertIn('cyclomatic_complexity', complexity)
        self.assertIn('complexity_level', complexity)
        
    def test_analyze_javascript(self):
        """测试JavaScript代码分析"""
        result = self.analyzer.analyze(self.js_code, 'javascript')
        
        # 验证结果包含预期的键
        self.assertIn('code_quality', result)
        self.assertIn('complexity', result)
        
        # 验证结构分析
        structure = result['structure']
        self.assertGreater(structure['total_lines'], 0)
        self.assertGreater(structure['function_count'], 0)
        
    def test_analyze_complexity(self):
        """测试代码复杂度分析"""
        result = self.analyzer._analyze_complexity(self.python_code, 'python')
        
        self.assertIn('cyclomatic_complexity', result)
        self.assertIn('complexity_level', result)
        self.assertIn('max_nesting_depth', result)
        self.assertIn('condition_count', result)
        self.assertIn('loop_count', result)
        
    def test_analyze_security(self):
        """测试代码安全性分析"""
        # 包含安全问题的代码
        insecure_code = """
        def process_user_data(user_id):
            password = "hardcoded_password123"
            query = f"SELECT * FROM users WHERE id = {user_id}"
            cursor.execute(query)  # 潜在的SQL注入
            return pickle.loads(data)  # 不安全的反序列化
        """
        
        result = self.analyzer._analyze_security(insecure_code, 'python')
        
        self.assertIn('issues', result)
        self.assertIn('risk_level', result)
        self.assertGreater(len(result['issues']), 0)  # 应该检测到至少一个安全问题

if __name__ == '__main__':
    unittest.main()