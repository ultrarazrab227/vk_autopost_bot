from telegram import *
from telegram.ext import *
import telegram
import vk_api
import youtube_dl
import configparser
import os
from time import sleep

config = configparser.ConfigParser()
config.read("config.ini")
#
token = config['vk']['bot_token']
print(token)
bot = Bot(token)

vk_session = vk_api.VkApi(config['vk']['email'], config['vk']['password'])
vk_session.auth()
vk = vk_session.get_api()
public_id = config['vk']['public_id']
admin_id = config['vk']['chanel_admin_id']
chat_id = config['vk']['chat_id']
last = vk.wall.get(owner_id=public_id, count=1)

print(admin_id)


# print(last)
# last['items'][0]['id']
def check():
    global last
    req = vk.wall.get(owner_id=public_id, count=1)
    if req['items'][0]['id'] != 1:
        if req['items'][0]['attachments'][0]['type'] != 'video':
            from_id = req['items'][0]['from_id']
            post_link = "https://vk.com/wall{}_{}".format(from_id, req['items'][0]['id'])
            bot.send_message(admin_id, post_link)
            return
        owner_id = req['items'][0]['attachments'][0]['video']['owner_id']
        video_id = req['items'][0]['attachments'][0]['video']['id']
        text = req['items'][0]['text']
        ydl_opts = {}
        print('https://vk.com/video{}_{}'.format(owner_id, video_id))
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://vk.com/video{}_{}'.format(owner_id, video_id)])
        filename = ""
        for root, dirs, files in os.walk("."):
            for name in files:
                if ".mp4" in name:
                    filename = name
        if filename == "":
            post_link = "https://vk.com/wall{}_{}".format(req['items'][0]['id'], owner_id)
            bot.send_message(admin_id, post_link)
            return
        video = open(filename, 'rb')
        try:
            bot.send_video(chat_id, video, caption=text)
        except telegram.error.NetworkError:
            from_id = req['items'][0]['from_id']
            post_link = "https://vk.com/wall{}_{}".format(from_id, req['items'][0]['id'])
            bot.send_message(admin_id, post_link)
        video.close()
        os.remove(filename)
        last = req


while True:
    check()
    sleep(30)
