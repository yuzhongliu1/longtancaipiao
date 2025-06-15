import streamlit as st
from datetime import datetime, timedelta, timezone

def fmt_num(n):
    if n is None:
        return "—"
    if n == int(n):
        return str(int(n))
    return f"{n:.2f}".rstrip('0').rstrip('.')

def main():
    st.set_page_config(page_title="🧮 彩票结算工具", page_icon="🧮")
    st.title("🧮 彩票结算工具")
    st.markdown("支持 **模式1（钱多多）**、**模式2（大赢家）** 和 **模式3（无佣金）**")

    china_time = datetime.now(timezone(timedelta(hours=8)))
    today_str = f"{china_time.month}月{china_time.day}日"

    mode = st.selectbox("请选择模式", ["1", "2", "3"], format_func=lambda x: {
        "1": "模式1：钱多多模式",
        "2": "模式2：大赢家模式",
        "3": "模式3：无佣金模式"
    }[x])

    result_lines = []

    if mode == "1":
        st.subheader("模式1：钱多多模式")
    
        amount_hit = st.number_input("今日出票金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        amount_won = st.number_input("今日中奖金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        leftover = st.number_input("昨日剩余", value=None, step=1.0, placeholder="请输入")
        if leftover is not None:
            options = [f"我收{fmt_num(leftover)}元", f"我付{fmt_num(leftover)}元"]
            leftover_choice = st.radio("选择昨日剩余类型", options)
            if leftover is not None:
                if "我付" in leftover_choice:
                    leftover = -leftover 
        include_date = st.checkbox("包含日期", value=True)
        has_h = st.checkbox("包含合买")

        if leftover is not None and leftover_choice == "我付":
            leftover = -leftover  # 内部转成负数
    
        fen = price = total_hemai = None
        if has_h:
            fen = st.number_input("合买份数", min_value=0.0, value=None, step=1.0, placeholder="请输入")
            price = st.number_input("每份金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
            if fen is not None and price is not None:
                total_hemai = fen * price
    
        kouyong = amount_hit * 0.96 if amount_hit is not None else None
        adjusted_hit = kouyong + (leftover if leftover and leftover > 0 else 0) if kouyong is not None else None
        adjusted_won = (amount_won or 0) + (abs(leftover) if leftover and leftover < 0 else 0) + (total_hemai or 0)
        net = (adjusted_hit or 0) - (adjusted_won or 0)
        action = "我收" if net >= 0 else "我付"
    
        prefix = f"{today_str}，" if include_date else ""
    
        if amount_hit is not None:
            first_line = f"{prefix}出票{fmt_num(amount_hit)}元，扣佣后{fmt_num(kouyong)}元"
            if leftover and leftover > 0:
                first_line += f"，昨日我应收{fmt_num(leftover)}元，共收{fmt_num(adjusted_hit)}元"
            result_lines.append(first_line)
    
        if amount_won is not None:
            second_line = "未中奖" if amount_won == 0 else f"中奖{fmt_num(amount_won)}元"
            if leftover and leftover < 0:
                second_line += f"，昨日我应付{fmt_num(abs(leftover))}元，共付{fmt_num(adjusted_won)}元"
            result_lines.append(second_line)
    
        if has_h and fen is not None and price is not None:
            result_lines.append(f"合买{fmt_num(fen)}份，每份{fmt_num(price)}元，我付{fmt_num(total_hemai)}元")
        
        if amount_hit is not None or amount_won is not None:
            result_lines.append(f"{action}{fmt_num(abs(net))}元" + ("，记着明天打票抵扣" if action == "我付" and abs(net) < 500 else ""))


    elif mode == "2":
        st.subheader("模式2：大赢家模式")
    
        ta_da = st.number_input("她找我打金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        wo_da = st.number_input("我找她打金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        amount_won = st.number_input("她中奖金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        include_date = st.checkbox("包含日期", value=True)
    
        kouyong_ta_da = ta_da * 0.96 if ta_da is not None else 0
        kouyong_wo_da = wo_da * 0.96 if wo_da is not None else 0
        income = kouyong_ta_da
        expense = kouyong_wo_da + (amount_won or 0)
        net = income - expense
        action = "我收" if net >= 0 else "我付"
    
        parts_desc = []
        if ta_da:
            parts_desc.append(f"你找我打{fmt_num(ta_da)}元")
        if wo_da:
            parts_desc.append(f"我找你打{fmt_num(wo_da)}元")
    
        prefix = f"{today_str}，" if include_date else ""
    
        if len(parts_desc) == 0:
            pass
        elif len(parts_desc) == 2:
            diff = ta_da - wo_da
            tag = "你找我打" if diff > 0 else "我找你打"
            if diff == 0:
                result_lines.append(f"{prefix}{parts_desc[0]}，{parts_desc[1]}，正好抵消")
            else:
                result_lines.append(f"{prefix}{parts_desc[0]}，{parts_desc[1]}，等于{tag}{fmt_num(abs(diff))}元，扣佣后{fmt_num(abs(diff) * 0.96)}元")
        else:
            result_lines.append(f"{prefix}{parts_desc[0]}，扣佣后{fmt_num(kouyong_ta_da if ta_da else kouyong_wo_da)}元")
    
        if amount_won is not None:
            result_lines.append("未中奖" if amount_won == 0 else f"中奖{fmt_num(amount_won)}元")
    
        if (ta_da is not None or wo_da is not None or amount_won is not None) and net != 0:
            result_lines.append(f"{action}{fmt_num(abs(net))}元")


    elif mode == "3":
        st.subheader("模式3：无佣金模式")
        amount_hit = st.number_input("今日出票金额", min_value=0.0, value=None, step=1.0, placeholder="请输入") or 0
        amount_won = st.number_input("今日中奖金额", min_value=0.0, value=None, step=1.0, placeholder="请输入") or 0
        include_date = st.checkbox("包含日期", value=True)
    
        if amount_hit != 0 or amount_won != 0:
            prefix = f"{today_str}，" if include_date else ""
            result_lines.append(f"{prefix}出票{fmt_num(amount_hit)}元，中奖{fmt_num(amount_won)}元")
    
            if amount_hit is not None and amount_won is not None:
                net = amount_hit - amount_won
                if net == 0:
                    result_lines.append("正好抵消")
                else:
                    action = "我收" if net >= 0 else "我付"
                    result_lines.append(f"{action}{fmt_num(abs(net))}元")

    # Render result box regardless of input completeness
    if not result_lines:
        full_output = f"{today_str}，无下注"
    else:
        full_output = "\n".join(result_lines)

    # Green result box (visual only)
    st.markdown("""
    <style>
    div[data-testid="stMarkdownContainer"] .green-box {
        background-color: #e6ffe6;
        border-left: 5px solid #33cc33;
        padding: 15px;
        margin-top: 20px;
        border-radius: 10px;
        white-space: pre-wrap;
        font-family: monospace;
        font-size: 16px;
        line-height: 1.6;
        color: black !important;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='green-box'>{full_output}</div>", unsafe_allow_html=True)
    st.markdown("<h4>结算结果可在下方复制</h4>", unsafe_allow_html=True)
    # Code box with built-in copy button
    st.code(full_output, language="text")

if __name__ == "__main__":
    main()
