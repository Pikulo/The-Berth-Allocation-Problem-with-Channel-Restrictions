import pandas as pd
import sys
import numpy as np
# 读取文件地址
filename_data = r'D:\APPS\Vscode\Vscode_files\Vscode\ZJU_STUDY\Papers_Codes\The Berth Allocation Problem with Channel Restrictions\dataset\ts-cb-t10-11.xlsx'
df = pd.read_excel(filename_data, sheet_name='Sheet1',engine='openpyxl') # 不同工作表对应sheet_name=""不一样
worksheet = df['dataset'].tolist()
print(f"worksheet\n{worksheet}")
chegs = df['ChSegs'].tolist()

# filename = r'D:\APPS\Vscode\Vscode_files\Vscode\ZJU_STUDY\Papers_Codes\The Berth Allocation Problem with Channel Restrictions\Output\ts-cb-t12\Hansen.txt'

# import Hansen_2003 as hs
# import ChSP_Decomposition as cd
# def combine_BAP_ChSP(out):
#     sort_out = sorted(out, key=lambda x: x[1])
#     berth_allocate = []
#     for i in sort_out:
#         berth_allocate.append(i[0]) # 从船舶1开始依次往后的泊位分配
#     print(berth_allocate)
#     return berth_allocate

# dict_allsheet = {}
# # sum1 = {}
# for sheet in worksheet[0:30]:
#     berth_num = df.loc[df['dataset'] == sheet, 'n'].values[0]
#     ship_num = df.loc[df['dataset'] == sheet, 'm'].values[0]
#     reslut = []
#     for i in range(0,10):
#         out = hs.mip_cal(berth_num,ship_num,2,i,sheet,filename_data)
#         berth_allocate = combine_BAP_ChSP(out[1]) # out[1]是存放船舶分配顺序的列表
#         # sum1['BAP'] = sum(out[3])
#         list_handlingtime = out[2]
#         out_2 = cd.mip_cal(list_handlingtime,berth_allocate,ship_num,2,i,sheet,filename_data)
#         reslut.append(out_2+sum(out[3])) # 加上泊位分配导致的额外处理时间
#         # sum1['chsp'] = out_2
#     dict_allsheet[sheet+'X'] = reslut
# print(dict_allsheet)
# for i in dict_allsheet.values():
#     for j in i:
#         print(j)
        
        
list_mean = []
for sheet in worksheet:
    df1 = pd.read_excel(filename_data, sheet_name=sheet+'X',engine='openpyxl')
    ect_df = df1.loc[df1['alg'] == 'DCMP', ['problem', 'z']]
    ect_df_tuples = ect_df.to_records(index=False)
    temp = []
    for row in ect_df_tuples:
        temp.append(row[1])
    list_mean.append(np.mean(temp))
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
# print(sum1)