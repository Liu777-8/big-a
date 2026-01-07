from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import akshare as ak
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)

# 配置CORS - 简化配置，允许所有来源
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"],
     supports_credentials=False)

def format_numeric_value(value, decimals=3):
    """
    格式化数值，保留指定位数小数
    """
    if value is None or value == '' or value == '-':
        return value
    
    try:
        # 尝试转换为浮点数
        num = float(value)
        # 保留指定位小数
        return round(num, decimals)
    except (ValueError, TypeError):
        # 如果不是数值，返回原值
        return value

def format_dict_values(data, decimals=3):
    """
    格式化字典中的所有数值，但保留股票代码为字符串
    """
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            # 股票代码相关字段保持字符串格式，不进行数值转换
            if k in ['代码', '股票代码', 'code', 'stock_code', '证券代码']:
                result[k] = str(v).zfill(6) if v else v  # 确保6位，不足前面补0
            else:
                result[k] = format_numeric_value(v, decimals)
        return result
    return data

def format_list_values(data_list, decimals=3):
    """
    格式化列表中所有字典的数值
    """
    if isinstance(data_list, list):
        return [format_dict_values(item, decimals) for item in data_list]
    return data_list

@app.route('/')
def index():
    return jsonify({
        'message': '股票信息查询 API',
        'version': '1.0.0'
    })

