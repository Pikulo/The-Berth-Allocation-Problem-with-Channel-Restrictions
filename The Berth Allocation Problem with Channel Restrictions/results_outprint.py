import pandas as pd
import sys
import numpy as np
# 读取文件地址
filename_data = r'D:\APPS\Vscode\Vscode_files\Vscode\ZJU_STUDY\Papers_Codes\The Berth Allocation Problem with Channel Restrictions\dataset\ts-cb-t6.xlsx'
df = pd.read_excel(filename_data, sheet_name='Sheet1',engine='openpyxl') # 不同工作表对应sheet_name=""不一样
worksheet = df['dataset'].tolist()
print(f"worksheet\n{worksheet}")
chegs = df['ChSegs'].tolist()
# 构建worksheet对应chegs的字典
dict_worksheet_chegs = {}
for i,j in enumerate(worksheet):
    dict_worksheet_chegs[j] = chegs[i]
print(f"dict_worksheet_chegs\n{dict_worksheet_chegs}")

# print(worksheet)
# m_value = df.loc[df['dataset'] == 'T6R4', 'm'].values[0]
# print(m_value)
# for i in worksheet:
#     print(i)
#     m_value = df.loc[df['dataset'] == i, 'm'].values[0]
#     print(m_value)

filename = r'D:\APPS\Vscode\Vscode_files\Vscode\ZJU_STUDY\Papers_Codes\The Berth Allocation Problem with Channel Restrictions\Output\ECT_results\ECT_t9.txt'

'''Table6-Table9'''
'''mip值'''
# import ChSP as cp
# dict_allsheet = {}
# # sys.stdout = open(filename, 'w')
# for sheet in worksheet[8:9]:
#     print(sheet)
#     ship_num = df.loc[df['dataset'] == sheet, 'm'].values[0]
#     reslut = []
#     for i in range(0,10):
#         out = cp.mip_cal(ship_num,dict_worksheet_chegs[sheet],i,sheet,filename_data)
#         reslut.append(out)
#         print(f"{out:<.4f}")
#     print('\n')
#     dict_allsheet[sheet] = reslut
# # sys.stdout = sys.__stdout__
# print(dict_allsheet)
# for i in dict_allsheet:
#     for j in dict_allsheet[i]:
#         print(j)
'''ChSP_ECT'''
'''求得ECT值'''
import ChSP_ECT as ce
dict_allsheet = {}
# sys.stdout = open(filename, 'w')
for sheet in worksheet[:]:
    print(sheet)
    reslut = []
    print('航段数(不包含泊位)',dict_worksheet_chegs[sheet])
    m_value = df.loc[df['dataset'] == sheet, 'm'].values[0]
    print('船舶数量：',m_value)
    for i in range(0,10):
        out = ce.calculate(sheet,i,dict_worksheet_chegs[sheet],m_value,filename_data)
        reslut.append(out[0])
        print(f"problem{i:<2} {out[0]:<.4f}")
    print('\n')
    dict_allsheet[sheet] = reslut
# print(dict_allsheet)
# sys.stdout = sys.__stdout__
'''计算Z_ECT/Z_mip'''
list_mean = []
for i in dict_allsheet:
    list_mean.append(np.mean(dict_allsheet[i]))
list_mean1 = []
for sheet in worksheet:
    df1 = pd.read_excel(filename_data, sheet_name=sheet+'X',engine='openpyxl')
    ect_df = df1.loc[df1['alg'] == 'MIP', ['problem', 'z']]
    ect_df_tuples = ect_df.to_records(index=False)
    temp = []
    for row in ect_df_tuples:
        temp.append(row[1])
    list_mean1.append(np.mean(temp))
ratio = []
for i in range(len(list_mean)):
    ratio.append(list_mean[i]/list_mean1[i])
    print(list_mean[i]/list_mean1[i])
print(ratio)
'''打印Excel表中的ECT对应z值'''
# sys.stdout = open(filename, 'w')
# for sheet in worksheet:
#     df1 = pd.read_excel(filename_data, sheet_name=sheet+'X',engine='openpyxl')
#     # print(df1)
#     ect_df = df1.loc[df1['alg'] == 'ECT', ['problem', 'z']]
#     # print(ect_df)
#     ect_df_tuples = ect_df.to_records(index=False)
#     # print(ect_df_tuples)
#     print(sheet+'X')
#     for row in ect_df_tuples:
#         print(f"problem{row[0]:<2} {row[1]:<.3f}")
#     print('\n')
# sys.stdout = sys.__stdout__


