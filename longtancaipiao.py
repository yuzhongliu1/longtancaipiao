import streamlit as st
from datetime import date

def fmt_num(n):
    if n == int(n):
        return str(int(n))
    else:
        return f"{n:.2f}".rstrip('0').rstrip('.')

def main():
    st.title("📋 彩票结算工具")
    st.markdown("支持 **模式1（钱多多）**、**模式2（大赢家）** 和 **模式3（无佣金）**")

    mode = st.selectbox("请选择模式", ["1", "2", "3"], format_func=lambda x: {
        "1": "模式1：钱多多模式",
        "2": "模式2：大赢家模式",
        "3": "模式3：无佣金模式"
    }[x])

    today = date.today()
    today_str = f"{today.month}月{today.day}日"

    # 创建一个空字符串，收集全部结果文本，后面放进绿色框和复制按钮
    result_text = ""

    if mode == "1":
        st.subheader("模式1：钱多多模式")

        # 不设默认值，min_value=0时，设置step=0.01，value=None让输入框空白
        amount_hit = st.number_input("今日出票金额", min_value=0.0, step=0.01, value=None)
        amount_won = st.number_input("今日中奖金额", min_value=0.0, step=0.01, value=None)
        leftover = st.number_input("昨日剩余（正数我收，负数我付）", step=0.01, value=None)
        has_h = st.checkbox("是否有合买")

        fen = price = total_hemai = 0.0
        if has_h:
            fen = st.number_input("合买份数", min_value=0.0, step=0.01, value=None)
            price = st.number_input("每份金额", min_value=0.0, step=0.01, value=None)
            if fen is not None and price is not None:
                total_hemai = fen * price

        # 处理输入为空的情况，默认0
        amount_hit = amount_hit or 0
        amount_won = amount_won or 0
        leftover = leftover or 0
        fen = fen or 0
        price = price or 0

        kouyong = amount_hit * 0.96
        adjusted_hit = kouyong + (leftover if leftover > 0 else 0)
        adjusted_won = amount_won + (abs(leftover) if leftover < 0 else 0) + total_hemai
        net = adjusted_hit - adjusted_won
        action = "我收" if net >= 0 else "我付"

        first_line = f"{today_str}，出票{fmt_num(amount_hit)}元，扣佣后{fmt_num(kouyong)}元"
        if leftover > 0:
            first_line += f"，昨日我应收{fmt_num(leftover)}元，共收{fmt_num(adjusted_hit)}元"

        second_line = "未中奖" if amount_won == 0 else f"中奖{fmt_num(amount_won)}元"
        if leftover < 0:
            second_line += f"，昨日我应付{fmt_num(abs(leftover))}元，共付{fmt_num(adjusted_won)}元"

        result_text += first_line + "\n"
        result_text += second_line + "\n"
        if has_h and fen > 0 and price > 0:
            result_text += f"合买{fmt_num(fen)}份，每份{fmt_num(price)}元，我付{fmt_num(total_hemai)}元\n"

        final_line = f"{action}{fmt_num(abs(net))}元"
        if action == "我付" and abs(net) < 500:
            final_line += "，记着明天打票抵扣"
        result_text += final_line

    elif mode == "2":
        st.subheader("模式2：大赢家模式")

        ta_da = st.number_input("她找我打金额", min_value=0.0, step=0.01, value=None)
        wo_da = st.number_input("我找她打金额", min_value=0.0, step=0.01, value=None)
        amount_won = st.number_input("她中奖金额", min_value=0.0, step=0.01, value=None)

        ta_da = ta_da or 0
        wo_da = wo_da or 0
        amount_won = amount_won or 0

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
            result_text += f"{today_str}，无下注\n"
        elif len(parts_desc) == 2:
            diff = ta_da - wo_da
            tag = "你找我打" if diff > 0 else "我找你打"
            if diff == 0:
                result_text += f"{today_str}，{parts_desc[0]}，{parts_desc[1]}，正好抵消\n"
            else:
                result_text += (f"{today_str}，{parts_desc[0]}，{parts_desc[1]}，等于{tag}{fmt_num(abs(diff))}元，"
                                f"扣佣后{fmt_num(abs(diff) * 0.96)}元\n")
        else:
            result_text += f"{today_str}，{parts_desc[0]}，扣佣后{fmt_num(kouyong_ta_da if ta_da > 0 else kouyong_wo_da)}元\n"

        result_text += "未中奖\n" if amount_won == 0 else f"中奖{fmt_num(amount_won)}元\n"
        result_text += f"{action}{fmt_num(abs(net))}元"

    else:  # mode == "3"
        st.subheader("模式3：无佣金模式")

        amount_hit = st.number_input("今日出票金额", min_value=0.0, step=0.01, value=None)
        amount_won = st.number_input("今日中奖金额", min_value=0.0, step=0.01, value=None)

        amount_hit = amount_hit or 0
        amount_won = amount_won or 0

        net = amount_hit - amount_won
        action = "我收" if net >= 0 else "我付"

        result_text += f"{today_str}，出票{fmt_num(amount_hit)}元，中奖{fmt_num(amount_won)}元\n"
        if net == 0:
            result_text += "正好抵消"
        else:
            result_text += f"{action}{fmt_num(abs(net))}元"

    # 显示全部结算结果在绿色框中
    st.success(result_text)

    # 复制按钮，利用st.code的交互性和js简易实现
    # Streamlit 本身不支持直接复制按钮，这里用st.text_area + st.button实现复制提示
    copied = False
    if st.button("复制结算结果"):
        st.query_params()  # 小技巧刷新一下避免重复点击
        st.code(result_text)  # 显示代码块供手动复制
        st.info("请手动选中上面内容，Ctrl+C 复制")
        copied = True


if __name__ == "__main__":
    main()
