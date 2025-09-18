import pandas as pd
from sqlalchemy import create_engine, text
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import json
from datetime import datetime, timedelta
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy.exc import IntegrityError
from tensorflow.keras.models import load_model
import os
import threading
import data_updater
import pandas_ta as ta
from werkzeug.security import generate_password_hash, check_password_hash # 新增
import jwt # 新增
from functools import wraps # **新增**

# --- 配置 ---
pymysql.install_as_MySQLdb()
engine = create_engine(
    'mysql+pymysql://root:123456@localhost/test?charset=utf8',
    pool_size=10, max_overflow=20, pool_recycle=3600
)
MODEL_PATH = 'models/stock_model_all.h5'
LOOK_BACK_DAYS = 60

# --- 全局变量 ---
app = Flask(__name__)
app.config["SECRET_KEY"] = "your_super_secret_key_change_this" # **新增：JWT密钥，请务必修改为一个复杂的字符串**
CORS(app)
model = None
scaler = MinMaxScaler(feature_range=(0, 1))
UPDATE_STATUS = {
    "running": False, "progress": 0, "total": 0, "message": "暂无更新任务"
}

# --- 辅助函数 ---
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, pd.Timestamp)): return obj.strftime('%Y-%m-%d')
        if hasattr(obj, 'tolist'): return obj.tolist()
        if isinstance(obj, bool): return 1 if obj else 0
        return super(CustomJSONEncoder, self).default(obj)


app.json_encoder = CustomJSONEncoder


def load_prediction_model():
    global model
    if os.path.exists(MODEL_PATH):
        try:
            model = load_model(MODEL_PATH)
            print(f"通用模型 {MODEL_PATH} 加载成功。")
        except Exception as e:
            print(f"模型加载失败: {e}")
    else:
        print(f"警告: 模型文件 {MODEL_PATH} 不存在。")


def predict_future_prices(daily_data_df):
    if model is None or len(daily_data_df) < LOOK_BACK_DAYS:
        return []
    try:
        # 使用 'price' 列进行预测
        data = daily_data_df['price'].values.reshape(-1, 1)
        scaled_data = scaler.fit_transform(data)
        last_sequence = scaled_data[-LOOK_BACK_DAYS:]
        current_sequence = last_sequence.reshape(1, LOOK_BACK_DAYS, 1)
        predictions = []
        last_date = daily_data_df.index[-1]
        for i in range(1, 6):
            predicted_scaled_price = model.predict(current_sequence)
            predicted_price = scaler.inverse_transform(predicted_scaled_price)
            next_date = last_date + timedelta(days=i)
            predictions.append({"date": next_date, "price": float(predicted_price[0][0])})
            new_sequence = np.append(current_sequence[0][1:], predicted_scaled_price, axis=0)
            current_sequence = new_sequence.reshape(1, LOOK_BACK_DAYS, 1)
        return predictions
    except Exception as e:
        print(f"价格预测时发生错误: {e}")
        return []


# **新增：JWT Token验证装饰器**
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': '缺少Token!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # 将用户信息存入g，以便后续使用 (可选)
            # from flask import g
            # g.current_user_id = data['user_id']
            current_user_id = data['user_id']
        except Exception as e:
            return jsonify({'message': f'Token无效或已过期! {e}'}), 401

        return f(current_user_id, *args, **kwargs)
    return decorated

# --- API 路由 ---
def get_stock_list(page=1, page_size=20, keyword=None):
    try:
        offset = (page - 1) * page_size
        base_sql = """
        WITH ranked_stocks AS (
            SELECT
                s.`股票代码` as code, COALESCE(b.`股票名称`, s.`股票代码`) as name,
                s.`收盘价` as price, s.`日期` as date,
                s.`开盘价` as prevPrice,
                ((s.`收盘价` - s.`开盘价`)/s.`开盘价`*100) as changePercent,
                s.`成交量` as volume,
                ROW_NUMBER() OVER (PARTITION BY s.`股票代码` ORDER BY s.`日期` DESC) as rn
            FROM t_stocks s
            LEFT JOIN t_stock_basic b ON s.`股票代码` = b.`股票代码`
            {where_clause}
        )
        SELECT code, name, price, prevPrice, date, changePercent, volume
        FROM ranked_stocks
        WHERE rn = 1
        """
        where_clause = ""
        params = {}
        if keyword:
            where_clause = "WHERE s.`股票代码` LIKE :keyword OR b.`股票名称` LIKE :keyword"
            params['keyword'] = f"%{keyword}%"
        full_sql = base_sql.format(where_clause=where_clause)
        list_sql = full_sql + " ORDER BY code LIMIT :limit OFFSET :offset"
        list_params = {**params, 'limit': page_size, 'offset': offset}
        df = pd.read_sql(text(list_sql), con=engine, params=list_params)
        count_sql = f"SELECT COUNT(*) FROM ({full_sql}) as subquery"
        with engine.connect() as connection:
            total_count = connection.execute(text(count_sql), params).scalar()
        if 'volume' in df.columns:
            df['volume'] = df['volume'].fillna(0) / 10000
            df['volume'] = df['volume'].round(2)
        return df, total_count
    except Exception as e:
        print(f"股票列表查询错误: {e}")
        return None, 0


