import pandas as pd
import numpy as np
import math
import os

from scipy.stats import pearsonr

RATING_DATASET_PATH="~/dataset/ml-latest-small/ratings.csv"
MOVIE_DATASET_PATH="~/dataset/ml-latest-small/movies.csv"

# read data and process
def process_raw_data(ratings_dataset_path,movie_dataset_path,output_filename):
    ratings= pd.read_csv(ratings_dataset_path)
    movie=pd.read_csv(movie_dataset_path)

    groups=ratings.groupby('userId')

    for name,group in groups:
        print('processing user {}'.format(name))
        movie[name]=pd.Series(group['rating'].tolist(),index=(group['movieId'].tolist()))

    movie.to_csv(output_filename)

# get movie-user matrix
def get_movie_user_mat(ratings_dataset,save_result=True,filename='movie_user_mat.npy'):
    if os.path.exists(filename):
        movie_user_mat=np.load(filename)
    else:
        movieId_list=np.sort(ratings_dataset['movieId'].unique())
        userId_list=np.sort(ratings_dataset['userId'].unique())
        movie_num=len(movieId_list)
        user_num=len(userId_list)
        movie_user_mat=np.empty([movie_num,user_num],dtype=float)

        for row in ratings_dataset.iterrows():
            movie_index=np.where(movieId_list==row[1]['movieId'])[0][0]
            user_index=np.where(userId_list==row[1]['userId'])[0][0]
            print('processing row {},movie index {}, user index {}, user id {}, movie id {}'.format(row[0],movie_index,user_index,row[1]['userId'],row[1]['movieId']))
            movie_user_mat[movie_index,user_index]=row[1]['rating']

        if save_result:
            np.save(filename,movie_user_mat)
    return movie_user_mat

# use function in numpy to calculate pearson correction coefficient
def get_pearson_coef(cal_mat,save_result=False,filename='pearson_coef.npy'):
    print("start calculating pearson coefficient")
    res=np.corrcoef(cal_mat)
    if save_result:
        np.save(filename,res)

    return res

# my implementation to calculate pearson correction coefficient
def get_pearson_coef_manual(cal_mat,save_result=False,filename='pearson_coef_manual.npy'):
    pearson_coef=None
    if os.path.exists(filename):
        pearson_coef=np.load(filename)
    else:
        print("start calculating pearson coefficient")
        vector_num=(cal_mat.shape)[0]
        col_num=(cal_mat.shape)[1]
        pearson_coef=np.empty([vector_num,vector_num],dtype=float)

        mean=np.mean(cal_mat,axis=1)
        subtract=np.subtract(cal_mat.T,mean)
        subtract=subtract.T

        dominator_mat=np.dot(subtract,subtract.T)
        norminator_mat=np.linalg.norm(subtract,axis=1,ord=2)
        norminator_mat=np.reshape(norminator_mat,[vector_num,1])
        norminator_mat=np.dot(norminator_mat,norminator_mat.T)
        pearson_coef=np.divide(dominator_mat,norminator_mat)
        
        if save_result:
            np.save(filename,pearson_coef)
    
    return pearson_coef

# calculating pearson coef by scipy
# def get_pearson_coef_scipy()

# calculating pearson coef by pandas
def get_pearson_coef_pandas(cal_mat,save_result=False,filename='pearson_coef_manual.npy'):
    print("start calculating pearson coefficient (pandas)")
    df=pd.DataFrame(cal_mat)
    df.corr()
    return df

# get k-neighbors
def get_k_neighbors(pearson_coef,movie_dataset,k=100):
    print('start calculating k neighbors')
    movie_num=(pearson_coef.shape)[0]
    movie_sorted_index=np.argsort(-pearson_coef,axis=1)

    k_neighbor={}

    for i in range(0,movie_num):
        print('calculating k neighbors of movie {}'.format(i))
        k_neighbor_item={}
        k_neighbor_item['index']=i
        k_neighbor_item['sim_movie_list']=[]
        for j in range(0,k):
            sim_movie_index=movie_sorted_index[i,j]
            if sim_movie_index!=i:
                k_neighbor_item['sim_movie_list'].append(
                    {
                        'index': sim_movie_index,
                        'movie_id': movie_dataset.loc[sim_movie_index,'movieId'],
                        'pearson_coef': pearson_coef[i,sim_movie_index],
                    }
                )
            else:
                j-=1

        k_neighbor['{}'.format(movie_dataset.loc[i,'movieId'])]=k_neighbor_item

    return k_neighbor

# get predict ratings
def get_predicted_rates(user_index,movie_index,sim_mat,sim_movie_index_list,movie_user_mat):
    i_mean=np.mean(movie_user_mat[movie_index,:])
    sum1=0
    sum2=0
    for i in range(0,10):
        sum1+=sim_mat[i,sim_movie_index_list[i]]*(movie_user_mat[movie_index,user_index]-i_mean)
        sum2+=abs(sim_mat[i,sim_movie_index_list[i]])

    prediction=i_mean +sum1/sum2
    return prediction

# get similar movie list
def get_sim_movie_list(movie_id,movie_dataset,k_neighbor,k):
    print('similar movies of {} are: '.format(movie_dataset.loc[k_neighbor['{}'.format(movie_id)]['index'],'title']))
    for i in range(0,k):
        sim_movie=k_neighbor[movie_id]['sim_movie_list'][i]
        print("{}. {}".format(i,movie_dataset.loc[sim_movie['index'],'title']))




ratings_dataset=pd.read_csv(RATING_DATASET_PATH)
movie_dataset=pd.read_csv(MOVIE_DATASET_PATH)

output_filename='rs.csv'

movie_user_mat=get_movie_user_mat(ratings_dataset)
pearson_coef=get_pearson_coef_manual(movie_user_mat,save_result=True)
k_neighbor=get_k_neighbors(pearson_coef,movie_dataset)

print(movie_user_mat)
print(pearson_coef)

user_index=0
movie_index=62
sim_mat=pearson_coef
sim_movie_index_list=[]
for i in range(0,10):
    sim_movie_index_list.append(k_neighbor['1']['sim_movie_list'][i]['index'])

print("prediction of user 1 on movie 1 is {}".format(
    get_predicted_rates(user_index,movie_index,sim_mat,sim_movie_index_list,movie_user_mat)
))

get_sim_movie_list('1',movie_dataset,k_neighbor,k=10)
# movie_id=input("input movie id you like: ")

# print('similar movies of {} are: '.format(movie_dataset.loc[k_neighbor['{}'.format(movie_id)]['index'],'title']))
# for i in range(0,10):
#     sim_movie=k_neighbor[movie_id]['sim_movie_list'][i]
#     print("{}. {}".format(i,movie_dataset.loc[sim_movie['index'],'title']))

