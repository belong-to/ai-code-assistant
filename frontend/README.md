# AI代码助手前端

## 项目介绍

这是AI代码助手的前端部分，使用HTML、CSS和Vue.js构建。该应用提供了一个用户友好的界面，用于与AI代码助手的后端API进行交互，实现代码分析、代码建议和问题解决功能。

## 功能特点

- **代码分析**：分析代码质量，找出潜在问题和改进空间
- **代码建议**：获取针对代码的具体改进建议和最佳实践
- **问题解决**：描述编程问题，获取解决方案和解释

## 技术栈

- HTML5
- CSS3
- Vue.js 2.x (通过CDN引入)
- Axios (用于API请求)

## 项目结构

```
frontend/
├── index.html          # 主HTML文件
├── styles/             # CSS样式文件
│   └── main.css        # 主样式文件
├── scripts/            # JavaScript文件
│   └── main.js         # 主脚本文件
└── README.md           # 项目说明文档
```

## 使用方法

1. 确保后端服务已启动并运行在 http://localhost:5000
2. 使用浏览器打开 `index.html` 文件
3. 在界面上选择需要的功能：代码分析、代码建议或问题解决
4. 填写相应的表单并提交
5. 查看结果

## API接口

前端应用与以下后端API接口交互：

- 代码分析：`/api/code-analysis/analyze`
- 代码建议：`/api/code-suggestion/suggest`
- 问题解决：`/api/problem-solving/solve`

## 响应式设计

应用采用响应式设计，适配不同尺寸的屏幕，包括桌面和移动设备。