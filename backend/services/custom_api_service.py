import logging
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class CustomAPIService:
    """自定义API服务类，用于与您的自定义API通信"""
    
    def __init__(self):
        """初始化自定义API服务"""
        self.api_key = os.getenv('CUSTOM_API_KEY')
        self.api_url = os.getenv('CUSTOM_API_URL')
        self.model = os.getenv('CUSTOM_API_MODEL', 'default-model')
        
        if not self.api_key or not self.api_url:
            logger.warning("未设置CUSTOM_API_KEY或CUSTOM_API_URL环境变量，自定义API将无法正常工作")
    
    def generate_response(self, prompt, max_tokens=2048):
        """调用自定义API生成回答
        
        Args:
            prompt (str): 提问内容
            max_tokens (int): 最大生成token数
            
        Returns:
            dict: 包含生成的回答和状态信息
        """
        if not self.api_key or not self.api_url:
            return {
                'success': False,
                'error': '未配置自定义API密钥或URL',
                'content': '系统未正确配置自定义API，请联系管理员设置CUSTOM_API_KEY和CUSTOM_API_URL环境变量。'
            }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 根据您的API要求调整payload结构
        payload = {
            'model': self.model,
            'prompt': prompt,
            'max_tokens': max_tokens
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 根据您的API响应格式调整解析逻辑
            if 'content' in result:
                return {
                    'success': True,
                    'content': result['content']
                }
            else:
                logger.error(f"自定义API返回了意外的响应格式: {result}")
                return {
                    'success': False,
                    'error': '自定义API返回了意外的响应格式',
                    'content': '处理请求时发生错误，请稍后再试。'
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"调用自定义API时发生错误: {str(e)}")
            return {
                'success': False,
                'error': f'API请求错误: {str(e)}',
                'content': '连接自定义API时发生错误，请稍后再试。'
            }
    
    def solve_problem(self, problem_description, code_context='', language='python'):
        """使用自定义API解决编程问题
        
        Args:
            problem_description (str): 问题描述
            code_context (str): 代码上下文，默认为空
            language (str): 代码语言，默认为python
            
        Returns:
            dict: 包含解决方案代码、解释和额外资源的结果
        """
        # 构建提示词
        prompt = f"""请解决以下{language}编程问题：

问题描述：
{problem_description}

"""
        
        if code_context:
            prompt += f"代码上下文：\n```{language}\n{code_context}\n```\n\n"
        
        prompt += """请提供以下格式的回答：
1. 解决方案代码
2. 详细解释
3. 相关资源或参考链接

请确保代码可以直接运行，并提供清晰的注释。"""
        
        # 调用自定义API
        response = self.generate_response(prompt)
        
        if not response['success']:
            return {
                'solution_code': '# 生成解决方案时发生错误',
                'explanation': response['content'],
                'additional_resources': ['请检查系统配置或稍后再试']
            }
        
        # 处理返回的内容
        content = response['content']
        
        # 提取解决方案代码、解释和资源
        solution_code = '# 自定义API生成的解决方案\n'
        explanation = '自定义API的解释：\n'
        additional_resources = ['自定义API提供的资源']
        
        # 尝试从内容中提取代码块
        if '```' in content:
            code_blocks = content.split('```')
            if len(code_blocks) > 1:
                # 提取第一个代码块作为解决方案代码
                solution_code = code_blocks[1].strip()
                if solution_code.startswith(language):
                    solution_code = solution_code[len(language):].strip()
        
        # 使用完整内容作为解释
        explanation = content
        
        return {
            'solution_code': solution_code,
            'explanation': explanation,
            'additional_resources': additional_resources
        }