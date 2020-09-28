from charm.toolbox.policytree import *
import copy
from sympy import *


class LSSSUtil(object):
    __c = 0
    __policy_tree = None
    __initialVec = None
    __matrix = None
    __column = 0
    __row = 0

    def __init__(self):
        self.__c = 1
        self.__initialVec = [1]
        self.__matrix = {}
        pass

    def createPolicyTree(self, policy_string):
        assert type(policy_string) == str, "policy_string need a string"
        parser = PolicyParser()
        self.__policy_tree = parser.parse(policy_string)
        print(self.__policy_tree)

    def genLSSSMatrix(self, subtree, vec):
        if (subtree == None): return None
        node_type = subtree.getNodeType()
        if node_type == OpType.OR:
            left_vec = vec
            right_vec = copy.copy(vec)
            self.genLSSSMatrix(subtree.getLeft(), left_vec)
            self.genLSSSMatrix(subtree.getRight(), right_vec)
        if node_type == OpType.AND:
            base_vec = [0 for i in range(self.__c)]
            while len(vec) < self.__c:
                vec.append(0)
            left_vec = vec
            left_vec.append(1)
            right_vec = base_vec
            right_vec.append(-1)
            self.__c += 1
            self.genLSSSMatrix(subtree.getLeft(), left_vec)
            self.genLSSSMatrix(subtree.getRight(), right_vec)
        if node_type == OpType.ATTR:
            # print(subtree.getAttributeAndIndex())
            self.__matrix[subtree.getAttributeAndIndex()] = vec

    def getMatrix(self):
        self.genLSSSMatrix(self.__policy_tree, self.__initialVec)
        max_len = 0
        for index in self.__matrix:
            if len(self.__matrix[index]) > max_len:
                max_len = len(self.__matrix[index])
            self.__row += 1
        print(max_len)
        self.__column = max_len
        for index in self.__matrix:
            while len(self.__matrix[index]) < max_len:
                self.__matrix[index].append(0)
        return self.__matrix

    def getPolicyTree(self):
        return self.__policy_tree

    def getMatrixSize(self):
        return {"row": self.__row,
                "column": self.__column}

    def genSubMatrixSetList(self):
        row_index_list = []
        print(self.__row)
        for i in range(self.__row):
            row_index_list.append(i + 1)
        sub_matrix_list = [[]]
        for i in range(self.__row):
            for j in range(len(sub_matrix_list)):
                sub_matrix = sub_matrix_list[j] + [row_index_list[i]]
                # print(sub_matrix)
                if sub_matrix not in sub_matrix_list:
                    sub_matrix_list.append(sub_matrix)
        sub_matrix_list.sort(key=len)
        sub_matrix_set_list = []
        for val in sub_matrix_list:
            sub_matrix_set_list.append(set(val))
        self.__sub_matrix_set_list = sub_matrix_set_list
        self.__sub_matrix_list = sub_matrix_list

    def genAllOmega(self):
        all_omega = []
        self.genSubMatrixSetList()
        print("len:", len(self.__sub_matrix_list), self.__sub_matrix_list)
        i = 0
        while i < len(self.__sub_matrix_set_list):
            sub_matrix_set = copy.deepcopy(self.__sub_matrix_set_list[i])
            sub_matrix_info = self.exportMatrix(list(sub_matrix_set))
            omega_dict = self.computeOmegas(sub_matrix_info)
            if omega_dict is not None:
                all_omega.append(omega_dict)
                j = 0
                while j < len(self.__sub_matrix_set_list):
                    if self.__sub_matrix_set_list[j] >= sub_matrix_set:
                        # print("Delete")
                        # print(self.__sub_matrix_set_list[j])
                        self.__sub_matrix_set_list.pop(j)
                    else:
                        j += 1

            else:
                self.__sub_matrix_set_list.pop(i)
        return all_omega

    def getInitialVec(self):
        return self.__initialVec

    def exportMatrix(self, index_list):
        matrix_list = []
        new_2_old = {}
        row_len = len(index_list)
        index_list = [str(index_list[i]) for i in range(row_len)]
        for index in range(row_len):
            matrix_list.append(self.__matrix[index_list[index]])
            new_2_old[index] = index_list[index]
        # print((matrix_list, new_2_old))
        return (matrix_list, new_2_old)

    def computeOmegas(self, sub_matrix_info):
        # print("sub_matrix_info")
        # print(sub_matrix_info)
        if len(sub_matrix_info[0]) == 0:
            return None
        matrix_list = sub_matrix_info[0]
        row_len = len(matrix_list)
        column_len = len(matrix_list[0])
        omega_list = [0] * row_len
        for index in range(row_len):
            omega_list[index] = symbols("omega_" + str(index))
        matrix = Matrix(matrix_list).T
        A = matrix
        b_list = [0] * column_len
        b_list[0] = 1
        b = Matrix(b_list)
        system = A, b
        solveset = linsolve(system, omega_list)
        if len(solveset.args) == 0:
            return None
        # print(type(solveset))
        initial_omega_dict = {}
        for index in range(len(omega_list)):
            initial_omega_dict[omega_list[index]] = 1
        solve_tuple = solveset.args[0]
        return_list = []
        for index in range(len(solve_tuple)):
            expression = solve_tuple[index]
            result = int(expression.subs(initial_omega_dict))
            return_list.append(result)
        omega_dict = {}
        for i, omega in enumerate(return_list):
            old_index = sub_matrix_info[1][i]
            omega_dict[old_index] = omega
        print(omega_dict)
        return omega_dict


if __name__ == '__main__':
    lsssUtil = LSSSUtil()
    lsssUtil.createPolicyTree("1 and (((2 and 3) and 4) or ((5 or 6) or 7))")
    # lsssUtil.genLSSSMatrix(lsssUtil.getPolicyTree(), lsssUtil.getInitialVec())
    lsssUtil.getMatrix()
    # sub_matrix_info = lsssUtil.exportMatrix((1, 7))
    # print(lsssUtil.computeOmegas(sub_matrix_info))
    print(lsssUtil.genAllOmega())
