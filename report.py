#!/usr/bin/python3
# coding=utf-8
from flask import Flask, send_file
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
from distlib.compat import raw_input
from matplotlib import pylab as pl
from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph
from wordcloud import WordCloud
from urllib.request import build_opener
from urllib.error import HTTPError
from urllib.parse import urlencode,quote_plus
import json
import datetime, pytz
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

__version__ = "0.5.5"
__author__ = "np1"
__license__ = "LGPLv3"

t1 = datetime.datetime.now()
print("start >> {}".format(t1))
year = str(time.strftime('%Y', time.localtime()))
month = str(time.strftime('%m', time.localtime()))
day = str(time.strftime('%d', time.localtime()))

missing = []
dir = os.path.join(os.getcwd(), "Takeout/YouTube and YouTube Music/")
if not os.path.exists(dir):
    missing.append(dir)
found = False
for path in ("Verlauf/Wiedergabeverlauf.html", "history/watch-history.html"):
    watch_history = os.path.join(dir, path)
    if os.path.exists(watch_history):
        found = True
        break
if not found:
    missing.append(watch_history)
found = False
for path in ("Verlauf/Suchverlauf.html", "history/search-history.html"):
    search_history = os.path.join(dir, path)
    if os.path.exists(search_history):
        found = True
        break
if not found:
    missing.append(search_history)
found = False
for path in ("Meine Kommentare/Meine Kommentare.html", "my-comments/my-comments.html"):
    comments_history = os.path.join(dir, path)
    if os.path.exists(comments_history):
        found = True
        break
if not found:
    missing.append(comments_history)
found = False
playlists_path = os.path.join(dir, 'playlists')

for path in ("Playlists/Positive Bewertungen.json", "playlists/Liked videos.csv"):
    like_history = os.path.join(dir, path)
    if os.path.exists(like_history):
        found = True
        break
if not found:
    missing.append(like_history)
del found
if len(missing) > 0:
    raise OSError("Required directories do not exist: %s" % (missing))
del missing

