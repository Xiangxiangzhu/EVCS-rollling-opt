import math


def slow_time_to_power(charge_time, constant_power=False):
    """电动汽车慢充 充电功率 与 充电时间 的关系

    详细描述：无

    Args:
        charge_time(float):soc对应的充电时间
        constant_power(bool): whether to charge at constant power

    Returns:
        充电功率
    """

    def b_part1(x):
        return -0.002056 * math.pow(x, 4) + 0.00921 * math.pow(x, 3) + 0.03562 * math.pow(x, 2) + 0.02379 * x + 6.007

    def b_part2(x):
        return (-4.041 * x + 21.1) / (x - 0.485)

    if constant_power:
        # print('const')
        if 14.68 >= charge_time >= 0:
            return 5.254973139368931
        else:
            return 0
    else:
        # print('curve')
        if charge_time < 2.33 * 4:
            return b_part1(charge_time / 4)  # * 100 / 19.285746346634653
        elif charge_time <= 3.67 * 4:
            return b_part2(charge_time / 4)  # * 100 / 19.285746346634653
        else:
            return 0


def slow_time_to_soc(charge_time, constant_power=False):
    """电动汽车慢充 soc 与 充电时间 的关系

    详细描述：无 t_max=14.68

    Args:
        charge_time(float):soc对应的充电时间
        constant_power(bool): whether to charge at constant power

    Returns:
        soc
    """

    def c_part1(x):
        return -0.0004112 * math.pow(x, 5) + 0.0023025 * math.pow(x, 4) \
               + (0.03562 / 3) * math.pow(x, 3) + 0.011895 * math.pow(
            x, 2) + 6.007 * x

    def c_part2(x):
        return -4.041 * x + 19.140115 * math.log(abs(x - 0.485)) + 11.943306312699628

    def c_hole(x):
        if x <= 2.33 * 4:
            return c_part1(x / 4)
        elif x <= 3.67 * 4:
            return c_part2(x / 4)
        else:
            return c_part2(3.67)

    if constant_power:
        # print('const')
        if charge_time <= 0:
            return 0
        elif charge_time >= 14.68:
            return 100
        else:
            return 100 * charge_time / 14.68
    else:
        # print('curve')
        return 100 * c_hole(charge_time) / 19.285746346634653


def slow_soc_to_time(soc, constant_power=False):
    """电动汽车慢充 soc 与 充电时间 的关系

    详细描述：无

    Args:
        soc(float):ev当前的soc状态
        constant_power(bool): whether to charge at constant power

    Returns:
        时间
    """

    def s_t_t_1(soc):
        return (-4.276 * (10 ** -5)) * math.pow(soc, 2) + 0.1295 * soc

    def s_t_t_2(soc):
        return (4.742 * (10 ** -6)) * math.pow(soc, 4) - 0.001529 * math.pow(soc, 3) \
               + 0.1871 * math.pow(soc, 2) - 10.15 * soc + 213.1 + 0.1787983924863248

    if constant_power:
        # print('const')
        if soc <= 0:
            return 0
        elif soc >= 100:
            return 14.68
        else:
            return 14.68 * soc / 100
    else:
        # print('curve')
        if soc < 0:
            return 0
        elif 0 <= soc <= 73.89239629561729:
            return s_t_t_1(soc)
        elif 73.89239629561729 < soc <= 100:
            return s_t_t_2(soc) + 0.2012016075138625 * (soc - 73.89239629561729) / 26.10760370438271
        else:
            return 14.68


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    #     time_test = [0.1 * i for i in range(170)]
    #     power_test = [slow_time_to_power(t) for t in time_test]
    #     plt.plot(power_test)
    #     # plt.show()
    #     time_test = 10.66
    #     print(slow_time_to_power(time_test))
    #     pass
    #
    # # -0.9      0
    # # 0         0
    # # 0         6
    # # 5        6.105
    # # 9.32     6.333
    # # 10.66    4.739
    # # 12       3.569
    # # 13.34    2.675
    # # 14.68    1.968
    # # 14.68    0
    # # 15       0

    time_test = [0.1 * i for i in range(170)]
    soc_test = [slow_time_to_soc(t) for t in time_test]
    plt.plot(soc_test)
    plt.show()
    time_test = 5
    print(slow_time_to_soc(time_test))
    pass

# -0.9      0
# 0         0
# 5         39.173
# 9.32      73.862
# 10.66     83.432
# 12        90.599
# 13.34     95.990
# 14.68     100
# 15        100

#     soc_test = [1 * i for i in range(110)]
#     time_test = [slow_soc_to_time(soc) for soc in soc_test]
#     plt.plot(soc_test)
#     plt.show()
#     soc_test = 13.34
#     print(slow_time_to_soc(soc_test))
#     pass
#
# # -0.9      0
# # 0         0
# # 9.32      73.862
# # 10.66     83.432
# # 12        90.599
# # 13.34     95.990
# # 14.68     100
# # 15        100
