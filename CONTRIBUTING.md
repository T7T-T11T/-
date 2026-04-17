# 贡献指南

感谢你考虑为在线投票系统项目做出贡献！以下是一些指导原则，帮助你顺利参与项目开发。

## 代码贡献流程

1. **Fork 仓库**
   - 在 GitHub 上 fork 本项目到你的个人账号

2. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/voting-system.git
   cd voting-system
   ```

3. **创建分支**
   - 为你的功能或修复创建一个新分支
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **开发和测试**
   - 实现你的功能或修复
   - 确保代码符合项目的代码风格
   - 测试你的更改，确保它们正常工作

6. **提交更改**
   - 使用清晰的提交信息，遵循 Conventional Commits 规范
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   # 或
   git commit -m "fix: 修复问题描述"
   ```

7. **推送到远程分支**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **创建 Pull Request**
   - 在 GitHub 上打开一个 Pull Request
   - 提供清晰的描述，说明你的更改内容和目的
   - 等待项目维护者的审核

## 提交规范

我们使用 Conventional Commits 规范来格式化提交信息。提交信息应该遵循以下格式：

```
<类型>: <描述>

[可选的正文]

[可选的页脚]
```

### 类型

- `feat`: 新功能
- `fix`: 修复问题
- `docs`: 文档更改
- `style`: 代码风格更改（不影响功能）
- `refactor`: 代码重构（不添加新功能或修复问题）
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的更改

### 示例

```
feat: 添加投票结果导出功能

添加了将投票结果导出为 CSV 文件的功能，管理员可以在投票详情页面下载结果。

fix: 修复防重复投票机制

修复了在某些情况下用户可以重复投票的问题，增强了基于 IP 地址和浏览器存储的验证。
```

## 代码风格

- 遵循 PEP 8 编码规范
- 使用 4 个空格进行缩进
- 保持代码简洁明了
- 添加适当的注释，特别是对于复杂的逻辑
- 确保所有函数和方法都有适当的文档字符串

## 报告问题

如果你发现任何问题或有建议，请在 GitHub 仓库中创建 Issue。在创建 Issue 时，请提供：

- 清晰的标题和描述
- 重现问题的步骤
- 期望的行为
- 实际的行为
- 环境信息（操作系统、Python 版本等）
- 相关的错误信息或截图

## 开发环境设置

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   - 复制 `.env.example` 为 `.env`
   - 修改 `.env` 文件中的配置

3. **初始化数据库**
   ```bash
   python init_db.py
   ```

4. **启动开发服务器**
   ```bash
   python app.py
   ```

## 行为准则

请参考 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 文件，了解我们的行为准则。

## 联系我们

如果你有任何问题或需要帮助，可以通过 GitHub Issues 或其他方式联系项目维护者。

感谢你的贡献！