from telegram import *
import telegram
import vk_api
import youtube_dl
import configparser
import os
from time import sleep
import uuid

config = configparser.ConfigParser()
config.read("config.ini")
#
token = config['vk']['bot_token']
bot = Bot(token)

vk_session = vk_api.VkApi(config['vk']['email'], config['vk']['password'])
vk_session.auth()
vk = vk_session.get_api()
public_id = config['vk']['public_id']
admin_id = config['vk']['chanel_admin_id']
chat_id = config['vk']['chat_id']
last = vk.wall.get(owner_id=public_id, count=1)


def check():
    global last
    req = vk.wall.get(owner_id=public_id, count=1)
    if req['items'][0]['id'] != last['items'][0]['id']:
        last = req
        if not 'attachments' in req['items'][0]:
            from_id = req['items'][0]['from_id']
            post_link = "https://vk.com/wall{}_{}".format(from_id, req['items'][0]['id'])
            bot.send_message(admin_id, post_link)
            return
        owner_id = req['items'][0]['attachments'][0]['video']['owner_id']
        video_id = req['items'][0]['attachments'][0]['video']['id']
        text = uuid.uuid4()
        print('https://vk.com/video{}_{}'.format(owner_id, video_id))
        try:
            ydl_opts = {'outtmpl': f'video/{text}.mp4', 'format': 'mp4'}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(['https://vk.com/video{}_{}'.format(owner_id, video_id)])
        except:
            post_link = "https://vk.com/wall{}_{}".format(req['items'][0]['id'], owner_id)
            bot.send_message(admin_id, post_link)
            return
        filename = f"{text}.mp4"
        video = open(os.path.join('video', filename), 'rb')

        try:
            text = req['items'][0]['text']
            bot.send_video(chat_id, video, caption=text)
        except telegram.error.NetworkError:
            from_id = req['items'][0]['from_id']
            post_link = "https://vk.com/wall{}_{}".format(from_id, req['items'][0]['id'])
            bot.send_message(admin_id, post_link)
        video.close()
        for f in os.listdir('video'):
            os.remove(os.path.join('video', f))


while True:
    try:
        check()
    except Exception as ex:
        print(ex)
        print("\n\n\n")
    sleep(3)
