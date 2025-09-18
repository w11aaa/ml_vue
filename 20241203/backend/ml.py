import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import os
import pymysql

# --- 配置区 ---
# 数据库连接
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_HOST = 'localhost'
DB_NAME = 'test'
DB_CHARSET = 'utf8'

# 模型参数
LOOK_BACK_DAYS = 60  # 使用过去60天的数据来预测未来1天
EPOCHS = 20  # 训练的回合数 (由于数据量增大，可以适当减少)
BATCH_SIZE = 64  # 每批次处理的数据量 (可以适当增大)
MODEL_SAVE_PATH = 'models/stock_model_all.h5'  # 新的通用模型保存路径

# 确保模型保存目录存在
os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)


# --- 训练逻辑 ---

def create_dataset(dataset, look_back=1):
    """
    将时间序列数据转换为监督学习问题的数据集
    """
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)


def train_all_stocks_model():
    """
    主训练函数 - 读取所有股票数据进行训练
    """
    print("开始通用模型训练...")

    # 1. 连接数据库
    try:
        pymysql.install_as_MySQLdb()
        engine = create_engine(
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset={DB_CHARSET}'
        )
        print("数据库连接成功。")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return

    # 2. 获取所有股票代码
    try:
        stock_codes_df = pd.read_sql("SELECT DISTINCT `股票代码` as code FROM t_stocks", con=engine)
        stock_codes = stock_codes_df['code'].tolist()
        if not stock_codes:
            print("错误：在数据库中未找到任何股票代码。")
            return
        print(f"发现 {len(stock_codes)} 支不同的股票。")
    except Exception as e:
        print(f"获取股票代码列表失败: {e}")
        return

    # 3. 循环加载所有股票数据并合并
    all_stocks_data = []
    print("开始加载所有股票的历史数据...")
    for code in stock_codes:
        sql = "SELECT `收盘价` as price FROM t_stocks WHERE `股票代码` = %s ORDER BY `日期` ASC"
        df = pd.read_sql(sql, con=engine, params=(code,))

        # 只有数据量足够长的股票才被用于训练
        if len(df) > LOOK_BACK_DAYS:
            # 我们只关心价格序列，将其添加到总列表中
            all_stocks_data.append(df['price'].values)

    if not all_stocks_data:
        print("没有找到足够长的股票数据来训练模型。")
        return

    print(f"数据加载完成，共找到 {len(all_stocks_data)} 支符合训练条件的股票。")

    # 4. 数据预处理
    # 将所有价格数据连接成一个长序列，然后reshape
    combined_data = np.concatenate(all_stocks_data).reshape(-1, 1)

    # 对所有数据进行统一归一化
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(combined_data)

    # 使用处理后的全部数据创建训练集
    X_train, y_train = create_dataset(scaled_data, LOOK_BACK_DAYS)

    # Reshape输入数据以满足LSTM的要求 [样本数, 时间步, 特征数]
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    print(f"数据预处理完成。总训练样本数: {X_train.shape[0]}")

    # 5. 构建LSTM模型 (模型结构可以保持不变)
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(LOOK_BACK_DAYS, 1)),
        Dropout(0.2),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(units=1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')
    print("通用LSTM模型构建完成。")
    model.summary()

    # 6. 训练模型
    print("开始模型训练（这可能需要一些时间）...")
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1)
    print("模型训练完成。")

    # 7. 保存模型
    model.save(MODEL_SAVE_PATH)
    print(f"通用模型已成功保存到: {MODEL_SAVE_PATH}")


if __name__ == '__main__':
    train_all_stocks_model()