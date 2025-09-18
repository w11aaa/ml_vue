import time
import random
import json
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- 配置 ---
DB_URI = 'mysql+pymysql://root:123456@localhost/test?charset=utf8mb4'
KLINE_URL = (
    "https://push2his.eastmoney.com/api/qt/stock/kline/get?"
    "secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&"
    "fields1=f1,f2,f3,f4,f5,f6&"
    "fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&"
    "klt=101&fqt=1&end=20500101&lmt=120"
)
MAX_WORKERS = 10

# --- 核心函数 ---
def fetch_kline_data(code: str) -> pd.DataFrame:
    """获取单支股票的K线数据"""
    try:
        market = '1' if code.startswith('6') else '0'
        secid = f'{market}.{code}'
        url = KLINE_URL.format(secid=secid)
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        })
        r = session.get(url, timeout=15)
        r.raise_for_status()
        j = r.json()
        if not j.get('data') or not j['data'].get('klines'): return pd.DataFrame()
        df = pd.DataFrame([kline.split(',') for kline in j['data']['klines']])
        df.columns = ['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
        df['股票代码'] = code
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        numeric_cols = ['开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
        return df[['股票代码', '日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']]
    except Exception as e:
        print(f"[{code}] 获取K线数据失败: {e}")
        return pd.DataFrame()

def save_data_to_db_bulk(df: pd.DataFrame, table_name: str):
    """批量数据库操作"""
    if df.empty:
        return
    engine = create_engine(DB_URI)
    stock_code = df['股票代码'].iloc[0]
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            delete_stmt = text(f"DELETE FROM {table_name} WHERE `股票代码` = :code")
            conn.execute(delete_stmt, {"code": stock_code})
            df.to_sql(table_name, conn, if_exists='append', index=False, chunksize=1000)
            trans.commit()
            print(f"股票 {stock_code} 批量写入完成。")
        except Exception as e:
            print(f"批量写入数据失败: {stock_code}, 错误: {e}")
            trans.rollback()

# --- 可调用的更新任务 ---
def update_single_stock_task(code: str) -> str:
    """更新单支股票数据的任务，并返回结果状态"""
    try:
        df = fetch_kline_data(code)
        if not df.empty:
            save_data_to_db_bulk(df, 't_stocks')
            return f"成功: {code}"
        else:
            return f"无数据: {code}"
    except Exception as e:
        return f"失败: {code} - {e}"

def update_all_stocks_task_with_progress(status_dict: dict):
    """使用多线程并行更新"""
    print("开始全部股票数据更新任务 (并行模式)...")
    status_dict.update({"running": True, "progress": 0, "total": 0, "message": "正在获取股票列表..."})
    engine = create_engine(DB_URI)
    try:
        sql_query = "SELECT DISTINCT `股票代码` as code FROM t_stock_basic LIMIT 500"
        codes_df = pd.read_sql(sql_query, con=engine)
        if codes_df.empty:
            status_dict.update({"running": False, "message": "数据库中没有股票可更新。"})
            return
        stock_codes = codes_df['code'].tolist()
        total = len(stock_codes)
        status_dict['total'] = total
        print(f"将要更新 {total} 支股票，使用 {MAX_WORKERS} 个并发线程...")
        processed_count = 0
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_code = {executor.submit(update_single_stock_task, code): code for code in stock_codes}
            for future in as_completed(future_to_code):
                processed_count += 1
                code = future_to_code[future]
                try:
                    result_message = future.result()
                    status_dict['message'] = f"({processed_count}/{total}) {result_message}"
                except Exception as exc:
                    status_dict['message'] = f"({processed_count}/{total}) {code} 执行出错: {exc}"
                status_dict['progress'] = processed_count
        status_dict['message'] = f"全部 {total} 支股票更新完成！"
        print("全部股票数据更新任务完成！")
    except Exception as e:
        status_dict['message'] = f"任务失败: {e}"
        print(f"全部更新任务失败: {e}")
    finally:
        status_dict['running'] = False