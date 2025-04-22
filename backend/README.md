# AI代码助手后端

## API集成

本项目已集成阿里云千问大模型API和自定义API，可以用于提供更专业的编程问题解决方案。

### 配置步骤

1. API服务配置
   - 阿里云千问API：
     - 访问[阿里云官网](https://www.aliyun.com/)注册账号
     - 开通[灵积模型服务](https://help.aliyun.com/document_detail/2400395.html)并获取API密钥
   - 自定义API：
     - 准备您的自定义API服务和API密钥

2. 配置环境变量
   - 在`backend`目录下创建`.env`文件（可复制`.env.example`文件）
   - 填入API密钥：
     ```
     # 千问API配置
     QIANWEN_API_KEY=your_api_key_here
     QIANWEN_API_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
     QIANWEN_MODEL=qwen-turbo
     
     # 自定义API配置
     CUSTOM_API_KEY=your_custom_api_key_here
     CUSTOM_API_URL=your_custom_api_url_here
     CUSTOM_API_MODEL=your_custom_model_name
     ```

3. 安装依赖
   ```
   pip install -r requirements.txt
   ```

4. 启动服务
   ```
   python app.py
   ```

### 使用方法

在前端界面的"问题解决"页面中：
- 勾选"使用阿里云千问API"选项，即可使用千问大模型来解决编程问题
- 勾选"使用自定义API"选项，即可使用您的自定义API来解决编程问题

### 注意事项

- 千问API为付费服务，使用时会产生费用
- 所有API密钥请妥善保管，不要泄露给他人
- 如遇到API调用问题，请查看日志获取详细错误信息
- 自定义API需要按照指定的请求和响应格式进行配置