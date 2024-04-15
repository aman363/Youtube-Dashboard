#!/usr/bin/python3
import math
import os
import re
import subprocess
import sys
from io import BytesIO
from shutil import which
import calmap
import datetime,time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import pylab as pl
from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph
from wordcloud import WordCloud
from parse import HTML
from googleapiclient.discovery import build
from urllib.request import build_opener
from urllib.error import HTTPError
from urllib.parse import urlencode,quote_plus
import json
from matplotlib.font_manager import FontProperties


__version__ = "0.5.5"
__author__ = "np1"
__license__ = "LGPLv3"


# youtube api
with open('key.txt', "r", encoding="utf-8") as f:
    api_key = f.read()
pfx =  "https://www.googleapis.com/youtube/v3/"
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
opener = build_opener()
opener.addheaders = [('User-Agent', user_agent)]

### 时间格式化函数
def time_format(str):
    num_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    str = str.replace('Sept', 'Sep')
    if str[-5] == 'M' and str[0] not in num_list:
        str = str[:-4]
        date = datetime.datetime.strptime(str, "%b %d, %Y, %I:%M:%S %p")
        date_string = date.strftime("%Y-%m-%d %H:%M:%S")
        str = date_string

    elif str[-5] != 'M' and str[0] not in num_list:
        str = str[:-4]
        date = datetime.datetime.strptime(str, "%b %d %Y, %H:%M:%S")
        date_string = date.strftime("%Y-%m-%d %H:%M:%S")
        str = date_string

    elif str[-5] == 'M' and str[0] in num_list:
        str = str[:-4]
        date = datetime.datetime.strptime(str, "%d %b, %Y, %I:%M:%S %p")
        date_string = date.strftime("%Y-%m-%d %H:%M:%S")
        str = date_string

    elif str[-5] != 'M' and str[0] in num_list:
        str = str[:-4]
        date = datetime.datetime.strptime(str, "%d %b %Y, %H:%M:%S")
        date_string = date.strftime("%Y-%m-%d %H:%M:%S")
        str = date_string

    return str
### YouTube api请求函数
def call_gdata(api, qs):
    """Make a request to the youtube api."""
    qs = dict(qs)
    qs['key'] = api_key
    url = pfx + api + '?' + urlencode(qs, safe = ',')
    url = url.replace('%2C',',')
    try:
        data = opener.open(url).read().decode('utf-8')
    except HTTPError as e:
        try:
            errdata = e.text.read().decode()
            error = json.loads(errdata)['error']['message']
            errmsg = 'Youtube Error %d: %s' % (e.getcode(), error)
        except:
            errmsg = str(e)
    dataz = json.loads(data)
    return url,dataz
### YouTube 分类id转名字
indict = {
    1:'Film & Animation',
    2:'Autos & Vehicles',
    10:'Music',
    15:'Pets & Animals',
    17:'Sports',
    18:'Short Movies',
    19:'Travel & Events',
    20:'Gaming',
    21:'Videoblogging',
    22:'People & Blogs',
    23:'Comedy',
    24:'Entertainment',
    25:'News & Politics',
    26:'Howto & Style',
    27:'Education',
    28:'Science & Technology',
    29:'Nonprofits & Activism',
    30:'Movies',
    31:'Anime / Animation',
    32:'Action / Adventure',
    33:'Classics',
    34:'Comedy',
    35:'Documentary',
    36:'Drama',
    37:'Family',
    38:'Foreign',
    39:'Horror',
    40:'Sci - Fi / Fantasy',
    41:'Thriller',
    42:'Shorts',
    43:'Shows',
    44:'Trailers'
    }
def id_name(id):
    switcher = indict
    return switcher.get(id)

### 处理&打开文件
image_dir = os.path.join(os.getcwd(),"Images/")
logo = os.path.join(image_dir,"LOGO.png")
csv_dir = os.getcwd()+'/csv_file/'
if not os.path.exists(csv_dir):
    os.mkdir(csv_dir)


### 实例化parse中的各个函数
urls_id = HTML().find_video_id()
channel_link = HTML().find_channel_link()
channel_title = HTML().find_channel_title()
video_title = HTML().find_video_title()
date_time = HTML().find_date_time()


