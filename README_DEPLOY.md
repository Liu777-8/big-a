# 部署指南

## 📋 配置文件已创建

所有部署所需的配置文件已经创建完成：

- ✅ `backend/requirements.txt` - Python依赖
- ✅ `backend/app.py` - 已修改支持云端部署
- ✅ `frontend/.env.production` - 生产环境配置
- ✅ `frontend/vite.config.js` - 已更新构建配置
- ✅ `vercel.json` - Vercel部署配置
- ✅ `.gitignore` - Git忽略文件

## 🚀 部署步骤

### 第一步：部署后端到 Render

1. 访问 https://render.com
2. 用 GitHub 账号登录
3. 点击 "New +" → "Web Service"
4. 选择你的 GitHub 仓库
5. 配置如下：
   - **Name**: `stock-api`（或你喜欢的名字）
   - **Region**: `Singapore` (离中国最近)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py` ⚠️ 注意：不是 gunicorn
   - **Instance Type**: `Free`
6. 点击 "Create Web Service"
7. **等待部署完成**，记录下你的后端地址，例如：
   ```
   https://stock-api-xxxx.onrender.com
   ```

### 第二步：更新前端配置

1. 打开 `frontend/.env.production` 文件
2. 将 `VITE_API_URL` 的值改成你的 Render 后端地址：
   ```env
   VITE_API_URL=https://stock-api-xxxx.onrender.com
   ```

3. 打开 `vercel.json` 文件
4. 将两处 `your-api-name.onrender.com` 替换成你的真实后端地址

### 第三步：提交更改

```bash
git add .
git commit -m "配置部署文件"
git push
```

### 第四步：部署前端到 Vercel

1. 访问 https://vercel.com
2. 用 GitHub 账号登录
3. 点击 "Add New..." → "Project"
4. 选择你的 GitHub 仓库
5. 配置如下：
   - **Framework Preset**: `Vite`
   - **Root Directory**: **留空或选 `./`**（重要！因为 vercel.json 已配置构建命令）
   - **Build Command**: 留空（会自动使用 vercel.json 中的配置）
   - **Output Directory**: 留空（会自动使用 vercel.json 中的配置）
   - **Install Command**: 留空
   
   > ⚠️ **关键点**：由于前后端在同一个仓库，vercel.json 已经配置了正确的构建路径：
   > - `buildCommand: "cd frontend && npm install && npm run build"`
   > - `outputDirectory: "frontend/dist"`
   > 
   > 所以 Vercel 会自动进入 frontend 目录构建。

6. 点击 "Deploy"
7. 等待部署完成，你会得到一个网址：
   ```
   https://your-project-name.vercel.app
   ```

### 第五步：测试

访问 Vercel 给你的网址，测试所有功能是否正常！

## ⚠️ 注意事项

### Render 免费套餐限制
- 闲置 15 分钟后会自动休眠
- 首次访问需要 30-50 秒启动时间
- 每月 750 小时免费时间（足够个人使用）

### 如果遇到 CORS 错误
1.**gunicorn: command not found**：Start Command 应该用 `python app.py`
- Python 版本不对：确保使用 Python 3.11+
- 依赖安装失败：检查 `requirements.txt`
- 端口配置错误：确保使用了 `PORT` 环境变量
- **Root Directory 设置错误**：必须设置为 `backend`

### 如果前端构建失败
- **找不到 package.json**：检查 vercel.json 中的 buildCommand 是否包含 `cd frontend`
- **outputDirectory 错误**：确保设置为 `frontend/dist`
- **Root Directory 问题**：保持为根目录 `./`，让 vercel.json 处理路径
   - Value: 你的 Vercel 网址

### 如果后端启动失败
查看 Render 的日志（Logs 标签页），常见问题：
- Python 版本不对：确保使用 Python 3.11+
- 依赖安装失败：检查 `requirements.txt`
- 端口配置错误：确保使用了 `PORT` 环境变量

## 📱 后续更新

每次修改代码后：

```bash
git add .
git commit -m "更新说明"
git push
```

Render 和 Vercel 会自动重新部署！

## 💰 成本

完全免费！
- GitHub: 免费
- Render: 免费套餐
- Vercel: 免费套餐

## 🔗 有用的链接

- Render Dashboard: https://dashboard.render.com/
- Vercel Dashboard: https://vercel.com/dashboard
- GitHub Repo: https://github.com/你的用户名/你的仓库名

## 🆘 需要帮助？

如果部署过程中遇到问题，可以：
1. 查看 Render 的 Logs 标签页
2. 查看 Vercel 的 Deployments 页面的错误信息
3. 检查浏览器控制台的错误信息
