import requests
from .models import YoutubeClip, KeyWord
import json
import datetime
from .settings import API_KEY
from .celery import app


def convert_to_dt(time):
    datestr = time[:-1]
    date = datetime.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f')
    return date


def get_urls(key_word, last_update):
    url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&order=date&q={q}&type=video&key={key}'
    url = url.format(key=API_KEY, q=key_word)
    clips_url = []
    r = requests.get(url)
    a = json.loads(r.content)
    if 'items' in a:
        # set newest date
        new_date = convert_to_dt(a['items'][0]['snippet']['publishedAt'])
        while 1:
            if 'items' not in a:
                return clips_url, new_date
            for item in a['items']:
                id = item['id']['videoId']
                date = convert_to_dt(item['snippet']['publishedAt'])
                if last_update and date <= last_update:
                    return clips_url, new_date
                else:
                    clips_url.append((id, date))
            if 'nextPageToken' in a:
                next_page_token = a['nextPageToken']
                r = requests.get(url + "&pageToken={}".format(next_page_token))
                a = json.loads(r.content)
            else:
                return clips_url, new_date
    else:
        return clips_url, None


@app.task
def request_for_new_video():
    key_words = KeyWord.objects.all()
    for key in key_words:
        new_youtube_urls, new_date_for_key = get_urls(key.key_word, key.last_clip_time)
        for url, date in new_youtube_urls:
            q = YoutubeClip(key_word=key, url='https://www.youtube.com/watch?v=' + url, uploaded=date)
            q.save()
        if new_youtube_urls:
            key.last_clip_time = new_date_for_key
            key.save()
        print("added {} new urls for  key :{}".format(len(new_youtube_urls), key.key_word))
