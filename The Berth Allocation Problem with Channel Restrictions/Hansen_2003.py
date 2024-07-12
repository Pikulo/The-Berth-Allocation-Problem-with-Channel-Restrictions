# 论文航道限制的泊位分配：P719求均匀分布
from docplex.mp.model import Model
from scipy.stats import uniform
import random
import pandas as pd
from icecream import ic
import unittest
import os
import sys

'''计算论文表12中的Zimai的BAP,用的是Hansen的方法'''

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
    # ic(r_j)

    # 每艘船的对应泊位/不确定泊位的情况需要更改代码
    df_berth = df.iloc[problem_num,len(T)+ship_num+1:len(T)+ship_num+ship_num*berth_num+1]
    # print('df_berth',df_berth)
    global berths_al
    berths_al = [i for i in df_berth.values] # 需要确定的量
    # print(berths_al)
    
    # 读取泊位处理时间C_ij
    C_i_j = {}
    index_berth = 0
    for j in range(1,ship_num+1):
        for i in B:
            C_i_j['C'+str(i)+str(j)] = berths_al[index_berth]
            index_berth+=1
    # print(C_i_j)
    '''{'C01': 58.9251, 'C11': 59.0938, 'C02': 51.4016, 'C12': 73.3932, 'C03': 81.3835, 'C13': 54.9617, 'C04': 92.3487, 'C14': 55.9635, 'C05': 102.643, 'C15': 64.7756, 'C06': 66.6519, 'C16': 69.4576}'''
    
    # O:orders
    O = [i for i in range(1,ship_num+1)]
    V = [i for i in range(1,ship_num+1)]

    '''建模'''
    model = Model(name="Hansen Vessel Allocation")
    # 生成决策变量x_ijk和连续变量y_ijk
    x_i_j_k = []
    z_i_k = []
    s_i_k = [] 
    for i in B:
        for j in range(1,ship_num+1):
            z_i_k.append((i,j))
            s_i_k.append((i,j))
            for k in range(1,ship_num+1):
                x_i_j_k.append((i,j,k))
    x_ijk = model.binary_var_dict(x_i_j_k, name='x')
    z_ik = model.binary_var_dict(z_i_k, name='z')
    s_ik = model.continuous_var_dict(s_i_k, lb=0,name='s') #the starting time for handling the kth ship at berth i

    # 目标函数
    a = [(C_i_j['C'+str(i)+str(j)] - min(C_i_j['C'+str(n)+str(j)] for n in B) - r_j['r'+str(j-1)])*x_ijk[(i,j,k)] for i in B for j in V for k in O]
    b = [s_ik[(i,k)] for i in B for k in O]
    model.minimize(sum(a)+sum(b))

    # 约束条件(10)-(12)

    # 约束(38)
    for j in V:
        model.add_constraint(sum([x_ijk[(i,j,k)] for i in B for k in O]) == 1)
    
    # 约束(39)
    for i in B:
        for k in O:
            model.add_constraint(sum([x_ijk[(i,j,k)] for j in V]) + z_ik[(i,k)] == 1)
    
    # 约束(40)
    for i in B:
        for k in O[1:]:
            model.add_constraint(z_ik[(i,k)] >= z_ik[(i,k-1)])
    
    # 约束(41)
    for i in B:
        for k in O:
            model.add_constraint( s_ik[(i,k)] >= sum([r_j['r'+str(j-1)]*x_ijk[(i,j,k)] for j in V]))
    
    # 约束(42)
    for i in B:
        for k in O[1:]:
            model.add_constraint(s_ik[(i,k)] >= s_ik[(i,k-1)] + sum([C_i_j['C'+str(i)+str(j)]*x_ijk[(i,j,k-1)] for j in V]) - M*z_ik[(i,k)] + delta_3)
    
    # 约束(43)
    for i in B:
        model.add_constraint(s_ik[(i,1)] >= 0)
    

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
    # model.print_information()
    model.parameters.timelimit=120 # 时间限制为2分钟
    sol = model.solve()
    result_x = sol.get_value_dict(x_ijk)
    list_x = []
    list_handlingtime = {}
    extra_time = [] # 因为泊位分配增加的时间
    for i in result_x:
        if round(result_x[i]) == 1:
            list_x.append(i)
            list_handlingtime[(i[1]-1)*(chsegs*2+1)+3]=C_i_j['C'+str(i[0])+str(i[1])] # 键用运输段表示
            extra_time.append(C_i_j['C'+str(i[0])+str(i[1])]-min(C_i_j['C'+str(j)+str(i[1])] for j in B))
    # print(sol.solve_details)
    # 恢复标准输出（stdout）
    # sys.stdout = sys.__stdout__
    # model.print_solution()
    # ic(model.objective_value)
    return model.objective_value,list_x,list_handlingtime,extra_time