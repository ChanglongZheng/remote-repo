import os
from os import remove
from re import split

'''
加载数据集，得到用户-物品-评分，用户-用户-关系的三元组列表
针对不同的数据集格式可以再增加更多的加载方式
'''


class LoadDataset:
    def __int__(self):
        pass

    # 数据集格式：两列或三列的用户-物品-（评分）
    @staticmethod
    def load_user_item_inter(file):
        contain_rate = False  # 数据集是否包含评分数据
        with open(file) as f:
            number = len(split(' ',f.readline().strip()))
            if number > 2 :
                contain_rate = True
        inter_data = []
        with open(file) as f:
            for line in f:
                record = split(' ', line.strip())
                user_name = record[0]
                item_name = record[1]
                if contain_rate:
                    rate = float(record[2])
                    # 如果需要二值化可以再加
                else:
                    rate = 1
                inter_data.append([user_name, item_name, rate])
        return inter_data

    # 数据集格式：两列的
    @staticmethod
    def load_social_data(file):
        contain_trust = False  # 数据集是否包含评分数据
        with open(file) as f:
            number = len(split(' ',f.readline().strip()))
            if number > 2 :
                contain_trust = True
        social_data = []
        with open(file) as f:
            for line in f:
                record = split(' ', line.strip())
                user1_name = record[0]
                user2_name = record[1]
                if contain_trust:
                    trust = 1
                else:
                    trust = float(record[2])  # 人与人之间的关系也许可以量化
                social_data.append([user1_name, user2_name, trust])
        return social_data

    # 写入
    @staticmethod
    def write_file(dir, file, content, op='w'):
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(dir + file, op) as f:
            f.writelines(content)

    # 删除文件
    @staticmethod
    def delete_file(file_path):
        if os.path.exists(file_path):
            remove(file_path)









