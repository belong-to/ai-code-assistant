import logging
import re
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

# 支持的编程语言列表
SUPPORTED_LANGUAGES = [
    'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'csharp', 
    'go', 'ruby', 'php', 'swift', 'kotlin', 'rust', 'scala', 'perl',
    'html', 'css', 'sql'
]

# 每种语言的最大代码长度限制（字符数）
MAX_CODE_LENGTH = 150000

# 每种语言的文件扩展名
LANGUAGE_EXTENSIONS = {
    'python': ['.py', '.pyw', '.pyx'],
    'javascript': ['.js', '.jsx', '.mjs'],
    'typescript': ['.ts', '.tsx'],
    'java': ['.java'],
    'c': ['.c', '.h'],
    'cpp': ['.cpp', '.hpp', '.cc', '.hh', '.cxx', '.hxx'],
    'csharp': ['.cs'],
    'go': ['.go'],
    'ruby': ['.rb'],
    'php': ['.php'],
    'swift': ['.swift'],
    'kotlin': ['.kt', '.kts'],
    'rust': ['.rs'],
    'scala': ['.scala'],
    'perl': ['.pl', '.pm'],
    'html': ['.html', '.htm'],
    'css': ['.css', '.scss', '.sass', '.less'],
    'sql': ['.sql']
}

def validate_code_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证代码输入数据
    
    Args:
        data (dict): 包含代码和相关参数的输入数据
        
    Returns:
        dict: 包含验证结果和错误消息的字典
    """
    validation_errors = []
    
    # 检查是否提供了代码
    if 'code' not in data:
        logger.warning("缺少必要参数 'code'")
        return {
            'valid': False,
            'message': "缺少必要参数 'code'",
            'field': 'code'
        }
    
    if not data['code']:
        logger.warning("代码内容为空")
        validation_errors.append("代码内容不能为空")
    
    # 检查语言参数是否有效（如果提供）
    if 'language' in data and data['language']:
        if data['language'] not in SUPPORTED_LANGUAGES:
            logger.warning(f"不支持的语言: {data['language']}")
            validation_errors.append(
                f"不支持的语言: {data['language']}。支持的语言包括: {', '.join(SUPPORTED_LANGUAGES)}"
            )
    else:
        # 如果未提供语言，尝试从文件扩展名或代码内容推断
        if 'filename' in data and data['filename']:
            data['language'] = detect_language_from_filename(data['filename'])
            logger.info(f"从文件名推断语言: {data['language']}")
    
    # 检查代码长度是否在合理范围内
    if 'code' in data and len(data['code']) > MAX_CODE_LENGTH:
        logger.warning(f"代码长度超过限制: {len(data['code'])} > {MAX_CODE_LENGTH}")
        validation_errors.append(
            f"代码长度超过限制，请提供不超过{MAX_CODE_LENGTH//1000}K字符的代码片段"
        )
    
    # 检查上下文参数（如果提供）
    if 'context' in data and data['context'] and len(data['context']) > MAX_CODE_LENGTH:
        logger.warning(f"上下文长度超过限制: {len(data['context'])} > {MAX_CODE_LENGTH}")
        validation_errors.append(
            f"上下文长度超过限制，请提供不超过{MAX_CODE_LENGTH//1000}K字符的上下文"
        )
    
    # 如果有验证错误，返回第一个错误
    if validation_errors:
        return {
            'valid': False,
            'message': validation_errors[0],
            'all_errors': validation_errors
        }
    
    # 所有验证通过
    return {
        'valid': True,
        'message': ""
    }

def detect_language_from_filename(filename: str) -> str:
    """从文件名推断编程语言
    
    Args:
        filename (str): 文件名或文件路径
        
    Returns:
        str: 推断的编程语言，如果无法推断则返回'python'作为默认值
    """
    if not filename:
        return 'python'  # 默认为Python
    
    # 获取文件扩展名
    extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    
    # 根据扩展名查找对应的语言
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if extension in extensions:
            return language
    
    # 无法确定语言时的默认值
    return 'python'