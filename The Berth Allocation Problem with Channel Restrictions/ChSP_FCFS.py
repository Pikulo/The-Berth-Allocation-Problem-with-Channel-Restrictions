# 论文航道限制的泊位分配：P719求均匀分布
from scipy.stats import uniform
import random
import pandas as pd
from icecream import ic
import unittest
import os
import sys
import time

R = random.uniform(0,1) # 没有这个也没影响
fun_a = lambda R: 2000*(2*R+1.5)/60
mean=uniform.expect(func=fun_a,loc=0,scale=1) # 平均装卸时间
# print(mean/5) # 83.33333333333333


# random.seed(0)

# P719生成船舶到达时间以及在锚地就绪时间
def generated(num_ship,num_berth):
    A_j = [random.uniform(1, (7000*num_ship)/(60*num_berth)) for _ in range(num_ship)] # 产生10艘船的到达时间
    # print(A_j)
    F = 0.5
    S_i = 16.3 + min(A_j) + F*(max(A_j) - min(A_j))
    r_j = [max(A_j[i]-S_i,0) for i in range(num_ship)]
    return A_j,S_i,r_j

A_j,S_i,r_j = generated(10,5)
# print(A_j)
# print(S_i)
# print(r_j)




'''对于10艘船的情况'''
# 参数规定
ship_num = 10
chsegs = 2
ship_turn = chsegs*2+1
delta_1 = 0.25
delta_2 = 0
delta_3 = 0.5
M = 10000
s_np = [i for i in range(1, 2*(chsegs//2+chsegs%2), 2)] # 不允许对立船舶通过的航段的集合
berths_num = 5 # 泊位数量
print('------------------------')
print('s_np',s_np)


# 定义一个空字典来存储列表
T_dict = {}
# 存放航段运输集合
for i in range(1, ship_num+1):
    # 定义列表并命名
    list_name = "T_" + str(i)
    T_dict[list_name] = []
    for j in range(1,ship_turn+1):
        num = (i - 1) * ship_turn + j
        T_dict[list_name].append(num)
print('------------------------')
print('T_dict',T_dict)

# 航段运输集合T
T = []
for i in T_dict:
    T+=T_dict[i]
print('T',T)
# 读取excel表数据
df = pd.read_excel(r'D:\APPS\Vscode\Vscode_files\Vscode\ZJU_STUDY\Papers_Codes\The Berth Allocation Problem with Channel Restrictions\dataset\ts-cb-t6.xlsx', sheet_name='T6R1',engine='openpyxl') # 不同工作表对应sheet_name=""不一样
# print(df)
problem_num = 0 #用于后期循环迭代，0表示第problem1，1表示第problem2
df_p = df.iloc[problem_num,1:len(T)+1] #0表示第problem1，提取problem1的所有p
p_a = {} # 每个航段运输时间(修改序号版)
p_a_dict = df_p.to_dict() # 每个航段运输时间
p_a_values = list(p_a_dict.values())
# ic(p_a_values)
for i in range(len(p_a_values)):
    p_a['p'+str(i+1)]=p_a_values[i]
# ic(p_a)

# 锚地就绪时间
df_r = df.iloc[problem_num,len(T)+1:len(T)+ship_num+1]
r_j = df_r.to_dict() # 锚地就绪时间
ic(r_j)

# 每艘船的对应泊位/不确定泊位的情况需要更改代码
df_berth = df.iloc[problem_num,len(T)+ship_num+1:len(T)+ship_num*2+1]
berths_al = [int(i) for i in df_berth.values] # 需要确定的量
print(berths_al)

# 定义in/berth/out,简称T_ibo
T_ibo = {}
k = 1
for i in range(1, ship_turn+1):
    if i <= ship_turn//2:
        list_name = "T_in_" + str(i)
        T_ibo[list_name] = []
        for j in T_dict:
            T_ibo[list_name].append(T_dict.get(j)[i-1])
    elif i == (ship_turn//2)+1:
        list_name = "T_berth_" + str(i)
        T_ibo[list_name] = []
        for j in T_dict:
            T_ibo[list_name].append(T_dict.get(j)[i-1])
    else:
        list_name = "T_out_" + str((ship_turn//2)+1-k)
        k+=1
        T_ibo[list_name] = []
        for j in T_dict:
            T_ibo[list_name].append(T_dict.get(j)[i-1])
print('------------------------')
print('T_ibo',T_ibo)
# 定义Q_F
Q_F = []
for key in T_ibo:
    if key != "T_berth_" + str((ship_turn//2)+1):
        # print(T_ibo[key])
        for i in range(ship_num-1):
            for j in range(i+1,ship_num):
                Q_F.append((T_ibo[key][i],T_ibo[key][j]))
print('------------------------')
print('Q_F',Q_F)

# 定义Q_P
def judge(a,b): # 判断a和b是一个船舶运动中
    for i in T_dict.values():
        if set(sorted(list((a,b)))).issubset(set(i)):
            return True
    return False
Q_P = []
for i in s_np:
    T_in = T_ibo.get("T_in_" + str(i)) # 存放限制通航的“进港”运输航段
    T_out = T_ibo.get("T_out_" + str(i)) # 存放限制通航的“出港”运输航段
    print('T_in',T_in)
    print('T_out',T_out)
    for m in T_in:
        for n in T_out:
            if judge(m,n): # 属于同一船舶运动j[a]=j[b] 
                continue
            else:
                if m < n:
                    Q_P.append((m,n))
                else:
                  Q_P.append((n,m))
Q_P = sorted(Q_P, key=lambda x: x[0]) # 排序处理
print('------------------------')
print('Q_P',Q_P)

# 根据航段运输序号返回船舶序号
def return_ship_num(seg_num):
    temp = [i for i in T_dict.values()]
    # print(temp)
    for i in range(len(temp)):
        if seg_num in temp[i]:
            return i # 如果船舶序号为1，返回的是0

# Q_B
Q_B = []
def judge_berth(a,b):
    if berths_al[return_ship_num(a)] == berths_al[return_ship_num(b)]:
        return True
T_berth = T_ibo.get("T_berth_" + str((ship_turn//2)+1))
print('------------------------')
print('T_berth',T_berth)
for i in range(len(T_berth)-1):
    for j in range(i+1,len(T_berth)):
        if judge_berth(T_berth[i],T_berth[j]):
            Q_B.append((T_berth[i],T_berth[j]))
print('------------------------')
print('Q_B',Q_B)

# Q_E
Q_E = []
print('------------------------')
# print(Q_F)
# print(Q_B)
print(Q_F+Q_B)
Q_F_B = Q_F+Q_B
for i in Q_F_B.copy():
    if (i[0]+1,i[1]+1) in Q_F_B and return_ship_num(i[0]) == return_ship_num(i[0]+1) and return_ship_num(i[1]) == return_ship_num(i[1]+1):
        Q_E.append(i)
print('------------------------')
print(Q_E)
# ic(Q_E)
# Q_X = Q_F+Q_P+Q_B
Q_X = Q_F+Q_P+Q_B



T_wait = T_ibo['T_in_1']+[i+1 for i in T_berth] # w_a

T_in_1 = T_ibo['T_in_1']


T_nw = []
for i in T_dict:
    for j in T_dict[i]:
        if j not in T_berth and j!=T_dict[i][-1]:
            T_nw.append(j)


# 基于FCFS的求解
'''修改船舶数量时,要修改sigma'''
sigma = [0,1,3,7,9,6,5,4,8,2] # 存放σ,按照船舶到达顺序，与船舶数量有关
Phi = [] # ships scheduled at the current point


def merge_intervals(intervals):
    intervals.sort()
    merged = []
    for interval in intervals:
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])
    return merged

t_a = {}
for i in range(5*len(sigma)):
    t_a['t'+str(i+1)] = 0
print(t_a)

start_time = time.time()

for i in range(len(sigma)):
    W = [] # 禁止窗口
    j = sigma[i]
    if len(Phi) == 0:
        alpha = T_dict['T_'+str(j+1)][0]
        # beta = T_dict['T_'+str(j+1)][chsegs+2-1]
        t_a['t'+str(alpha)] = r_j['r'+str(j)]
        for transit in range(alpha+1,T_dict['T_'+str(j+1)][-1]+1):
            t_a['t'+str(transit)] = t_a['t'+str(transit-1)] + p_a['p'+str(transit-1)]
    else:

        # 船舶j的inbound和已安排的outbound的禁止窗口
        W.append([float('-inf'),r_j['r'+str(j)]])
        i_b = s_np
        alpha = T_dict['T_'+str(j+1)][0] # 船舶j的第一个进港运输段
        beta = T_dict['T_'+str(j+1)][chsegs+2-1]
        print('alpha',alpha)
        for ship in Phi:
            # 找出a和b,升序排列
            inbound_b = []
            outbound_a = []
            T_j_b = set(T_dict['T_'+str(j+1)]) # 船j的分段运输集合
            print('T_j_b',T_j_b)
            T_j_a = set(T_dict['T_'+str(ship+1)]) # 已经规划好的一艘船舶的分段运输集合
            print('T_j_a',T_j_a)
            for seg in i_b:
                # 将两个列表转换为集合
                T_in_i  = set(T_ibo['T_in_'+str(seg)])
                T_out_i = set(T_ibo['T_out_'+str(seg)])
                print('T_in_i',T_in_i)
                print('T_out_i',T_out_i)
                # 计算交集
                intersection = T_j_b.intersection(T_in_i)
                # 将交集转换为列表
                inbound_b.append(list(intersection)[0])
                intersection = T_j_a.intersection(T_out_i)
                outbound_a.append(list(intersection)[0])
            print('inbound_b,outbound_a',inbound_b,outbound_a)
            outbound_a = outbound_a[::-1] # 把一个列表逆序，为了3航段的计算正确性
            for cla_time in range(len(inbound_b)):
                sum_1 = 0.0 # 左边部分的求和部分
                sum_2 = 0.0 # 右边部分的求和部分
                if inbound_b[cla_time]>=alpha:
                    sum_1+=sum([p_a['p'+str(temp)] for temp in range(alpha,inbound_b[cla_time]+1)])
                    sum_2+=sum([p_a['p'+str(temp)] for temp in range(alpha,inbound_b[cla_time])])
                W.append([t_a['t'+str(outbound_a[cla_time])]-delta_2-sum_1,t_a['t'+str(outbound_a[cla_time])]+p_a['p'+str(outbound_a[cla_time])]+delta_2-sum_2])
                W = merge_intervals(W)
            print(W)

            # 船舶j的inbound和已安排的inbound的禁止窗口inbound_a
            inbound_b = T_dict['T_'+str(j+1)][0:(ship_turn//2)]# 船j的分段运输集合
            print('inbound_b',inbound_b)
            inbound_a = T_dict['T_'+str(ship+1)][0:(ship_turn//2)] # 已经规划好的一艘船舶的分段运输集合
            print('inbound_a',inbound_a)
            for cla_time in range(len(inbound_b)):
                sum_1 = 0.0 # 左边部分的求和部分
                sum_2 = 0.0 # 右边部分的求和部分
                if inbound_b[cla_time]>=alpha:
                    sum_1+=sum([p_a['p'+str(temp)] for temp in range(alpha,inbound_b[cla_time])])
                    sum_2+=sum([p_a['p'+str(temp)] for temp in range(alpha,inbound_b[cla_time])])
                W.append([t_a['t'+str(inbound_a[cla_time])]-delta_1-sum_1,t_a['t'+str(inbound_a[cla_time])]+delta_1-sum_2])
                W = merge_intervals(W)
            print(W)

            # 当两艘船的泊位一致时,船舶j的靠泊和已安排的靠泊的禁止窗口berth_a
            # if T_dict['T_'+str(j+1)][(ship_turn//2)] == T_dict['T_'+str(ship+1)][(ship_turn//2)]:
            if berths_al[j] == berths_al[ship]:
                berth_b = [T_dict['T_'+str(j+1)][(ship_turn//2)]]# 船j的分段运输集合
                print('berth_b',berth_b)
                berth_a = [T_dict['T_'+str(ship+1)][(ship_turn//2)]] # 已经规划好的一艘船舶的分段运输集合
                print('berth_a',berth_a)
                for cla_time in range(len(berth_b)):
                    sum_1 = 0.0 # 左边部分的求和部分
                    sum_2 = 0.0 # 右边部分的求和部分
                    if berth_b[cla_time]>=alpha:
                        sum_1+=sum([p_a['p'+str(temp)] for temp in range(alpha,berth_b[cla_time]+1)])
                        sum_2+=sum([p_a['p'+str(temp)] for temp in range(alpha,berth_b[cla_time])])
                    W.append([t_a['t'+str(berth_a[cla_time])]-delta_3-sum_1,t_a['t'+str(berth_a[cla_time]+1)]+delta_3-sum_2])
                    W = merge_intervals(W)
                print(W)
        # 进行t_alpha的取值
        my_list = W
        min_val = min([x[1] if x[0] == -float('inf') else x[0] for x in my_list]) # 禁止窗口中获得的最小值
        print('min_val',min_val)
        t_a['t'+str(alpha)] = min_val
        for transit in range(alpha+1,alpha+(ship_turn//2)+1):
            t_a['t'+str(transit)] = t_a['t'+str(transit-1)] + p_a['p'+str(transit-1)]
        
        # 进行船舶j的outbound和已经安排的inbound
        W = []
        W.append([float('-inf'),t_a['t'+str(beta-1)]+p_a['p'+str(beta-1)]])
        for ship in Phi:
            # 找出a和b,升序排列
            outbound_b = []
            inbound_a = []
            T_j_b = set(T_dict['T_'+str(j+1)]) # 船j的分段运输集合
            print('T_j_b',T_j_b)
            T_j_a = set(T_dict['T_'+str(ship+1)]) # 已经规划好的一艘船舶的分段运输集合
            print('T_j_a',T_j_a)
            for seg in i_b:
                # 将两个列表转换为集合
                T_in_i  = set(T_ibo['T_in_'+str(seg)])
                T_out_i = set(T_ibo['T_out_'+str(seg)])
                print('T_in_i',T_in_i)
                print('T_out_i',T_out_i)
                # 计算交集
                intersection = T_j_b.intersection(T_out_i)
                # 将交集转换为列表
                outbound_b.append(list(intersection)[0])
                intersection = T_j_a.intersection(T_in_i)
                inbound_a.append(list(intersection)[0])
            print('outbound_b,inbound_a',outbound_b,inbound_a)
            inbound_a = inbound_a[::-1] # 把一个列表逆序，为了3航段的计算正确性
            for cla_time in range(len(outbound_b)):
                sum_1 = 0.0 # 左边部分的求和部分
                sum_2 = 0.0 # 右边部分的求和部分
                if outbound_b[cla_time]>=beta:
                    sum_1+=sum([p_a['p'+str(temp)] for temp in range(beta,outbound_b[cla_time]+1)])
                    sum_2+=sum([p_a['p'+str(temp)] for temp in range(beta,outbound_b[cla_time])])
                W.append([t_a['t'+str(inbound_a[cla_time])]-delta_2-sum_1,t_a['t'+str(inbound_a[cla_time])]+p_a['p'+str(inbound_a[cla_time])]+delta_2-sum_2])
                W = merge_intervals(W)
            print(W)

            # 船舶j的outbound和已安排的outbound的禁止窗口
            outbound_b = T_dict['T_'+str(j+1)][(ship_turn//2)+1:ship_turn]# 船j的分段运输集合
            print('outbound_b',outbound_b)
            outbound_a = T_dict['T_'+str(ship+1)][(ship_turn//2)+1:ship_turn] # 已经规划好的一艘船舶的分段运输集合
            print('outbound_a',outbound_a)
            for cla_time in range(len(outbound_b)):
                sum_1 = 0.0 # 左边部分的求和部分
                sum_2 = 0.0 # 右边部分的求和部分
                if outbound_b[cla_time]>=beta:
                    sum_1+=sum([p_a['p'+str(temp)] for temp in range(beta,outbound_b[cla_time])])
                    sum_2+=sum([p_a['p'+str(temp)] for temp in range(beta,outbound_b[cla_time])])
                W.append([t_a['t'+str(outbound_a[cla_time])]-delta_1-sum_1,t_a['t'+str(outbound_a[cla_time])]+delta_1-sum_2])
                W = merge_intervals(W)
            print(W)

        # 进行t_beta的取值
        my_list = W
        min_val = min([x[1] if x[0] == -float('inf') else x[0] for x in my_list]) # 禁止窗口中获得的最小值
        print('min_val',min_val)
        t_a['t'+str(beta)] = min_val
        for transit in range(beta+1,beta+(ship_turn//2)):
            t_a['t'+str(transit)] = t_a['t'+str(transit-1)] + p_a['p'+str(transit-1)]
        
    Phi.append(j) # 遍历完了一艘船j，将其加入Phi
end_time = time.time()
run_time = end_time - start_time
print('t_a',t_a)
print("FCFS运行时间为：", run_time)
# 求总等待时间
sum_z = 0.0
# 锚地等待时间
for i in T_ibo['T_in_1']:
    sum_z+=(t_a['t'+str(i)]-r_j['r'+str(return_ship_num(i))])
# 泊位等待时间
for i in T_berth:
    sum_z+=(t_a['t'+str(i+1)]-t_a['t'+str(i)]-p_a['p'+str(i)])
print('FCFS得到的problem{0}的结果:'.format(problem_num+1),sum_z)


'''p_a:
        {'p1': 8.33333, 'p2': 8.33333, 'p3': 58.9251, 'p4': 8.33333, 'p5': 8.33333, 'p6': 8.33333, 'p7': 8.33333, 'p8': 80.081, 'p9': 8.33333, 'p10': 8.33333, 'p11': 8.33333, 'p12': 8.33333, 'p13': 73.3932, 'p14': 8.33333, 'p15': 8.33333, 'p16': 8.33333, 'p17': 8.33333, 'p18': 81.3835, 'p19': 8.33333, 'p20': 8.33333, 'p21': 8.33333, 'p22': 8.33333, 'p23': 87.9898, 'p24': 8.33333, 'p25': 8.33333, 'p26': 8.33333, 'p27': 8.33333, 'p28': 55.9635, 'p29': 8.33333, 'p30': 8.33333, 'p31': 8.33333, 'p32': 8.33333, 'p33': 102.643, 'p34': 8.33333, 'p35': 8.33333, 'p36': 8.33333, 'p37': 8.33333, 'p38': 77.9112, 'p39': 8.33333, 'p40': 8.33333, 'p41': 8.33333, 'p42': 8.33333, 'p43': 69.4576, 'p44': 8.33333, 'p45': 8.33333, 'p46': 8.33333, 'p47': 8.33333, 'p48': 81.6396, 'p49': 8.33333, 'p50': 8.33333}'''