@app.route('/api/stock/info', methods=['GET'])
def get_stock_info():
    """
    获取个股综合信息（基本信息 + 实时数据）
    参数: code - 股票代码，如：600000（查询参数）
    """
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({'success': False, 'message': '缺少股票代码参数'}), 400
    
    try:
        info_result = {}
        realtime_data = None
        
        # 1. 获取个股基本信息
        try:
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            for index, row in stock_info.iterrows():
                info_result[row['item']] = format_numeric_value(row['value'])
        except Exception as e:
            print(f"基本信息获取失败: {e}")
            # 基本信息失败时返回空字典，继续尝试获取实时数据
        
        # 2. 获取实时行情数据 - 使用单个股票查询避免超时
        try:
            # 使用更轻量级的方法：获取单日历史数据作为实时数据
            today = datetime.now().strftime('%Y%m%d')
            yesterday = (datetime.now() - timedelta(days=3)).strftime('%Y%m%d')
            
            df_hist = ak.stock_zh_a_hist(
                symbol=stock_code,
                period='daily',
                start_date=yesterday,
                end_date=today,
                adjust=''
            )
            
            if not df_hist.empty:
                # 获取最新一条数据
                latest = df_hist.iloc[-1].to_dict()
                # 构造类似实时数据的格式
                realtime_data = {
                    '代码': stock_code,
                    '名称': info_result.get('股票简称', stock_code),
                    '最新价': format_numeric_value(latest.get('收盘')),
                    '涨跌幅': format_numeric_value(latest.get('涨跌幅')),
                    '涨跌额': format_numeric_value(latest.get('涨跌额')),
                    '成交量': format_numeric_value(latest.get('成交量')),
                    '成交额': format_numeric_value(latest.get('成交额')),
                    '振幅': format_numeric_value(latest.get('振幅')),
                    '最高': format_numeric_value(latest.get('最高')),
                    '最低': format_numeric_value(latest.get('最低')),
                    '今开': format_numeric_value(latest.get('开盘')),
                    '昨收': format_numeric_value(latest.get('昨收', latest.get('收盘'))),
                    '换手率': format_numeric_value(latest.get('换手率')),
                }
        except Exception as e:
            print(f"实时数据获取失败: {e}")
            # 实时数据获取失败，保持为None
        
        # 如果两个数据都为空，返回错误
        if not info_result and not realtime_data:
            return jsonify({
                'success': False,
                'message': '无法获取股票信息，请检查股票代码是否正确'
            }), 404
        
        return jsonify({
            'success': True,
            'code': stock_code,
            'data': {
                'basic_info': info_result,
                'realtime_data': realtime_data
            }
        })
    except Exception as e:
        print(f"接口异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500

@app.route('/api/stock/history', methods=['GET'])
def get_stock_history():
    """
    获取历史行情数据
    参数: 
        code - 股票代码（查询参数）
        start_date - 开始日期 (format: 20210101)
        end_date - 结束日期 (format: 20211231)
        period - 周期 (daily, weekly, monthly)
        adjust - 复权类型 (qfq-前复权, hfq-后复权, 空-不复权)
    """
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({'success': False, 'message': '缺少股票代码参数'}), 400
    
    try:
        start_date = request.args.get('start_date', '20240101')
        end_date = request.args.get('end_date', '20241231')
        period = request.args.get('period', 'daily')
        adjust = request.args.get('adjust', '')
        
        # 获取历史行情数据
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        
        if df.empty:
            return jsonify({
                'success': False,
                'message': '未找到历史数据'
            }), 404
        
        # 转换为列表格式并格式化数值
        result = format_list_values(df.to_dict('records'))
        
        return jsonify({
            'success': True,
            'code': stock_code,
            'count': len(result),
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 400

@app.route('/api/stock/limit-up/previous', methods=['GET'])
def get_previous_limit_up():
    """
    获取涨停股票池
    参数: date - 日期 (format: 20241009)，可选，默认为今天或最近交易日
    """
    try:
        # 获取日期参数
        date_param = request.args.get('date', '')
        
        if date_param:
            # 如果指定了日期，直接使用
            target_date = datetime.strptime(date_param, '%Y%m%d')
        else:
            # 如果没有指定日期，从今天开始查找最近的交易日
            target_date = datetime.now()
        
        # 尝试获取数据，如果是周末或节假日则往前推
        max_attempts = 10  # 最多尝试10天，覆盖周末和长假
        df = None
        
        for i in range(max_attempts):
            current_date = target_date - timedelta(days=i)
            
            # 跳过周末
            if current_date.weekday() >= 5:  # 5=周六, 6=周日
                continue
            
            date_str = current_date.strftime('%Y%m%d')
            
            try:
                df = ak.stock_zt_pool_em(date=date_str)
                
                if not df.empty:
                    # 找到有数据的交易日
                    date_param = date_str
                    break
            except Exception as e:
                # 该日期可能无数据（节假日），继续尝试前一天
                print(f"尝试日期 {date_str} 失败: {e}")
                continue
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'message': f'未找到最近{max_attempts}天内的涨停数据，可能遇到长假期'
            }), 404
        
        # 转换为列表格式并格式化数值
        result = format_list_values(df.to_dict('records'))
        
        # 格式化日期显示
        display_date = datetime.strptime(date_param, '%Y%m%d').strftime('%Y年%m月%d日')
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result,
            'date': date_param,
            'display_date': display_date,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 400

@app.route('/api/stock/strong', methods=['GET'])
def get_strong_stocks():
    """
    获取强势股票池
    参数: date - 日期 (format: 20241009)，可选，默认为今天或最近交易日
    """
    try:
        # 获取日期参数
        date_param = request.args.get('date', '')
        
        if date_param:
            # 如果指定了日期，直接使用
            target_date = datetime.strptime(date_param, '%Y%m%d')
        else:
            # 如果没有指定日期，从今天开始查找最近的交易日
            target_date = datetime.now()
        
        # 尝试获取数据，如果是周末或节假日则往前推
        max_attempts = 10
        df = None
        
        for i in range(max_attempts):
            current_date = target_date - timedelta(days=i)
            
            # 跳过周末
            if current_date.weekday() >= 5:
                continue
            
            date_str = current_date.strftime('%Y%m%d')
            
            try:
                df = ak.stock_zt_pool_strong_em(date=date_str)
                
                if not df.empty:
                    date_param = date_str
                    break
            except Exception as e:
                print(f"尝试日期 {date_str} 失败: {e}")
                continue
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'message': f'未找到最近{max_attempts}天内的强势股票数据'
            }), 404
        
        # 转换为列表格式并格式化数值
        result = format_list_values(df.to_dict('records'))
        
        # 格式化日期显示
        display_date = datetime.strptime(date_param, '%Y%m%d').strftime('%Y年%m月%d日')
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result,
            'date': date_param,
            'display_date': display_date,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 400

