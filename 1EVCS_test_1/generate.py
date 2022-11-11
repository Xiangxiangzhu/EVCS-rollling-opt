import pickle
import numpy as np

TEST = 96
prop = 5

file_dir = 'data/'
file_name = file_dir + 'car_flow_in_2evcs_save.pkl'
with open(file_name, 'rb') as fo:
    car_flow_in = pickle.load(fo)

test_time = TEST

test_car_flow_in = []
if TEST == 24:
    for i in range(TEST):
        temp_flow = car_flow_in[4 * i] + car_flow_in[4 * i + 1] + car_flow_in[4 * i + 2] + car_flow_in[4 * i + 3]
        test_car_flow_in.append(temp_flow)
else:
    test_car_flow_in = car_flow_in

print('sum', sum(car_flow_in))
print('test_sum', sum(test_car_flow_in))
test_car_flow_in = [int(t / prop) for t in test_car_flow_in]
test_car_flow_in[0] = 1

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

if TEST == 24:
    test_stay_time_300 = [np.ceil((s + 1) / 4) for s in stay_time_300]
else:
    test_stay_time_300 = stay_time_300

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
        aaaa = yyt + test_stay_time_300[car_number]

        if TEST == 24:
            if aaaa <= TEST - 1:
                my_list[car_number].append(yyt)
                my_list[car_number].append(aaaa)
                car_number += 1
        else:
            if aaaa <= 95:
                my_list[car_number].append(yyt)
                my_list[car_number].append(aaaa + 1)
                car_number += 1
    pass

pass

# my_list_last = my_list[:sum(test_car_flow_in)]
my_list_last = my_list[:car_number]

# pickle　保存
# file_name = 'my_list_93_save.pkl'
file_name = 'my_list_8_test' + str(prop) + '_save.pkl'
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
print("max_car_number", max(car_already_in))
# pickle　保存
# file_name = 'n_car_number_2evcs_save.pkl'
file_name = 'n_car_number_2evcs_test' + str(prop) + '_save.pkl'
with open(file_name, 'wb') as fp:
    pickle.dump(car_already_in, fp)
