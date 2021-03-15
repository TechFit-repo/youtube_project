from oauth2client.tools import argparser
from apiclient.errors import HttpError
from apiclient.discovery import build
import pandas as pd
import json

class YouTube():
    def __init__(self):
        config = json.loads(open('config.json').read())
        key=list(config['dict'].keys())[0]
        api_key = config['dict'][key]
        api_service_name = 'youtube'
        api_version = 'v3'
        self.youtube = build(api_service_name, api_version,developerKey=api_key)
    
    def searchChannels(self, query, max_results=1000, order='relevance'):
        search_results = self.youtube.search().list(
        q=query, type='video', pageToken=None, order=order,
        part='id, snippet', maxResults=max_results, location=None,
        locationRadius=None).execute()
        self.query = query
        return search_results
    
    def createDatabase(self, results):
        channelId = []
        channelTitle = []
        title = []
        categoryId = []
        videoId = []
        publishedAt = []
        viewCount = []
        likeCount = []
        dislikeCount = []
        commentCount = []
        tags = []
        for search in results.get('items', []):
            title.append(search['snippet']['title'])
            videoId.append(search['id']['videoId'])
            
            analytics = self.youtube.videos().list(
                part='statistics, snippet',
                id=search['id']['videoId']).execute()
            
            try:
                channelId.append(analytics['items'][0]['snippet']['channelId'])
            except:
                channelId.append(0)
                
            try:
                channelTitle.append(analytics['items'][0]['snippet']['channelTitle'])
            except:
                channelTitle.append(0)
                
            try:
                categoryId.append(analytics['items'][0]['snippet']['categoryId'])
            except:
                categoryId.append(0)
            
            try:
                publishedAt.append(analytics['items'][0]['snippet']['publishedAt'])
            except:
                publishedAt.append(0)
                
            try:
                viewCount.append(analytics['items'][0]['statistics']['viewCount'])
            except:
                viewCount.append(0)
                
            try:
                likeCount.append(analytics['items'][0]['statistics']['likeCount'])
            except:
                likeCount.append(0)
                
            try:
                dislikeCount.append(analytics['items'][0]['statistics']['dislikeCount'])
            except:
                dislikeCount.append(0)
                
            try:
                commentCount.append(analytics['items'][0]['statistics']['commentCount'])
            except:
                commentCount.append(0)
            try:
                tags.append(analytics['items'][0]['snippet']['tags'])
            except:
                tags.append(0)
                
        youtube_df = pd.DataFrame(dict(channelId = channelId, channelTitle = channelTitle,
                                       categoryId = categoryId, title = title, videoId = videoId, publishedAt=publishedAt,
                                       viewCount = viewCount, likeCount = likeCount, dislikeCount = dislikeCount,
                                       commentCount = commentCount, tags = tags
                                       ))
        youtube_df = youtube_df[youtube_df['channelTitle'] == self.query]
        youtube_df = youtube_df.sort_values('publishedAt', ascending = False).head(30).reset_index()
        return youtube_df

if __name__ == '__main__':
    data = pd.DataFrame()
    channels = ['Meet Kevin','Andrei Jikh','Joma Tech','Ali Abdaal','Graham Stephan']
    you_tube = YouTube()
    for channel in channels:
        results = you_tube.searchChannels(query=channel)
        youtube_df = you_tube.createDatabase(results=results)
        data = data.append(youtube_df)
    data = data.reset_index()
