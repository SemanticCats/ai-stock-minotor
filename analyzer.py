# analyzer.py
import pandas as pd
from data_fetcher import get_stock_fund_flow

def safe_get_concepts(row):
    """安全提取所属概念，兼容不同数据格式"""
    concepts = row.get('所属概念', '')
    if pd.isna(concepts) or concepts == '' or concepts == '-':
        return []
    return [c.strip() for c in str(concepts).split(';') if c.strip()]

def detect_main_theme(limit_up_df):
    """识别最强题材，带字段容错"""
    concept_count = {}
    
    for _, row in limit_up_df.iterrows():
        concepts = safe_get_concepts(row)
        for c in concepts:
            concept_count[c] = concept_count.get(c, 0) + 1
    
    if not concept_count:
        return {"name": "未知题材", "count": len(limit_up_df), "strength": 0}
    
    top_concept = max(concept_count, key=concept_count.get)
    return {
        "name": top_concept,
        "count": concept_count[top_concept],
        "strength": concept_count[top_concept] * 100
    }

def safe_get_float(value, default=0.0):
    """安全转换为浮点数"""
    try:
        if pd.isna(value):
            return default
        if isinstance(value, str):
            # 处理 '5.23%' 或 '5.23' 等格式
            clean_val = value.replace('%', '').strip()
            return float(clean_val) if clean_val else default
        return float(value)
    except (ValueError, TypeError):
        return default

def find_potential_stocks(limit_up_df, main_theme_name):
    """筛选潜力股，增强字段兼容性"""
    candidates = []
    
    for _, row in limit_up_df.iterrows():
        # 安全获取涨幅
        change_pct = safe_get_float(row.get('涨跌幅', row.get('changepercent', 0)))
        
        # 跳过已涨停或涨幅不足的
        if change_pct >= 9.5 or change_pct < 5.0:
            continue
        
        if change_pct <= 8.5:
            symbol = row.get('代码', row.get('symbol', ''))
            name = row.get('名称', row.get('name', '未知'))
            price = safe_get_float(row.get('最新价', row.get('close', 0)))
            
            # 安全获取换手率（支持 '换手率' 或 'turnover'）
            turnover = safe_get_float(row.get('换手率', row.get('turnover', 0)))
            
            # 获取资金流
            flow = get_stock_fund_flow(symbol) if symbol else {"net_inflow": 0}
            net_inflow = flow['net_inflow']  # 单位：万元
            
            # 筛选条件
            if net_inflow > 3000 and 5 <= turnover <= 20 and symbol:
                candidates.append({
                    "code": symbol,
                    "name": name,
                    "price": price,
                    "change_pct": change_pct,
                    "net_inflow": net_inflow,
                    "turnover": turnover
                })
                
    return candidates[:3]  # 最多返回3只