@app.route('/api/stocklist', methods=['GET'])
def stock_list():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 20))
        keyword = request.args.get('keyword', None)
    except ValueError:
        return jsonify({"error": "无效的分页参数"}), 400
    df, total_count = get_stock_list(page, page_size, keyword)
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
    if df is not None:
        if not df.empty:
            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
            df['prevPrice'] = pd.to_numeric(df['prevPrice'], errors='coerce').fillna(0)
            df['changePercent'] = pd.to_numeric(df['changePercent'], errors='coerce').fillna(0)
            if 'volume' in df.columns:
                df['volume'] = df['volume'].apply(lambda x: f"{x:.2f}" if x > 0 else "0.00")
        return jsonify({
            'data': df.to_dict('records'),
            'pagination': {'page': page, 'pageSize': page_size, 'total': total_count, 'totalPages': total_pages,
                           'has_more': page < total_pages}
        })
    else:
        return jsonify({'data': [], 'pagination': {'page': page, 'pageSize': page_size, 'total': 0, 'totalPages': 0,
                                                   'has_more': False}})


def get_stock_kline(stock_code, period='day', page_size=200):
    try:
        basic_sql = "SELECT `股票代码` as code, `股票名称` as name FROM t_stock_basic WHERE `股票代码` = %s"
        basic_df = pd.read_sql(basic_sql, con=engine, params=(stock_code,))
        stock_info = basic_df.iloc[0].to_dict() if not basic_df.empty else {"code": stock_code, "name": stock_code}
        sql = "SELECT `日期` as date, `开盘价` as open, `收盘价` as price, `最低价` as low, `最高价` as high, `成交量` as volume FROM t_stocks WHERE `股票代码` = %s ORDER BY `日期` ASC"
        df_daily = pd.read_sql(sql, con=engine, params=(stock_code,))
        if df_daily.empty:
            return None
        df_daily['date'] = pd.to_datetime(df_daily['date'])
        df_daily.set_index('date', inplace=True)

        df_daily.rename(columns={'price': 'close'}, inplace=True)
        df_daily.ta.sma(length=5, append=True)
        df_daily.ta.sma(length=10, append=True)
        df_daily.ta.sma(length=20, append=True)
        df_daily.rename(columns={'close': 'price'}, inplace=True)

        prediction_data = []
        if period == 'day':
            prediction_data = predict_future_prices(df_daily)

        df_display = df_daily
        if period in ['week', 'month']:
            period_map = {'week': 'W', 'month': 'M'}
            logic = {'open': 'first', 'high': 'max', 'low': 'min', 'price': 'last', 'volume': 'sum'}
            df_display = df_daily.resample(period_map[period]).apply(logic).dropna()

        df_display.reset_index(inplace=True)
        df_final = df_display.tail(page_size).copy()
        df_final['date'] = df_final['date'].dt.strftime('%Y-%m-%d')
        df_final.replace({np.nan: None}, inplace=True)
        return {"stockInfo": stock_info, "data": df_final, "predictionData": prediction_data}
    except Exception as e:
        print(f"K线数据处理错误: {e}")
        return None


@app.route('/api/stockkline', methods=['GET'])
def stock_kline():
    try:
        stock_code = request.args.get('stockCode');
        period = request.args.get('period', 'day')
        page_size = int(request.args.get('pageSize', 200))
        if not stock_code: return jsonify({"error": "股票代码不能为空"}), 400
    except ValueError:
        return jsonify({"error": "无效的参数"}), 400
    result = get_stock_kline(stock_code, period, page_size)
    if result and not result['data'].empty:
        return jsonify({'stockInfo': result['stockInfo'], 'data': result['data'].to_dict('records'),
                        'predictionData': result['predictionData']})
    else:
        return jsonify({'stockInfo': {"code": stock_code, "name": stock_code}, 'data': [], 'predictionData': []})


@app.route('/api/update_stock', methods=['POST'])
def update_stock_endpoint():
    stock_code = request.json.get('stockCode')
    if not stock_code: return jsonify({"status": "error", "message": "股票代码不能为空"}), 400
    thread = threading.Thread(target=data_updater.update_single_stock_task, args=(stock_code,))
    thread.start()
    return jsonify({"status": "success", "message": f"已启动对 {stock_code} 的更新任务。"}), 202


@app.route('/api/update_all_stocks', methods=['POST'])
def update_all_stocks_endpoint():
    global UPDATE_STATUS
    if UPDATE_STATUS['running']:
        return jsonify({"status": "warning", "message": "已有更新任务正在运行中。"}), 409
    thread = threading.Thread(target=data_updater.update_all_stocks_task_with_progress, args=(UPDATE_STATUS,))
    thread.start()
    return jsonify({"status": "success", "message": "已启动全部股票的后台更新任务。"}), 202


