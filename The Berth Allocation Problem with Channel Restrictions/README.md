### 程序介绍
1.ChSP和BAP_CR分别是限制航道和考虑泊位分配的限制航道的MIP模型求解；  
2.ChSP_FCFS和ChSP_ECT分别是在限制航道下，FCFS和ECT规则下确定Phi的方法；  
3.BAP_CR_ECT_origin是论文里中的方法，即从每一次循环泊位中，确定应该分配的船舶。BAP_CR_ECT是我按照理解，在考虑所有泊位下，寻找有最小ECT的船舶，并分配对应的泊位。
4.[IMAI_test.py]中,思路是想通过找出的泊位分配和idle时间,反推应该增加的delta3,但是我觉得这个方法不太行,没有继续下去了,命名为XX_test.py.
5.[IMAI.py]我想的是能不能在原本模型的基础上,怎么把delta3加进去?目前还没想到具体思路,关键是他这个模型的构建，不太方便加入delta3.
6.[Hansen_2003.py]中是论文《A Note on Formulations of Static and Dynamic Berth Allocation Problems》提出的需要更少约束的模型,能够轻松地将delta3的值加进去,已经验证过,方法正确的.
