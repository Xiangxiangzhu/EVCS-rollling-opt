import pickle
import time as time_count
import gurobipy as gp
from gurobipy import GRB

time1 = time_count.time()

file_name = 'price_after_MAD_96.pkl'
with open(file_name, 'rb') as fo:
    mean_for_MAD = pickle.load(fo)
print('max_price', max(mean_for_MAD))

file_name = './2EVCS/my_list_93_save.pkl'
with open(file_name, 'rb') as fo:
    my_list_last = pickle.load(fo)

file_name = './2EVCS/n_car_number_2evcs_save.pkl'
with open(file_name, 'rb') as fo:
    car_already_in = pickle.load(fo)

car_max = len(my_list_last)
print('car_max', car_max)

# create price dict
price_dict = {}
for i in range(len(mean_for_MAD)):
    # noinspection PyRedundantParentheses
    price_dict[(i)] = 30 - mean_for_MAD[i]
time, price = gp.multidict(price_dict)

# create car number
car_num = {}

for i in range(96):
    # noinspection PyRedundantParentheses
    car_num[(i)] = car_already_in[i]
time, N_car = gp.multidict(car_num)

# create car arrive time
in_time_dict = {}
for i in range(car_max):
    # noinspection PyRedundantParentheses
    in_time_dict[(i)] = my_list_last[i][2]
car, T_in = gp.multidict(in_time_dict)

# create car arrive soc
in_soc_dict = {}
for i in range(car_max):
    # noinspection PyRedundantParentheses
    in_soc_dict[(i)] = my_list_last[i][0]
car, SOC_in = gp.multidict(in_soc_dict)

# create car leave time
out_time_dict = {}
for i in range(car_max):
    # noinspection PyRedundantParentheses
    out_time_dict[(i)] = my_list_last[i][3]
car, T_out = gp.multidict(out_time_dict)

# create car leave soc
out_soc_dict = {}
for i in range(car_max):
    # noinspection PyRedundantParentheses
    out_soc_dict[(i)] = my_list_last[i][1]
car, SOC_out = gp.multidict(out_soc_dict)


def my_multiply(list1, list2, index):
    assert len(list1) == len(list2) == len(index)
    sum_temp = 0
    for item2, ind in zip(list2, index):
        sum_temp += list1[ind] * item2
    return sum_temp


# Create a new model
evcssp_model = gp.Model("evcssp")

day_time = [i for i in range(96)]  # t
car_number = [i for i in range(car_max)]  # m
evcs_list = [5, 20, 15, 20]
evcs_max_number_list = [num_temp + 10 for num_temp in evcs_list]
evcs_number = [i for i in range(len(evcs_list))]  # p
evcs_station = [[k for k in range(i)] for i in evcs_max_number_list]  # k

slow_const_power = 5.254973139368931
transformer_list = []
for evcs in evcs_list:
    transformer_list.append(evcs * slow_const_power)

x_dict = {}
for t_temp in day_time:
    for m_temp in car_number:
        for p_temp in evcs_number:
            for k_temp in evcs_station[p_temp]:
                aaa = (t_temp, m_temp, p_temp, k_temp)
                x_dict[aaa] = None
my_index, x_none = gp.multidict(x_dict)

my_car_index = {}
for t_temp in day_time:
    for m_temp in car_number:
        aaa = (t_temp, m_temp)
        my_car_index[aaa] = None
my_car_index, x_car_none = gp.multidict(my_car_index)

# Create variables
z_overline = evcssp_model.addVars(my_index, vtype=GRB.BINARY, name="z_overline")
z = evcssp_model.addVars(my_index, vtype=GRB.BINARY, name="z")
u = evcssp_model.addVars(my_index, vtype=GRB.BINARY, name="u")
soc = evcssp_model.addVars(my_car_index, lb=0.0, ub=100.0, vtype=GRB.CONTINUOUS, name='soc')
energy = evcssp_model.addVars(time, lb=0.0, vtype=GRB.CONTINUOUS, name='energy')
time_temp_square = evcssp_model.addVars(my_car_index, lb=0.0, vtype=GRB.CONTINUOUS, name='soc_temp_1')
time_temp_star = evcssp_model.addVars(my_car_index, lb=0.0, vtype=GRB.CONTINUOUS, name='soc_temp_2')

