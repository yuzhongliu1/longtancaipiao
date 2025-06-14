import streamlit as st
from datetime import datetime, timedelta, timezone

# Format numbers (remove trailing zeros)
def fmt_num(n):
    if n == int(n):
        return str(int(n))
    else:
        return f"{n:.2f}".rstrip('0').rstrip('.')

# Main app
def main():
    st.set_page_config(page_title="彩票结算工具", page_icon="📋")
    st.title("📋 彩票结算工具")
    st.markdown("支持 **模式1（钱多多）**、**模式2（大赢家）** 和 **模式3（无佣金）**")

    # China timezone
    china_time = datetime.now(timezone(timedelta(hours=8)))
    today_str = f"{china_time.month}月{china_time.day}日"

    # Mode selection
    mode = st.selectbox("请选择模式", ["1", "2", "3"], format_func=lambda x: {
        "1": "模式1：钱多多模式",
        "2": "模式2：大赢家模式",
        "3": "模式3：无佣金模式"
    }[x])

    result_lines = []

    if mode == "1":
        st.subheader("模式1：钱多多模式")
        amount_hit = st.number_input("今日出票金额", min_value=0.0, value=None, placeholder="请输入")
        amount_won = st.number_input("今日中奖金额", min_value=0.0, value=None, placeholder="请输入")
        leftover = st.number_input("昨日剩余（正数我收，负数我付）", value=None, placeholder="请输入")
        has_h = st.checkbox("是否有合买")

        fen = price = total_hemai = 0.0
        if has_h:
            fen = st.number_input("合买份数", min_value=0.0, value=None, placeholder="请输入")
            price = st.number_input("每份金额", min_value=0.0, value=None, placeholder="请输入")
            if fen and price:
                total_hemai = fen * price

        if amount_hit is not None and amount_won is not None and leftover is not None:
            kouyong = amount_hit * 0.96
            adjusted_hit = kouyong + (leftover if leftover > 0 else 0)
            adjusted_won = amount_won + (abs(leftover) if leftover < 0 else 0) + total_hemai
            net = adjusted_hit - adjusted_won
            action = "我收" if net >= 0 else "我付"

            first_line = f"{today_str}，出票{fmt_num(amount_hit)}元，扣佣后{fmt_num(kouyong)}元"
            if leftover > 0:
                first_line += f"，昨日我应收{fmt_num(leftover)}元，共收{fmt_num(adjusted_hit)}元"
            result_lines.append(first_line)

            second_line = "未中奖" if amount_won == 0 else f"中奖{fmt_num(amount_won)}元"
            if leftover < 0:
                second_line += f"，昨日我应付{fmt_num(abs(leftover))}元，共付{fmt_num(adjusted_won)}元"
            result_lines.append(second_line)

            if has_h and fen and price:
                result_lines.append(f"合买{fmt_num(fen)}份，每份{fmt_num(price)}元，我付{fmt_num(total_hemai)}元")

            final_line = f"{action}{fmt_num(abs(net))}元"
            if action == "我付" and abs(net) < 500:
                final_line += "，记着明天打票抵扣"
            result_lines.append(final_line)

    elif mode == "2":
        st.subheader("模式2：大赢家模式")

        ta_da = st.number_input("她找我打金额", min_value=0.0, value=None, placeholder="请输入")
        wo_da = st.number_input("我找她打金额", min_value=0.0, value=None, placeholder="请输入")
        amount_won = st.number_input("她中奖金额", min_value=0.0, value=None, placeholder="请输入")

        if ta_da is not None and wo_da is not None and amount_won is not None:
            kouyong_ta_da = ta_da * 0.96
            kouyong_wo_da = wo_da * 0.96
            income = kouyong_ta_da
            expense = kouyong_wo_da + amount_won
            net = income - expense
            action = "我收" if net >= 0 else "我付"

            parts_desc = []
            if ta_da > 0:
                parts_desc.append(f"你找我打{fmt_num(ta_da)}元")
            if wo_da > 0:
                parts_desc.append(f"我找你打{fmt_num(wo_da)}元")

            if len(parts_desc) == 0:
                result_lines.append(f"{today_str}，无下注")
            elif len(parts_desc) == 2:
                diff = ta_da - wo_da
                tag = "你找我打" if diff > 0 else "我找你打"
                if diff == 0:
                    result_lines.append(f"{today_str}，{parts_desc[0]}，{parts_desc[1]}，正好抵消")
                else:
                    result_lines.append(f"{today_str}，{parts_desc[0]}，{parts_desc[1]}，等于{tag}{fmt_num(abs(diff))}元，扣佣后{fmt_num(abs(diff) * 0.96)}元")
            else:
                result_lines.append(f"{today_str}，{parts_desc[0]}，扣佣后{fmt_num(kouyong_ta_da if ta_da > 0 else kouyong_wo_da)}元")

            result_lines.append("未中奖" if amount_won == 0 else f"中奖{fmt_num(amount_won)}元")
            result_lines.append(f"{action}{fmt_num(abs(net))}元")

    else:  # mode == "3"
        st.subheader("模式3：无佣金模式")

        amount_hit = st.number_input("今日出票金额", min_value=0.0, value=None, placeholder="请输入")
        amount_won = st.number_input("今日中奖金额", min_value=0.0, value=None, placeholder="请输入")

        if amount_hit is not None and amount_won is not None:
            net = amount_hit - amount_won
            action = "我收" if net >= 0 else "我付"

            result_lines.append(f"{today_str}，出票{fmt_num(amount_hit)}元，中奖{fmt_num(amount_won)}元")
            if net == 0:
                result_lines.append("正好抵消")
            else:
                result_lines.append(f"{action}{fmt_num(abs(net))}元")

    # Show result in custom green box with copy button
    if result_lines:
        final_result = "\n".join(result_lines)

        custom_css = """
        <style>
        .green-box {
            background-color: #e6ffe6;
            border-left: 5px solid #33cc33;
            padding: 15px;
            margin-top: 20px;
            border-radius: 10px;
            white-space: pre-wrap;
            font-size: 16px;
        }
        .copy-btn {
            background-color: #33cc33;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        </style>
        """

        st.markdown(custom_css, unsafe_allow_html=True)
        st.markdown(f"<div class='green-box' id='resultBox'>{final_result}</div>", unsafe_allow_html=True)
        st.markdown("""
            <button class='copy-btn' onclick="
                navigator.clipboard.writeText(document.getElementById('resultBox').innerText);
                alert('已复制结果');
            ">复制结果</button>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