@app.route('/api/stock/limit-down', methods=['GET'])
def get_limit_down_stocks():
    """
    获取跌停股票池
    参数: date - 日期 (format: 20241009)，可选，默认为今天或最近交易日
    """
    try:
        # 获取日期参数
        date_param = request.args.get('date', '')
        
        if date_param:
            # 如果指定了日期，直接使用
            target_date = datetime.strptime(date_param, '%Y%m%d')
        else:
            # 如果没有指定日期，从今天开始查找最近的交易日
            target_date = datetime.now()
        
        # 尝试获取数据，如果是周末或节假日则往前推
        max_attempts = 10
        df = None
        
        for i in range(max_attempts):
            current_date = target_date - timedelta(days=i)
            
            # 跳过周末
            if current_date.weekday() >= 5:
                continue
            
            date_str = current_date.strftime('%Y%m%d')
            
            try:
                df = ak.stock_zt_pool_dtgc_em(date=date_str)
                
                if not df.empty:
                    date_param = date_str
                    break
            except Exception as e:
                print(f"尝试日期 {date_str} 失败: {e}")
                continue
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'message': f'未找到最近{max_attempts}天内的跌停股票数据'
            }), 404
        
        # 转换为列表格式并格式化数值
        result = format_list_values(df.to_dict('records'))
        
        # 格式化日期显示
        display_date = datetime.strptime(date_param, '%Y%m%d').strftime('%Y年%m月%d日')
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result,
            'date': date_param,
            'display_date': display_date,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 400

@app.route('/api/stock/download', methods=['GET'])
def download_stock_data():
    """
    下载股票历史数据为Excel
    参数: 
        code - 股票代码（查询参数）
        days - 天数，默认7天
    """
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({'success': False, 'message': '缺少股票代码参数'}), 400
    
    try:
        # 获取天数参数，默认7天
        days = int(request.args.get('days', 7))
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 1. 获取基本信息
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        
        # 2. 获取实时数据
        df_spot = ak.stock_zh_a_spot_em()
        realtime_data = df_spot[df_spot['代码'] == stock_code]
        
        if realtime_data.empty:
            return jsonify({
                'success': False,
                'message': '未找到该股票代码'
            }), 404
        
        stock_name = realtime_data['名称'].values[0]
        
        # 3. 获取历史数据
        history_df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period='daily',
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d'),
            adjust=''
        )
        
        # 格式化数值列（保留3位小数）
        for col in stock_info.columns:
            if col == 'value':
                stock_info[col] = stock_info[col].apply(lambda x: format_numeric_value(x))
        
        # 格式化实时数据的数值列
        for col in realtime_data.columns:
            if col not in ['代码', '名称', '所属行业']:
                realtime_data[col] = realtime_data[col].apply(lambda x: format_numeric_value(x))
        
        # 格式化历史数据的数值列
        if not history_df.empty:
            for col in history_df.columns:
                if col != '日期':
                    history_df[col] = history_df[col].apply(lambda x: format_numeric_value(x))
        
        # 4. 获取今天的分时数据
        intraday_df = None
        try:
            intraday_df = ak.stock_intraday_em(symbol=stock_code)
            if not intraday_df.empty:
                # 格式化分时数据的数值列
                for col in intraday_df.columns:
                    if col not in ['时间']:
                        intraday_df[col] = intraday_df[col].apply(lambda x: format_numeric_value(x))
        except Exception as e:
            print(f"获取分时数据失败: {e}")
        
        # 创建Excel文件
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 工作表1: 基本信息
            stock_info.to_excel(writer, sheet_name='基本信息', index=False)
            
            # 工作表2: 实时数据（添加当前时间）
            # 添加查询时间列
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            realtime_data_copy = realtime_data.copy()
            realtime_data_copy.insert(0, '查询时间', current_time)
            realtime_data_copy.to_excel(writer, sheet_name='实时数据', index=False)
            
            # 工作表3: 今日分时数据
            if intraday_df is not None and not intraday_df.empty:
                intraday_df.to_excel(writer, sheet_name='今日分时数据', index=False)
            
            # 工作表4: 历史数据
            if not history_df.empty:
                sheet_name = f'近{days}天历史数据' if days <= 31 else f'近{days//30}个月历史数据'
                history_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)
        
        # 生成文件名
        period_text = f'近{days}天' if days <= 31 else f'近{days//30}个月'
        filename = f"{stock_code}_{stock_name}_{period_text}数据_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下载失败: {str(e)}'
        }), 400

