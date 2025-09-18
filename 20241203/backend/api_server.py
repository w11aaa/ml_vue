import pandas
from sqlalchemy import create_engine
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import json
from datetime import datetime

# 解决MySQL连接问题
pymysql.install_as_MySQLdb()

app = Flask(__name__)
CORS(app)

# 数据库连接
engine = create_engine(
    'mysql+pymysql://root:123456@localhost/test?charset=utf8',
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)


# 自定义JSON编码器，处理特殊类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # 处理日期时间类型
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        # 处理numpy类型
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        # 处理布尔类型
        if isinstance(obj, bool):
            return 1 if obj else 0
        # 处理其他未知类型
        return super(CustomJSONEncoder, self).default(obj)


# 应用自定义JSON编码器
app.json_encoder = CustomJSONEncoder


def get_stock_list(page=1, page_size=20):
    try:
        offset = (page - 1) * page_size

        # 查询每个股票的最新一条记录
        sql = """
        WITH ranked_stocks AS (
            SELECT 
                s.`股票代码` as code,
                COALESCE(b.`股票名称`, s.`股票代码`) as name,
                s.`收盘价` as price,
                s.`日期` as date,
                ((s.`收盘价` - s.`开盘价`)/s.`开盘价`*100) as changePercent,
                s.`成交量` as volume,  -- 新增成交量字段
                ROW_NUMBER() OVER (PARTITION BY s.`股票代码` ORDER BY s.`日期` DESC) as rn
            FROM t_stocks s
            LEFT JOIN t_stock_basic b ON s.`股票代码` = b.`股票代码`
        )
        SELECT code, name, price, date, changePercent, volume
        FROM ranked_stocks
        WHERE rn = 1
        ORDER BY code
        LIMIT %s OFFSET %s
        """

        df = pandas.read_sql(
            sql,
            con=engine,
            params=(page_size, offset)
        )

        # 确保所有数值类型正确，避免布尔值出现
        for col in df.columns:
            if df[col].dtype == 'bool':
                df[col] = df[col].astype(int)

        # 处理成交量，转换为万手并保留两位小数
        if 'volume' in df.columns:
            df['volume'] = df['volume'].fillna(0) / 10000
            df['volume'] = df['volume'].round(2)

        return df

    except Exception as e:
        print(f"股票列表查询错误: {e}")
        return None


def get_stock_kline(stock_code, period='day', page_size=200):
    try:
        # 获取股票基本信息
        stock_info = None
        basic_sql = "SELECT `股票代码` as code, `股票名称` as name FROM t_stock_basic WHERE `股票代码` = %s"
        basic_df = pandas.read_sql(basic_sql, con=engine, params=(stock_code,))
        if not basic_df.empty:
            stock_info = basic_df.iloc[0].to_dict()
        else:
            # 如果基本信息表中没有，使用代码作为名称
            stock_info = {"code": stock_code, "name": stock_code}

        # 构建K线数据查询SQL
        sql = """
            SELECT 
                `日期` as date,
                `开盘价` as open,
                `收盘价` as price,
                `最低价` as low,
                `最高价` as high,
                `成交量` as volume
            FROM t_stocks
            WHERE `股票代码` = %s
        """

        # 根据周期添加筛选条件
        if period == 'week':
            # 每周最后一个交易日（假设为周五）
            sql += " AND DAYOFWEEK(`日期`) = 6 "
        elif period == 'month':
            # 每月最后一个交易日
            sql += " AND DAYOFMONTH(`日期`) = DAYOFMONTH(LAST_DAY(`日期`)) "

        # 按日期排序并限制数量
        sql += " ORDER BY `日期` ASC LIMIT %s"

        df = pandas.read_sql(
            sql,
            con=engine,
            params=(stock_code, page_size)
        )

        # 处理可能的布尔值列
        for col in df.columns:
            if df[col].dtype == 'bool':
                df[col] = df[col].astype(int)

        return {
            "stockInfo": stock_info,
            "data": df
        }

    except Exception as e:
        print(f"K线数据查询错误: {e}")
        return None


@app.route('/api/stocklist', methods=['GET'])
def stock_list():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 20))
    except ValueError:
        return jsonify({"error": "无效的分页参数"}), 400

    df = get_stock_list(page, page_size)

    if df is not None and not df.empty:
        # 确保价格和涨跌幅为数值类型
        df['price'] = pandas.to_numeric(df['price'], errors='coerce').fillna(0)
        df['changePercent'] = pandas.to_numeric(df['changePercent'], errors='coerce').fillna(0)

        # 处理成交量显示
        if 'volume' in df.columns:
            df['volume'] = df['volume'].apply(lambda x: f"{x:.2f}万" if x > 0 else "0.00万")

        return jsonify({
            'data': df.to_dict('records'),
            'pagination': {
                'page': page,
                'pageSize': page_size,
                'has_more': len(df) == page_size
            }
        })
    else:
        return jsonify({
            'data': [],
            'pagination': {
                'page': page,
                'pageSize': page_size,
                'has_more': False
            }
        })


@app.route('/api/stockkline', methods=['GET'])
def stock_kline():
    try:
        stock_code = request.args.get('stockCode')
        period = request.args.get('period', 'day')
        page_size = int(request.args.get('pageSize', 200))

        if not stock_code:
            return jsonify({"error": "股票代码不能为空"}), 400
    except ValueError:
        return jsonify({"error": "无效的参数"}), 400

    result = get_stock_kline(stock_code, period, page_size)

    if result and result['data'] is not None and not result['data'].empty:
        return jsonify({
            'stockInfo': result['stockInfo'],
            'data': result['data'].to_dict('records')
        })
    else:
        return jsonify({
            'stockInfo': {"code": stock_code, "name": stock_code},
            'data': []
        })


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')