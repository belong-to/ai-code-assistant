import logging
import requests
import os
import json
import time
from functools import lru_cache
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class QianwenService:
    """阿里云千问API服务类，用于与千问大模型API通信"""
    
    def __init__(self):
        """初始化千问服务"""
        self.api_key = os.getenv('QIANWEN_API_KEY','************')
        self.api_url = os.getenv('QIANWEN_API_URL', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation')
        self.model = os.getenv('QIANWEN_MODEL', 'qwen-turbo')
        self.request_timeout = int(os.getenv('QIANWEN_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('QIANWEN_MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('QIANWEN_RETRY_DELAY', '2'))
        self.cache_enabled = os.getenv('ENABLE_RESPONSE_CACHE', 'true').lower() == 'true'
        
        if not self.api_key:
            logger.warning("未设置QIANWEN_API_KEY环境变量，千问API将无法正常工作")
    
    @lru_cache(maxsize=100)
    def _cached_generate_response(self, prompt_hash, max_tokens):
        """带缓存的响应生成（内部方法）
        
        Args:
            prompt_hash (str): 提问内容的哈希值，用于缓存键
            max_tokens (int): 最大生成token数
            
        Returns:
            dict: 包含生成的回答和状态信息
        """
        # 此方法由generate_response调用，实现实际的API调用逻辑
        logger.debug(f"缓存未命中，调用千问API生成回答，prompt_hash={prompt_hash[:8]}...")
        return self._call_qianwen_api(prompt_hash, max_tokens)
    
    def _call_qianwen_api(self, prompt, max_tokens):
        """执行实际的千问API调用
        
        Args:
            prompt (str): 提问内容
            max_tokens (int): 最大生成token数
            
        Returns:
            dict: API响应结果
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-Request-ID': f'ai-code-assistant-{int(time.time())}'  # 添加请求ID便于跟踪
        }
        
        payload = {
            'model': self.model,
            'input': {
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            },
            'parameters': {
                'max_tokens': max_tokens
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"调用千问API (尝试 {attempt+1}/{self.max_retries})")
                start_time = time.time()
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
                    json=payload,
                    timeout=self.request_timeout
                )
                elapsed_time = time.time() - start_time
                logger.info(f"千问API响应时间: {elapsed_time:.2f}秒")
                
                response.raise_for_status()
                result = response.json()
                
                # 解析千问API的响应
                if 'output' in result and 'text' in result['output']:
                    return {
                        'success': True,
                        'content': result['output']['text'],
                        'model': self.model,
                        'response_time': elapsed_time
                    }
                else:
                    logger.error(f"千问API返回了意外的响应格式: {json.dumps(result, ensure_ascii=False)}")
                    return {
                        'success': False,
                        'error': '千问API返回了意外的响应格式',
                        'content': '处理请求时发生错误，请稍后再试。',
                        'raw_response': result
                    }
                    
            except requests.exceptions.Timeout:
                logger.warning(f"千问API请求超时 (尝试 {attempt+1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return {
                    'success': False,
                    'error': 'API请求超时',
                    'content': '连接千问API时超时，请稍后再试。'
                }
                
            except requests.exceptions.RequestException as e:
                logger.error(f"调用千问API时发生错误: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return {
                    'success': False,
                    'error': f'API请求错误: {str(e)}',
                    'content': '连接千问API时发生错误，请稍后再试。'
                }
    
    def generate_response(self, prompt, max_tokens=2048):
        """调用千问API生成回答
        
        Args:
            prompt (str): 提问内容
            max_tokens (int): 最大生成token数
            
        Returns:
            dict: 包含生成的回答和状态信息
        """
        if not self.api_key:
            logger.error("未配置千问API密钥，无法处理请求")
            return {
                'success': False,
                'error': '未配置千问API密钥',
                'content': '系统未正确配置千问API，请联系管理员设置QIANWEN_API_KEY环境变量。'
            }
        
        # 使用缓存机制（如果启用）
        if self.cache_enabled:
            # 创建提示词的哈希值作为缓存键
            # 注意：在实际应用中，可能需要更复杂的缓存键生成策略
            prompt_hash = str(hash(prompt))
            return self._cached_generate_response(prompt_hash, max_tokens)
        else:
            return self._call_qianwen_api(prompt, max_tokens)
    
    def solve_problem(self, problem_description, code_context='', language='python'):
        """使用千问API解决编程问题
        
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
        
        # 调用千问API
        response = self.generate_response(prompt)
        
        if not response['success']:
            return {
                'solution_code': '# 生成解决方案时发生错误',
                'explanation': response['content'],
                'additional_resources': ['请检查系统配置或稍后再试']
            }
        
        # 简单处理返回的内容，实际项目中可能需要更复杂的解析
        content = response['content']
        
        # 提取解决方案代码、解释和资源
        # 这里使用简单的分割方法，实际项目中可能需要更复杂的解析
        solution_code = '# 千问AI生成的解决方案\n'
        explanation = '千问AI的解释：\n'
        additional_resources = ['千问AI提供的资源']
        
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