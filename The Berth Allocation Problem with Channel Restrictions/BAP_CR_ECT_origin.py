from scipy.stats import uniform
import pandas as pd
from icecream import ic
import time
import copy

# 根据航段运输序号返回船舶序号
def return_ship_num(seg_num):
    temp = [i for i in T_dict.values()]
    # print(temp)
    for i in range(len(temp)):
        if seg_num in temp[i]:
            return i # 如果船舶序号为1，返回的是0

# 把两个W融合到一起
def merge_intervals(intervals):
    intervals.sort()
    merged = []
    for interval in intervals:
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])
    return merged

# 返回选择的船舶
def choose_ship(sigma,Phi,B,choose_berth):
    if len(Phi) == 0: # 只执行一次
        dic_vessel_ect = {}
        for vessel in sigma:
            alpha = T_dict['T_'+str(vessel+1)][0]
            y_j = T_dict['T_'+str(vessel+1)][(ship_turn//2)]
            dic_vessel_ect[(vessel,B)] = r_j['r'+str(vessel)]+sum([p_a['p'+str(temp)] for temp in range(alpha,y_j)])+p_a_k['p'+str(y_j)+str(B)]
        # dic_vessel_ect = dict(sorted(dic_vessel_ect.items(), key=lambda x: x[1]))
        min_ectship_berth = min(dic_vessel_ect.items(), key=lambda x: x[1])[0] # 元组格式
        return min_ectship_berth
    else:
        dic_vessel_ect = {}
        for vessel in sigma:
            max_right = []
            for i in choose_berth: 
                if B == i[1]: # 判断是否是同一泊位,是的话再执行以下条件
                    y_j = T_dict['T_'+str(i[0]+1)][(ship_turn//2)]
                    max_right.append(t_a['t'+str(y_j)]+p_a_k['p'+str(y_j)+str(i[1])]+delta_3)
                else:
                    max_right.append(0.0)
            max_right.sort()
            max_ship_values = max_right[-1]
            alpha = T_dict['T_'+str(vessel+1)][0]
            y_j = T_dict['T_'+str(vessel+1)][(ship_turn//2)]
            a = r_j['r'+str(vessel)]+sum([p_a['p'+str(temp)] for temp in range(alpha,y_j)])
            b = max_ship_values
            dic_vessel_ect[(vessel,B)] =max(a,b) +p_a_k['p'+str(y_j)+str(B)]
        min_ectship_berth = min(dic_vessel_ect.items(), key=lambda x: x[1])[0]
        return min_ectship_berth

def calculate(sheet_name,problem_num,chsegs,berth_num,ship_num,filename):
    ''' sheet_name:表名,
        problem_num:第几个问题0,1,2...9
        chsegs:航段数(不包括泊位)
        ship_num:船舶数量
        filename:读取文件的绝对地址'''
    # 参数规定
    sheet_name = sheet_name
    problem_num = problem_num #用于后期循环迭代，0表示第problem1，1表示第problem2
    # df = pd.read_excel(filename, sheet_name='Sheet1',engine='openpyxl') # 不同工作表对应sheet_name=""不一样
    ship_num = ship_num # 读取船舶数量
    chsegs = chsegs
    global ship_turn
    ship_turn = chsegs*2+1
    delta_1 = 0.25
    delta_2 = 0
    global delta_3
    delta_3 = 0.5
    s_np = [i for i in range(1, 2*(chsegs//2+chsegs%2), 2)] # 不允许对立船舶通过的航段的集合
    B = [i for i in range(berth_num)] # 读取泊位数量

    # print('------------------------')
    # print('s_np',s_np)

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
    # print('------------------------')
    # print('T_dict',T_dict)

    # 航段运输集合T
    T = []
    for i in T_dict:
        T+=T_dict[i]
    # print('T',T)
    # 读取excel表数据
    df = pd.read_excel(filename, sheet_name=sheet_name,engine='openpyxl') # 不同工作表对应sheet_name=""不一样
    # print(df)
    df_p = df.iloc[problem_num,1:len(T)+1] #0表示第problem1，提取problem1的所有p
    global p_a
    p_a = {} # 每个航段运输时间(修改序号版)
    p_a_dict = df_p.to_dict() # 每个航段运输时间
    p_a_values = list(p_a_dict.values())
    # ic(p_a_values)
    for i in range(len(p_a_values)):
        p_a['p'+str(i+1)]=p_a_values[i]
    # ic(p_a)

    # 锚地就绪时间
    df_r = df.iloc[problem_num,len(T)+1:len(T)+ship_num+1]
    global r_j
    r_j = df_r.to_dict() # 锚地就绪时间
    # ic(r_j)
    # print(r_j)

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
    # print('------------------------')
    # print('T_ibo',T_ibo)


    T_berth = T_ibo.get("T_berth_" + str((ship_turn//2)+1))
    # print('------------------------')
    # print('T_berth',T_berth)

    # 每艘船的对应泊位/不确定泊位的情况需要更改代码
    df_berth = df.iloc[problem_num,len(T)+ship_num+1:len(T)+ship_num+ship_num*berth_num+1]
    # print('df_berth',df_berth)
    global berths_al
    berths_al = [i for i in df_berth.values] # 需要确定的量
    # print('berths_al',berths_al)
    # print(len(T_berth)*len(B))
    # 读取泊位处理时间
    global p_a_k
    p_a_k = {}
    index_berth = 0
    for i in T_berth:
        for j in B:
            p_a_k['p'+str(i)+str((j))] = berths_al[index_berth]
            index_berth+=1

    T_in_1 = T_ibo['T_in_1']

    # 基于ECT的求解
    # sigma = [0,1,3,7,9,6,5,4,8,2] # 存放σ,按照船舶到达顺序,与船舶数量有关
    sigma = [i for i in range(0,ship_num)] # ETC下与初始顺序无关,而是取决于船舶到达时间以及在泊位停留时间。
    Phi = [] # ships scheduled at the current point
    sigma_copy = copy.deepcopy(sigma)

    global t_a
    t_a = {}
    for i in range((chsegs*2+1)*len(sigma)):
        t_a['t'+str(i+1)] = 0.0
    # print(t_a)

    choose_berth = []
    # 算法1
    start_time = time.time()
    index_1 = 0
    for i in range(len(sigma)):
        W = [] # 禁止窗口
        # j = sigma[i] # 确定j的取值
        '''更改'''
        B_choose = B[index_1]
        # print('选择泊位:',B_choose)
        index_1+=1
        if index_1 == len(B):
            index_1=0
        out = choose_ship(sigma_copy,Phi,B_choose,choose_berth)
        # out = choose_ship(sigma_copy,Phi,B,choose_berth)
        j = out[0]
        # print('选择船舶',j)
        # print('选择泊位',out[1])
        # print('--------------------')
        # print('选择船舶:',j)
        sigma_copy.remove(j)
        # print('sigma_copy',sigma_copy)

        # 将p_a中泊位处理时间对应的-1改为选择泊位的处理时间
        berth_transit = j*ship_turn+chsegs+1
        # print('原本p_a:',j,'p'+str(berth_transit),p_a['p'+str(berth_transit)] )
        p_a['p'+str(berth_transit)] = p_a_k['p'+str(berth_transit)+str(out[1])]
        # print('更改p_a:',str(out[1]),p_a['p'+str(berth_transit)] )

        if len(Phi) == 0:
            alpha = T_dict['T_'+str(j+1)][0]
            t_a['t'+str(alpha)] = r_j['r'+str(j)]
            for transit in range(alpha+1,T_dict['T_'+str(j+1)][-1]+1):
                t_a['t'+str(transit)] = t_a['t'+str(transit-1)] + p_a['p'+str(transit-1)]
        else:
            # 船舶j的inbound和已安排的outbound的禁止窗口
            W.append([float('-inf'),r_j['r'+str(j)]])
            i_b = s_np
            alpha = T_dict['T_'+str(j+1)][0] # 船舶j的第一个进港运输段
            beta = T_dict['T_'+str(j+1)][chsegs+2-1]
            # print('alpha',alpha)
            for ship in choose_berth:
                # 找出a和b,升序排列
                inbound_b = []
                outbound_a = []
                T_j_b = set(T_dict['T_'+str(j+1)]) # 船j的分段运输集合
                # print('T_j_b',T_j_b)
                T_j_a = set(T_dict['T_'+str(ship[0]+1)]) # 已经规划好的一艘船舶的分段运输集合
                # print('T_j_a',T_j_a)
                for seg in i_b:
                    # 将两个列表转换为集合
                    T_in_i  = set(T_ibo['T_in_'+str(seg)])
                    T_out_i = set(T_ibo['T_out_'+str(seg)])
                    # print('T_in_i',T_in_i)
                    # print('T_out_i',T_out_i)
                    # 计算交集
                    intersection = T_j_b.intersection(T_in_i)
                    # 将交集转换为列表
                    inbound_b.append(list(intersection)[0])
                    intersection = T_j_a.intersection(T_out_i)
                    outbound_a.append(list(intersection)[0])
                # print('inbound_b,outbound_a',inbound_b,outbound_a)
                # outbound_a = outbound_a[::-1] # 把一个列表逆序，为了3航段的计算正确性
                for cla_time in range(len(inbound_b)):
                    sum_1 = 0.0 # 左边部分的求和部分
                    sum_2 = 0.0 # 右边部分的求和部分
                    if inbound_b[cla_time]>=alpha:
                        sum_1+=sum([p_a['p'+str(temp)] for temp in range(alpha,inbound_b[cla_time]+1)])
                        sum_2+=sum([p_a['p'+str(temp)] for temp in range(alpha,inbound_b[cla_time])])
                    W.append([t_a['t'+str(outbound_a[cla_time])]-delta_2-sum_1,t_a['t'+str(outbound_a[cla_time])]+p_a['p'+str(outbound_a[cla_time])]+delta_2-sum_2])
                    # W = merge_intervals(W)
                # print(W)

                # 船舶j的inbound和已安排的inbound的禁止窗口inbound_a
                inbound_b = T_dict['T_'+str(j+1)][0:(ship_turn//2)]# 船j的分段运输集合
                # print('inbound_b',inbound_b)
                inbound_a = T_dict['T_'+str(ship[0]+1)][0:(ship_turn//2)] # 已经规划好的一艘船舶的分段运输集合
                # print('inbound_a',inbound_a)
                for cla_time in range(len(inbound_b)):
                    sum_1 = 0.0 # 左边部分的求和部分
                    sum_2 = 0.0 # 右边部分的求和部分
                    if inbound_b[cla_time]>=alpha:
                        sum_1+=sum([p_a['p'+str(temp)] for temp in range(alpha,inbound_b[cla_time])])
                        sum_2+=sum([p_a['p'+str(temp)] for temp in range(alpha,inbound_b[cla_time])])
                    W.append([t_a['t'+str(inbound_a[cla_time])]-delta_1-sum_1,t_a['t'+str(inbound_a[cla_time])]+delta_1-sum_2])
                    # W = merge_intervals(W)
                # print(W)

                # 当两艘船的泊位一致时,船舶j的靠泊和已安排的靠泊的禁止窗口berth_a
                # if T_dict['T_'+str(j+1)][(ship_turn//2)] == T_dict['T_'+str(ship+1)][(ship_turn//2)]:
                if out[1] == ship[1]:
                    berth_b = [T_dict['T_'+str(j+1)][(ship_turn//2)]]# 船j的分段运输集合
                    # print('berth_b',berth_b)
                    berth_a = [T_dict['T_'+str(ship[0]+1)][(ship_turn//2)]] # 已经规划好的一艘船舶的分段运输集合
                    # print('berth_a',berth_a)
                    for cla_time in range(len(berth_b)):
                        sum_1 = 0.0 # 左边部分的求和部分
                        sum_2 = 0.0 # 右边部分的求和部分
                        if berth_b[cla_time]>=alpha:
                            sum_1+=sum([p_a['p'+str(temp)] for temp in range(alpha,berth_b[cla_time]+1)])
                            sum_2+=sum([p_a['p'+str(temp)] for temp in range(alpha,berth_b[cla_time])])
                        W.append([t_a['t'+str(berth_a[cla_time])]-delta_3-sum_1,t_a['t'+str(berth_a[cla_time]+1)]+delta_3-sum_2])
                        # W = merge_intervals(W)
                    # print(W)
            # 进行t_alpha的取值
            W = merge_intervals(W)
            my_list = W
            min_val = min([x[1] if x[0] == -float('inf') else x[0] for x in my_list]) # 禁止窗口中获得的最小值
            # print('min_val',min_val)
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
                # print('T_j_b',T_j_b)
                T_j_a = set(T_dict['T_'+str(ship+1)]) # 已经规划好的一艘船舶的分段运输集合
                # print('T_j_a',T_j_a)
                for seg in i_b:
                    # 将两个列表转换为集合
                    T_in_i  = set(T_ibo['T_in_'+str(seg)])
                    T_out_i = set(T_ibo['T_out_'+str(seg)])
                    # print('T_in_i',T_in_i)
                    # print('T_out_i',T_out_i)
                    # 计算交集
                    intersection = T_j_b.intersection(T_out_i)
                    # 将交集转换为列表
                    outbound_b.append(list(intersection)[0])
                    intersection = T_j_a.intersection(T_in_i)
                    inbound_a.append(list(intersection)[0])
                # print('outbound_b,inbound_a',outbound_b,inbound_a)
                # inbound_a = inbound_a[::-1] # 把一个列表逆序，为了3航段的计算正确性
                for cla_time in range(len(outbound_b)):
                    sum_1 = 0.0 # 左边部分的求和部分
                    sum_2 = 0.0 # 右边部分的求和部分
                    if outbound_b[cla_time]>=beta:
                        sum_1+=sum([p_a['p'+str(temp)] for temp in range(beta,outbound_b[cla_time]+1)])
                        sum_2+=sum([p_a['p'+str(temp)] for temp in range(beta,outbound_b[cla_time])])
                    W.append([t_a['t'+str(inbound_a[cla_time])]-delta_2-sum_1,t_a['t'+str(inbound_a[cla_time])]+p_a['p'+str(inbound_a[cla_time])]+delta_2-sum_2])
                    # W = merge_intervals(W)
                # print(W)

                # 船舶j的outbound和已安排的outbound的禁止窗口
                outbound_b = T_dict['T_'+str(j+1)][(ship_turn//2)+1:ship_turn]# 船j的分段运输集合
                # print('outbound_b',outbound_b)
                outbound_a = T_dict['T_'+str(ship+1)][(ship_turn//2)+1:ship_turn] # 已经规划好的一艘船舶的分段运输集合
                # print('outbound_a',outbound_a)
                for cla_time in range(len(outbound_b)):
                    sum_1 = 0.0 # 左边部分的求和部分
                    sum_2 = 0.0 # 右边部分的求和部分
                    if outbound_b[cla_time]>=beta:
                        sum_1+=sum([p_a['p'+str(temp)] for temp in range(beta,outbound_b[cla_time])])
                        sum_2+=sum([p_a['p'+str(temp)] for temp in range(beta,outbound_b[cla_time])])
                    W.append([t_a['t'+str(outbound_a[cla_time])]-delta_1-sum_1,t_a['t'+str(outbound_a[cla_time])]+delta_1-sum_2])
                    # W = merge_intervals(W)
                # print(W)

            # 进行t_beta的取值
            W = merge_intervals(W)
            my_list = W
            min_val = min([x[1] if x[0] == -float('inf') else x[0] for x in my_list]) # 禁止窗口中获得的最小值
            # print('min_val',min_val)
            t_a['t'+str(beta)] = min_val
            for transit in range(beta+1,beta+(ship_turn//2)):
                t_a['t'+str(transit)] = t_a['t'+str(transit-1)] + p_a['p'+str(transit-1)]
        Phi.append(j) # 遍历完了一艘船j，将其加入Phi
        choose_berth.append(out)
    end_time = time.time()
    run_time = end_time - start_time
    # print('t_a',t_a)
    # print("ECT运行时间为：", run_time)
    # 求总等待时间
    sum_z = 0.0
    # 锚地等待时间
    for i in T_ibo['T_in_1']:
        w_a = t_a['t'+str(i)]-r_j['r'+str(return_ship_num(i))]
        sum_z+=w_a
    # 泊位等待时间
    # print('p_a:',p_a)
    for i in T_berth:
        # w_a = t_a['t'+str(i+1)]-t_a['t'+str(i)]-p_a['p'+str(i)]
        w_a = t_a['t'+str(i+1)]-t_a['t'+str(i)]-min([p_a_k['p'+str(i)+str(j)] for j in B])
        sum_z+=w_a
    # print('ECT得到的problem{0}的结果:'.format(problem_num+1),sum_z)
    return sum_z,run_time,t_a
# calculate('T6R3',0,2)
# print(calculate('T6R3',0,2))
'''p_a:
        {'p1': 8.33333, 'p2': 8.33333, 'p3': 58.9251, 'p4': 8.33333, 'p5': 8.33333, 'p6': 8.33333, 'p7': 8.33333, 'p8': 80.081, 'p9': 8.33333, 'p10': 8.33333, 'p11': 8.33333, 'p12': 8.33333, 'p13': 73.3932, 'p14': 8.33333, 'p15': 8.33333, 'p16': 8.33333, 'p17': 8.33333, 'p18': 81.3835, 'p19': 8.33333, 'p20': 8.33333, 'p21': 8.33333, 'p22': 8.33333, 'p23': 87.9898, 'p24': 8.33333, 'p25': 8.33333, 'p26': 8.33333, 'p27': 8.33333, 'p28': 55.9635, 'p29': 8.33333, 'p30': 8.33333, 'p31': 8.33333, 'p32': 8.33333, 'p33': 102.643, 'p34': 8.33333, 'p35': 8.33333, 'p36': 8.33333, 'p37': 8.33333, 'p38': 77.9112, 'p39': 8.33333, 'p40': 8.33333, 'p41': 8.33333, 'p42': 8.33333, 'p43': 69.4576, 'p44': 8.33333, 'p45': 8.33333, 'p46': 8.33333, 'p47': 8.33333, 'p48': 81.6396, 'p49': 8.33333, 'p50': 8.33333}'''