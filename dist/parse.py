#!/usr/bin/python3
import re
import os
import datetime,pytz
import pandas as pd
import time

missing = []
dir = os.path.join(os.getcwd(),"Takeout/YouTube/")
playlists_path = os.path.join(dir,"playlists/Liked videos")
if not os.path.exists(dir):
    missing.append(dir)

### watch_history
path = "history/watch-history.html"
watch_history = os.path.join(dir,path)

### search
search_path = "history/search-history.html"
search_history = os.path.join(dir,path)

### comment
comment_path = "my-comments/my-comments.html"
comments_history = os.path.join(dir,path)

### like
like_path = "playlists/Liked videos.csv"
like_history = os.path.join(dir,path)


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


    # 下面的watch history的id/title/date_time可与video_id一并写入一个函数，从而直接输出三列的df而无需在report中分别再处理它们
    def find_video_id(self):
        video_id = []
        pattern = re.compile(r"""Watched\xa0<a href=\".[^v]*v=(.[^\"]*)\">.[^<]*<\/a><br><a href=\".[^\"]*\">.[^<]*<\/a>""")
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
        pattern = re.compile(r"""Watched\xa0<a href=\".[^\"]*\">.[^<]*<\/a><br><a href=\".[^\"]*\">.[^<]*<\/a><br>(\w{1,3}\s.*?)<\/div>""")
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
                # return tz
                if is_regex1:
                    date_time_time = datetime.datetime.strptime(timez, regex1[1])
                else:
                    date_time_time = datetime.datetime.strptime(timez, regex2[1])
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
            return times2

    ### 正则处理筛选search
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
        df0 = pd.DataFrame(search_link_list)
        df1 = pd.DataFrame(search_list)
        df2 = pd.DataFrame(time_list)
        df_searches = pd.concat([df1,df0,df2], axis=1)
        df_searches.columns = ['SEARCHES','SEARCHES_LINK','DATE_TIME']
        return df_searches
    ### 正则处理筛选comment
    def comment_history(self):
        try:
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
            df_comments = pd.concat([df1,df2],axis=1)
            df_comments.columns = ['COMMENTS','DATE_TIME']
            link = match_list1[-1][9:-2]
            return df_comments
        except Exception:
            pass
    ### 正则处理筛选like
    def like_history(self):
            df_likes = pd.read_csv(playlists_path+'/'+ 'Liked videos.csv', encoding="utf_8_sig")
            df_likes.drop([0, 1], axis=0, inplace=True)
            df_likes.drop(df_likes.iloc[:, 2:], axis=1, inplace=True)
            df_likes.columns = ['liked_video_id','liked_time']
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
            return df_likes


    # 第二个热力图的元数据
    def dataframe_heatmap(self, day):
        times = self.raw_find_times()
        watchtimes=[0 for t in range(12)]
        
        for time in times:
            if time.weekday()==day:
                watchtimes[(time.hour//2)-time.hour%2]+=1

        return watchtimes