'''最优解'''
# import BAP_CR as bc
# berth_num = df.loc[df['dataset'] == 'T10R4', 'n'].values[0]
# bc.mip_cal(berth_num,6,2,0,'T10R4',filename_data)



'''1.BAP_CR_ECT_origin(论文方法求解)'''
# import BAP_CR_ECT_origin as bceo
# berth_num = df.loc[df['dataset'] == 'T10R1', 'n'].values[0]
# ship_num = df.loc[df['dataset'] == 'T10R1', 'm'].values[0]
# for i in range(0,10):
#     out = bceo.calculate('T10R1',i,2,berth_num,ship_num,filename_data)
#     print(out[0])
# # 我的答案是105.527,但是t_a和表格一样，说明我求错了z，说明z的求解不对!少加了部分东西——>将p_a_k改为:min([p_a_k['p'+str(i)+str(j)] for j in B]

'''2.BAP_CR_ECT'''
# import BAP_CR_ECT as bce
# # berth_num = df.loc[df['dataset'] == 'T10R2', 'n'].values[0]
# # ship_num = df.loc[df['dataset'] == 'T10R2', 'm'].values[0]
# for i in range(0,10):
#     out = bce.calculate('T10R2',i,2,berth_num,ship_num,filename_data)
#     print(out[0])


'''将1和2的结果保存到excel中'''
# import BAP_CR_ECT_origin as bceo
# import BAP_CR_ECT as bce
# for sheet in worksheet:
#     print(sheet)
#     berth_num = df.loc[df['dataset'] == sheet, 'n'].values[0]
#     ship_num = df.loc[df['dataset'] == sheet, 'm'].values[0]
#     result_paper = []
#     result_mine = []
#     for i in range(0,10):
#         out1 = bceo.calculate(sheet,i,2,berth_num,ship_num,filename_data)
#         result_paper.append(out1[0])
#     for i in range(0,10):
#         out2 = bce.calculate(sheet,i,2,berth_num,ship_num,filename_data)
#         result_mine.append(out2[0])
#     # print(result_mine)
#     # 创建数据
#     data = {'Problem': [i for i in range(1,11)],
#             'z_paper': result_paper,
#             'z_mine':  result_mine}
#     # 创建DataFrame对象
#     df1 = pd.DataFrame(data)
#     # 文件路径和工作表名称
#     filename = r'D:\APPS\Vscode\Vscode_files\Vscode\ZJU_STUDY\Papers_Codes\The Berth Allocation Problem with Channel Restrictions\Output\ts-cb-t10-11\data.xlsx'
#     # 创建Excel文件
#     # 写入数据到不同的工作表
#     sheet_name=sheet
#     # 导入openpyxl引擎
#     import openpyxl
#     # 打开ExcelWriter对象
#     with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
#         # 加载现有的工作簿
#         writer.book = openpyxl.load_workbook(filename)
#         # 将DataFrame写入现有工作表中
#         df1.to_excel(writer, sheet_name=sheet_name, index=False)

'''BAP_NO_CR:表12的Zbap'''
# import BAP_CR_for_BAP_Zbap as bcbz
# for sheet in worksheet[29:30]:
#     berth_num = df.loc[df['dataset'] == sheet, 'n'].values[0]
#     ship_num = df.loc[df['dataset'] == sheet, 'm'].values[0]
#     result = []
#     for i in range(0,10):
#         out = bcbz.mip_cal(berth_num,ship_num,2,i,sheet,filename_data)
#         result.append(out)
# print(result)
# import numpy as np
# # sorted_list = sorted(result)
# # print(sorted_list)
# # trimmed_list = sorted_list[1:-1]
# # print(trimmed_list)|
# mean = np.mean(result)
# print(mean)


