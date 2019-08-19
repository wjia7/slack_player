#!/usr/bin/python

from googleapiclient.discovery import build
import argparse
import random
import global_vars

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.

# get around 10,000 units limit for youtube api. created mutiple account
YOUTUBE_KEYS = global_vars.YOUTUBE_KEYS
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def youtube_search(youtube_id):

    youtube_key = random.choice(YOUTUBE_KEYS)
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=youtube_key , cache_discovery=False)

    # Call the search.list method to retrieve results matching the specified
    # query term. Change maxResult to find how close is the final recommendation
    # maybe use random generator between 3 and 7
    search_number=random.randint(4,10)
    search_response = youtube.search().list(
    part='snippet',
    relatedToVideoId=youtube_id,
    maxResults=search_number,
    type='video'
    ).execute()

    videos = []
    # channels = []
    # playlists = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    # print(search_response.get('items', [])[5])
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            title = search_result['snippet']['title']

    return title

        #     videos.append('%s (%s)' % (search_result['snippet']['title'], search_result['id']['videoId']))
        # elif search_result['id']['kind'] == 'youtube#channel':
        #     channels.append('%s (%s)' % (search_result['snippet']['title'],
        #                                search_result['id']['channelId']))
        # elif search_result['id']['kind'] == 'youtube#playlist':
        #     playlists.append('%s (%s)' % (search_result['snippet']['title'],
        #                                 search_result['id']['playlistId']))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--q', help='Search term', default='i want it all')
    parser.add_argument('--max-results', help='Max results', default=1)
    args = parser.parse_args()

    youtube_id='hFDcoX7s6rE'
    youtube_search(youtube_id)