e_for_E = evcssp_model.addVars(my_index, lb=0.0, vtype=GRB.CONTINUOUS, name='v_e_for_E')
f_for_E = evcssp_model.addVars(my_index, lb=0.0, vtype=GRB.CONTINUOUS, name='v_f_for_E')

r_for_satisfaction = evcssp_model.addVars(my_car_index, lb=0.0, vtype=GRB.CONTINUOUS, name='r_for_satisfy')
s_for_satisfaction = evcssp_model.addVars(my_car_index, lb=0.0, vtype=GRB.CONTINUOUS, name='s_for_satisfy')
v_for_satisfaction = evcssp_model.addVars(my_car_index, lb=0.0, vtype=GRB.CONTINUOUS, name='v_for_satisfy')

limit_temp = evcssp_model.addVars(my_car_index, lb=0.0, vtype=GRB.CONTINUOUS, name='limit_temp')
p_for_restrict = evcssp_model.addVars(my_car_index, lb=0.0, vtype=GRB.CONTINUOUS, name='p_for_restrict')
w_for_restrict = evcssp_model.addVars(my_index, lb=0.0, vtype=GRB.CONTINUOUS, name='w_for_restrict')

overline_SOC = 100
overline_POWER = 6.333

#################################################################################################################
# Add constraints: E_t=\sum (soc_{t} -soc_{t-1})z_{t-1}
energy_consumption_p0 = {}
for t in time:
    if t >= 1:
        energy_consumption_p0[t] = evcssp_model.addConstr(
            energy[t] == gp.quicksum(
                e_for_E[t, m, p, k] - f_for_E[t, m, p, k] for tt, m, p, k in my_index if (tt == t)),
            name='energy_consumption_p0' + str(t))

energy_consumption_p1_1 = {}
for t, m, p, k in my_index:
    if t >= 1:
        energy_consumption_p1_1[t, m, p, k] = evcssp_model.addConstr(
            e_for_E[t, m, p, k] <= overline_SOC * z[(t - 1), m, p, k],
            name='energy_consumption_p1_1' + str(t) + ',' + str(m) + ',' + str(p) + ',' + str(k))

energy_consumption_p1_2 = {}
for t, m, p, k in my_index:
    energy_consumption_p1_2[t, m, p, k] = evcssp_model.addConstr(
        e_for_E[t, m, p, k] <= soc[t, m],
        name='energy_consumption_p_1_2' + str(t) + ',' + str(m) + ',' + str(p) + ',' + str(k))

energy_consumption_p1_3 = {}
for t, m, p, k in my_index:
    if t >= 1:
        energy_consumption_p1_3[t, m, p, k] = evcssp_model.addConstr(
            e_for_E[t, m, p, k] >= soc[t, m] - overline_SOC * (1 - z[(t - 1), m, p, k]),
            name='energy_consumption_p1_3' + str(t) + ',' + str(m) + ',' + str(p) + ',' + str(k))

energy_consumption_p1_4 = {}
for t, m, p, k in my_index:
    energy_consumption_p1_4[t, m, p, k] = evcssp_model.addConstr(
        e_for_E[t, m, p, k] >= 0,
        name='energy_consumption_p_1_4' + str(t) + ',' + str(m) + ',' + str(p) + ',' + str(k))

###
energy_consumption_p2_1 = {}
for t, m, p, k in my_index:
    if t >= 1:
        energy_consumption_p2_1[t, m, p, k] = evcssp_model.addConstr(
            f_for_E[t, m, p, k] <= overline_SOC * z[(t - 1), m, p, k],
            name='energy_consumption_p2_1' + str(t) + ',' + str(m) + ',' + str(p) + ',' + str(k))

energy_consumption_p2_2 = {}
for t, m, p, k in my_index:
    if t >= 1:
        energy_consumption_p2_2[t, m, p, k] = evcssp_model.addConstr(
            f_for_E[t, m, p, k] <= soc[(t - 1), m],
            name='energy_consumption_p_2_2' + str(t) + ',' + str(m) + ',' + str(p) + ',' + str(k))