'''BAP_CR:表12的Zmip'''
# import BAP_CR as bc
# for sheet in worksheet[0:1]:
#     berth_num = df.loc[df['dataset'] == sheet, 'n'].values[0]
#     ship_num = df.loc[df['dataset'] == sheet, 'm'].values[0]
#     result = []
#     for i in range(1,2):
#         out = bc.mip_cal(berth_num,ship_num,2,i,sheet,filename_data)
#         result.append(out)
# print(result)
# import numpy as np
# # sorted_list = sorted(result)
# # print(sorted_list)
# # trimmed_list = sorted_list[1:-1]
# # print(trimmed_list)
# mean = np.mean(result)
# print(mean)

'''Hansen'''
# import Hansen_2003 as hs
# dict_allsheet = {}
# # sys.stdout = open(filename, 'w')
# for sheet in worksheet[29:]:
#     print(sheet)
#     berth_num = df.loc[df['dataset'] == sheet, 'n'].values[0]
#     ship_num = df.loc[df['dataset'] == sheet, 'm'].values[0]
#     reslut = []
#     for i in range(0,1):
#         out = hs.mip_cal(berth_num,ship_num,2,i,sheet,filename_data)
#         # out2 = bcbz.mip_cal(berth_num,ship_num,2,i,sheet,filename_data)
#         # print(out2)
#         reslut.append(out[0])
#         print(f"{out[0]:<.4f}")
#         print(out[1])
#     print('\n')
#     dict_allsheet[sheet] = reslut
# # sys.stdout = sys.__stdout__
# print(dict_allsheet)


