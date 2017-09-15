# -*- coding: utf-8 -*-

import json
import time
import codecs
import crawler

import pandas as pd
import data_io as dio
from nnls import NNLS
from sklearn import linear_model
from collections import defaultdict
from sklearn.datasets import load_svmlight_file

basic_info_path = './data/2017_basic_info.csv'  
comments_path = './data/comments.json'
training_path = './data/features.libsvm.txt'
movie_comments_handled = './data/movie_comments_handled.json'
box_office_path = './data/box_office.json'
def get_movie_comments_handled():
    return json.load(codecs.open(movie_comments_handled,'r','utf-8'))

def get_box_office():
    return json.load(codecs.open(box_office_path,'r','utf-8'))
def extend_info(info_path=basic_info_path):
    """
    Add casts info to raw dataFrame
    """
    info = pd.read_csv(info_path)
    info = info.fillna(info.mean())
    info['casts'] = ['' for i in range(info.shape[0])]
    for index, movie in info.iterrows():
        print(movie['name'])
        extend_info = crawler.get_douban_related_movie_info(movie['name'], movie['year'])
        if extend_info == None:
            info.set_value(index, 'casts', '')
            continue
        casts = [i['name'] for i in extend_info['casts']]
        director = [i['name'] for i in extend_info['directors']]
        info.set_value(index, 'casts', ';'.join(casts))
        time.sleep(5)
    return info

def analyse_comment(data):
    

    movie_comments = defaultdict(dict)
    # count the comments that not related with any actor
    movie_comments_count = defaultdict(int) 

    for index, movie in data.iterrows():
        for actor in movie['casts'].split(';'):
            movie_comments[movie['name']][actor] = []
    comments = json.load(codecs.open(comments_path, 'r', 'utf-8'))
    for comment in comments:
        flag = True
        name = comment['movieName']
        content = comment.get('content', '')
        score = comment['score']
        for actor in movie_comments[name].keys():
            if actor in content:
                flag = False
                movie_comments[name][actor].append(score)
        if flag:
            movie_comments_count[name] += 1
    return movie_comments, movie_comments_count        

def extract_features(data, movie_comments, counts, output_file=training_path):
    """
    """
    scores = ['score.douban', 'score.gewara', 'score.imdb', 'score.maoyan', 'score.mtime', \
    'score.nuomi', 'score.taobao', 'score.weibo', 'score.wepiao']
    features = []
    for index, movie in data.iterrows():
        count = counts[movie['name']]
        box = movie['box']
        feature = [movie[i] * count for i in scores]
        total = 0
        for actor in movie_comments[movie['name']]:
            total += sum(movie_comments[movie['name']][actor])
        feature.append(total)
        features.append(str(box) + ' ' + ' '.join([str(i) + ':' + str(feature[i]) for i in range(len(feature))]))
    with open(output_file, 'w') as f:
        f.write('\n'.join(features))

def train(data_path=training_path):
    X, y = load_svmlight_file(training_path)
    X = X.toarray()
    reg = NNLS()
    reg.fit(X, y)
    return (reg.coef_, reg.intercept_)

def estimate_actor_influence(movie_comments, coef, intercept, movie_box):
    """
    movie_comments 
    coef - the coef of model.coef_[-1] - the box office related with casts
    intercept - model.intercept_
    movie_box - dict of {'movie name': box office; ...}
    """
    box_influence = defaultdict(dict)

    for movie in movie_comments:
        for actor in movie_comments[movie]:
            box_influence[movie][actor] = (movie_box[movie] / (movie_box[movie] - intercept)) * coef * sum(movie_comments[movie][actor])
    return box_influence

