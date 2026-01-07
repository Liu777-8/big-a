# 股票信息查询后端 API

## 功能说明

基于 Flask 和 akshare 库实现的股票信息查询 API 服务。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python app.py
```

服务将在 http://localhost:5000 启动

## API 接口

### 1. 获取个股信息

**接口地址**: `GET /api/stock/info/{stock_code}`

**参数**:

- `stock_code`: 股票代码（如：600000）

**返回示例**:

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

### 2. 获取实时行情数据（预留）

**接口地址**: `GET /api/stock/realtime/{stock_code}`

**参数**:

- `stock_code`: 股票代码

**返回示例**:

```json
{
  "success": true,
  "code": "600000",
  "data": {
    "代码": "600000",
    "名称": "浦发银行",
    "最新价": "8.50",
    ...
  }
}
```
