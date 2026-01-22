import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def get_today_date():
    return datetime.now().strftime("%Y%m%d")

def safe_get_zt_pool(date_str):
    max_try = 3
    current = datetime.strptime(date_str, "%Y%m%d")
    for i in range(max_try):
        try:
            df = ak.stock_zt_pool_em(date=current.strftime("%Y%m%d"))
            if not df.empty and len(df) > 5:
                return df, current.strftime("%Y%m%d")
        except Exception as e:
            print(f"[{current.strftime('%Y%m%d')}] 获取涨停池失败: {e}")
        current -= timedelta(days=1)
    return pd.DataFrame(), ""

def get_stock_fund_flow(symbol):
    market = "sh" if symbol.startswith("6") else "sz"
    try:
        df = ak.stock_individual_fund_flow(stock=symbol, market=market)
        if df.empty:
            return {"net_inflow": 0}
        latest = df.iloc[0]
        net_inflow = float(latest["净流入"]) if pd.notna(latest["净流入"]) else 0
        return {"net_inflow": net_inflow}
    except Exception as e:
        print(f"资金流获取失败 {symbol}: {e}")
        return {"net_inflow": 0}
