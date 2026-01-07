# 股票信息查询系统

基于 Python Flask + Vue3 + Element Plus + AKShare 的股票信息查询系统

## 项目结构

```
D_A/
├── backend/                 # 后端项目
│   ├── app.py              # Flask 应用主文件
│   ├── requirements.txt    # Python 依赖
│   └── README.md          # 后端说明文档
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── components/
│   │   │   └── StockQuery.vue  # 股票查询组件
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   ├── index.html         # HTML 模板
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # Vite 配置
└── README.md              # 项目总说明（本文件）
```

## 功能特性

✅ **已完成功能**：

- 个股信息查询（使用 `stock_individual_info_em`）
- 实时行情数据接口（预留，使用 `stock_zh_a_spot_em`）
- 美观的前端界面
- 跨域支持

🚧 **后续规划**：

- 更多股票数据查询功能
- 数据可视化图表
- 历史数据查询
- 股票对比功能

## 快速开始

### 1. 后端启动

进入后端目录并安装依赖：

```bash
cd backend
pip install -r requirements.txt
```

启动后端服务：

```bash
python app.py
```

后端服务将在 http://localhost:5000 启动

### 2. 前端启动

进入前端目录并安装依赖：

```bash
cd frontend
npm install
```

启动前端开发服务器：

```bash
npm run dev
```

前端将在 http://localhost:3000 启动

### 3. 访问应用

打开浏览器访问：http://localhost:3000

## 使用说明

1. 在输入框中输入股票代码（如：600000、000001）
2. 点击"查询"按钮或按回车键
3. 查看股票详细信息

## 技术栈

### 后端

- **Python 3.x**
- **Flask** - Web 框架
- **AKShare** - 金融数据接口
- **Flask-CORS** - 跨域支持

### 前端

- **Vue 3** - 前端框架
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **Axios** - HTTP 客户端

## API 接口说明

### 获取个股信息

```
GET /api/stock/info/{stock_code}
```

**参数**：

- `stock_code`：股票代码（如：600000）

**返回示例**：

```json
{
  "success": true,
  "code": "600000",
  "data": {
    "股票代码": "600000",
    "股票简称": "浦发银行",
    "总市值": "xxx",
    ...
  }
}
```

### 获取实时行情（预留）

```
GET /api/stock/realtime/{stock_code}
```

## 注意事项

1. 首次运行需要安装所有依赖
2. 确保 Python 和 Node.js 已正确安装
3. 后端需先启动，前端才能正常请求数据
4. 股票代码格式：6 位数字（如：600000、000001）
5. AKShare 数据来源于公开数据，请合理使用

## 开发环境要求

- Python >= 3.8
- Node.js >= 16.0
- pip
- npm 或 yarn

## 常见问题

**Q: 查询失败怎么办？**
A: 请检查：

- 股票代码是否正确（6 位数字）
- 后端服务是否正常运行
- 网络连接是否正常

**Q: 如何添加更多功能？**
A:

- 后端：在 `app.py` 中添加新的路由和 AKShare 接口
- 前端：在 `components` 目录下创建新组件

## 许可证

MIT License