@app.route('/api/stock/download-limit-up', methods=['GET'])
def download_limit_up_data():
    """
    下载涨停股票池数据为Excel
    参数: 
        date - 日期，格式 YYYYMMDD，可选
    """
    try:
        # 获取日期参数
        date_param = request.args.get('date', '')
        
        if date_param:
            target_date = datetime.strptime(date_param, '%Y%m%d')
        else:
            target_date = datetime.now()
        
        # 尝试获取数据
        max_attempts = 10
        df = None
        
        for i in range(max_attempts):
            current_date = target_date - timedelta(days=i)
            
            if current_date.weekday() >= 5:
                continue
            
            date_str = current_date.strftime('%Y%m%d')
            
            try:
                df = ak.stock_zt_pool_em(date=date_str)
                
                if not df.empty:
                    date_param = date_str
                    break
            except Exception as e:
                print(f"尝试日期 {date_str} 失败: {e}")
                continue
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'message': '未找到涨停数据'
            }), 404
        
        # 格式化数值列
        for col in df.columns:
            if col not in ['代码', '名称', '所属行业', '首次封板时间', '最后封板时间', '涨停统计', '涨停开板']:
                df[col] = df[col].apply(lambda x: format_numeric_value(x))
        
        # 添加查询时间列
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.insert(0, '查询时间', current_time)
        
        # 创建Excel文件
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='涨停股票池', index=False)
        
        output.seek(0)
        
        # 格式化日期显示
        display_date = datetime.strptime(date_param, '%Y%m%d').strftime('%Y%m%d')
        filename = f"涨停股票池_{display_date}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下载失败: {str(e)}'
        }), 400

@app.route('/api/stock/download-limit-down', methods=['GET'])
def download_limit_down_data():
    """
    下载跌停股票池数据为Excel
    参数: 
        date - 日期，格式 YYYYMMDD，可选
    """
    try:
        # 获取日期参数
        date_param = request.args.get('date', '')
        
        if date_param:
            target_date = datetime.strptime(date_param, '%Y%m%d')
        else:
            target_date = datetime.now()
        
        # 尝试获取数据
        max_attempts = 10
        df = None
        
        for i in range(max_attempts):
            current_date = target_date - timedelta(days=i)
            
            if current_date.weekday() >= 5:
                continue
            
            date_str = current_date.strftime('%Y%m%d')
            
            try:
                df = ak.stock_zt_pool_dtgc_em(date=date_str)
                
                if not df.empty:
                    date_param = date_str
                    break
            except Exception as e:
                print(f"尝试日期 {date_str} 失败: {e}")
                continue
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'message': '未找到跌停数据'
            }), 404
        
        # 格式化数值列
        for col in df.columns:
            if col not in ['代码', '名称', '所属行业']:
                df[col] = df[col].apply(lambda x: format_numeric_value(x))
        
        # 添加查询时间列
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.insert(0, '查询时间', current_time)
        
        # 创建Excel文件
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='跌停股票池', index=False)
        
        output.seek(0)
        
        # 格式化日期显示
        display_date = datetime.strptime(date_param, '%Y%m%d').strftime('%Y%m%d')
        filename = f"跌停股票池_{display_date}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下载失败: {str(e)}'
        }), 400

if __name__ == '__main__':
    import os
    import socket
    
    # 设置全局 socket 超时
    socket.setdefaulttimeout(30)
    
    # 生产环境使用环境变量PORT，本地开发使用5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Render 部署时使用 Werkzeug 服务器（对于小项目足够）
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
