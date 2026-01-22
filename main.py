import os
from datetime import datetime
from data_fetcher import safe_get_zt_pool
from analyzer import detect_main_theme, find_potential_stocks
from notify import push_to_wechat

def main():
    date_str = datetime.now().strftime("%Y%m%d")
    print(f"开始分析 {date_str} 的A股数据...")
    
    limit_up_df, actual_date = safe_get_zt_pool(date_str)
    if limit_up_df.empty:
        error_msg = "❌ 无法获取有效涨停数据（可能为节假日）"
        print(error_msg)
        push_to_wechat("A股盯盘失败", error_msg)
        return
    
    print(f"使用数据日期: {actual_date}, 共 {len(limit_up_df)} 只股票")
    
    main_theme = detect_main_theme(limit_up_df)
    potentials = find_potential_stocks(limit_up_df, main_theme["name"])
    
    report = f"""
📅 数据日期: {actual_date}
🔥 主线题材: {main_theme['name']}
📈 涨停数量: {main_theme['count']} 只

🎯 潜力股推荐（非投资建议）:
"""
    if potentials:
        for p in potentials:
            report += f"- {p['name']} ({p['code']})\n"
            report += f"  涨幅: {p['change_pct']:.2f}% | 资金流入: {p['net_inflow']:.0f}万 | 换手: {p['turnover']:.1f}%\n"
    else:
        report += "暂无符合策略的标的\n"
    
    report += "\n💡 策略: 5%~8.5%涨幅 + 资金流入>3000万 + 换手5%~20%\n⚠️ 仅学习研究，请勿跟单！"
    
    print(report)
    push_to_wechat(f"A股盯盘日报 {actual_date}", report)

if __name__ == "__main__":
    main()