energy_consumption_p2_3 = {}
for t, m, p, k in my_index:
    if t >= 1:
        energy_consumption_p2_3[t, m, p, k] = evcssp_model.addConstr(
            f_for_E[t, m, p, k] >= soc[(t - 1), m] - overline_SOC * (1 - z[(t - 1), m, p, k]),
            name='energy_consumption_p2_3' + str(t) + ',' + str(m) + ',' + str(p) + ',' + str(k))

energy_consumption_p2_4 = {}
for t, m, p, k in my_index:
    energy_consumption_p2_4[t, m, p, k] = evcssp_model.addConstr(
        f_for_E[t, m, p, k] >= 0,
        name='energy_consumption_p_2_4' + str(t) + ',' + str(m) + ',' + str(p) + ',' + str(k))

#################################################################################################################
# Add constraints: soc_{t,m}=S(   T( soc(t-1,m) ) + z \delta t  )
charge_according_to_z_1 = {}
for t, m in my_car_index:
    if t >= 1:
        charge_according_to_z_1[t, m] = evcssp_model.addGenConstrPWL(time_temp_square[t, m], soc[t, m],
                                                                     [-0.9, 0, 5, 9.32, 10.66, 12, 13.34, 14.68, 15],
                                                                     [0, 0, 39.173, 73.862, 83.432, 90.599, 95.990, 100,
                                                                      100], name='charge_according_to_z_1' + str(
                t) + '+' + str(m))

charge_according_to_z_2 = {}
for t, m in my_car_index:
    if t >= 1:
        charge_according_to_z_2[t, m] = evcssp_model.addConstr(
            time_temp_square[t, m] == time_temp_star[t, m] + gp.quicksum(
                z[t, m, p, k] for tt, mm, p, k in my_index if (tt == t and mm == m)) * 1,
            name='charge_according_to_z_2' + str(t) + '+' + str(m))

charge_according_to_z_3 = {}
for t, m in my_car_index:
    if t >= 1:
        charge_according_to_z_3[t, m] = evcssp_model.addGenConstrPWL(soc[(t - 1), m], time_temp_star[t, m],
                                                                     [-0.9, 0, 39.173, 73.862, 83.432, 90.599, 95.990,
                                                                      100, 101],
                                                                     [0, 0, 5, 9.32, 10.66, 12, 13.34, 14.68, 14.68],
                                                                     name='charge_according_to_z_3' + str(
                                                                         t) + '+' + str(m))

#################################################################################################################
# Add constraints: (soc_{t,m} - \beta Q T_leave) sum sum u >=0
user_satisfaction = {}
for t, m in my_car_index:
    leave_flag_2 = True if t == T_out[m] else False
    user_satisfaction[t, m] = evcssp_model.addConstr(
        ((soc[t, m] - SOC_out[m] * leave_flag_2) * gp.quicksum(
            u[t, m, p, k] for tt, mm, p, k in my_index if (tt == t and mm == m))) >= 0,
        name='user_satisfaction' + str(t) + ',' + str(m))

user_satisfaction_1 = {}
for t, m in my_car_index:
    leave_flag_2 = True if t == T_out[m] else False
    user_satisfaction_1[t, m] = evcssp_model.addConstr(
        r_for_satisfaction[t, m] == soc[t, m] - SOC_out[m] * leave_flag_2,
        name='user_satisfaction_1' + str(t) + ',' + str(m))

user_satisfaction_2 = {}
for t, m in my_car_index:
    user_satisfaction_2[t, m] = evcssp_model.addConstr(
        s_for_satisfaction[t, m] == gp.quicksum(
            u[t, m, p, k] for tt, mm, p, k in my_index if (tt == t and mm == m)),
        name='user_satisfaction_2' + str(t) + ',' + str(m))

user_satisfaction_3 = {}
for t, m in my_car_index:
    user_satisfaction_3[t, m] = evcssp_model.addConstr(
        v_for_satisfaction[t, m] <= overline_SOC * s_for_satisfaction[t, m],
        name='user_satisfaction_3' + str(t) + ',' + str(m))

