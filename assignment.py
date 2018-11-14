# facilities planning: assignment IP
# this model is intended to minimize the total cost of investing in a set of producers to supply a set of consumers

# ---- setup the model ----

from pyomo.environ import *    # imports the pyomo envoirnment
model = AbstractModel()    # creates an abstract model
model.name = "Assignment IP Model"    # gives the model a name

# ---- define set(s) ----

model.P = Set()    # a set of producers
model.C = Set()    # a set of consumers

# ---- define parameter(s) ----

model.k = Param(model.P)    # cost to set up a producer
model.c = Param(model.P)    # the total cost/distance for a producer to satisfy a consumer (ie. transportation, labor, maintenance, etc.)
model.max = Param(model.P)    # the max number of consumers that a producer can satisfy
model.xcor = Param(model.C)    # the x coordinate of a consumer
model.ycor = Param(model.C)    # the y coordinate of a consumer
model.r = Param()    # range for a consumer to be satisfied

# ---- define variable(s) ----

model.x = Var(model.C, domain = NonNegativeReals)    # the x coordinate of a consumer's producer
model.y = Var(model.C, domain = NonNegativeReals)    # the y coordinate of a consumer's producer
model.z = Var(model.P, model.C, domain = Binary)    # a producer does/doesn't service a consumer
model.o = Var(model.P, domain = Binary)    # a producer is/isn't open
model.dx = Var(model.C, domain = NonNegativeReals)    # the x-distance between a consumer and it's producer
model.dy = Var(model.C, domain = NonNegativeReals)    # the y-distance between a consumer and it's producer

# ---- define objective function(s) ----

def obj(model):
    return sum(model.o[i] * model.k[i] for i in model.P) + sum(sum(model.c[i] * (model.dx[i,j] + model.dy[i,j]) for i in model.P) for j in model.C)

model.obj = Objective(rule = obj, sense = minimize)    # a minimization problem of the function defined above

# ---- define constraint(s) ----

def Open(model, i, j):
    return model.z[i,j] <= model.o[i]    # a producer cannot statisfy a consumer unless it is open

def Prod(model, i):
    return sum(model.z[i,j] for j in model.C) <= model.max[i]    # a producer cannot satisfy more consumers than it's max

def Cons(model, j):
    return sum(model.z[i,j] for i in model.P) == 1    # a consumer must be satisfied by one producer

def RangeX(model, j):
    return (model.xcor[j] - model.r) <= model.x[j] <= (model.xcor[j] + model.r)    # the x-coordinate of a consumer's producer must be within service range 

def RangeY(model, j):
    return (model.ycor[j] - model.r) <= model.y[j] <= (model.ycor[j] + model.r)    # the y-coordinate of a consumer's producer must be within service range

def EqnX1(model, i, j):
    return model.dx[i,j] >= model.x[j] - model.xcor[j]    # set 1 of 2 to calculate the x-distance between a consumer and it's producer

def EqnX2(model, i, j):
    return model.dx[i,j] >= model.xcor[j] - model.x[j]    # set 2 of 2 to calculate the x-distance between a consumer and it's producer

def EqnY1(model, i, j):
    return model.dy[i,j] >= model.y[j] - model.ycor[j]    # set 1 of 2 to calculate the y-distance between a consumer and it's producer

def EqnY2(model, i, j):
    return model.dy[i,j] >= model.ycor[j] - model.y[j]    # set 2 of 2 to calculate the y-distance between a consumer and it's producer

model.Setup = Constraint(model.P, model.C, rule = Open)    # the setup constraint for every producer
model.Producers = Constraint(model.P, rule = Prod)    # the service constraint for every producer
model.Consumers = Constraint(model.C, rule = Cons)    # the assignment constraint for every consumer
model.Xrange = Constraint(model.C, rule = RangeX)    # the x range constraint on a producer for every consumer
model.Yrange = Constraint(model.C, rule = RangeY)    # the y range constraint on a producer for every consumer
model.Xdistance1 = Constraint(model.P, model.C, rule = EqnX1)    # the x distance calculation between every producer and consumer (set 1 of 2)
model.Xdistance2 = Constraint(model.P, model.C, rule = EqnX2)    # the x distance calculation between every producer and consumer (set 2 of 2)
model.Ydistance1 = Constraint(model.P, model.C, rule = EqnY1)    # the y distance calculation between every producer and consumer (set 1 of 2)
model.Ydistance2 = Constraint(model.P, model.C, rule = EqnY2)    # the y distance calculation between every producer and consumer (set 2 of 2)

# ---- execute solver ----

from pyomo.opt import SolverFactory
opt = SolverFactory("glpk")
# opt = SolverFactory('ipopt',solver_io='nl')
instance = model.create_instance("assignment.dat")
results = opt.solve(instance)
instance.display()