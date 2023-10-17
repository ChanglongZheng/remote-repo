import numpy as np
import scipy.sparse as sp
from collections import defaultdict

'''
从分割好的数据集中准备好数据的矩阵形式存储
参考了https://github.com/Coder-Yu/QRec的写法，感觉他的比较明晰，自己太菜了，写出来也是shit，谢谢Coder-Yu！
根据不同的论文和数据集，这代码也可以随时改，重要的是学习一种代码风格，学习人家怎么写的
'''

class UIInteraction(object):
    def __init__(self, train_data, test_data):
        # 训练集和测试集
        self.train_data = train_data[:]
        self.test_data = test_data[:]
        # 矩阵是高度稀疏的，需要用稀疏矩阵，将数据集中的用户转为id方便搭建矩阵。
        self.user2id = {}  # key为数据集中的user_name，value为编码后的user_id
        self.item2id = {}
        self.id2user = {}  # key为编码后的user_id，value为数据集中的user_name
        self.id2item = {}
        # 确定每个用户交互的所有物品，或，每个物品交互过的用户
        self.trainSetUi = defaultdict(dict)
        self.trainSetIu = defaultdict(dict)
        self.testSetUi = defaultdict(dict)
        self.testSetIu = defaultdict(dict)
        # 训练集中用户和物品数量
        self.user_num_train = len(self.trainSetUi)
        self.item_num_train = len(self.trainSetIu)

    def generate_set(self):
        for entry in self.train_data:
            user_name, item_name, rate = entry
            if user_name not in self.user2id:
                self.user2id[user_name] = len(self.user2id)
                self.id2user[self.user2id[user_name]] = user_name
            if item_name not in self.item2id:
                self.item2id[item_name] = len(self.item2id)
                self.id2item[self.item2id[item_name]] = item_name
            self.trainSetUi[user_name][item_name] = rate
            self.trainSetIu[item_name][user_name] = rate
        for entry in self.test_data:
            user_name, item_name, rate = entry
            self.testSetUi[user_name][item_name] = rate
            self.testSetIu[item_name][user_name] = rate

    # 交互矩阵
    def create_interaction_matrix(self):
        row_coordinate, col_coordinate, values = [], [], []
        for entry in self.train_data:
            row_coordinate += [self.user2id[entry[0]]]
            col_coordinate += [self.item2id[entry[1]]]
            # 这个值如果一直都是1的话，可以处理的更简单一些
            values += [float(entry[2])]
        interaction_mat = sp.csr_matrix((values, (row_coordinate, col_coordinate)),
                                        shape=(self.user_num_train, self.item_num_train),
                                        dtype=np.float32)
        return interaction_mat

    # 邻接矩阵
    def create_adjacent_matrix(self, self_connection=False):
        n_nodes = self.user_num_train + self.item_num_train
        # 按他的写吧，避免重复
        row_ids = [self.user2id[pair[0]] for pair in self.train_data]
        col_ids = [self.item2id[pair[1]] for pair in self.train_data]
        # 这里同样，如果二值化了，并不是1-5的数据，可以直接全部写为1，更简单一些
        rate = [pair[2] for pair in self.train_data]
        user_np = np.array(row_ids)
        item_np = np.array(col_ids)
        rate_np = np.array(rate, dtype=np.float32)
        interaction_shifting = sp.csr_matrix((rate_np, (user_np,item_np + self.user_num_train)),
                                             shape=(n_nodes, n_nodes), dtype=np.float32)
        adj_mat = interaction_shifting + interaction_shifting.T
        if self_connection:
            adj_mat += sp.eye(n_nodes)  # 加上一个单位矩阵
        return adj_mat

    # 归一化的邻接矩阵，A^ = D^-1/2 * A * D^-1/2，这个归一化是可以用矩阵去算一下的
    def create_norm_adjacent_matrix(self, adj_mat):
        shape = adj_mat.get_shape()
        # 用一行的和来做归一化
        # 涉及到axis时，应该这样理解，axis的要collapse，即要塌缩的axis。axis为0时，塌缩行，axis为1时，塌缩列
        # 以这里的axis为1为例，塌缩所有的列，得到的便是每行的求和值
        row_sum = np.array(adj_mat.sum(axis=1))
        # 考虑方阵和不是方阵的情况
        # 得到度矩阵D和D^ -1/2
        if shape[0] == shape[1]:
            d_inv = np.power(row_sum, -0.5).flatten()  # 拉平
            d_inv[np.isinf(d_inv)] = 0.  # 处理无穷值
            d_mat_inv = sp.diags(diagonals=d_inv)  # 由给定值构建对角矩阵
            norm_adj_tmp = d_mat_inv.dot(adj_mat)
            norm_adj_mat = norm_adj_tmp.dot(d_mat_inv)
        # 如果不是方阵，（好像没见过诶），用每行的和来归一化。这个画下矩阵，很简单的
        else:
            d_inv = np.power(row_sum, -1).flatten()
            d_inv[np.isinf(d_inv)] = 0.
            d_mat_inv = sp.diags(diagonals=d_inv)
            norm_adj_mat = d_mat_inv.dot(d_inv)
        return norm_adj_mat


# just a test