### 第一张热力图（github版）
df_urls_id = pd.DataFrame(urls_id)
df_video_title = pd.DataFrame(video_title)
df_channel_link = pd.DataFrame(channel_link)
df_channel_title = pd.DataFrame(channel_title)
dftime = pd.DataFrame(date_time)
url_list = df_urls_id.iloc[:,0].tolist()
links_list = []
for i in url_list:
    i = 'https://www.youtube.com/watch?v='+i
    links_list.append(i)
df_urls_id['video_link'] = links_list
df_urls_id = df_urls_id.rename(columns={0: "video_id"})
dftime.columns =['watch_time']
time_list = []
for i in dftime['watch_time']:
    i = time_format(i)
    time_list.append(i)
dftime['watch_time'] = time_list
time_day_list = []
for i in dftime['watch_time']:
    match = re.match(r"\d{4}\-\d{2}\-\d{2}", i)
    i = match.group()
    time_day_list.append(i)
dftime['watch_time_day'] = time_day_list
df_new = pd.DataFrame(dftime.groupby("watch_time_day").size()).reset_index()
df_new.columns=['watch_time','values']
active_day = df_new['watch_time'].count()
watch_time = []
for i in df_new['watch_time']:
    watch_time.append(i)
values = []
for i in df_new['values']:
    values.append(i)
ts = pd.Series(values, index=pd.DatetimeIndex(watch_time))
plt.figure(figsize=(20,10))
calmap.yearplot(ts, cmap='YlGn', fillcolor='lightgrey',daylabels='MTWTFSS',dayticks=[0, 2, 4, 6],
                linewidth=2)
plt.savefig(os.path.join(image_dir,"heatmap.png"))




### BASIC
if(len(channel_link)==0):
    raise ValueError("Could not find any links. Please send the developer your takeout data, so the issue can be addressed")

## 实例化search
df_searches = HTML().search_history()
for i,j in df_searches['DATE_TIME'].items():
    ## 时间格式化
    k = time_format(j)
    df_searches.loc[i,'DATE_TIME'] = k
## 过滤非2022年数据
df_searches_yr = df_searches[df_searches['DATE_TIME'].str.contains('2022')]

## 实例化search
try:
    df_comments = HTML().comment_history()
except TypeError:
    all_links = ""
## 过滤非2022年数据
df_comments_yr = df_comments[df_comments['DATE_TIME'].str.contains('2022')]

## 实例化like
try:
    df_likes = HTML().like_history()
except FileNotFoundError:
    df_likes = ""
## 过滤非2022年数据
df_likes_yr = df_likes[df_likes['liked_time'].str.contains('2022')]



### 观看数
watched_video = len(urls_id)
### 搜索数
searches_yr = df_searches_yr['SEARCHES'].count()
### 点赞数
likes_yr = df_likes_yr['liked_video_id'].count()
### 评论数
comments_yr = df_comments_yr['COMMENTS'].count()
### 活跃天数
active_total_day = str(active_day) + '/' + '365'
### 全年活跃占比
UpTime = '{:.2%}'.format(active_day/365)
vpd ='{:.2f}'.format(watched_video/365)
## csv相关
stat_list_yr = [watched_video,searches_yr,likes_yr,comments_yr,active_total_day,UpTime,vpd]
dfstat_yr = pd.DataFrame(stat_list_yr).T
dfstat_yr.columns=['watched','searches','likes','comments','active_total_day','UpTime','video_watched_per_day']
## csv相关

### TOP5_WATCH
url_sizes = df_urls_id.groupby("video_id").size()
sorted_watch = dict(url_sizes.sort_values(ascending=False))
## csv相关
df_sorted_watch = pd.DataFrame(sorted_watch,index =[0]).T
df_sorted_watch.reset_index(inplace=True)
df_sorted_watch.columns = ['video_id','watch_time']
df_top5 = pd.DataFrame({'watch_time_rank':[0],'video_id':[0],'video_link':[0],'watch_times':[0]})
for i in range(5):
    list_top5 = ['TOP'+str(i+1),df_sorted_watch.iloc[i,0],
                 'https://www.youtube.com/watch?v='+str(df_sorted_watch.iloc[i,0]),df_sorted_watch.iloc[i,1]]
    df_top5.loc[i,:] = list_top5
    # df.to_csv('watch_top5.csv', mode='a',encoding='utf_8_sig', header=True, index=True)
