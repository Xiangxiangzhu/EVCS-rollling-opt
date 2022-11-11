import gurobipy as gp
from gurobipy import GRB

# model = gp.Model("my_test")
#
# x = model.addVar(vtype=GRB.CONTINUOUS, name='x')
# y = model.addVar(vtype=GRB.CONTINUOUS, name='y')
#
# xc = model.addConstr(x == 1.5, 'x_value')
# gc = model.addGenConstrPWL(x, y, [0, 1, 2], [1.5, 0, 3], "myPWLConstr")
#
# model.optimize()
#
# for v in model.getVars():
#     if v.varName == 'y':
#         print(v.varName, v.x)
# print('Obj:', model.objVal)

y_list = []
xx = 0
for _ in range(150):
    model = gp.Model("my_test")

    x = model.addVar(vtype=GRB.CONTINUOUS, name='x')
    y = model.addVar(vtype=GRB.CONTINUOUS, name='y')

    xc = model.addConstr(x == xx, 'x_value')
    # slow_time_to_power
    gc = model.addGenConstrPWL(x, y, [-0.9, 0, 0, 5, 9.32, 10.66, 12, 13.34, 14.68, 14.68, 15],
                               [0, 0, 6, 6.105, 6.333, 4.739, 3.596, 2.675, 1.968, 0, 0], "myPWLConstr")

    # slow_time_to_soc
    # gc = model.addGenConstrPWL(x, y, [-0.9, 0, 5, 9.32, 10.66, 12, 13.34, 14.68, 15],
    #                            [0, 0, 39.173, 73.862, 83.432, 90.599, 95.990, 100, 100], 'myPWLConstr')

    # slow_soc_to_time
    # gc = model.addGenConstrPWL(x, y,
    #                            [-0.9, 0, 39.173, 73.862, 83.432, 90.599, 95.990, 100, 101],
    #                            [0, 0, 5, 9.32, 10.66, 12, 13.34, 14.68, 14.68], 'myPWLConstr')

    # gc = model.addConstr(x <= y <= 15)
    # gc1 = model.addConstr(x <= y)

    model.optimize()
    xx += 0.1
    for v in model.getVars():
        if 'y' in v.varName:
            y_list.append(v.x)

    pass

import matplotlib.pyplot as plt

plt.plot(y_list)
print(max(y_list))
plt.show()
