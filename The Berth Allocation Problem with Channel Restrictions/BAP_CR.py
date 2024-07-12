# 论文航道限制的泊位分配：P719求均匀分布
from docplex.mp.model import Model
from scipy.stats import uniform
import random
import pandas as pd
from icecream import ic
import unittest
import os
import sys

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


def judge(a,b): # 判断a和b是一个船舶运动中
    for i in T_dict.values():
        if set(sorted(list((a,b)))).issubset(set(i)):
            return True
    return False

# 根据航段运输序号返回船舶序号
def return_ship_num(seg_num):
    temp = [i for i in T_dict.values()]
    # print(temp)
    for i in range(len(temp)):
        if seg_num in temp[i]:
            return i # 如果船舶序号为1，返回的是0

def judge_berth(a,b):
    if berths_al[return_ship_num(a)] == berths_al[return_ship_num(b)]:
        return True

def mip_cal(berth_num,ship_num,chsegs,problem_num,sheet_name,fliename):
    # cplex模型建立
    '''对于10艘船的情况'''
    # 参数规定
    ship_num = ship_num
    chsegs = chsegs
    ship_turn = chsegs*2+1
    delta_1 = 0.25
    delta_2 = 0
    delta_3 = 0.5
    M = 10000
    s_np = [i for i in range(1, 2*(chsegs//2+chsegs%2), 2)] # 不允许对立船舶通过的航段的集合
    B = [i for i in range(berth_num)]
    print('------------------------')
    print('s_np',s_np)


    # 定义一个空字典来存储列表
    global T_dict
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

    # 读取excel表数据
    df = pd.read_excel(fliename, sheet_name=sheet_name,engine='openpyxl') # 不同工作表对应sheet_name=""不一样
    # print(df)
    problem_num = problem_num #用于后期循环迭代，0表示第problem1，1表示第problem2
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
    df_berth = df.iloc[problem_num,len(T)+ship_num+1:len(T)+ship_num+ship_num*berth_num+1]
    print('df_berth',df_berth)
    global berths_al
    berths_al = [i for i in df_berth.values] # 需要确定的量
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

    T_berth = T_ibo.get("T_berth_" + str((ship_turn//2)+1))

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



    # Q_B
    Q_B = []
    for i in T_berth:
        for j in T_berth:
            if i<j:
                Q_B.append((i,j))
    print('Q_B',Q_B)


    # Q_E
    Q_E = []
    print('------------------------')
    # print(Q_F)
    # print(Q_B)
    print(Q_F)
    Q_F_B = Q_F
    for i in Q_F_B.copy():
        if (i[0]+1,i[1]+1) in Q_F_B and return_ship_num(i[0]) == return_ship_num(i[0]+1) and return_ship_num(i[1]) == return_ship_num(i[1]+1):
            Q_E.append(i)
    print('------------------------')
    print(Q_E)
    # ic(Q_E)
    # Q_X = Q_F+Q_P+Q_B
    Q_X = Q_F+Q_P+Q_B

    # 读取泊位处理时间
    p_a_k = {}
    index_berth = 0
    for i in T_berth:
        for j in B:
            p_a_k['p'+str(i)+str((j))] = berths_al[index_berth]
            index_berth+=1

    '''建模'''
    model = Model(name="Vessel Allocation")
    # 生成决策变量X_ab/t_a/w_a
    X_ab = model.binary_var_dict(Q_X, name='X') # X_ab
    # ic(X_ab)


    # ic(T)
    t_a = model.continuous_var_dict(T, lb=0, name='T') # t_a
    # ic(t_a)

    T_wait = T_ibo['T_in_1']+[i+1 for i in T_berth] # w_a
    w_a = model.continuous_var_dict(T_wait, lb=0, name='w')
    # ic(w_a)

    # 生成Z_a_k
    
    Z_a_k = []
    for i in T_berth:
        for j in B:
            Z_a_k.append((i,j))
    Z_ak = model.binary_var_dict(Z_a_k, name='Z')


    # 目标函数
    # for i in T_wait:
    #     ic(w_a[i])
    model.minimize(sum(w_a[i] for i in T_wait))

    # 约束条件(2)-(12)

    # 约束(2)
    T_in_1 = T_ibo['T_in_1']
    # ic(T_in_1)
    r_index = 0
    for i in T_in_1:
        # ic(t_a[i])
        k = 'r'+str(r_index)
        model.add_constraint(t_a[i] == r_j[k] + w_a[i])
        ic(t_a[i],r_j[k],w_a[i])
        r_index+=1

    # 约束(3)
    T_nw = []
    for i in T_dict:
        for j in T_dict[i]:
            if j not in T_berth and j!=T_dict[i][-1]:
                T_nw.append(j)
    # ic(T_nw)
    for i in T_nw:
        model.add_constraint(t_a[i+1] == t_a[i] + p_a['p'+str(i)])
        # ic(i)
        # ic(t_a[i+1], t_a[i] , p_a['p'+str(i)])

    
    # 约束(5)
    # ic(X_ab)
    for i in Q_F:
        model.add_constraint(t_a[i[0]] + delta_1 <= t_a[i[1]] + M*(1-X_ab[i]))

    # 约束(6)
    for i in Q_F:
        model.add_constraint(t_a[i[1]] + delta_1 <= t_a[i[0]] + M*X_ab[i])

    # 约束(7)
    for i in Q_P:
        model.add_constraint(t_a[i[0]] + p_a['p'+str(i[0])] + delta_2 <= t_a[i[1]] + M*(1-X_ab[i]))

    # 约束(8)
    for i in Q_P:
        model.add_constraint(t_a[i[1]] + p_a['p'+str(i[1])] + delta_2 <= t_a[i[0]] + M*X_ab[i])

    # 约束(11)
    for i in Q_E:
        model.add_constraint(X_ab[(i[0]+1,i[1]+1)] == X_ab[i])


    # 约束(12)
    # 方程（12）使得如果可能的话，可以使用固定的优先约束来减少混合整数规划（MIP）求解的时间。
    Q_prec = [] # Q_prec is in Q_X
    # 暂时先不要这个约束，也不影响，有的话能加快求解速度

    # 约束(22)
    for i in T_berth:
        model.add_constraint(sum([Z_ak[(i,j)] for j in B])==1)

    # 约束(23)
    # ic(T_berth) #T_berth: [3, 8, 13, 18, 23, 28, 33, 38, 43, 48]
    for i in T_berth:
        model.add_constraint(t_a[i+1] >= t_a[i] + sum(p_a_k['p'+str(i)+str(j)]*Z_ak[(i,j)] for j in B))
    
    # 约束(24)
    for i in T_berth:
        model.add_constraint(t_a[i+1] == t_a[i] + min([p_a_k['p'+str(i)+str(j)] for j in B])+w_a[i+1])

    # 约束(25)
    for i in Q_B:
        for j in B:
            model.add_constraint(t_a[i[0]+1] + delta_3 <= t_a[i[1]] + M*(3-X_ab[i]-Z_ak[(i[0],j)]-Z_ak[(i[1],j)]))

    # 约束(26)
    for i in Q_B:
        for j in B:
            model.add_constraint(t_a[i[1]+1] + delta_3 <= t_a[i[0]] + M*(2+X_ab[i]-Z_ak[(i[0],j)]-Z_ak[(i[1],j)]))


    # 求解
    # model.print_information()
    # sol = model.solve()
    # model.print_solution()
    # print(sol.solve_details)
    # ic(model.objective_value)


    # 创建指定文件夹保存结果
    # filename = r"D:\APPS\Vscode\Vscode_files\Vscode\ZJU_STUDY\Papers_Codes\The Berth Allocation Problem with Channel Restrictions\Output"
    # filename = filename+'\T6R{0}X'.format(str(1)) # 根据excel表中dataset数量来决定,1表示T6R1X
    # directory_output = filename
    # if not os.path.exists(directory_output):
    #     os.makedirs(directory_output)
    # filename = directory_output+'\problem{0}.txt'.format(str(problem_num+1))

    # 保存文件
    # sys.stdout = open(filename, 'w')
    # 终端输出一些内容
    print('problem_num:',problem_num+1)
    model.print_information()
    model.parameters.timelimit=120 # 时间限制为2分钟
    sol = model.solve()
    model.print_solution()
    print(sol.solve_details)
    # 恢复标准输出（stdout）
    # sys.stdout = sys.__stdout__
    # model.print_solution()
    ic(model.objective_value)
    return model.objective_value