df_top5.to_csv(csv_dir + 'TOP5_watch.csv', encoding='utf_8_sig', index = False)
dftime.columns=['watch_time','watch_time_day']
## csv相关

### 下面都是导出csv
df = pd.concat([df_video_title,df_urls_id,df_channel_link,df_channel_title,dftime,df_searches,df_likes,df_comments],axis=1)
df.columns=['video_title','video_id','video_link','channel_link','df_channel_title','watch_time','time_day',
            'searches','searches_link','search_time','liked_video_id','liked_video_link','liked_time','comments',
            'comment_time']
df.drop(['time_day'],axis=1,inplace=True)
df_yr = pd.concat([df_video_title,df_urls_id,df_channel_link,df_channel_title,dftime,df_searches_yr,df_likes_yr,
                   df_comments_yr],axis=1)
df_yr.columns=['video_title','video_id','video_link','channel_link','channel_title','watch_time','time_day',
               'searches','searches_link','search_time','liked_video_id','liked_video_link','liked_time','comments',
               'comment_time']
df_yr.drop(['time_day'],axis=1,inplace=True)
### 上面都是导出csv


## YouTube v3 api请求
df_yr_dlc = pd.DataFrame({'publishedAt':0,'title':0,'categoryId':0,'defaultAudioLanguage':0,'duration':0,'licensedContent':0,
                          'viewCount':0, 'likeCount':0, 'commentCount':0,},index=[0])

ids = dict(df_yr['video_id'])
for i,j in ids.items():
    print(i)
    print(j)
    # if i > 13:
    #     break
    # else:
    query = {'id': j,
            'part': 'snippet,contentDetails'}
    catchinfo = call_gdata('videos', query)[1]
    ### 要用的只有categoryId/defaultAudioLanguage/duration
    for item in catchinfo.get('items', []):
                    s1 = item.get('snippet', {})
                    s1_names = ['publishedAt', 'title', 'categoryId', 'defaultAudioLanguage']  # 'tags','description'
                    s1_ = {key: value for key, value in s1.items() if key in s1_names}
                    for k in s1_names:
                        if s1.get(k) != None:
                            continue
                        else:
                            s1_[k] = 'N/A'
                    ## 将带有zh、en的字符串转化zh、en
                    p1 = re.compile(r'zh.*')
                    p2 = re.compile(r'en.*')
                    if p1.search(s1_['defaultAudioLanguage']):
                        s1_['defaultAudioLanguage'] = 'cn'
                    elif p2.search(s1_['defaultAudioLanguage']):
                        s1_['defaultAudioLanguage'] = 'en'
                    ## 将带有zh、en的字符串转化zh、en
                    ## 获取duration
                    s2 = item.get('contentDetails', {})
                    s2_names = ['duration', 'licensedContent']
                    s2_ = {key: value for key, value in s2.items() if key in s2_names}
                    sz = {}
                    sz.update(s1_)
                    sz.update(s2_)
                    dataz = list(sz.values())
                    df_yr_dlc.loc[i, :] = dataz
### 将duration数据转为00:00:00格式
for i,j in df_yr_dlc['duration'].items():
    hours_pattern = re.compile(r'(\d+)H')
    minutes_pattern = re.compile(r'(\d+)M')
    seconds_pattern = re.compile(r'(\d+)S')
    hours = hours_pattern.search(j)
    minutes = minutes_pattern.search(j)
    seconds = seconds_pattern.search(j)
    hours = int(hours.group(1)) if hours else 0
    minutes = int(minutes.group(1)) if minutes else 0
    seconds = int(seconds.group(1)) if seconds else 0
    s = f'{hours}:{minutes}:{seconds}'
    df_yr_dlc.loc[i,'duration'] = s

df_yr_dlc = df_yr_dlc.reindex(columns=['title','publishedAt','categoryId','duration','licensedContent',
                          'viewCount', 'likeCount', 'commentCount','defaultAudioLanguage'])

