import streamlit as st
from datetime import datetime, timedelta, timezone

# 格式化数字：整数不显示小数，保留最多两位小数，末尾去掉0和点
def fmt_num(n):
    if n is None:
        return "—"
    if n == int(n):
        return str(int(n))
    return f"{n:.2f}".rstrip('0').rstrip('.')

def init_session():
    defaults = {
        "mode": "1",
        "amount_hit": None,
        "amount_won": None,
        "leftover": None,
        "leftover_choice": "我收0元",
        "has_h": False,
        "fen": None,
        "price": None,
        "include_date": True
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

def main():
    # 设置网页标题和图标
    st.set_page_config(page_title="🧮 彩票结算工具", page_icon="🧮")
    st.title("🧮 彩票结算工具")
    st.markdown("帮你快速算清今天谁收钱、谁付钱的彩票结算神器")

    # 获取当前北京时间字符串，例如 "6月15日"
    china_time = datetime.now(timezone(timedelta(hours=8)))
    today_str = f"{china_time.month}月{china_time.day}日"

    if "amount_hit" not in st.session_state:
        st.session_state.amount_hit = None
    if "amount_won" not in st.session_state:
        st.session_state.amount_won = None

    # 模式选择下拉框，显示为中文名称
    mode = st.selectbox("请选择模式", ["1", "2", "3", "4"], format_func=lambda x: {
        "1": "模式1：钱多多模式",
        "2": "模式2：大赢家模式",
        "3": "模式3：无佣金模式",
        "4": "模式4：营业额模式",
    }[x])

    result_lines = []  # 用于存储每行结算说明文本

    # ===== 模式1：钱多多 =====
    if mode == "1":
        st.subheader("模式1：钱多多模式")
    
        # 输入区：出票金额、中奖金额、昨日剩余金额
        amount_hit = st.number_input("今日出票金额", min_value=0.0, value=st.session_state.amount_hit, step=1.0, key="amount_hit", placeholder="请输入")
        amount_won = st.number_input("今日中奖金额", min_value=0.0, value=st.session_state.amount_won, step=1.0, key="amount_won", placeholder="请输入")
        leftover = st.number_input("昨日剩余", min_value=0.0, value=None, step=1.0, placeholder="选填")
        
        # 处理“昨日剩余”的收/付方向
        if leftover is not None and leftover != 0:
            options = [f"我收{fmt_num(leftover)}元", f"我付{fmt_num(leftover)}元"]
            leftover_choice = st.radio("选择昨日剩余类型", options)
            if leftover is not None:
                if "我付" in leftover_choice:
                    leftover = -leftover  # 内部处理为负数，表示“我付”

        include_date = st.checkbox("包含日期", value=True)  # 是否在输出中包含日期
        has_h = st.checkbox("包含合买")  # 是否包含合买信息

        # 合买部分的输入与处理
        fen = price = total_hemai = None
        if has_h:
            fen = st.number_input("合买份数", min_value=0.0, value=None, step=1.0, placeholder="请输入")
            price = st.number_input("每份金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
            if fen is not None and price is not None:
                total_hemai = fen * price  # 合买总金额
                total_hemai_kouyong = total_hemai * 0.92  # 合买扣佣后
    
        # 出票金额按96%结算
        kouyong = amount_hit * 0.96 if amount_hit is not None else None
        
        # 加上“我应收的昨日剩余”后，计算我总收入
        adjusted_hit = kouyong + (leftover if leftover and leftover > 0 else 0) if kouyong is not None else None
        if amount_hit is None:
            adjusted_hit = leftover if leftover and leftover > 0 else 0
        
        # 加上“我应付的昨日剩余”和合买后，计算我总支出
        adjusted_won = (amount_won or 0) + (abs(leftover) if leftover and leftover < 0 else 0) + (total_hemai_kouyong if fen is not None and price is not None else 0)

        # 结算金额 = 收入 - 支出
        net = (adjusted_hit or 0) - (adjusted_won or 0)
        action = "我收" if net >= 0 else "我付"

        prefix = f"{today_str}，" if include_date else ""

        # 构造第一行输出（出票）
        if amount_hit is not None:
            if amount_hit == 0:
                first_line = f"{prefix}今日未出票"
            else:
                first_line = f"{prefix}出票{fmt_num(amount_hit)}元，扣佣后{fmt_num(kouyong)}元"
            if leftover and leftover > 0:
                first_line += f"，昨日我应收{fmt_num(leftover)}元。【共收{fmt_num(adjusted_hit)}元】"
            result_lines.append(first_line)
            if amount_won is None and leftover and leftover < 0:
                result_lines.append(f"昨日我应付{fmt_num(abs(leftover))}元")
            
        # 构造第二行输出（中奖）
        if amount_won is not None:
            second_line = "未中奖" if amount_won == 0 else f"中奖{fmt_num(amount_won)}元"
            if leftover and leftover < 0:
                second_line += f"，昨日我应付{fmt_num(abs(leftover))}元"
                if fen is None or price is None:
                    second_line += f"。【共付{fmt_num(adjusted_won)}元】"
            if fen is None or fen == 0 or price is None or price == 0:
                result_lines.append(second_line)
            if amount_hit is None and leftover and leftover > 0:
                result_lines.insert(0, f"{prefix}昨日我应收{fmt_num(leftover)}元")
            
        # 如果既没有出票也没有中奖，但有昨日剩余，也要输出
        if amount_hit is None and amount_won is None and leftover:
            if leftover > 0:
                result_lines.append(f"{prefix}昨日我应收{fmt_num(leftover)}元")
            elif leftover < 0:
                result_lines.append(f"{prefix}昨日我应付{fmt_num(abs(leftover))}元")
            action = "我收" if leftover >= 0 else "我付"
            result_lines.append(f"{action}{fmt_num(abs(leftover))}元")

        # 输出合买信息
        if has_h and fen is not None and price is not None:
            if total_hemai != 0:
                second_line += f"\n合买{fmt_num(fen)}份{fmt_num(total_hemai)}元，扣佣后{fmt_num(total_hemai_kouyong)}元"
                if amount_hit is not None and amount_hit != 0:
                    second_line += f"。【共付{fmt_num(adjusted_won)}元】"
                result_lines.append(second_line)
        
        # 输出最后的结算结果
        if amount_hit is not None or amount_won is not None:
            result_lines.append(f"{action}{fmt_num(abs(net))}元" + ("，记着明天打票抵扣" if action == "我付" and abs(net) < 500 else ""))

        # 彩蛋
        if fen == 5201314:
            result_lines.clear()
            result_lines.append("""To：我最闪耀的茜子宝贝✨
你像夏天的汽水，冒着泡、带着甜，
我呢，就是那个每天被你晃晕的小笨蛋。
认识你之后，世界都开始有了滤镜，
路边的花更香了，晚霞更粉了...
每天想你，不是习惯，是喜欢。
你笑的时候，世界都亮了。
你不在的时候，我就偷偷想你。
我爱你，真的很爱那种——
“全世界都不重要，只想缠着你说废话”的爱！
你的小跟班--小刘❤️""")

    # ===== 模式2：大赢家 =====
    elif mode == "2":
        st.subheader("模式2：大赢家模式")
    
        # 四个输入项：她打的、我打的、她中奖、我中奖
        ta_da = st.number_input("她找我打金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        wo_da = st.number_input("我找她打金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        ta_won = st.number_input("她中奖金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        wo_won = st.number_input("我中奖金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        include_date = st.checkbox("包含日期", value=True)

        # 打票金额统一按96%结算
        kouyong_ta_da = ta_da * 0.96 if ta_da is not None else 0
        kouyong_wo_da = wo_da * 0.96 if wo_da is not None else 0
        income = kouyong_ta_da  # 我从她这里收的钱
        expense = kouyong_wo_da  # 我付给她的钱
        net = income - expense
        action = "我收" if net >= 0 else "我付"

        parts_desc = []  # 存储打票相关描述

        if ta_da:
            parts_desc.append(f"你找我打{fmt_num(ta_da)}元")
        if wo_da:
            parts_desc.append(f"我找你打{fmt_num(wo_da)}元")

        prefix = f"{today_str}，" if include_date else ""

        # 票款抵消情况输出
        if len(parts_desc) == 2:
            diff = ta_da - wo_da
            tag = "你找我打" if diff > 0 else "我找你打"
            if diff == 0:
                result_lines.append(f"{prefix}{parts_desc[0]}，{parts_desc[1]}，出票抵消")
            else:
                result_lines.append(f"{prefix}{parts_desc[0]}，{parts_desc[1]}，等于{tag}{fmt_num(abs(diff))}元，扣佣后{fmt_num(abs(diff) * 0.96)}元")
        elif len(parts_desc) == 1:
            result_lines.append(f"{prefix}{parts_desc[0]}，扣佣后{fmt_num(kouyong_ta_da if ta_da else kouyong_wo_da)}元")

        # 中奖金额处理
        prize_parts_desc = []
        if ta_won:
            prize_parts_desc.append(f"你中奖{fmt_num(ta_won)}元")
        if wo_won:
            prize_parts_desc.append(f"我中奖{fmt_num(wo_won)}元")
        
        if len(prize_parts_desc) == 2:
            prize_diff = ta_won - wo_won
            prize_tag = "你中奖" if prize_diff > 0 else "我中奖"
            if prize_diff == 0:
                result_lines.append(f"{prize_parts_desc[0]}，{prize_parts_desc[1]}，中奖抵消")
            else:
                result_lines.append(f"{prize_parts_desc[0]}，{prize_parts_desc[1]}，等于{prize_tag}{fmt_num(abs(prize_diff))}元")
                net -= prize_diff if prize_diff > 0 else -prize_diff
        elif len(prize_parts_desc) == 1:
            result_lines.append(prize_parts_desc[0])
            if ta_won and not wo_won:
                net -= ta_won
            elif wo_won and not ta_won:
                net += wo_won

        # 最终结算输出
        if (ta_da is not None or wo_da is not None or ta_won is not None or wo_won is not None):
            if net != 0:
                final_action = "我收" if net >= 0 else "我付"
                result_lines.append(f"{final_action}{fmt_num(abs(net))}元")
            else:
                result_lines.append("正好抵消")

    # ===== 模式3：无佣金模式 =====
    elif mode == "3":
        st.subheader("模式3：无佣金模式")
        amount_hit = st.number_input("今日出票金额", min_value=0.0, value=None, step=1.0, placeholder="请输入") or 0
        amount_won = st.number_input("今日中奖金额", min_value=0.0, value=None, step=1.0, placeholder="请输入") or 0
        include_date = st.checkbox("包含日期")
    
        if amount_hit != 0 or amount_won != 0:
            prefix = f"{today_str}，" if include_date else ""
            result_lines.append(f"{prefix}出票{fmt_num(amount_hit)}元，中奖{fmt_num(amount_won)}元")
    
            net = amount_hit - amount_won
            if net == 0:
                result_lines.append("正好抵消")
            else:
                action = "我收" if net >= 0 else "我付"
                result_lines.append(f"{action}{fmt_num(abs(net))}元")

    elif mode == "4":
        st.subheader("模式4：营业额模式")
        fucai = st.number_input("福彩出票金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        ticai = st.number_input("体彩出票金额", min_value=0.0, value=None, step=1.0, placeholder="请输入")
        qdd = st.number_input("钱多多出票金额", min_value=0.0, value=None, step=1.0, placeholder="选填")
        dyj = st.number_input("大赢家出票金额", min_value=0.0, value=None, step=1.0, placeholder="选填")
        ggl = st.number_input("刮刮乐金额", min_value=0.0, value=None, step=1.0, placeholder="选填")
        error = False
        if qdd is not None and fucai is not None and qdd > fucai:
            st.warning("钱多多出票大于本店福彩出票金额，请检查，如正确可忽略")
        if qdd is not None and ticai is not None and qdd > ticai:
            st.warning("钱多多出票大于本店体彩出票金额，请检查，如正确可忽略")
        if dyj is not None and fucai is not None and dyj > fucai:
            st.warning("大赢家出票大于本店福彩出票金额，请检查，如正确可忽略")
        if dyj is not None and ticai is not None and dyj > ticai:
            st.warning("大赢家出票大于本店体彩出票金额，请检查，如正确可忽略")
        if qdd is not None and dyj is not None and ticai is not None and fucai is not None:
            if (qdd > (fucai + ticai)) or (qdd > (fucai + ticai)) or ((qdd + dyj) > (fucai + ticai)):
                st.error("钱多多或大赢家出票大于本店总出票金额，请再次核对！")
                error = True
        total = (fucai or 0) + (ticai or 0) + (ggl or 0)
        total_bendian = max((fucai or 0) + (ticai or 0) - (qdd or 0) - (dyj or 0) + (ggl or 0), 0)
        fucai_kouyong = fucai * 0.92 if fucai is not None else 0
        ticai_kouyong = ticai * 0.92 if ticai is not None else 0
        ggl_kouyong = ggl * 0.92 if ggl is not None else 0
        total_kouyong = (fucai_kouyong or 0) + (ticai_kouyong or 0) + (ggl_kouyong or 0)
        profit = max(max(((fucai or 0) + (ticai or 0) - (qdd or 0) - (dyj or 0)) * 0.08, 0) + ((qdd or 0) + (dyj or 0)) * 0.04 + (ggl or 0) * 0.08, 0)
        
        if error == False:
            if fucai is not None:
                result_lines.append(f"福彩本店出票约{fmt_num(max((fucai - (dyj or 0)), 0))}元，本店收入约{fmt_num(max(((fucai - (dyj or 0)) * 0.08), 0))}元")
            if ticai is not None:
                result_lines.append(f"体彩本店出票约{fmt_num(max((ticai - (qdd or 0)), 0))}元，本店收入约{fmt_num(max(((ticai - (qdd or 0)) * 0.08), 0))}元")
            if ggl is not None:
                result_lines.append(f"刮刮乐收入{fmt_num(ggl - ggl_kouyong)}元")
            if fucai is not None or ticai is not None or ggl is not None:
                result_lines.append("----------")
                result_lines.append(f"今日总营业额{fmt_num(total)}元，本店营业额{fmt_num(total_bendian)}元")
                result_lines.append(f"今日净收入{fmt_num(profit)}元")
            if fucai is None and ticai is None and ggl is None:
                result_lines.append("请输入至少一项")

    # ===== 输出渲染 =====
    if mode in ["1", "2", "3"]:
        if not result_lines:
            full_output = f"{today_str}，无下注"
        else:
            full_output = "\n".join(result_lines)
    else:
        full_output = "\n".join(result_lines)
        
    # 自定义绿色背景结果展示框（美观）
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

    # 输出结果代码框，方便复制
    if mode in ["1", "2", "3"]:
        st.markdown("<h4>结算结果可在下方复制</h4>", unsafe_allow_html=True)
        if not result_lines:
            spaced_output = "请输入至少一项"
        else:
            spaced_output = "\n\n".join(result_lines)
        st.code(spaced_output, language="text")

# 主函数入口
if __name__ == "__main__":
    main()