user_satisfaction_4 = {}
for t, m in my_car_index:
    user_satisfaction_4[t, m] = evcssp_model.addConstr(
        v_for_satisfaction[t, m] <= r_for_satisfaction[t, m],
        name='user_satisfaction_4' + str(t) + ',' + str(m))

user_satisfaction_5 = {}
for t, m in my_car_index:
    user_satisfaction_5[t, m] = evcssp_model.addConstr(
        v_for_satisfaction[t, m] >= r_for_satisfaction[t, m] - overline_SOC * (1 - s_for_satisfaction[t, m]),
        name='user_satisfaction_5' + str(t) + ',' + str(m))

user_satisfaction_6 = {}
for t, m in my_car_index:
    user_satisfaction_6[t, m] = evcssp_model.addConstr(
        v_for_satisfaction[t, m] >= 0,
        name='user_satisfaction_6' + str(t) + ',' + str(m))
#################################################################################################################
# Add constraints: soc>= \alpha Q
init_soc_1 = {}
for t, m in my_car_index:
    init_soc_1[t, m] = evcssp_model.addConstr(soc[t, m] >= SOC_in[m], name='init_soc_1' + str(t) + ',' + str(m))

# Add constraints: soc>= soc_{t-1}
init_soc_2 = {}
for t, m in my_car_index:
    if t >= 1:
        init_soc_2[t, m] = evcssp_model.addConstr(soc[t, m] >= soc[(t - 1), m],
                                                  name='init_soc_2' + str(t) + ',' + str(m))

# Add constraints: soc<= 100(1-T_arrive) + alpha Q T
init_soc_3 = {}
for t, m in my_car_index:
    arrive_flag = True if t == T_in[m] else False
    init_soc_3[t, m] = evcssp_model.addConstr(soc[t, m] <= (100 * (1 - arrive_flag) + SOC_in[m] * arrive_flag),
                                              name='init_soc_3' + str(t) + ',' + str(m))

#################################################################################################################
# Add constraints:  0<= sum sum z P(T(soc)) <=P_overline
transformer_limit = {}
for t, m in my_car_index:
    transformer_limit[t, m] = evcssp_model.addGenConstrPWL(soc[t, m], limit_temp[t, m],
                                                           [-0.9, 0, 39.173, 73.862, 83.432, 90.599, 95.990,
                                                            100, 101],
                                                           [0, 0, 5, 9.32, 10.66, 12, 13.34, 14.68, 14.68],
                                                           name='transformer_limit' + str(
                                                               t) + '+' + str(m))

transformer_restrict_1 = {}
for t, m in my_car_index:
    transformer_restrict_1[t, m] = evcssp_model.addGenConstrPWL(limit_temp[t, m], p_for_restrict[t, m],
                                                                [-0.9, 0, 0, 5, 9.32, 10.66, 12, 13.34, 14.68, 14.68,
                                                                 15],
                                                                [0, 0, 6, 6.105, 6.333, 4.739, 3.596, 2.675, 1.968, 0,
                                                                 0],
                                                                name='transformer_restrict_1' + str(
                                                                    t) + '+' + str(m))

transformer_restrict_2 = {}
for t, m, p, k in my_index:
    transformer_restrict_2[t, m, p, k] = evcssp_model.addConstr(
        w_for_restrict[t, m, p, k] <= overline_POWER * z[t, m, p, k],
        name='transformer_restrict_2' + str(t) + '+' + str(m))

transformer_restrict_3 = {}
for t, m, p, k in my_index:
    transformer_restrict_3[t, m, p, k] = evcssp_model.addConstr(
        w_for_restrict[t, m, p, k] <= p_for_restrict[t, m],
        name='transformer_restrict_3' + str(t) + '+' + str(m))

transformer_restrict_4 = {}
for t, m, p, k in my_index:
    transformer_restrict_4[t, m, p, k] = evcssp_model.addConstr(
        w_for_restrict[t, m, p, k] >= p_for_restrict[t, m] - overline_POWER * (1 - z[t, m, p, k]),
        name='transformer_restrict_4' + str(t) + '+' + str(m))

