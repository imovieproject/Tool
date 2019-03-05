# 协同过滤（Collaborative Filtering）Demo
> 这个小程序实现了简单的基于物品的协同过滤，基于用户的协同过滤方法是一致的。主要是为了熟悉一下这个算法

## 环境配置
- Python 3.5.2
- 第三方模块(对模块版本应该没有什么要求)
  - numpy
  - pandas

## 运行
- 安装相关的第三方模块
  ```shell
  pip install numpy
  pip install pandas
  ```
- 修改数据集路径
  ```python
  RATING_DATASET_PATH="~/dataset/ml-latest-small/ratings.csv"
  MOVIE_DATASET_PATH="~/dataset/ml-latest-small/movies.csv"
  ```
- 运行
  ```python
  python3 demo.py
  ```

## 原理说明
### 1. 什么是协同过滤
- 协同过滤简单的来说就是通过计算两种物品之间或者两个用户之间的相似度来进行推荐的一种算法
- 以电影的例子为例，一部电影会被很多个用户进行评分。我们把一部电影看作一个1×m的向量，m为系统中的用户数量。那么两部电影有多相似，就可以通过代表这两个电影的向量来进行度量。
- 协同过滤主要是包括基于用户的协同过滤（UserBased）和基于物品的协同过滤（ItemBased）。但是这两种方法本质上是一样的，都是通过计算用户或者物品之间的相似度来实现推荐
### 2. 通过什么方法去计算相似度
既然物品或者用户都已经抽象成为向量了，那么计算用户或物品之间的相似度实际上就是计算两个向量的相似度。计算两个向量相似度的方法有很多种

设代表物品i的向量为$R_i$用户u对物品i的评分为 $r_{ui}$ ,两个物品i和j之间的相似度为 $sim(i,j)$ 
- **欧氏距离** 
  - 单纯就是计算两个向量之间的距离
    $$sim(i,j)=\sqrt{\sum_{u\in{U}}(r_{ui}-r_{uj})^2}$$
  - 为了讲相似度映射到0到1之间，所以一般还会对相似度做一下处理 
   $$sim(i,j)=\frac{1}{1+sim(i,j)}$$

- **余弦相似性**
  - 这种方法就是计算两个向量之间夹角的余弦值来判断两个向量的相似度。如果两个向量的夹角越小，证明两个向量的方向趋向一致，则两个向量就越相似
  - 向量夹角的余弦值可以通过数量积来求出来 
     $$R_{i}\cdot R_{j}=\sum_{u\in U} {(r_{ui}r_{uj})}= \left| R_{i} \right|\left| R_{j} \right|\cos {(R_i,R_j)}$$
     $$\cos {(R_i,R_j)} = \frac{R_{i}\cdot R_{j}}{\left| R_{i} \right|\left| R_{j} \right|}=\frac{\sum_{u\in U} {(r_{ui}r_{uj})}}{\left| R_{i} \right|\left| R_{j} \right|}=\frac{\sum_{u\in U} {(r_{ui}r_{uj})}}{\sqrt{\sum_{u\in U}{r_{ui}^2}}\sqrt{\sum_{u\in U}{r_{uj}^2}}}=sim(i,j)$$

- **皮尔逊相关系数/相关相似性**
  - 皮尔逊相关系数是在余弦相似性的基础上改进得来的。因为对物品的评分也会收到用户的评分习惯有关。对于被评分的物品，有些用户习惯打高分，而另一些用户可能习惯打低分。因此需要消除这些个人习惯带来的影响，引入了皮尔逊相关系数。在用户评分的基础上，减去物品的平均分
   $$sim(i,j)=\frac{\sum_{u\in U}(r_{ui}-\overline{r_i})(r_{uj}-\overline{r_j})}{\sqrt{\sum_{u\in U}(r_{ui}-\overline{r_i})}\sqrt{\sum_{u\in U}(r_{uj}-\overline{r_j})}}$$

## 实现说明
### 1. 数据处理
- 实现使用的数据集是movielens的ml-latest-small数据集
- 使用pandas的read_csv函数读取csv文件
- 逐行遍历rating.csv里面的数据，得到movie-user的矩阵
> **注意** 这个数据集里面的movieid并不是与电影的索引相匹配的。就是如果将movie按id从小到大进行排列，那么排序后的第10部电影的id不一定是10，可能是11、 21等等
### 2. 计算相似度.
- 这个实现是使用皮尔逊相似度来衡量两个向量的相似性的
- 实现了两个个计算皮尔逊相似度，一个是用numpy.corrcoef函数来算，另一个是我自己实现的计算函数
- 大致说说我自己是怎么实现这个函数的吧
  - 面对这个皮尔逊相关系数的计算公式，最直白的实现方法就是三重循环，暴力算。但实际上这样算是比较慢的，我们可以借助矩阵计算来加速
  - 看到之前的公式，其实我们可以将分子分母都看作是矩阵想成的形式
  - 可以先来看这两个矩阵相乘，假设结果矩阵是result，那么result矩阵里面的第i行第j列的元素就是$\sum_{u\in U}(r_{ui}-\overline{r_i})(r_{uj}-\overline{r_j})$的值
   $$\begin{bmatrix}
       r_{00}-\overline{r_0}&r_{01}-\overline{r_0}&\cdots&r_{0u}-\overline{r_0}\\
       r_{10}-\overline{r_1}&r_{11}-\overline{r_1}&\cdots&r_{1u}-\overline{r_1}\\
       \vdots&\vdots&\ddots&\vdots\\ 
       r_{i0}-\overline{r_i}&r_{i1}-\overline{r_i}&\cdots&r_{iu}-\overline{r_i}\\
   \end{bmatrix}*
    \begin{bmatrix}
       r_{00}-\overline{r_0}& r_{10}-\overline{r_1}&\dots& r_{i0}-\overline{r_i}\\
       r_{01}-\overline{r_0}& r_{11}-\overline{r_1}&\dots& r_{i1}-\overline{r_i}\\
        \vdots&\vdots&\ddots&\vdots\\ 
       r_{0u}-\overline{r_0}& r_{1u}-\overline{r_1}&\dots& r_{iu}-\overline{r_i}\\
   \end{bmatrix}=result $$
        
  - 分子可以做同样的操作，$\sqrt{\sum_{u\in U}(r_{ui}-\overline{r_i})}$实际上就是$\left |R_i\right|$。那么看下面两个矩阵相乘，实际上result矩阵的第i行第j列的元素就是$\sqrt{\sum_{u\in U}(r_{ui}-\overline{r_i})}\sqrt{\sum_{u\in U}(r_{uj}-\overline{r_j})}$的值
    $$ \begin{bmatrix}
        \left |R_0\right|\\
        \left |R_1\right|\\
        \vdots\\
        \left |R_i\right|
    \end{bmatrix}*
    \begin{bmatrix}
        \left |R_0\right|&\left |R_1\right|&\cdots&\left |R_i\right|
    \end{bmatrix}=result$$

  - 所以实际上我们只要构造出分母矩阵和分子矩阵，再将分母矩阵的元素一一对应去除分子矩阵的元素即可。得到的结果矩阵就是皮尔逊相关系数矩阵。实际上这样做运行时间与用numpy库函数来算的时间差不多的
### 3. 获取k近邻
- 获取k近邻比较简单了，单纯遍历皮尔逊系数矩阵的每一行，找到前k大的元素，即可