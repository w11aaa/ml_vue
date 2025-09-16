import pandas
from sqlalchemy import create_engine
from flask import Flask, jsonify
from flask_cors import CORS
import pymysql

# 确保pymysql被正确加载
pymysql.install_as_MySQLdb()

# --- 数据库连接逻辑 ---
def getDFfromMySQL():
    """从MySQL数据库获取数据并加载到DataFrame中"""
    try:

        uri = 'mysql+pymysql://root:123456@localhost/test?charset=utf8'
        engine = create_engine(uri)
        
        # 确保您的表名为 t_stocks 且包含这些列
        sql = """
            SELECT 
                `日期`, `开盘价`, `收盘价`, `最高价`, `最低价`, `成交量`
            FROM t_stocks
            ORDER BY `日期` ASC
        """
        df = pandas.read_sql(sql, con=engine)
        
        # 数据清洗
        for col in df.columns:
            if col != '日期':
                df[col] = pandas.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"数据库连接或查询失败: {e}")
        return None

# --- Flask 应用 ---
app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求

@app.route('/api/stockdata', methods=['GET'])
def get_stock_data():
    """提供股票数据的API接口"""
    df = getDFfromMySQL()
    
    if df is not None and not df.empty:
        # 准备前端ECharts所需的数据格式
        kline_data = df[['开盘价', '收盘价', '最低价', '最高价']].values.tolist()
        dates = df['日期'].astype(str).tolist()
        volumes = df['成交量'].tolist()
        
        response_data = {
            'dates': dates,
            'klineData': kline_data,
            'volumes': volumes
        }
        return jsonify(response_data)
    else:
        return jsonify({"error": "无法从数据库获取数据或数据为空"}), 500

if __name__ == '__main__':
    # 启动Flask服务器，监听在5000端口
    app.run(debug=True, port=5000)