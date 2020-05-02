from colorthief import ColorThief
from urllib.request import urlopen
from PIL import Image, ImageDraw

import sys
import io
import tweepy
import time
import random

FILE_NAME = 'last_seen_id.txt'
access_token = 'XXXXXXXXXXXXXXXX'
access_token_secret = 'XXXXXXXXXXXXXXXX'
consumer_key = 'XXXXXXXXXXXXXXXX'
consumer_secret = 'XXXXXXXXXXXXXXXX'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()

    return last_seen_id


def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()

    return


def get_status(status_id_str):
    status = api.get_status(id=status_id_str)
    try:
        image_url = status._json["entities"]["media"][0]["media_url"]
    except:
        image_url = 0

    return image_url


def get_color_palette(image_url):
    image = urlopen(image_url)
    image_bytes = io.BytesIO(image.read())

    color_thief = ColorThief(image_bytes)
    color_palette = color_thief.get_palette(color_count=100)

    return color_palette


def create_color_palette_image(color_palette):
    height = 600
    width = 600
    color_palette_image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(color_palette_image)

    porcentage = width / 100
    x0 = 0
    y0 = 0
    x1 = porcentage
    y1 = porcentage

    while (y1 <= height):
        while(x1 <= width):
            draw.rectangle(((x0, y0), (x1, y1)),
                           fill=random.choice(color_palette))
            x0 += porcentage
            x1 += porcentage
        x0 = 0
        x1 = porcentage
        y0 += porcentage
        y1 += porcentage

    color_palette_image.save('image.png')


def post_color_palette_image(user_screen_name, status_id):
    r1 = api.media_upload('image.png')
    media_ids = [r1.media_id_string]

    api.update_status(status='@' + user_screen_name,
                      in_reply_to_status_id=status_id, media_ids=media_ids)


def post_error(user_screen_name, status_id, mensagem):
    api.update_status(status='@' + user_screen_name + ' Sorry, error with the ' + mensagem,
                      in_reply_to_status_id=status_id)


def main():
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(last_seen_id)

    for mention in reversed(mentions):
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)

        status_id = mention.id_str
        user_screen_name = mention.user.screen_name
        print('Processing @' + user_screen_name + ' tweet...')

        in_reply_to_status_id = mention.in_reply_to_status_id_str
        if in_reply_to_status_id:
            image_url = get_status(in_reply_to_status_id)
            if image_url:
                color_palette = get_color_palette(image_url)
                create_color_palette_image(color_palette)
                post_color_palette_image(user_screen_name, status_id)
                print('Ready!')
            else:
                post_error(user_screen_name, status_id, 'image')
                print('Erro with the image')
        else:
            post_error(user_screen_name, status_id, 'Tweet')
            print('Erro with the Tweet')


while True:
    main()
    time.sleep(15)
