"""
测试昨日数据API
"""
import requests
import json

def test_stock_info():
    """测试股票信息API，验证昨日数据和对比功能"""
    
    # 测试股票代码
    test_codes = ['600000', '000001', '600519']
    
    base_url = 'http://localhost:5000'
    
    for code in test_codes:
        print(f"\n{'='*60}")
        print(f"测试股票代码: {code}")
        print('='*60)
        
        try:
            response = requests.get(
                f'{base_url}/api/stock/info',
                params={'code': code}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    print(f"✓ 查询成功")
                    
                    # 检查基本信息
                    basic_info = data['data'].get('basic_info', {})
                    print(f"\n基本信息: {basic_info.get('股票简称', 'N/A')}")
                    
                    # 检查实时数据
                    realtime = data['data'].get('realtime_data', {})
                    if realtime:
                        print(f"\n实时数据:")
                        print(f"  最新价: {realtime.get('最新价', 'N/A')}")
                        print(f"  涨跌幅: {realtime.get('涨跌幅', 'N/A')}%")
                        
                        # 检查昨日数据
                        yesterday = realtime.get('昨日数据')
                        if yesterday:
                            print(f"\n昨日数据:")
                            print(f"  日期: {yesterday.get('昨日日期', 'N/A')}")
                            print(f"  开盘: {yesterday.get('昨日开盘', 'N/A')}")
                            print(f"  最高: {yesterday.get('昨日最高', 'N/A')}")
                            print(f"  最低: {yesterday.get('昨日最低', 'N/A')}")
                            print(f"  收盘: {yesterday.get('昨日收盘', 'N/A')}")
                            
                            print(f"\n今日实时价与昨日对比:")
                            print(f"  相比开盘: {yesterday.get('相比昨日开盘涨跌幅', 'N/A')}%")
                            print(f"  相比最高: {yesterday.get('相比昨日最高涨跌幅', 'N/A')}%")
                            print(f"  相比最低: {yesterday.get('相比昨日最低涨跌幅', 'N/A')}%")
                            print(f"  相比收盘: {yesterday.get('相比昨日收盘涨跌幅', 'N/A')}%")
                        else:
                            print("\n⚠ 未获取到昨日数据")
                    else:
                        print("\n⚠ 未获取到实时数据")
                else:
                    print(f"✗ 查询失败: {data.get('message', '未知错误')}")
            else:
                print(f"✗ HTTP错误: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("✗ 连接失败: 请确保后端服务正在运行")
            break
        except Exception as e:
            print(f"✗ 异常: {str(e)}")

if __name__ == '__main__':
    print("开始测试昨日数据API...")
    print("请确保后端服务已启动 (python app.py)")
    test_stock_info()
    print("\n测试完成!")
