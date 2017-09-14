
# coding: utf-8


import os
import json
import codecs
import pandas as pd
import data_io as di
from scattertext import chinese_nlp
from scattertext import CorpusFromParsedDocuments
from scattertext import produce_scattertext_explorer
from IPython.display import IFrame
from IPython.core.display import display, HTML
display(HTML("<style>.container {width:98% !important;}</style>"))



# 由于相比于ipython，notebook在处理大量数据时容易假死，这里为了方便演示，我在代码中设置了如果有处理好的数据文件就直接读入。



raw_comment_path = './data/raw_comment.json'
movie_info_path = './data/movie_info.csv'
comments_dataframe_path = './data/comment_dataframe.csv'
comments_after_clean = './data/fine_comment.csv'
html_file = './output/影片质量-评论分析.html'


# 读取电影基本数据，将其按照豆瓣评分分类，大于7.5分的归类为**好片**，低于5分的归为**烂片**。


movie_info = pd.read_csv(movie_info_path)
good = set()
bad = set()
for i, r in movie_info.iterrows():
    if r['score.douban'] >= 7.5:
        good.add(r['name'])
    if r['score.douban'] <= 5:
        bad.add(r['name'])
print(good, bad)


# 下面我们将原始评论数据读入，筛出对上面好片和烂片的评论并提取它们的作者，文本内容和情感分数信息。
# 缺失的评论数据用‘’补全，
# 处理完成的数据存到本地。


comments = di.read_multi_json(raw_comment_path)
comments_dataframe = pd.DataFrame(columns=['Cate', 'Auther', 'Text','Score'])
for i in range(len(comments)):
    m_name = comments[i]['movieName']
    if m_name in good:
        cate = 'good'
    elif m_name in bad:
        cate = 'bad'
    else:
        continue
    comments_dataframe.loc[i] = [cate, comments[i]['user'].get('displayName', ''), comments[i].get('content', ''), comments[i]['score'] ]
comments_dataframe['text'].fillna('', inplace=True)
comments_dataframe.to_csv('./data/comments_dataframe.csv', index=False)



# 去除停用词，除了常见停用词外，这里我们把片名/演员名/角色名的分词结果也当做停用词。

def remove_stop_words(text):
    text = str(text)
    stop_words = '的 了 的 吗 啊 # [ ] 。 ，2017 三生 三世 十里 桃花 战狼 绣春刀 修罗 战场 \
    京城 81 逆时 营救 建军 大业 大闹 天竺 沈炼 裴纶 叶挺 达康 达康书记 崇祯 王宝强 杨幂 吴京 \
    弗兰克·格里罗 吴刚 成龙 李治廷 张艺兴 吴亦凡 林更新 姚晨 白客 岳云鹏 彭于晏 倪妮 余文乐 \
    尚雯婕 鲍春来 孙建弘 刘亦菲 杨洋 罗晋 刘德华 姜武 宋佳 刘烨 朱亚文 黄志忠 王景春 欧豪 \
    黄渤 段奕宏 徐静蕾 张震 张译 王凯 张鲁一 林心如 张智霖 梅婷 钟欣潼 金城武 周冬雨 孙艺洲 \
    霍建华 金士杰 余文乐 杨千嬅 蒋梦婕 夜华 冷锋 魏忠贤 信王'.split(' ')
    for i in stop_words:
        text = text.replace(i, ' ')
    return text

comments_dataframe['Text'] = comments_dataframe.apply(lambda row: remove_stop_words(row['Text']), axis=1)
comments_dataframe['Text'] = comments_dataframe['Text'].apply(chinese_nlp)
    




courpus = CorpusFromParsedDocuments(comments_dataframe, category_col='Cate', parsed_col='Text').build()
html = produce_scattertext_explorer(corpus,
                                    category='good',
                                    category_name='好片',
                                    not_category_name='烂片',
                                    width_in_pixels=1000,
                                    jitter=0.1,
                                    minimum_term_frquency=100,
                                    metadata=comments_dataframe['Author'],
                                    asian_mode=True)
codecs.open(html_file, 'wb').write(html.encode('utf-8'))
IFrame(src=html_file, width=1200, height=700)