### 下面都是导出csv
df.to_csv(csv_dir+'info_total.csv',encoding='utf_8_sig',header = True,index=True)
df_yr.to_csv(csv_dir+'info_yr.csv',encoding='utf_8_sig',header = True,index=True)
df_yr_dlc.to_csv(csv_dir+'info_yr_dlc.csv',encoding='utf_8_sig',header = True,index=True)
dfstat_yr.to_csv(csv_dir+'info_misc_yr.csv',encoding='utf_8_sig',header = True,index=True)
### 上面都是导出csv


### 下面所有处理都是以df_yr_dlc为

## language
df_lang = pd.DataFrame(dict(df_yr_dlc['defaultAudioLanguage'].value_counts(ascending=False)),index =[0]).T
df_lang.reset_index(inplace=True)
df_lang.columns = ['language','lanCounts']
df_lang.drop(df_lang[df_lang['language']=='N/A'].index,inplace=True)
# csv相关
other = 0
if len(df_lang) < 3:
    df_lang = df_lang.sort_index().reset_index(drop=True)
    df_lang['lanCounts'] = df_lang['lanCounts'].apply(int)
else:
    for i,j in df_lang['lanCounts'].items():
        if i < 3:
            continue
        else:
          other += j
    df_lang.loc[3.5, :] = ['other', other]
    df_lang = df_lang.sort_index().reset_index(drop=True)
    df_lang['lanCounts'] = df_lang['lanCounts'].apply(int)
# csv相关


### categoryName & ~watchTime/~watchTime_min
df_api_dlc = df_yr_dlc.copy(deep=False)
df_api_dlc.insert(3,'categoryName',value ='NaN')
for i,j in df_api_dlc['categoryId'].items():
    k = id_name(int(j))
    df_api_dlc.loc[i,'categoryName'] = k


## categoryWatchTimes
# insert a new columns 'duration in seconds'
df_api_dlc.insert(5,'durations',value ='NaN')
# 转化为秒数计和
for i,j in df_api_dlc['duration'].items():
    j = str(j)
    p = re.compile(r'(\d+):(\d+):(\d+)')
    s = p.search(j)
    h = int(s.group(1))
    m = int(s.group(2))
    s = int(s.group(3))
    total = h*60 + m*60 + s
    df_api_dlc.loc[i,'durations'] = total
df_catSize= pd.DataFrame(df_api_dlc["categoryName"].value_counts())
df_catSize.reset_index(inplace=True)
df_catSize.columns=['categoryName','watchTimes1']

## 类别观看时长（in minutes）
dict_catDu = {}
for i in indict.keys():
    if i==0:
        continue
    dfid = df_api_dlc[df_api_dlc['categoryId'] == str(i)]
    # print(dfid['durations'])
    dict_catDu[id_name(i)] = dfid['durations'].sum() * 0.34
df_catDu = pd.DataFrame(dict_catDu,index=[0]).T
df_catDu.reset_index(inplace=True)
df_catDu.columns=['categoryName','watchTime_min']
for i,j in df_catDu['watchTime_min'].items():
    df_catDu.iloc[i,1] = '{:.2f}'.format(j/60)
    df_catDu.iloc[i, 1] = float(df_catDu.iloc[i, 1])
df_catDu.sort_values(['watchTime_min'],ascending=False,inplace=True)
df_catDu.reset_index(inplace=True,drop=True)
df_cat = pd.concat([df_catSize,df_catDu],axis=1)


### 频道观看次数
df_chnlSize = pd.DataFrame(df_yr["channel_title"].value_counts())
df_chnlSize.reset_index(inplace=True)
## csv相关
df_chnlSize.columns=['channelTitle','watchTimes2']
df_chnlSize.insert(2,'channelLink',value ='NaN')
for i,j in df_chnlSize['channelTitle'].items():
      dictz=dict(df_yr.loc[df_yr['channel_title']==j,'channel_link'])
      chnlLink = dictz.get(int(next(iter(dictz))))
      df_chnlSize.loc[i, 'channelLink'] = chnlLink
dfz = pd.concat([df_cat,df_chnlSize,df_lang],axis=1)
dfz = dfz.fillna('')
dfz.to_csv(csv_dir+'api_rep.csv',encoding='utf_8_sig')
## csv相关