class HTML:
    with open(watch_history, "r", encoding="utf-8") as f:
        html_watch = f.read()
    with open(search_history, "r", encoding="utf-8") as f:
        html_search = f.read()
    try:
        with open(comments_history, "r", encoding="utf-8") as f:
            html_comment = f.read()
    except Exception:
        print("Could not parse comments.")

    # 下面的watch history的title/time可与video_id一并写入一个函数，从而直接输出三列的df而无需在report中分别再处理它们
    def find_video_id(self):
        video_id = []
        pattern = re.compile(
            r"""Watched\xa0<a href=\".[^v]*v=(.[^\"]*)\">.[^<]*<\/a><br><a href=\".[^\"]*\">.[^<]*<\/a>""")
        matchList = pattern.findall(str(self.html_watch))
        for match in matchList:
            if type(match) == str:
                video_id.append(match)
        return video_id
        links2 = []
        for i in video_id:
            if '</a>' in i:
                p = re.compile(r"""(.*)<\/a>""")  # (.[^ <] *)
                j = p.findall(str(i))
                # return i
                # links2.append(j)
                # return j
            else:
                links2.append(i)
        return links2

    def find_video_title(self):
        video_title = []
        pattern = re.compile(r"""Watched\xa0<a href=\".[^\"]*\">(.[^<]*)<\/a><br><a href=\".[^\"]*\">.[^<]*<\/a>""")
        matchList = pattern.findall(str(self.html_watch))
        for match in matchList:
            if type(match) == str:
                video_title.append(match)
        return video_title

    def find_date_time(self):
        # search all links based on your personal html file
        date_time = []
        pattern = re.compile(
            r"""Watched\xa0<a href=\".[^\"]*\">.[^<]*<\/a><br><a href=\".[^\"]*\">.[^<]*<\/a><br>(\w{1,3}\s.*?)<\/div>""")
        matchList = pattern.findall(str(self.html_watch))
        for match in matchList:
            if type(match) == str:
                date_time.append(match)
        return date_time

    def find_channel_link(self):
        channel_link = []
        pattern = re.compile(r"""Watched\xa0<a href=\".*?\">.*?<\/a><br><a href=\"(.*?)\">.*?<\/a>""")
        matchList = pattern.findall(str(self.html_watch))
        for match in matchList:
            if type(match) == str:
                channel_link.append(match)
        return channel_link

    def find_channel_title(self):
        channel_title = []
        pattern = re.compile(r"""Watched\xa0<a href=\".*?\">.*?<\/a><br><a href=\".*?\">(.*?)<\/a>""")
        matchList = pattern.findall(str(self.html_watch))
        for match in matchList:
            if type(match) == str:
                channel_title.append(match)
        return channel_title

    # def raw_find_links(self,translation):
    def raw_find_times(self):
        regex0 = r"<\/a><br><a href=.*?<.*?<.*?>.*?<\/div>"
        regex1 = [r"<\/a><br><a href=.*?<.*?<.*?>([A-Z][a-z]{2,3}\s\d\d?.*?)<\/div>", '%b %d %Y %I:%M:%S %p']
        regex2 = [r"<\/a><br><a href=.*?<.*?<.*?>(\d\d?\s[A-Z][a-z]{2,3}.*?)<\/div>", '%d %b %Y %H:%M:%S']
        pattern0 = re.compile(regex0)
        pattern1 = re.compile(regex1[0])
        pattern2 = re.compile(regex2[0])
        raw_matchlist = pattern0.findall(str(self.html_watch))
        raw_matchlist_element = raw_matchlist[0]
        # return raw_matchlist_element
        is_regex1 = True
        testlist = pattern1.findall(str(raw_matchlist_element))
        # return matchList
        if len(testlist) != 0:
            matchList = pattern1.findall(str(raw_matchlist))
            times1 = []
            for time in matchList:
                if type(time) != str:
                    time = ' '.join(time)
                time = time.replace(',', '')
                time = time.replace('Sept', 'Sep')
                times1.append(time)
                # return times1
            times2 = []
            for i in times1:
                i = re.sub(r'.{3}$', 'UTC', i)
                i = i.split()
                tz = ''.join(i[-1])
                timez = ' '.join(i[:-1])
                timez_cleaned = timez.replace('\\u202f', '')
                timez_corrected = timez_cleaned[:-2] + ' ' + timez[-2:]
                # return tz
                if is_regex1:
                    date_time_time = datetime.datetime.strptime(timez_corrected, regex1[1])
                else:
                    date_time_time = datetime.datetime.strptime(timez_corrected, regex2[1])
                times2.append(pytz.timezone(tz).localize(date_time_time))
            # return is_regex1
            return times2
        else:
            is_regex1 = False
            matchList = pattern2.findall(str(raw_matchlist))
            times1 = []
            for time in matchList:
                if type(time) != str:
                    time = ' '.join(time)
                time = time.replace(',', '')
                time = time.replace('Sept', 'Sep')
                times1.append(time)
                # return times1
            times2 = []
            for i in times1:
                i = re.sub(r'.{3}$', 'UTC', i)
                i = i.split()
                tz = ''.join(i[-1])
                timez = ' '.join(i[:-1])
                # return tz
                if is_regex1:
                    date_time_time = datetime.datetime.strptime(timez, regex1[1])
                else:
                    date_time_time = datetime.datetime.strptime(timez, regex2[1])
                times2.append(pytz.timezone(tz).localize(date_time_time))
            # return is_regex1
            return times2

    # def _find_times(self):
    #     """
    #     Find and format times within the HTML file.
    #
    #     Returns
    #     -------
    #     times : List[str]
    #         e.g. "19 Feb 2013, 11:56:19 UTC Tue"
    #     """
    #     # Format all matched dates
    #     times = [
    #         datetime_obj.strftime("%d %b %Y, %H:%M:%S UTC %a")
    #         for datetime_obj in self._find_times_datetime()
    #     ]
    #     return times

    def search_history(self):
        pattern1 = re.compile(r"""Searched for\xa0<a href=\"(.*?\?search_query=.*?)\"\>(.*?)<\/a><br>(.*?)<""")
        raw_data = pattern1.findall(HTML.html_search)
        search_list = []
        search_link_list = []
        time_list = []
        for i in raw_data:
            search_link_list.append(i[0])
            search_list.append(i[1])
            time_list.append(i[2])
        # return search_link_list
        df0 = pd.DataFrame(search_link_list)
        df1 = pd.DataFrame(search_list)
        df2 = pd.DataFrame(time_list)
        df_searches = pd.concat([df1, df0, df2], axis=1)
        df_searches.columns = ['SEARCHES', 'SEARCHES_LINK', 'DATE_TIME']
        return df_searches

    def comment_history(self):
        try:
            # regex = r'(?<="\s+at\s+{yyyy}-{mm}-{dd}\s+{hh}:{mm}:{ss}\s+UTC\.\s+")\S+(?=")'
            # r"<a href=\".*\">[^<]*<\/a>\"([^\"]*)\"<br>"
            # r"<a href=\".*\">[^<]*<\/a>\"([^\"]*)\"<br>"
            pattern1 = re.compile(r"""<a href=['"].*?['"]>""")
            match_list1 = pattern1.findall(str(HTML.html_comment))
            pattern2 = re.compile(r"""at\s(.*?\s.[^\s]*).*?<br\/>(.*?)<\/li>""")
            match_list2 = pattern2.findall(str(HTML.html_comment))
            comments_list = []
            time_list = []
            for i in match_list2:
                time_list.append(i[0])
                comments_list.append(i[1])
            df1 = pd.DataFrame(comments_list)
            df2 = pd.DataFrame(time_list)
            df_comments = pd.concat([df1, df2], axis=1)
            df_comments.columns = ['COMMENTS', 'DATE_TIME']
            link = match_list1[-1][9:-2]
            return df_comments  # match_list1, match_list2
        except Exception:
            pass

    '''def like_history(self):
        df_likes = pd.read_csv(playlists_path + '/' + 'Liked videos.csv', encoding="utf_8_sig")
        # df = pd.DataFrame(f)
        df_likes.drop([0, 1], axis=0, inplace=True)
        df_likes.drop(df_likes.iloc[:, 2:], axis=1, inplace=True)
        df_likes.columns = ['liked_video_id', 'liked_time']
        df_likes.reset_index(inplace=True, drop=True)
        liked_video_url = []
        for i in df_likes['liked_video_id']:
            i = "https://www.youtube.com/watch?v=" + str(i)
            liked_video_url.append(i)
        df_likes['liked_video_url'] = liked_video_url
        liked_time = []
        for i in df_likes['liked_time']:
            i = i[:-4]
            liked_time.append(i)
        df_likes['liked_time'] = liked_time
        df_likes = df_likes.reindex(columns=["liked_video_id", 'liked_video_url', "liked_time"])
        return df_likes'''

    def dataframe_heatmap(self, day):
        times = self.raw_find_times()
        watchtimes = [0 for t in range(12)]

        for time in times:
            if time.weekday() == day:
                watchtimes[(time.hour // 2) - time.hour % 2] += 1

        return watchtimes
# print((HTML().html_watch))
# print(len((HTML().find_video_id())))
# print(HTML().raw_find_times())
# print(HTML().search_history())


# youtube api
with open('key.txt', "r", encoding="utf-8") as f:
    api_key = f.read()
pfx =  "https://www.googleapis.com/youtube/v3/"
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
opener = build_opener()
opener.addheaders = [('User-Agent', user_agent)]
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
    # return (data)
    dataz = json.loads(data)
    return url,dataz


image_dir = os.path.join(os.getcwd(),"Images/")
logo = os.path.join(image_dir,"LOGO.png")
csv_dir = os.getcwd()+'/csv_file/'
if not os.path.exists(csv_dir):
    os.mkdir(csv_dir)


def time_format(str):
    num_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    str = str.replace('Sept', 'Sep')
    # print(i[0])
    # print(i[0] in num_list)
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


### watch_rel
urls_id = HTML().find_video_id()
channel_link = HTML().find_channel_link()
channel_title = HTML().find_channel_title()
video_title = HTML().find_video_title()
date_time = HTML().find_date_time()

### heatmap_github
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
# print(dfid)
dftime.columns =['watch_time']
time_list = []
for i in dftime['watch_time']:
    # print(i)
    i = time_format(i)
    time_list.append(i)
dftime['watch_time'] = time_list
# print(dftime)
# print(type(dftime['time']))
time_day_list = []
for i in dftime['watch_time']:
    match = re.match(r"\d{4}\-\d{2}\-\d{2}", i)
    i = match.group()
    time_day_list.append(i)
    # print(list)
    # print(i)
dftime['watch_time_day'] = time_day_list
df_new = pd.DataFrame(dftime.groupby("watch_time_day").size()).reset_index()
df_new.columns=['watch_time','values']
active_day = df_new['watch_time'].count()
# print(df_new['watch_time'].count())
watch_time = []
for i in df_new['watch_time']:
    watch_time.append(i)
# print(watch_time)
values = []
for i in df_new['values']:
    values.append(i)
# print(values)
ts = pd.Series(values, index=pd.DatetimeIndex(watch_time))
# print(ts)
plt.figure(figsize=(20,10))
calmap.yearplot(ts, cmap='YlGn', fillcolor='lightgrey',daylabels='MTWTFSS',dayticks=[0, 2, 4, 6],
                linewidth=2)
plt.savefig(os.path.join(image_dir,"heatmap.png"))


### BASIC
if(len(channel_link)==0):
    raise ValueError("Could not find any links. Please send the developer your takeout data, so the issue can be addressed")
df_searches = HTML().search_history()
HTML().search_history()
for i,j in df_searches['DATE_TIME'].items():
    k = time_format(j)
    df_searches.loc[i,'DATE_TIME'] = k
df_searches_yr = df_searches[df_searches['DATE_TIME'].str.contains('2024')]
# print(df_searches)
# print(type(df_searches['SEARCHES']))
try:
    df_comments = HTML().comment_history()
except TypeError:
    all_links = ""
df_comments_yr = 0
# print(df_comments_yr)
try:
    df_likes = 0
except FileNotFoundError:
    df_likes = ""
# print(df_likes['liked_time'])
df_likes_yr = 0

#
watched_video = len(urls_id)
searches = df_searches['SEARCHES'].count()
likes = 0
comments = 0

searches_yr = df_searches_yr['SEARCHES'].count()
likes_yr = 0
comments_yr = 0
active_total_day = str(active_day)
UpTime = '{:.2%}'.format(active_day/365)
vpd ='{:.2f}'.format(watched_video/active_day)

stat_list = [watched_video,searches,likes,comments,active_total_day,UpTime,vpd]
dfstat = pd.DataFrame(stat_list).T
dfstat.columns=['watched','searches','likes','comments','active_total_day','UpTime','video_watched_per_day']
stat_list_yr = [watched_video,searches_yr,likes_yr,comments_yr,active_total_day,UpTime,vpd]
dfstat_yr = pd.DataFrame(stat_list_yr).T
dfstat_yr.columns=['watched','searches','likes','comments','active_total_day','UpTime','video_watched_per_day']
# print(dfstat)

### TOP5_WATCH
url_sizes = df_urls_id.groupby("video_id").size()
sorted_watch = dict(url_sizes.sort_values(ascending=False))
df_sorted_watch = pd.DataFrame(sorted_watch,index =[0]).T
df_sorted_watch.reset_index(inplace=True)
df_sorted_watch.columns = ['video_id','watch_time']
# print(df_sorted_watch)
df_top5 = pd.DataFrame({'watch_time_rank':[0],'video_id':[0],'video_link':[0],'watch_times':[0]})
# print(df_top5)
for i in range(5):
    list_top5 = ['TOP'+str(i+1),df_sorted_watch.iloc[i,0],
                 'https://www.youtube.com/watch?v='+str(df_sorted_watch.iloc[i,0]),df_sorted_watch.iloc[i,1]]
    df_top5.loc[i,:] = pd.Series(list_top5, index=df_top5.columns)
    # df.to_csv('watch_top5.csv', mode='a',encoding='utf_8_sig', header=True, index=True)
# print(df_top5)
df_top5.to_csv(csv_dir + 'TOP5_watch.csv', encoding='utf_8_sig', index = False)
# print(dftime)
dftime.columns=['watch_time','watch_time_day']


df = pd.concat([df_video_title,df_urls_id,df_channel_link,df_channel_title,dftime],axis=1)
df.columns=['video_title','video_id','video_link','channel_link','df_channel_title','watch_time','time_day']
df.drop(['time_day'],axis=1,inplace=True)
df_yr = pd.concat([df_video_title,df_urls_id,df_channel_link,df_channel_title,dftime],axis=1)
df_yr.columns=['video_title','video_id','video_link','channel_link','channel_title','watch_time','time_day']
df_yr.drop(['time_day'],axis=1,inplace=True)

# top 5 channels csv with video titles
video_titles = []

# Iterate over the rows of df_top5
for index, row in df_top5.iterrows():
    # Get the video_id for the current row
    video_id = row['video_id']
    
    # Look up the video title in df_video_title based on the video_id
    video_title = df[df['video_id'] == video_id]['video_title'].iloc[0]
    
    # Append the video title to the list
    video_titles.append(video_title)

# Add the list of video titles as a new column to df_top5
df_top5['video_title'] = video_titles
df_top5.to_csv(csv_dir + 'watch_top5.csv', mode='a',encoding='utf_8_sig', header=True, index=True)

## api requests
df_yr_dlc = pd.DataFrame({'publishedAt':0,'title':0,'categoryId':0,'defaultAudioLanguage':0,'duration':0,'licensedContent':0,
                          'viewCount':0, 'likeCount':0, 'commentCount':0,},index=[0])

ids = dict(df_yr['video_id'])
for i,j in ids.items():
    print(i)
    print(j)
    if i > 13:
        break
    else:
        query = {'id': j,
                'part': 'snippet,contentDetails,statistics'}
        catchinfo = call_gdata('videos', query)[1]
        for item in catchinfo.get('items', []):
                        s1 = item.get('snippet', {})
                        s1_names = ['publishedAt', 'title', 'categoryId', 'defaultAudioLanguage']  # 'tags','description'
                        s1_ = {key: value for key, value in s1.items() if key in s1_names}
                        for k in s1_names:
                            if s1.get(k) != None:
                                continue
                            else:
                                s1_[k] = 'N/A'
                        p1 = re.compile(r'zh.*')
                        p2 = re.compile(r'en.*')
                        if p1.search(s1_['defaultAudioLanguage']):
                            s1_['defaultAudioLanguage'] = 'cn'
                        elif p2.search(s1_['defaultAudioLanguage']):
                            s1_['defaultAudioLanguage'] = 'en'

                        s2 = item.get('contentDetails', {})
                        s2_names = ['duration', 'licensedContent']
                        s2_ = {key: value for key, value in s2.items() if key in s2_names}
                        s3 = item.get('statistics', {})
                        s3_names = ['viewCount', 'likeCount', 'commentCount']
                        s3_ = {key: value for key, value in s3.items() if key in s3_names}
                        for k in s3_names:
                            if s3.get(k) != None:
                                continue
                            else:
                                s3_[k] = 'N/A'
                        sz = {}
                        sz.update(s1_)
                        sz.update(s2_)
                        sz.update(s3_)
                        # dfz = pd.DataFrame(sz, index=[0])
                        # print(dfz)
                        dataz = list(sz.values())
                        # print(dataz)
                        df_yr_dlc.loc[i, :] = dataz


for i,j in df_yr_dlc['publishedAt'].items():
    j = re.sub(r'[a-z]|[A-Z]',' ',j)
    j = j.rstrip(' ')
    df_yr_dlc.loc[i,'publishedAt'] =j
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
# print(df_yr_dlc)

df.to_csv(csv_dir+'info_total.csv',encoding='utf_8_sig',header = True,index=True)
df_yr.to_csv(csv_dir+'info_yr.csv',encoding='utf_8_sig',header = True,index=True)
df_yr_dlc.to_csv(csv_dir+'info_yr_dlc.csv',encoding='utf_8_sig',header = True,index=True)
dfstat.to_csv(csv_dir+'info_misc.csv',encoding='utf_8_sig',header = True,index=True)
dfstat_yr.to_csv(csv_dir+'info_misc_yr.csv',encoding='utf_8_sig',header = True,index=True)

### df_api_dlc
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

## language
df_lang = pd.DataFrame(dict(df_yr_dlc['defaultAudioLanguage'].value_counts(ascending=False)),index =[0]).T
df_lang.reset_index(inplace=True)
df_lang.columns = ['language','lanCounts']
df_lang.drop(df_lang[df_lang['language']=='N/A'].index,inplace=True)
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
# print(df_lang)

### categoryName & ~watchTime/~watchTime_min
df_api_dlc = df_yr_dlc.copy(deep=False)
# if len(df_api_dlc['Unnamed: 0']):
#     df_api_dlc.drop(columns='Unnamed: 0',inplace=True)
df_api_dlc.insert(3,'categoryName',value ='NaN')
for i,j in df_api_dlc['categoryId'].items():
    k = id_name(int(j))
    df_api_dlc.loc[i,'categoryName'] = k


## categoryWatchTimes
# insert a new columns 'duration in seconds'
df_api_dlc.insert(5,'durations',value ='NaN')
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
# print(df_api_dlc['durations'])
print(df.columns)
## categoryWatchTime_min
dict_catDu = {}
for i in indict.keys():
    if i==0:
        continue
    dfid = df_api_dlc[df_api_dlc['categoryId'] == str(i)]
    # print(dfid['durations'])
    dict_catDu[id_name(i)] = dfid['durations'].sum() * 0.34
df_catDu = pd.DataFrame(dict_catDu,index=[0]).T
df_catDu.reset_index(inplace=True)
print(df_catDu)
df_catDu.columns=['categoryName','watchTime_min']
for i,j in df_catDu['watchTime_min'].items():
    print(df_catDu["watchTime_min"].items())
    df_catDu.iloc[i,1] = '{:.2f}'.format(j/60)
    df_catDu.iloc[i, 1] = float(df_catDu.iloc[i, 1])
df_catDu.sort_values(['watchTime_min'],ascending=False,inplace=True)
df_catDu.reset_index(inplace=True,drop=True)
cnt = 0
for i in df_catDu['watchTime_min']:
    if i:
        cnt += 1
if 1:
    list1 = []
    total = 0
    other = 0
    for j, k in df_catDu['watchTime_min'].items():
        if j < 3:
            list1.append(k)
            total += k
        else:
            list1.append(k)
            other += k
    total += other
    list1.insert(3, other)
    list2 = []
    for i, j in enumerate(list1):
        if type(j) != str:
            list2.append('{:.2f}'.format(list1[i] / total))
        else:
            list2.append(j)
    list2.pop(-1)
    df_catDu.insert(2, 'categoryRatio', value=list2)
elif cnt == 3:
    list1 = []
    total = 0
    for j, k in df_catDu['watchTime_min'].items():
            list1.append(k)
            total += k
            continue
    list2 = ['{:.2f}'.format(list1[0] / total), '{:.2f}'.format(list1[1] / total), '{:.2f}'.format(list1[2] / total)]
    df_catDu.insert(2, 'categoryRatio', value=list2)
elif cnt == 2:
    list1 = []
    total = 0
    for j, k in df['watchTime_min'].items():
            list1.append(k)
            total += k
            continue
    list2 = ['{:.2f}'.format(list1[0] / total), '{:.2f}'.format(list1[1] / total)]
    df_catDu.insert(2, 'categoryRatio', value=list2)
elif cnt == 1:
    list1 = []
    total = 0
    for j, k in df['watchTime_min'].items():
            list1.append(k)
            total += k
            continue
    list2 = ['{:.2f}'.format(list1[0] / total)]
    df_catDu.insert(2, 'categoryRatio', value=list2)
print('-----------------------xxxxxxxxx-----------------------')
print(df_catDu)
df_cat = pd.concat([df_catSize,df_catDu],axis=1)

# ### channelWatchTimes
df_chnlSize = pd.DataFrame(df_yr["channel_title"].value_counts())
df_chnlSize.reset_index(inplace=True)
df_chnlSize.columns=['channelTitle','watchTimes2']
# print(df_chnlSize)
df_chnlSize.insert(2,'channelLink',value ='NaN')
for i,j in df_chnlSize['channelTitle'].items():
      dictz=dict(df_yr.loc[df_yr['channel_title']==j,'channel_link'])
      chnlLink = dictz.get(int(next(iter(dictz))))
      df_chnlSize.loc[i, 'channelLink'] = chnlLink
# print(df_chnlSize)
dfz = pd.concat([df_cat,df_chnlSize,df_lang],axis=1)
dfz = dfz.fillna('')
dfz.to_csv(csv_dir+'api_rep.csv',encoding='utf_8_sig')


english_stopwords = [
            "i",
            "me",
            "my",
            "myself",
            "we",
            "our",
            "ours",
            "ourselves",
            "you",
            "you're",
            "you've",
            "you'll",
            "you'd",
            "your",
            "yours",
            "yourself",
            "yourselves",
            "he",
            "him",
            "his",
            "himself",
            "she",
            "she's",
            "her",
            "hers",
            "herself",
            "it",
            "it's",
            "its",
            "itself",
            "they",
            "them",
            "their",
            "theirs",
            "themselves",
            "what",
            "which",
            "who",
            "whom",
            "this",
            "that",
            "that'll",
            "these",
            "those",
            "am",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "having",
            "do",
            "does",
            "did",
            "doing",
            "a",
            "an",
            "the",
            "and",
            "but",
            "if",
            "or",
            "because",
            "as",
            "until",
            "while",
            "of",
            "at",
            "by",
            "for",
            "with",
            "about",
            "against",
            "between",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "to",
            "from",
            "up",
            "down",
            "in",
            "out",
            "on",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "any",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "s",
            "t",
            "can",
            "will",
            "just",
            "don",
            "don't",
            "should",
            "should've",
            "now",
            "d",
            "ll",
            "m",
            "o",
            "re",
            "ve",
            "y",
            "ain",
            "aren",
            "aren't",
            "couldn",
            "couldn't",
            "didn",
            "didn't",
            "doesn",
            "doesn't",
            "hadn",
            "hadn't",
            "hasn",
            "hasn't",
            "haven",
            "haven't",
            "isn",
            "isn't",
            "ma",
            "mightn",
            "mightn't",
            "mustn",
            "mustn't",
            "needn",
            "needn't",
            "shan",
            "shan't",
            "shouldn",
            "shouldn't",
            "wasn",
            "wasn't",
            "weren",
            "weren't",
            "won",
            "won't",
            "wouldn",
            "wouldn't",
            'youtube',
            'www'
        ]

import os

class Visualization:
    def generate_html_from_dataframe(self):
    # Start with the HTML content including the styling
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Times New Roman', Times, serif, sans-serif;
            margin: 0;
            padding: 0;
        }

        h1 {
            text-align: center;
            margin-top: 20px;
            
        }

        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .card {
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            padding: 5px;
            margin: 20px;
            width: 250px;
            text-align: center;
            transition: transform 0.3s ease-in-out;
        }
        .violet { background-color: #97e7e1; }
        .indigo { background-color: #97e7e1; }
        .blue { background-color: #97e7e1; }
        .green { background-color: #97e7e1; }
        .yellow { background-color: #97e7e1; }
        .orange { background-color: #ffa500; }
        .red {background-color: red}

        .card:hover {
            transform: scale(1.1);
        }
        p {
            font-size: 25px; /* Adjust the size as needed */
        }

    </style>
</head>
<body>
    <div class="container">
"""

    # Add the data categories as cards
        categories = ["watched", "searches", "likes", "active_total_day", "video_watched_per_day"]
        display_names = {
    "watched": "Watched",
    "searches": "Searches",
    "likes": "Likes",
    "comments": "Comments",
    "active_total_day": "Active Days",
    "UpTime": "Up Time",
    "video_watched_per_day": "Videos/Day"
        }
        colors = ["violet", "indigo", "blue", "green", "yellow", "orange", "red"]
        for category, color in zip(categories, colors):
            html_content += f"""
            <div class="card {color}">
                <h3>{display_names.get(category, category)}</h3>
                <p>{dfstat[category].iloc[0]}</p>
            </div>
"""

    # Complete the HTML content
        html_content += """
    </div>
</body>
</html>
"""

    # Do something with the html_content (e.g., save it to a file)
    # ...

        
        # Save the HTML content to a file
        html_file_path = os.path.join(image_dir, "header_shivalee.html")
        with open(html_file_path, "w") as html_file:
            html_file.write(html_content)


    def heat_map_week(self):
        print("Generating Heat Map.....")
        html = HTML()
        Mon = html.dataframe_heatmap(0)
        Tue = html.dataframe_heatmap(1)
        Wed = html.dataframe_heatmap(2)
        Thu = html.dataframe_heatmap(3)
        Fri = html.dataframe_heatmap(4)
        Sat = html.dataframe_heatmap(5)
        Sun = html.dataframe_heatmap(6)
        df = np.vstack((Mon, Tue, Wed, Thu, Fri, Sat, Sun))

        Index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        Cols = [
            "0",
            "2",
            "4",
            "6",
            "8",
            "10",
            "12",
            "14",
            "16",
            "18",
            "20",
            "22",
        ]

        # blue palette
#         colors = [
#     [0, 'rgb(248, 246, 227)'],
#     [0.25, 'rgb(151, 231, 225)'],
#     [0.5, 'rgb(106, 212, 221)'],
#     [1, 'rgb(122, 162, 227)']
# ]       
        # red palette
        colors = [
            [0, 'rgb(169, 68, 56)'],
            [0.25, 'rgb(210, 69, 69)'],
            [0.5,'rgb(230, 186, 163)'],
            [1, 'rgb(228, 222, 190)']
        ]
        fig = go.Figure(data=go.Heatmap(z=df, x=Cols, y=Index, colorscale=colors, text=df, hoverinfo='z'))

        fig.update_layout(
            # title="What Time Do You Usually Watch Youtube Videos?",
            # title_font_size=24,
            # title_font_color="steelblue",
            # title_font_family="Times New Roman",
            xaxis=dict(
                title="Hour of Day",
                titlefont=dict(
                color="black", size=20
            ),
            tickvals=[i-0.5 for i in range(13)], 
            tickfont=dict(color='black',size=16), 
            ticktext=[str(i * 2) for i in range(13)], 
            tickmode='array', 
            tickangle=0,
        ),
        yaxis=dict(title='Day', title_font=dict(color="black", size=20),tickfont=dict(color='black', size=16),),
       
        plot_bgcolor='white',
        paper_bgcolor='white'
        )
        fig.write_html(os.path.join(image_dir, "week_heatmap_shivalee.html"))

    
    def bar_graph_week(self):
        print("Generating Line Chart for Weekly Views.....")
        # Sample data for weekly views
        html = HTML()
        views_by_day = [
            html.dataframe_heatmap(0),
            html.dataframe_heatmap(1),
            html.dataframe_heatmap(2),
            html.dataframe_heatmap(3),
            html.dataframe_heatmap(4),
            html.dataframe_heatmap(5),
            html.dataframe_heatmap(6)
        ]
        

        # Sum the views for each day
        total_views = np.sum(views_by_day, axis=1)
        print(total_views)

        # Define weekdays
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Create line chart with shadow shading
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weekdays,
            y=total_views,
            mode='lines+markers',
            line=dict(color='#D24545', width=5),  # Adjust line color and width
            marker=dict(color='#A94438', size=10),  # Adjust marker color and size
            fill='tozeroy',
            fillcolor='#E6BAA3',  # Adjust shading color and opacity
        ))
        fig.update_layout(
            
            xaxis_title="Weekdays",
            yaxis_title="Number of Views",
            xaxis=dict(
                tickfont=dict(size=16, color="black"),  # Adjust tick font color
                title_font=dict(color="black", size= 20),        # Adjust axis title font color
            ),
            yaxis=dict(
                tickfont=dict(size=16, color="black"),  # Adjust tick font color
                title_font=dict(color="black", size= 20 ),        # Adjust axis title font color
            ),
            plot_bgcolor='white',  # Set plot background color
            paper_bgcolor='white'  # Set paper background color
        )

        # Write to HTML file
        fig.write_html(os.path.join(image_dir, "bar_graph_week_shivalee.html"))

    def word_cloud_watch(self):
        cm = HTML().find_video_title()
        if len(cm) == 0:
            unique_string = 'None'
            title = "You didn't watch any video this year"
        else:
            unique_string = (" ").join(cm)
            title = "What Do You Usually Watch on YouTube?"

        word_cloud_watch = WordCloud(
            stopwords=["amp", "quot"] + english_stopwords,
            background_color="white",
            colormap="Set2",
            max_words=380,
            contour_width=2,
            prefer_horizontal=1
        ).generate(unique_string)

        fig = px.imshow(word_cloud_watch)
        fig.update_layout(
            title=title,
            title_font_size=24,
            title_font_color="steelblue",
            title_font_family="Times New Roman"
        )

        fig.write_html(os.path.join(image_dir, "word_cloud_watch_shivalee.html"))
    
    

    def word_cloud_search(self):
        print("Generating Word Cloud.....")
        list = df_searches_yr['SEARCHES']    #.tolist()

        if len(list) == 0:
            unique_string = 'None'
            title = "You didn't search anything this year"
        else:
            unique_string = (" ").join(list)
            title = "What Do You Usually Search on YouTube?"

        stop_words = ["amp", "quot"] + english_stopwords
        word_cloud_search = WordCloud(
            stopwords=stop_words,
            background_color="white",
            colormap="Set2",
            max_words=380,
            contour_width=2,
            prefer_horizontal=1
        ).generate(unique_string)

        fig = px.imshow(word_cloud_search)
        fig.update_layout(
            title=title,
            title_font_size=24,
            title_font_color="steelblue",
            title_font_family="Times New Roman"
        )


        # Save as HTML
        pio.write_html(fig, os.path.join(image_dir, "word_cloud_search_shivalee.html"))


    ### WSLC
    def bar1(self):
        print("Generating Bar Plot.....")
        plt.figure(figsize=(14, 7))
        sns.set(style="white", font_scale=1.5)
        splot = sns.barplot(
            x=[
                len(urls_id),
                searches_yr,
                likes_yr,
                comments_yr,
            ],
            y=["Watch", "Search",'Like', "Comment"],
            palette='vlag',
        )
        for p in splot.patches:
            width = p.get_width()
            splot.text(
                width,
                p.get_y() + p.get_height() / 2 + 0.1,
                "{:1.0f}".format(width),
                ha="left",
            )
        splot.grid(False)
        plt.title("Breakdown of Your Activity on Youtube",
                  fontsize=24,
                  color="steelblue",
                  fontweight="bold",
                  fontname="Comic Sans MS")
        plt.savefig(os.path.join(image_dir,"bar1.png"), dpi=400)
        plt.clf()
    ### TOP5
    def bar2(self):
        print("Generating Bar Plot.....")

        current_df = pd.read_csv(os.path.join(os.getcwd(),"csv_file_Shivalee/watch_top5.csv"))
        data = [
            current_df.iloc[0, 4],
            current_df.iloc[1, 4],
            current_df.iloc[2, 4],
            current_df.iloc[3, 4],
            current_df.iloc[4, 4]
        ]
        data.reverse()  # Reverse the data to have the highest values at the top
        
        # Get the corresponding text for each bar
        text_data = []
        for i in range(5):
            words = re.split(r'\s+|[\-|]', current_df.iloc[i, 5])
    
            # Keep the first three words and discard the rest
            title = ' '.join(words[:3])
            # title = current_df.iloc[i, 5].split("|" or "-")
            text_data.append(title)
        text_data.reverse()  # Reverse the text data
        
        link_data=[df_top5.iloc[0, 3],
            current_df.iloc[1, 3],
            current_df.iloc[2, 3],
            current_df.iloc[3, 3],
            current_df.iloc[4, 3]

        ]

        link_data.reverse()
        y_labels = ["#5", "#4", "#3", "#2", "#1"]  # Reverse the labels accordingly
        
        fig = go.Figure(data=[
            go.Bar(
                x=data,
                y=y_labels,
                  # Place the text inside the bars
                marker=dict(color='#D24545'), 
                orientation='h',
            )
        ])
        
        # Add annotations as links
        for i, text in enumerate(text_data):
            font_color = "#E4DEBE"
            fig.add_annotation(
                x=data[i] / 2,  # Position the annotation in the middle of the bar
                y=y_labels[i],
                text=f'<a href="{link_data[i]}" style="color: {font_color}; text-decoration: underline; font-size: 14px;"><b>{text_data[i]}</b></a>',
                showarrow=False,
                font=dict(color='black', size=16),  # Customize the font color and size
                xanchor='center',  # Anchor the text in the center of the bar
                yanchor='middle',
            )
        
        fig.update_layout(
            # title="Most Watched Videos This Year",
            # title_font_size=24,
            # title_font_color="steelblue",
            # title_font_family="Times New Roman",
            xaxis=dict(
                title="Number of Times Viewed",  # Add x-axis title
                title_font=dict(size=20, color="black"),  # Set x-axis title font size and color
                tickfont=dict(color='black', size =16),
                showgrid=False,
            ),
        yaxis=dict(
            title_font=dict(color="black", size =20),
            tickfont=dict(color='black', size =16),
            showgrid=False,
            ),
        plot_bgcolor='white',
        paper_bgcolor='white'
        )

        html_file = os.path.join(image_dir, "bar2_shivalee.html")
        pio.write_html(fig, html_file)  # Save the plot as HTML
        print(f"Bar plot saved as HTML: {html_file}")



    ## Category
    def bar3(self):
        print("Generating Bar Plot.....")
        sns.set(style="white", color_codes=True,font_scale=1.5)
        data = [dfz.iloc[0,1], dfz.iloc[1,1], dfz.iloc[2,1], dfz.iloc[3,1], dfz.iloc[4,1]]
        pal = sns.color_palette("RdPu", len(data))
        rank = np.array(data).argsort().argsort()
        plt.figure(figsize=(14, 7))
        splot = sns.barplot(
            x=[
                dfz.iloc[0,0],
                dfz.iloc[1,0],
                dfz.iloc[2,0],
                dfz.iloc[3,0],
                dfz.iloc[4,0]
            ],
            y=[dfz.iloc[0,1],dfz.iloc[1,1],dfz.iloc[2,1],dfz.iloc[3,1],dfz.iloc[4,1]],
            palette=np.array(pal)[rank],
        )
        for p in splot.patches:
            heighth = p.get_height()+dfz.iloc[0,1]/20
            splot.text(
                p.get_x() + p.get_width() / 2-0.07,
                heighth,
                "{:1.0f}".format(heighth),
                va="top",
            )
        splot.grid(False)
        plt.title("TOP5 Categories You Watched This Year",
                  fontsize=24,
                  color="steelblue",
                  fontweight="bold",
                  fontname="Comic Sans MS")
        plt.savefig(os.path.join(image_dir,"bar3.png"), dpi=400)
        plt.clf()
    ## Channel

    def bar4(self):
        sns.set(style="white", font="SimSun", color_codes=True, font_scale=1.5)

        dfz = pd.read_csv(os.path.join(os.getcwd(),"csv_file_Shivalee/api_rep.csv"))

        # Get the top 10 data
        top_10_data = dfz.iloc[:10, -4]
        top_10_names = dfz.iloc[:10, -5]

        top_10_data = top_10_data[::-1]
        top_10_names = top_10_names[::-1]
    
        print("Generating Bar Plot with Plotly.....")

        fig = go.Figure()

        

        for i, name in enumerate(top_10_names[::-1]):
            fig.add_shape(
                type="line",
                x0=0, y0=name,
                x1=top_10_data[i], y1=name,
                line=dict(color='#D24545', width=4),
                # hoverinfo='none'
            )

        fig.add_trace(go.Scatter(
            x=top_10_data,
            y=top_10_names,
            mode='markers',
            marker=dict(color='#A94438', symbol='circle', size=10),
            text=[f"{val:1.0f}" for val in top_10_data],
            textposition='middle right',  # Adjust text position
            hoverinfo='text'
        ))

        fig.update_layout(
            # title="Most Watched Channels This Year",
            # title_font_size=24,
            # title_font_color="steelblue",
            # title_font_family="Times New Roman",
            xaxis=dict(title='Number of Views', showgrid=False, title_font=dict(size=20, color="black"),  # Set x-axis title font size and color
                tickfont=dict(color='black', size=16),),
            yaxis=dict(title='Names', showgrid=False, ticklen=10,title_font=dict(size=20, color="black"),  # Set x-axis title font size and color
                tickfont=dict(color='black', size = 16),),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(
                family="Times New Roman",
                size=14,
                color="black"
            ),
             hoverlabel=dict(bgcolor="white", font_size=12),
        )

        html_file_path = os.path.join(image_dir, "bar4_shivalee.html")
        pio.write_html(fig, html_file_path)
        print(f"Bar plot saved as HTML file: {html_file_path}")


    

    def language(self):
        print("Calculating Your Favorite Video's Language.....")
        colors = ["#1f77b4", "#aec7e8", "#7fbf7b", "#2ca02c", "#ff7f0e", "#ffbb78", "#d62728", "#ff9896", "#9467bd", "#c5b0d5"]


        # Read CSV file
        dfz = pd.read_csv(os.path.join(os.getcwd(), "csv_file_Shivalee/api_rep.csv"))

        # Check the number of languages
        cnt = len(dfz)

        if cnt == 0:
            print("No language data available.")
            return

        # Prepare data for the chart
        labels = dfz['language']
        values = dfz['lanCounts']

        # Create the donut chart
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='percent', hoverinfo='label+percent',
                                     marker=dict(colors=colors[:cnt]), hole=0.7)])

        # Remove legend
        

        fig.update_layout(title="Your Favorite Videos Language",
                          title_font_size=24,
                          title_font_color="steelblue",
                          title_font_family="Times New Roman")


        # Save the chart as HTML
        html_file_path = os.path.join(image_dir, "language_shivalee.html")
        pio.write_html(fig, html_file_path)

    


    def categoryRatio(self):
        print("Calculating Your Category Rank: .....")
        colors = ["#1f77b4", "#aec7e8", "#7fbf7b", "#2ca02c", "#ff7f0e", "#ffbb78", "#d62728", "#ff9896", "#9467bd", "#c5b0d5"]

        # Read CSV file
        dfz = pd.read_csv(os.path.join(os.getcwd(), "csv_file_Shivalee/api_rep.csv"))

        # Check the number of categories
        cnt = len(dfz)

        if cnt == 0:
            print("No category data available.")
            return

        # Extract category names and ratios
        category_names = dfz['categoryName']
        category_ratios = dfz['categoryRatio']

        labels = list(category_names)
        values = list(category_ratios)

        # Create the pie chart
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='percent', hoverinfo='label+percent',
                                     marker=dict(colors=colors[:cnt]), hole=0.7)])

        
        
        fig.update_layout(title="Your Favorite Videos Category Ratio",
                          title_font_size=24,
                          title_font_color="steelblue",
                          title_font_family="Times New Roman")

        
        # Save the chart as HTML
        html_file_path = os.path.join(image_dir, "categoryRatio_shivalee.html")
        pio.write_html(fig, html_file_path)


    def radarChartComparison(self):
        print("Creating Radar Chart Comparison: ...")
        # Define file paths
        file_paths = {
            "Ritam": "csv_file_Ritam/api_rep.csv",
            "Shivalee": "csv_file_Shivalee/api_rep.csv",
            "Aman": "csv_file_Aman/api_rep.csv"
        }
    
        # Define colors for each category
        colors = ["#1f77b4", "#aec7e8", "#7fbf7b", "#2ca02c", "#ff7f0e", "#ffbb78", "#d62728", "#ff9896", "#9467bd", "#c5b0d5"]
    
        # Initialize radar chart data
        data = []
    
        # Iterate over each user's CSV file
        for user, file_path in file_paths.items():
            dfz = pd.read_csv(file_path)
            cnt = len(dfz)
            if cnt == 0:
                print(f"No category data available for {user}.")
                continue
        
            # Extract category names and ratios
            category_names = dfz['categoryName']
            category_ratios = dfz['categoryRatio']
        
            # Normalize ratios to percentages
            normalized_ratios = [ratio * 100 for ratio in category_ratios]
        
            # Add radar chart trace for current user
            trace = go.Scatterpolar(
                r=normalized_ratios,
                theta=category_names,
                fill='toself',
                name=user,
                marker=dict(color=colors[:cnt]),
            )
            data.append(trace)
    
        # Create radar chart layout
        layout = go.Layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 50]  # Adjust the range as needed
                )),
            showlegend=True,
            title='Category Ratio Comparison',
            title_font_size=24,
            title_font_color="steelblue",
            title_font_family="Times New Roman",
        )

        # Create radar chart figure
        fig = go.Figure(data=data, layout=layout)

        # Save the chart as HTML
        html_file_path = os.path.join(image_dir, "radarChart_comparison.html")
        pio.write_html(fig, html_file_path)



    def barGraphComparison(self):
        print("Creating Bar Graph Comparison: ...")
        # Define file paths
        file_paths = {
            "Ritam": "csv_file_Ritam/api_rep.csv",
            "Shivalee": "csv_file_Shivalee/api_rep.csv",
            "Aman": "csv_file_Aman/api_rep.csv"
        }

        user_colors = {
            "Ritam": "#A94438",
            "Shivalee": "#D24545",
            "Aman": "#E6BAA3"
        }
        # Initialize bar graph data
        data = []

        # Iterate over each user's CSV file
        for user, file_path in file_paths.items():
            dfz = pd.read_csv(file_path)
            cnt = len(dfz)
            if cnt == 0:
                print(f"No category data available for {user}.")
                continue

            # Extract category names and ratios
            category_names = dfz['categoryName']
            category_ratios = dfz['categoryRatio']

            # Add bar graph trace for current user
            trace = go.Bar(
                x=category_names,
                y=category_ratios,
                name=user,
                marker=dict(color=user_colors[user]),
            )
            data.append(trace)

        # Create bar graph layout
        layout = go.Layout(
            barmode='group',  # Adjust the bar mode as needed (group, stacked, overlay)
            showlegend=True,
            plot_bgcolor='white',  # Set plot background color to white
            legend=dict(yanchor="bottom", y=1.02, xanchor="right", x=0.85),
            # title='Category Ratio Comparison',
            # title_font_size=24,
            # title_font_color="steelblue",
            # title_font_family="Times New Roman",
        )

        # Create bar graph figure
        fig = go.Figure(data=data, layout=layout)

        # Save the chart as HTML
        html_file_path = os.path.join(image_dir, "barGraph_comparison.html")
        pio.write_html(fig, html_file_path)


    def weeklyWatchComparison(self):
        print("Creating Weekly Watch Comparison: ...")

        weekly_watch_shivalee=[3437,3899, 3372, 3379, 3606, 4751, 3422]
        weekly_watch_ritam=[6136, 6416, 5899, 6539, 7370, 5953, 5609]
        weekly_watch_aman=[392, 307, 294, 288, 334, 359, 376]
        # Normalize the weekly watch time data
        max_watch_time = max(max(weekly_watch_shivalee), max(weekly_watch_ritam), max(weekly_watch_aman))
        normalized_watch_shivalee = [watch_time / max_watch_time for watch_time in weekly_watch_shivalee]
        normalized_watch_ritam = [watch_time / max_watch_time for watch_time in weekly_watch_ritam]
        normalized_watch_aman = [watch_time / max_watch_time for watch_time in weekly_watch_aman]

        # Define x-axis labels
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Create area chart traces for each user
        trace_shivalee = go.Scatter(
            x=days_of_week,
            y=normalized_watch_shivalee,
            mode='lines',
            name='Shivalee',
            fill='tozeroy',  # Fill the area below the line
            line=dict(color='#1f77b4'),
        )

        trace_ritam = go.Scatter(
            x=days_of_week,
            y=normalized_watch_ritam,
            mode='lines',
            name='Ritam',
            fill='tozeroy',  # Fill the area below the line
            line=dict(color= '#aec7e8'),
        )

        trace_aman = go.Scatter(
            x=days_of_week,
            y=normalized_watch_aman,
            mode='lines',
            name='Aman',
            fill='tozeroy',  # Fill the area below the line
            line=dict(color= '#7fbf7b'),
        )

        # Create layout for the area chart
        layout = go.Layout(
            # title='Weekly Watch Time Comparison',
            # title_font_size=24,
            # title_font_color="steelblue",
            # title_font_family="Times New Roman",
            xaxis=dict(title='Day of Week'),
            yaxis=dict(title='Normalized Watch Time'),
            # legend=dict(x=0, y=1),
            legend=dict(yanchor="bottom", y=1.02, xanchor="right", x=0),
            margin=dict(l=40, r=40, t=80, b=40),
            plot_bgcolor='white',
        )

        # Create the figure with data and layout
        fig = go.Figure(data=[trace_shivalee, trace_ritam, trace_aman], layout=layout)

        #  Save the chart as HTML
        html_file_path = os.path.join(image_dir, "weeklyWatch_comparison.html")
        pio.write_html(fig, html_file_path)


if __name__ == "__main__":
    print(dfz)
    visual = Visualization()
    visual.heat_map_week()
    visual.bar_graph_week()
    # visual.generate_html_from_dataframe()
    # visual.table()
    # visual.word_cloud_watch()
    # visual.word_cloud_search()
    # visual.bar1()
    visual.bar2()
    # visual.bar3()
    visual.bar4()
    #visual.language()
    #visual.categoryRatio()
    #visual.radarChartComparison()
    visual.barGraphComparison()
    visual.weeklyWatchComparison()


t2= datetime.datetime.now()
print("end >> {}".format(t2))
print("end >> {}".format(t2))
print("RUNTIME >> {}".format(t2-t1))
