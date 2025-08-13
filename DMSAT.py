from pysat.solvers import Cadical195
from pysat.formula import CNF
import itertools
import time

start_time = time.time()

LARGER = 32
SMALLER = 8
CASES = 2 ** SMALLER #all possible values for 8 variables

num_i = LARGER
num_j = SMALLER + 2 #SMALLER variables and 2 constants


dmf = [0] * (LARGER - 1)
strng = "OAOAOAOAAAAOOAAAOAOOOOOAAAAOOOO" #O denotes "or", A - "and"
#make an array of internal nodes for larher tree with 0 for ors and 1 for ands
for i in range(LARGER - 1):
    if strng[i] == "A":
        dmf[i] = 1

small_tree = [0] * (SMALLER - 1)

#Classes of variables in cnf
def l(i, j): #True if i-th leaf contains j-th variable
    return (i - 1) * num_j + j

def m(i): #Value in i-th leaf of larger tree
    return num_i * num_j + i

def y(j): #Value of j-th variable
    return num_i * num_j + num_i * CASES + j

def g(k): #Values in internal nodes of larger tree
    return num_i * num_j + (num_i + num_j) * CASES + k + 1

def fi(k): #Values in internal nodes of smaller tree
    return num_i * num_j + (num_i + num_j + num_i) * CASES + k + 1


def get_children(k):
    #returns indeces of children of k-th node
    left_child = 2 * k + 1
    right_child = 2 * k + 2
    return left_child, right_child

for binary_string_tuple in itertools.product([0, 1], repeat=(SMALLER - 1)): #iterating through all structures of smaller tree
    binary_string = ''.join(map(str, binary_string_tuple)) 
    print(binary_string)
    for i in range((SMALLER - 1)): 
        if binary_string[i] == '0':
            small_tree[i] = 0 #0 in binary_string means "or" in the node of the smaller tree
        else:
            small_tree[i] = 1 #1 in binary_string means "and" in the node of the smaller tree

    cnf = CNF()
    #Add the first clause type: (¬l(i, j) ∨ ¬l(i, k)) for all i, j ≠ k
    #It ensures that there is only one variable or constant in each leaf of larger tree
    for i in range(1, num_i + 1):
        cnf.append([l(i, j) for j in range(1, num_j + 1)])  #At least one variable or constant in i-th of larger tree
        for j in range(1, num_j + 1):
            for k in range(j + 1, num_j + 1):
                cnf.append([-l(i, j), -l(i, k)])

    counter = 0
    #Now we iterate through all possible values for variables
    #counter indicates on which iteration we are
    for bst in itertools.product([0, 1], repeat=(SMALLER)):
        binary_string = ''.join(map(str, bst)) 
        for j in range(SMALLER):
            if binary_string[j] == '0':
                cnf.append([-y(counter * num_j + j + 1)]) #j-th variable is 0
            else:
                cnf.append([y(counter * num_j + j + 1)]) #j-th variable is 1

        #Add the second clause type: (¬l(i, j) ∨ ¬y(j) ∨ m(i)) and (¬l(i, j) ∨ y(j) ∨ ¬m(i)) for all i, j
        #It ensures that y(j) = m(i) if l(i, j) is true, in other words, if there is j-th variable in i-th leaf of larger tree,
        #then its the value in the leaf (m(i)) is equal to the value of the variable (y(j))
        for i in range(1, num_i + 1):
            for j in range(1, num_j + 1):
                cnf.append([-l(i, j), -y(counter * num_j + j), m(counter * num_i + i)])
                cnf.append([-l(i, j), y(counter * num_j + j), -m(counter * num_i + i)])

        #Add clauses for internal nodes based on dmf[k]
        for k in range(LARGER - 1):  # Internal nodes
            #Calculating the value in k-th node of the larger tree
            left_child, right_child = get_children(k)
            node_variable = g(counter * num_i + k)
            if (k < LARGER // 2 - 1): #Check if k is an internal node or leaf
                left_child_variable = g(counter * num_i + left_child)
                right_child_variable = g(counter * num_i + right_child)
            else:
                left_child_variable = m(counter * num_i + left_child)
                right_child_variable = m(counter * num_i + right_child)
            #Check if we are dealing with an OR or AND operation
            if dmf[k] == 0:  # OR operation
                cnf.append([-node_variable, left_child_variable, right_child_variable])
                cnf.append([node_variable, -left_child_variable])
                cnf.append([node_variable, -right_child_variable])
            else:  # AND operation
                cnf.append([node_variable, -left_child_variable, -right_child_variable])
                cnf.append([-node_variable, left_child_variable])
                cnf.append([-node_variable, right_child_variable])

        cnf.append([-y(counter * num_j + SMALLER + 1)])  #Variable with index (SMALLER + 1) is a 0 constant
        cnf.append([y(counter * num_j + SMALLER + 2)])   #Variable with index (SMALLER + 2) is a 1 constant

        #Same clauses for smaller tree
        for k in range(SMALLER - 1):
            left_child, right_child = get_children(k)
            node_variable = fi(counter * num_i + k)
            if (k < SMALLER // 2 - 1): #Check if k is an internal node or leaf
                left_child_variable = fi(counter * num_i + left_child)
                right_child_variable = fi(counter * num_i + right_child)
            else:
                left_child_variable = y(counter * num_i + left_child)
                right_child_variable = y(counter * num_i + right_child)
            # Check if we are dealing with an OR or AND operation
            if dmf[k] == 0:  # OR operation
                cnf.append([-node_variable, left_child_variable, right_child_variable])
                cnf.append([node_variable, -left_child_variable])
                cnf.append([node_variable, -right_child_variable])
            else:  # AND operation
                cnf.append([node_variable, -left_child_variable, -right_child_variable])
                cnf.append([-node_variable, left_child_variable])
                cnf.append([-node_variable, right_child_variable])

        #Checking that values in roots are the same
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

