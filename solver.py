import networkx as nx
import numpy as np
import operator as op
import copy
import os

###########################################
# Change this variable to the path to
# the folder containing all three input
# size category folders
###########################################
path_to_inputs = "./all_inputs"

###########################################
# Change this variable if you want
# your outputs to be put in a
# different folder
###########################################
path_to_outputs = "./outputs"

def parse_input(folder_name):
    '''
        Parses an input and returns the corresponding graph and parameters

        Inputs:
            folder_name - a string representing the path to the input folder

        Outputs:
            (graph, num_buses, size_bus, constraints)
            graph - the graph as a NetworkX object
            num_buses - an integer representing the number of buses you can allocate to
            size_buses - an integer representing the number of students that can fit on a bus
            constraints - a list where each element is a list vertices which represents a single rowdy group
    '''
    graph = nx.read_gml(folder_name + "/graph.gml")
    parameters = open(folder_name + "/parameters.txt")
    num_buses = int(parameters.readline())
    size_bus = int(parameters.readline())
    constraints = []

    for line in parameters:
        line = line[1: -2]
        curr_constraint = [num.replace("'", "") for num in line.split(", ")]
        constraints.append(curr_constraint)

    return graph, num_buses, size_bus, constraints

def solve(graph, k, s, sgs):
    edges = graph.edges()
    names = list(graph.nodes())

    N = len(names)
    G = np.zeros((N, N))
    studentInfo = {}
    id = 0

    for name in names:
        studentInfo[name] = [id, 0]
        id += 1

    for i in range(N):
        myguy = names[i]
        neighbors = graph.neighbors(myguy)
        for neighbor in neighbors:
            G[studentInfo.get(myguy)[0], studentInfo.get(neighbor)[0]] = 1

    buses = []
    for i in range(k):
        buses.append([])

    for i in range(N):
        a = 0
        for j in range(N):
            if G[i,j] == 1:
                a += 1
        name = names[i]
        studentInfo[name] = [studentInfo[name][0], a]

    dictDown = copy.deepcopy(studentInfo)

    SSI = sorted(studentInfo.items(), key=lambda e: e[1][1], reverse=True)
    SSI2 = sorted(dictDown.items(), key=lambda e: e[1][1])
    # print(names)
    i = 0
    while len(SSI) > 0:
        # print(i)
        # i += 1
        vipName = SSI[0][0] # label of the person with most friends so far
        # print(vipName)
        vipID = SSI[0][1][0] # ID number of this person. i.e. position in adjacency matrix
        if vipName not in studentInfo:
            SSI.pop(0)
            continue
        friends = list(graph.neighbors(vipName)) # list of freinds of VIP


        CreatingRowdyGroup = True
        listofBadBuses = []
        listofRowdyGroups = [4206969] * k
        while(CreatingRowdyGroup):
            bigSoFar = 0
            bigBoyBus = None
            index = None
            for busNumber in range(k):
                if len(buses[busNumber]) < s and (bigBoyBus == None or len(buses[bigBoyBus]) < len(buses[busNumber])):
                    if busNumber not in listofBadBuses:
                        bigBoyBus = busNumber
            if bigBoyBus is None:
                bigBoyBus = listofRowdyGroups.index(min(listofRowdyGroups))
                buses[bigBoyBus].append(vipName)
                break

            buses[bigBoyBus].append(vipName)
            groups_with_vip = []
            for group in sgs:
                if vipName in group:
                    groups_with_vip.append(group)
            issubset = False
            for group in groups_with_vip:
                if not issubset:
                    issubset = all([z in buses[bigBoyBus] for z in group])
                size = len(group)
                if issubset:
                    bigSoFar = size
            if issubset:
                # print("yeehaw")
                listofBadBuses.append(bigBoyBus)
                buses[bigBoyBus].remove(vipName)
                listofRowdyGroups[bigBoyBus] = bigSoFar
            else:
                CreatingRowdyGroup = False
        studentInfo.pop(vipName)
        SSI.pop(0)
        while len(buses[bigBoyBus]) < s and len(friends) > 0: # Placing friends in bus with VIP
            friend = friends.pop()
            if friend in studentInfo:
                buses[bigBoyBus].append(friend)
                groups_with_friend = []
                for group in sgs:
                    if friend in group:
                        groups_with_friend.append(group)
                for group in groups_with_friend:
                    issubset = all([z in buses[bigBoyBus] for z in group])
                    if issubset:
                        break
                if issubset:
                    buses[bigBoyBus].remove(friend)
                    # print("what")
                else:
                    studentInfo.pop(friend)

    # print("SSI 2 is " + str(len(SSI2)))
    for bus in buses:
        if len(bus) == 0:
            Removed = False
            while not Removed:
                # print("SSI 2 now is " + str(len(SSI2)))
                loser = SSI2.pop(0)
                for biz in buses:
                    if loser[0] in biz and len(biz) > 1:
                        # print("ENTERS")
                        biz.remove(loser[0])
                        Removed = True
                # print(loser[0])
            bus.append(loser[0])

    for bus in buses:
        if len(bus) == 0:
            return 1/0

    print(buses)
    # checkforDuplicates(buses)
    # checkAllPlaced(names, buses)
    return buses

def checkforDuplicates(nested_array):
    for array in nested_array:
        for item in array:
            #print("checking " + item)
            i = 0
            for checking_array in nested_array:
                if item in checking_array:
                    i += 1
                    if i > 1:
                        #print("DUPLICATE")
                        print(item)

def checkAllPlaced(nodes,nested_array):
    for node in nodes:
        found = False
        for array in nested_array:
            if node in array:
                found = True
        if not found:
            print(node + "not found")

def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        The student should modify `solve` to return their solution and modify
        the portion which writes it to a file to make sure their output is
        formatted correctly.
    '''
    size_categories = ["small", "medium", "large"]
    if not os.path.isdir(path_to_outputs):
        os.mkdir(path_to_outputs)

    for size in size_categories:
        category_path = path_to_inputs + "/" + size
        output_category_path = path_to_outputs + "/" + size
        category_dir = os.fsencode(category_path)

        if not os.path.isdir(output_category_path):
            os.mkdir(output_category_path)

        for input_folder in os.listdir(category_dir):
            input_name = os.fsdecode(input_folder)
            graph, num_buses, size_bus, constraints = parse_input(category_path + "/" + input_name)
            solution = solve(graph, num_buses, size_bus, constraints)
            output_file = open(output_category_path + "/" + input_name + ".out", "w")

            for bus in solution:
                output_file.write(str(bus) + "\n")

            output_file.close()

if __name__ == '__main__':
    main()
