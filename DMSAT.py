from pysat.solvers import Cadical195
from pysat.formula import CNF
import itertools
import time

start_time = time.time()

num_i = 64
num_j = 18

cnf = CNF()

dmf = [0] * 63

def l(i, j):
    return (i - 1) * num_j + j

def m(i):
    return num_i * num_j + i

def y(j):
    return num_i * num_j + num_i + j

def g(k):
    return num_i * num_j + num_i + num_j + k + 1

def fi(k):
    return num_i * num_j + num_i + num_j + num_i + k

def get_children(k):
    left_child = 2 * k + 1
    right_child = 2 * k + 2
    return left_child, right_child

# Add the first clause type: (¬l(i, j) ∨ ¬l(i, k)) for all i, j ≠ k
for i in range(1, num_i + 1):
    for j in range(1, num_j + 1):
        for k in range(1, num_j + 1):
            if j != k:
                cnf.append([-l(i, j), -l(i, k)])

# Add the second clause type: (¬l(i, j) ∨ ¬y(j) ∨ m(i)) for all i, j
for i in range(1, num_i + 1):
    for j in range(1, num_j + 1):
        cnf.append([-l(i, j), -y(j), m(i)])

# Add clauses for internal nodes based on dmf[k]
for k in range(31):  # Internal nodes are from 0 to 62
    left_child, right_child = get_children(k)
    
    # Check if we are dealing with an OR or AND operation
    if dmf[k] == 0:  # OR operation
        cnf.append([-g(k), g(left_child), g(right_child)])
    else:  # AND operation
        cnf.append([-g(k), -g(left_child), -g(right_child)])

for k in range(31, 63):  # Leaves
    left_child = (k - 30) * 2 - 1
    right_child = left_child + 1
    
    # Check if we are dealing with an OR or AND operation
    if dmf[k] == 0:  # OR operation
        cnf.append([-g(k), m(left_child), m(right_child)])
    else:  # AND operation
        cnf.append([-g(k), -m(left_child), -m(right_child)])

cnf.append([-y(1)])  # y(1) = 0
cnf.append([y(2)])   # y(2) = 1

counter = 0
for binary_string_tuple in itertools.product([0, 1], repeat=15):
    binary_string = ''.join(map(str, binary_string_tuple)) 
    for k in range(7):  # Internal nodes are from 0 to 6
        left_child, right_child = get_children(k)
        
        # Check if we are dealing with an OR or AND operation
        if binary_string[k] == '0':  # OR operation
            cnf.append([-fi(counter + k), fi(counter + left_child), fi(counter + right_child)])
        else:  # AND operation
            cnf.append([-fi(counter + k), -fi(counter + left_child), -fi(counter + right_child)])
    for k in range(7, 15):  # Leaves
        left_child = (k - 6) * 2 - 1
        right_child = left_child + 1
        
        # Check if we are dealing with an OR or AND operation
        if binary_string[k] == '0':  # OR operation
            cnf.append([-fi(counter + k), y(left_child), y(right_child)])
        else:  # AND operation
            cnf.append([-fi(counter + k), -y(left_child), -y(right_child)])

    cnf.append([-g(0), fi(counter)])
    cnf.append([g(0), -fi(counter)]) 
    counter += 15

solver = Cadical195()
solver.append_formula(cnf)

satisfiable = solver.solve()
print("Satisfiable" if satisfiable else "Unsatisfiable")

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Execution time: {elapsed_time} seconds")


