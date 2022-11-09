import pickle

file_dir = 'data/'
file_name = file_dir + 'car_flow_in_2evcs_save.pkl'
with open(file_name, 'rb') as fo:
    car_flow_in = pickle.load(fo)

test_time = 96

test_car_flow_in = [0 for _ in range(test_time)]
test_car_flow_in[1] = 1

test_car_flow_in = car_flow_in

print('sum', sum(car_flow_in))
print('test_sum', sum(test_car_flow_in))

file_name = file_dir + 'end_soc_300_save.pkl'
with open(file_name, 'rb') as fo:
    end_soc_300 = pickle.load(fo)

file_name = file_dir + 'init_soc_300_save.pkl'
with open(file_name, 'rb') as fo:
    init_soc_300 = pickle.load(fo)

file_name = file_dir + 'stay_time_300_save.pkl'
with open(file_name, 'rb') as fo:
    stay_time_300 = pickle.load(fo)

my_list = [[] for _ in range(300)]

for tt, time_list in enumerate(my_list):
    time_list.append(init_soc_300[tt])
    time_list.append(end_soc_300[tt])

# my_list = [my_list[18] for _ in range(300)]

car_number = 0
for yyt, ev_flow in enumerate(test_car_flow_in):
    # print('yyt', yyt)
    # print('ev_flow', ev_flow)
    for ev_nnn in range(ev_flow):
        # print('car_number', car_number)
        # print('ev_nnn', ev_nnn)
        # noinspection SpellCheckingInspection
        aaaa = yyt + stay_time_300[car_number] + 1
        if aaaa <= 95:
            my_list[car_number].append(yyt)
            my_list[car_number].append(aaaa)
            car_number += 1
    pass

pass

# my_list_last = my_list[:sum(test_car_flow_in)]
my_list_last = my_list[:car_number]

# pickle　保存
file_name = 'my_list_8_test' + '_save.pkl'
with open(file_name, 'wb') as fp:
    pickle.dump(my_list_last, fp)

#  净车流量
net_car_flow_in = []
car_already_in = []
car_already_in_temp = 0
for time_temp in range(test_time):
    number_temp = 0
    for ev_number, car_temp in enumerate(my_list_last):
        if time_temp == car_temp[2]:
            number_temp += 1
        if time_temp == car_temp[3]:
            number_temp -= 1
    car_already_in_temp += number_temp
    net_car_flow_in.append(number_temp)
    car_already_in.append(car_already_in_temp)

# SOC_out
# T_out
# SOC_in
# T_in
# N_car

# pickle　保存
file_name = 'n_car_number_2evcs_test' + '_save.pkl'
with open(file_name, 'wb') as fp:
    pickle.dump(car_already_in, fp)
