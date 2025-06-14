from datetime import date


def fmt_num(n):
    if n == int(n):
        return str(int(n))
    else:
        return f"{n:.2f}".rstrip('0').rstrip('.')


def main():
    today = date.today()

    while True:
        quick_input = input(
            "请输入(模式, 数值1, 数值2, 数值3)，例如: 1, 100, 90, 10\n"
            "模式1(钱多多模式): 今日出票, 今日中奖, 昨日剩余[可留空，正数我收，负数我付]，结尾加h可输入合买\n"
            "模式2(大赢家模式): 她找我打, 我找她打, 今日中奖\n"
            "模式3(无佣金模式): 今日出票, 今日中奖\n"
        ).strip()

        try:
            parts = quick_input.replace(",", " ").split()
            if len(parts) < 2:
                raise ValueError("参数不足")
            mode = parts[0]
            if mode not in ["1", "2", "3"]:
                raise ValueError("模式必须是1、2或3")

            today_str = f"{today.month}月{today.day}日"

            if mode == "1":
                amount_hit = abs(float(parts[1]))
                amount_won = abs(float(parts[2])) if len(parts) > 2 and parts[2] else 0
                leftover = 0.0
                has_h = False

                # 判断最后一个参数是否是"h"
                if len(parts) > 3:
                    if parts[-1].lower() == "h":
                        has_h = True
                        if len(parts) == 5:
                            leftover = float(parts[3])
                        elif len(parts) > 5:
                            raise ValueError("模式1输入参数太多")
                    else:
                        leftover = float(parts[3])

                kouyong = amount_hit * 0.96
                adjusted_hit = kouyong + (leftover if leftover > 0 else 0)
                adjusted_won = amount_won + (abs(leftover) if leftover < 0 else 0)

                # 如果有合买，要求用户输入份数和金额
                while has_h:
                    try:
                        hemai_input = input("请输入合买份数和一份金额：\n").strip()
                        fen_str, price_str = hemai_input.replace(",", " ").split()
                        fen = abs(float(fen_str))
                        price = abs(float(price_str))
                        if fen == 0 or price == 0:
                            has_h = False
                            break
                        total_hemai = fen * price
                        adjusted_won += total_hemai
                        break  # 成功输入就跳出循环
                    except Exception as e:
                        print(f"❌ 合买输入错误: {e}，请重新输入。")

                net = adjusted_hit - adjusted_won
                action = "我收" if net >= 0 else "我付"

                first_line = f"{today_str}，出票{fmt_num(amount_hit)}元，扣佣后{fmt_num(kouyong)}元"
                if leftover > 0:
                    first_line += f"，昨日我应收{fmt_num(leftover)}元，共收{fmt_num(adjusted_hit)}元"

                second_line = "未中奖" if amount_won == 0 else f"中奖{fmt_num(amount_won)}元"
                if leftover < 0:
                    second_line += f"，昨日我应付{fmt_num(abs(leftover))}元"
                    if not has_h:
                        second_line += f"，共付{fmt_num(adjusted_won)}元"

                print(first_line)
                print(second_line)
                if has_h:
                    print(f"合买{fmt_num(fen)}份，每份{fmt_num(price)}元，我付{fmt_num(total_hemai)}元")
                final_line = f"{action}{fmt_num(abs(net))}元"
                if action == "我付" and abs(net) < 500:
                    final_line += "，记着明天打票抵扣"
                print(final_line)
                print()

            elif mode == "2":
                ta_da = abs(float(parts[1]))  # 她找我打（我应收）
                wo_da = abs(float(parts[2])) if len(parts) > 2 and parts[2] else 0  # 我找她打（我应付本金）
                amount_won = abs(float(parts[3])) if len(parts) > 3 and parts[3] else 0 # 她中奖（我应付奖金）
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
                    print(f"{today_str}，无下注")
                elif len(parts_desc) == 2:
                    diff = ta_da - wo_da
                    tag = "你找我打" if diff > 0 else "我找你打"
                    if diff == 0:
                        print(f"{today_str}，{parts_desc[0]}，{parts_desc[1]}，正好抵消")
                    else:
                        print(
                        f"{today_str}，{parts_desc[0]}，{parts_desc[1]}，等于{tag}{fmt_num(abs(diff))}元，扣佣后{fmt_num(abs(diff) * 0.96)}元")
                else:
                    # 只有一边有金额
                    if ta_da > 0:
                        print(f"{today_str}，{parts_desc[0]}，扣佣后{fmt_num(kouyong_ta_da)}元")
                    else:
                        print(f"{today_str}，{parts_desc[0]}，扣佣后{fmt_num(kouyong_wo_da)}元")

                print("未中奖" if amount_won == 0 else f"中奖{fmt_num(amount_won)}元")
                print(f"{action}{fmt_num(abs(net))}元")
                print()

            else:  # mode == "3"
                amount_hit = abs(float(parts[1]))
                amount_won = abs(float(parts[2])) if len(parts) > 2 and parts[2] else 0

                net = amount_hit - amount_won
                action = "我收" if net >= 0 else "我付"

                print(f"{today_str}，出票{fmt_num(amount_hit)}元，中奖{fmt_num(amount_won)}元")
                if net == 0:
                    print("正好抵消")
                    print()
                else:
                    print(f"{action}{fmt_num(abs(net))}元")
                    print()
            #break

        except Exception as e:
            print(f"❌ 输入错误: {e}")
            print("请重新输入。\n")


if __name__ == "__main__":
    main()