transformer_restrict_5 = {}
for t, m, p, k in my_index:
    transformer_restrict_5[t, m, p, k] = evcssp_model.addConstr(
        w_for_restrict[t, m, p, k] >= 0,
        name='transformer_restrict_5' + str(t) + '+' + str(m))

transformer_restrict_6 = {}
for t in time:
    for p in evcs_number:
        transformer_restrict_6[t, p] = evcssp_model.addConstr(
            gp.quicksum(w_for_restrict[t, m, p, k] for tt, m, pp, k in my_index if
                        (tt == t and pp == p)) <= transformer_list[p],
            name='transformer_restrict_6' + ',' + str(t) + ',' + str(p))

#################################################################################################################

# Add constraints: \sum{z_overline}=N_car[t]
in_car_sum = {}
for t in time:
    in_car_sum[t] = evcssp_model.addConstr(
        gp.quicksum(z_overline[t, m, p, k] for tt, m, p, k in my_index if (tt == t)) == N_car[t],
        name='sum_of_in_cars' + str(t))

# Add constraints: u<=z_overline
chargeable_cars = {}
for t, m, p, k in my_index:
    chargeable_cars[t, m, p, k] = evcssp_model.addConstr(u[t, m, p, k] <= z_overline[t, m, p, k],
                                                         name='chargeable_cars' + str(t) + ',' + str(
                                                             m) + ',' + str(p) + ',' + str(k))

# Add constraints: \sum{u}<=M_{p}_overline
charging_pile_limit = {}
for t in time:
    for p in evcs_number:
        charging_pile_limit[t, p] = evcssp_model.addConstr(
            gp.quicksum(u[t, m, p, k] for tt, m, pp, k in my_index if (tt == t and pp == p)) <=
            evcs_list[p], name='charging_pile_limit' + ',' + str(t) + ',' + str(p))

# Add constraints: u_{t}>=u_{t-1}(1-T)
car_leave_pile = {}
for t, m, p, k in my_index:
    if t > 0:
        leave_flag = True if t == T_out[m] else False
        car_leave_pile[t, m, p, k] = evcssp_model.addConstr(u[t, m, p, k] >= u[(t - 1), m, p, k] * (1 - leave_flag),
                                                            name='car_leave_pile' + str(t) + ',' + str(
                                                                m) + ',' + str(p) + ',' + str(k))

# Add constraints: z<=u
decide_charge_cars = {}
for t, m, p, k in my_index:
    decide_charge_cars[t, m, p, k] = evcssp_model.addConstr(z[t, m, p, k] <= u[t, m, p, k],
                                                            name='decide_charge_cars' + str(t) + ',' + str(
                                                                m) + ',' + str(p) + ',' + str(k))

# Add constraints: sum z_overline <=1
# one_car_in_position
one_car_in_position = {}
for t in time:
    for p in evcs_number:
        for k in evcs_station[p]:
            one_car_in_position[t, p, k] = evcssp_model.addConstr(
                gp.quicksum(
                    z_overline[t, m, p, k] for tt, m, pp, kk in my_index if (tt == t and pp == p and kk == k)) <= 1,
                name='one_car_in_position' + str(t) + ',' + str(
                    p) + ',' + str(k))

# Add constraints: sum sum z_overline <=1
# position_for_one_car
position_for_one_car = {}
for t, m in my_car_index:
    position_for_one_car[t, m] = evcssp_model.addConstr(
        gp.quicksum(z_overline[t, m, p, k] for tt, mm, p, k in my_index if (tt == t and mm == m)) <= 1,
        name='position_for_one_car' + str(t) + '+' + str(m))

# Set objective
obj = my_multiply(energy, price, time)
evcssp_model.setObjective(obj, GRB.MAXIMIZE)

time2 = time_count.time()
print('############################', time2 - time1)

evcssp_model.optimize()

time3 = time_count.time()
print('############################', time3 - time2)
evcssp_model.write("evcssp_out.sol")