final_out ={
    'T12R1': [252.1236, 227.75652000000005, 299.22569999999996, 164.75970000000007, 280.9384, 290.3087, 326.56159999999994, 213.17539999999963, 199.16699999999997, 235.33640000000003], 'T12R2': [553.2683999999997, 392.9462000000002, 345.1432, 278.01390000000004, 247.1723, 247.47640000000024, 579.7714000000001, 461.12839999999994, 530.9394730000004, 416.6244999999999], 'T12R3': [740.4173, 312.9054, 1038.9480599999997, 558.2219000000001, 803.675, 588.7515000000001, 842.3700000000002, 951.572, 919.95124, 701.9215000000003], 'T12R4': [59.351899999999944, 85.2878, 124.51899999999998, 152.45460000000003, 123.66439999999992, 137.25649999999996, 129.82009999999997, 103.86469999999994, 133.74940000000004, 116.50100000000003], 'T12R5': [201.0365, 234.26779999999988, 448.31125399999996, 227.82257999999987, 272.8376000000002, 353.4483, 357.21500000000003, 235.64649999999997, 183.02109999999993, 149.92341999999982], 'T12R6': [516.8495, 742.6615999999999, 567.5605999999999, 481.71859999999987, 569.9572999999998, 570.1753, 577.3881000000001, 566.1857399999998, 280.77736500000015, 763.49318], 'T12R7': [221.59210000000007, 135.1799999999999, 184.48760000000007, 91.40470000000005, 119.29590000000002, 144.8440999999999, 154.87710000000004, 147.55250000000018, 193.18879999999956, 159.9298999999999], 'T12R8': [232.0037000000001, 347.64569999999986, 257.1439999999999, 363.9072999999998, 160.4396, 588.2350999999998, 509.5379000000001, 445.79049999999995, 560.4222400000003, 418.5680000000001], 'T12R9': [249.96392999999995, 81.8169999999999, 143.64130000000003, 172.4645999999999, 162.08911999999987, 206.7771199999999, 175.49879999999996, 176.07857, 138.94780000000017, 93.03340000000006], 'T12R10': [517.6605999999998, 433.4829999999999, 425.1374999999999, 499.83663999999965, 246.2762, 675.6314000000001, 656.4327999999998, 325.47749999999996, 392.79270000000014, 332.4539999999999], 'T12R11': [339.7036999999999, 329.7812, 380.5279000000001, 297.53239999999994, 411.26462540000006, 258.89189999999996, 271.95759999999996, 342.86439999999993, 369.0509100000001, 364.1692], 'T12R12': [704.0765, 717.7625199999999, 747.6306, 668.3081, 655.0691199999999, 687.2700000000002, 653.8845999999999, 633.6014000000002, 707.0341499999998, 640.945], 'T12R13': [1036.7819000000004, 1071.0597000000002, 1385.5884, 1155.3848, 1295.18442, 1137.1358, 1201.9660999999999, 1119.0178, 1089.2831, 1139.9402999999998], 'T12R14': [169.03947000000005, 188.77496000000002, 168.25750000000002, 192.4706, 182.5005000000001, 186.07889999999998, 228.9776, 128.91907999999995, 222.0586, 187.34699999999998], 'T12R15': [436.0375000000001, 521.1543999999998, 468.5646999999998, 529.12432, 577.1545000000001, 525.14202, 431.4272299999999, 424.2454999999999, 488.2823000000002, 435.1113999999998], 'T12R16': [1000.2646999999998, 859.4147200000002, 907.4022100000002, 981.2722699999999, 926.7934000000002, 924.0715, 888.6223000000002, 895.0568999999998, 929.4119999999999, 784.9327000000001], 'T12R17': [239.04199999999997, 246.54579999999996, 245.32940000000002, 193.5827, 292.58579999999995, 227.35499999999996, 211.18478999999996, 226.58970000000008, 272.96469999999994, 226.7032000000001], 'T12R18': [623.17713, 673.6488999999999, 565.4606999999999, 520.1548999999999, 686.466, 565.5427719999999, 663.7444, 672.3614999999999, 596.5448799999999, 511.66129999999987], 'T12R19': [267.47660000000013, 290.55294000000004, 303.34170000000006, 229.78370000000007, 277.6067, 249.60037000000005, 262.5081000000002, 263.83372000000014, 281.14230000000003, 268.79659999999996], 'T12R20': [853.6129759999999, 751.8842499999996, 771.9762999999999, 836.4556299999999, 667.2905000000002, 735.3671000000003, 878.9953000000002, 766.8837999999998, 694.9335399999997, 719.21229], 'T12R21': [313.2744, 374.27070000000003, 432.13849999999996, 334.1778, 400.52619999999996, 347.8372999999999, 437.2186, 422.2403, 455.00570000000005, 379.9962000000001], 'T12R22': [804.1704999999998, 848.7047, 790.8858, 830.3131, 733.9354000000001, 801.3626, 826.9390999999999, 738.7532000000002, 804.1752999999999, 815.806], 'T12R23': [1166.8856, 1347.8443000000002, 1228.7755000000002, 1336.7063999999996, 1311.561, 1298.6228999999998, 1267.0348, 1168.1803000000004, 1345.2823999999996, 1268.8203000000003], 'T12R24': [185.4139, 212.20779999999996, 246.9455000000001, 172.4116999999999, 251.43719999999996, 196.14499999999998, 185.01980000000003, 180.02470000000005, 190.70320000000004, 177.67440000000005], 'T12R25': [552.0265999999999, 552.7161, 553.0552, 574.9942000000002, 603.8109000000001, 564.6137999999999, 634.1552, 579.3783999999999, 505.7336999999999, 608.0776], 'T12R26': [1087.3900999999998, 1088.1495000000002, 1095.2349999999997, 1132.3633999999997, 1020.4236000000001, 1094.3157, 1078.6671, 1047.25, 1103.5402, 1037.6026], 'T12R27': [247.51229999999998, 226.98779999999994, 222.47150000000002, 228.4976000000001, 286.5087, 243.03079999999997, 257.4257, 273.9486, 261.28080000000006, 267.43299999999994], 'T12R28': [704.5688000000001, 685.995, 768.9399000000001, 719.0273, 701.8800000000001, 755.1632999999999, 720.3577999999999, 726.6215, 701.2167999999997, 753.9815999999998], 'T12R29': [296.93070000000006, 305.1198999999999, 348.6106000000001, 310.17999999999995, 304.1846, 292.8672999999998, 280.0094, 290.779, 312.1289, 281.2310000000001], 'T12R30': [881.5423999999997, 862.4439000000001, 888.7649999999999, 883.4264, 938.0523000000004, 872.2185000000001, 882.3186000000002, 874.4028000000003, 877.1074, 878.4102999999999]
    }
'''求IMAI均值'''
# for i in final_out:
#     print(np.mean(final_out[i]))
'''
IMAI均值:
248.935302
405.2484173000001
745.8733900000001
116.64693999999997
266.3530053999999
563.6767285
1273.9713500000003
199.79832000000005
572.85617
1078.49372
251.50967999999997
723.7751999999999
302.20414
883.86876
'''
