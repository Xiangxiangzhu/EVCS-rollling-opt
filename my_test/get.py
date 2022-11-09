import gurobipy as gp
from gurobipy import GRB

m = gp.Model("mip1")

# Create variables
x = m.addVar(vtype=GRB.BINARY, name="x")
y = m.addVar(vtype=GRB.BINARY, name="y")
z = m.addVar(vtype=GRB.BINARY, name="z")


m.update()
m.read("out.sol")
print(1)
