from pysat.solvers import Cadical195
from pysat.formula import CNF
import itertools
import time

start_time = time.time()

LARGER = 32
SMALLER = 8
CASES = 2 ** SMALLER

num_i = LARGER
num_j = SMALLER + 2


dmf = [0] * (LARGER - 1)
strng = "OAOAOAOAAAAOOAAAOAOOOOOAAAAOOOO"
for i in range(LARGER - 1):
    if strng[i] == "A":
        dmf[i] = 1

small_tree = [0] * (SMALLER - 1)


def l(i, j):
    return (i - 1) * num_j + j

def m(i):
    return num_i * num_j + i

def y(j):
    return num_i * num_j + num_i * CASES + j

def g(k):
    return num_i * num_j + (num_i + num_j) * CASES + k + 1

def fi(k):
    return num_i * num_j + (num_i + num_j + num_i) * CASES + k + 1
#print(m(1), y(1), g(0), fi(0))
def get_children(k):
    left_child = 2 * k + 1
    right_child = 2 * k + 2
    return left_child, right_child

for binary_string_tuple in itertools.product([0, 1], repeat=(SMALLER - 1)):
    binary_string = ''.join(map(str, binary_string_tuple)) 
    print(binary_string)
    for i in range((SMALLER - 1)):
        if binary_string[i] == '0':
            small_tree[i] = 0
        else:
            small_tree[i] = 1

    cnf = CNF()
    # Add the first clause type: (¬l(i, j) ∨ ¬l(i, k)) for all i, j ≠ k
    for i in range(1, num_i + 1):
        cnf.append([l(i, j) for j in range(1, num_j + 1)])  # At least one
        for j in range(1, num_j + 1):
            for k in range(j + 1, num_j + 1):
                cnf.append([-l(i, j), -l(i, k)])

    counter = 0
    for bst in itertools.product([0, 1], repeat=(SMALLER)):
        binary_string = ''.join(map(str, bst)) 
        for i in range(SMALLER):
            if binary_string[i] == '0':
                cnf.append([-y(counter * num_j + i + 1)])
            else:
                cnf.append([y(counter * num_j + i + 1)])

        # Add the second clause type: (¬l(i, j) ∨ ¬y(j) ∨ m(i)) for all i, j
        for i in range(1, num_i + 1):
            for j in range(1, num_j + 1):
                cnf.append([-l(i, j), -y(counter * num_j + j), m(counter * num_i + i)])
                cnf.append([-l(i, j), y(counter * num_j + j), -m(counter * num_i + i)])

        # Add clauses for internal nodes based on dmf[k]
        for k in range(LARGER // 2 - 1):  # Internal nodes
            left_child, right_child = get_children(k)
    
            # Check if we are dealing with an OR or AND operation
            if dmf[k] == 0:  # OR operation
                cnf.append([-g(counter * num_i + k), g(counter * num_i + left_child), g(counter * num_i + right_child)])
                cnf.append([g(counter * num_i + k), -g(counter * num_i + left_child)])
                cnf.append([g(counter * num_i + k), -g(counter * num_i + right_child)])
            else:  # AND operation
                cnf.append([g(counter * num_i + k), -g(counter * num_i + left_child), -g(counter * num_i + right_child)])
                cnf.append([-g(counter * num_i + k), g(counter * num_i + left_child)])
                cnf.append([-g(counter * num_i + k), g(counter * num_i + right_child)])

        for k in range(LARGER // 2 - 1, LARGER - 1):  # Leaves
            left_child = (k - LARGER // 2 + 2) * 2 - 1
            right_child = left_child + 1
            #print(k, left_child, right_child)
    
            # Check if we are dealing with an OR or AND operation
            if dmf[k] == 0:  # OR operation
                cnf.append([-g(counter * num_i + k), m(counter * num_i + left_child), m(counter * num_i + right_child)])
                cnf.append([g(counter * num_i + k), -m(counter * num_i + left_child)])
                cnf.append([g(counter * num_i + k), -m(counter * num_i + right_child)])
            else:  # AND operation
                cnf.append([g(counter * num_i + k), -m(counter * num_i + left_child), -m(counter * num_i + right_child)])
                cnf.append([-g(counter * num_i + k), m(counter * num_i + left_child)])
                cnf.append([-g(counter * num_i + k), m(counter * num_i + right_child)])

        cnf.append([-y(counter * num_j + SMALLER + 1)])  # y(1) = 0
        cnf.append([y(counter * num_j + SMALLER + 2)])   # y(2) = 1

        for k in range(SMALLER // 2 - 1):  # Internal nodes
            left_child, right_child = get_children(k)
        
            # Check if we are dealing with an OR or AND operation
            if small_tree[k] == 0:  # OR operation
                cnf.append([-fi(counter * num_j + k), fi(counter * num_j + left_child), fi(counter * num_j + right_child)])
                cnf.append([fi(counter * num_j + k), -fi(counter * num_j + left_child)])
                cnf.append([fi(counter * num_j + k), -fi(counter * num_j + right_child)])
            else:  # AND operation
                cnf.append([fi(counter * num_j + k), -fi(counter * num_j + left_child), -fi(counter * num_j + right_child)])
                cnf.append([-fi(counter * num_j + k), fi(counter * num_j + left_child)])
                cnf.append([-fi(counter * num_j + k), fi(counter * num_j + right_child)])

        for k in range(SMALLER // 2 - 1, SMALLER - 1):  # Leaves
            left_child = (k - SMALLER // 2 + 2) * 2 - 1
            right_child = left_child + 1
            #print(k, left_child, right_child)
        
            # Check if we are dealing with an OR or AND operation
            if small_tree[k] == 0:  # OR operation
                cnf.append([-fi(counter * num_j + k), y(counter * num_j + left_child), y(counter * num_j + right_child)])
                cnf.append([fi(counter * num_j + k), -y(counter * num_j + left_child)])
                cnf.append([fi(counter * num_j + k), -y(counter * num_j + right_child)])
            else:  # AND operation
                cnf.append([fi(counter * num_j + k), -y(counter * num_j + left_child), -y(counter * num_j + right_child)])
                cnf.append([-fi(counter * num_j + k), y(counter * num_j + left_child)])
                cnf.append([-fi(counter * num_j + k), y(counter * num_j + right_child)])

        cnf.append([-g(counter * num_i), fi(counter * num_j)])
        cnf.append([g(counter * num_i), -fi(counter * num_j)]) 
        counter += 1

    solver = Cadical195()
    solver.append_formula(cnf)

    satisfiable = solver.solve()
    model = solver.get_model()

    # Interpret the model
    assignment = {}
    #for i in range(num_i * num_j):
    #    if model[i] > 0:
    #        print(i + 1, i // num_j, i % num_j)
    print(1 if satisfiable else 0)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Execution time: {elapsed_time} seconds")