@app.route('/api/update_status', methods=['GET'])
def get_update_status():
    global UPDATE_STATUS
    return jsonify(UPDATE_STATUS)


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空!"}), 400

    # 检查用户名是否已存在
    with engine.connect() as conn:
        user_exists = conn.execute(text("SELECT id FROM t_users WHERE username = :username"), {"username": username}).scalar()
        if user_exists:
            return jsonify({"message": "用户名已存在!"}), 409

        # 创建新用户
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        insert_stmt = text("INSERT INTO t_users (username, password_hash) VALUES (:username, :password)")
        conn.execute(insert_stmt, {"username": username, "password": hashed_password})
        conn.commit() # 确保提交事务

    return jsonify({"message": "注册成功!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空!"}), 400

    with engine.connect() as conn:
        user = conn.execute(text("SELECT id, password_hash FROM t_users WHERE username = :username"), {"username": username}).first()

        if not user or not check_password_hash(user[1], password):
            return jsonify({"message": "用户名或密码错误!"}), 401

        # 生成JWT Token
        token = jwt.encode({
            'user_id': user[0],
            'exp': datetime.utcnow() + timedelta(hours=24) # Token有效期24小时
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token, 'username': username})


@app.route('/api/watchlist', methods=['GET'])
@token_required
def get_watchlist(current_user_id):
    """获取当前用户的自选股列表"""
    try:
        sql = """
            SELECT s.`股票代码` as code, b.`股票名称` as name, s.`收盘价` as price,
                   s.`开盘价` as prevPrice, ((s.`收盘价` - s.`开盘价`)/s.`开盘价`*100) as changePercent,
                   (s.`成交量`/10000) as volume
            FROM t_watchlists w
            JOIN (
                SELECT `股票代码`, `收盘价`, `开盘价`, `成交量`,
                       ROW_NUMBER() OVER (PARTITION BY `股票代码` ORDER BY `日期` DESC) as rn
                FROM t_stocks
            ) s ON w.stock_code = s.`股票代码` AND s.rn = 1
            JOIN t_stock_basic b ON w.stock_code = b.`股票代码`
            WHERE w.user_id = :user_id
        """
        df = pd.read_sql(text(sql), engine, params={"user_id": current_user_id})
        df.replace({np.nan: None}, inplace=True)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({"message": f"获取自选股列表失败: {e}"}), 500


@app.route('/api/watchlist', methods=['POST'])
@token_required
def add_to_watchlist(current_user_id):
    """向当前用户的自选列表添加一支股票"""
    stock_code = request.json.get('stockCode')
    if not stock_code:
        return jsonify({"message": "股票代码不能为空"}), 400

    try:
        with engine.connect() as conn:
            stmt = text("INSERT INTO t_watchlists (user_id, stock_code) VALUES (:user_id, :stock_code)")
            conn.execute(stmt, {"user_id": current_user_id, "stock_code": stock_code})
            conn.commit()
        return jsonify({"message": "添加自选成功"}), 201
    except IntegrityError:  # 捕获唯一索引冲突
        return jsonify({"message": "股票已在自选列表中"}), 409
    except Exception as e:
        return jsonify({"message": f"添加自选失败: {e}"}), 500


@app.route('/api/watchlist/<string:stock_code>', methods=['DELETE'])
@token_required
def remove_from_watchlist(current_user_id, stock_code):
    """从当前用户的自选列表移除一支股票"""
    try:
        with engine.connect() as conn:
            stmt = text("DELETE FROM t_watchlists WHERE user_id = :user_id AND stock_code = :stock_code")
            result = conn.execute(stmt, {"user_id": current_user_id, "stock_code": stock_code})
            conn.commit()
            if result.rowcount > 0:
                return jsonify({"message": "移除自选成功"}), 200
            else:
                return jsonify({"message": "股票不在自选列表中"}), 404
    except Exception as e:
        return jsonify({"message": f"移除自选失败: {e}"}), 500


@app.route('/api/watchlist/status', methods=['GET'])
@token_required
def get_watchlist_status(current_user_id):
    """检查多支股票是否在用户的自选列表中"""
    stock_codes_str = request.args.get('stockCodes')  # 接收一个用逗号分隔的字符串
    if not stock_codes_str:
        return jsonify({})

    stock_codes = stock_codes_str.split(',')

    try:
        with engine.connect() as conn:
            # 使用 IN 查询来一次性检查所有股票
            stmt = text("SELECT stock_code FROM t_watchlists WHERE user_id = :user_id AND stock_code IN :codes")
            result = conn.execute(stmt, {"user_id": current_user_id, "codes": stock_codes})

            in_watchlist = {row[0] for row in result}  # 将结果存入一个集合以便快速查找
            status = {code: (code in in_watchlist) for code in stock_codes}

            return jsonify(status)
    except Exception as e:
        return jsonify({"message": f"检查状态失败: {e}"}), 500

if __name__ == '__main__':
    load_prediction_model()
    app.run(debug=True, port=5000, host='0.0.0.0')