import pandas as pd
from docplex.mp.model import Model
from scipy.stats import uniform
import random
from icecream import ic
import unittest
import os
import sys
import numpy as np


random.seed(1)
R = random.uniform(0,1)
p_k_a = lambda R: 2000*(2*R+1.5)/60
mean=uniform.expect(func=p_k_a,loc=0,scale=1) # 平均装卸时间
L = mean/5
print(f"装卸时间期望\n{L}") #16.666666666666664

# P719生成船舶到达时间以及在锚地就绪时间
def generated(num_ship,num_berth):
    # A_j = [random.uniform(1, (7000*num_ship)/(60*num_berth)) for _ in range(num_ship)]
    A_j = random.uniform(1, (7000*num_ship)/(60*num_berth))
    A_j = [random.uniform(1, A_j) for _ in range(num_ship)]
    # print(A_j)
    F = 0.5 # 控制到达模式的参数
    S_i = L + min(A_j) + F*(max(A_j) - min(A_j))
    r_j = [max(A_j[i]-S_i,0) for i in range(num_ship)]
    R = np.random.uniform(0, 1, size=num_ship*num_berth)
    p_k_a = 2000 * (2 * R + 1.5) / 60
    p_k_a = list(p_k_a)
    return A_j,S_i,r_j,p_k_a

A_j,S_i,r_j,p_k_a = generated(6,2)
print(f"船舶到达时间\nA_j:{A_j}")
print(f"泊位空闲时间\nS_i:{S_i}")
print(f"船舶在锚地就绪时间\nr_j:{r_j}")
print(f"船舶装卸时间\np_k_a:{p_k_a}")

