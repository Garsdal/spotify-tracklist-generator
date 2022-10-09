import requests

# images
from PIL import Image
from io import BytesIO

def search_artist_track(sp, artist, track):
    response = sp.search(q="artist:" + artist + " track:" + track, type="track")

    return response

def get_image_url(response):
    # If there are images in the response
    try:
        if response['tracks']['items'][0]['album']['images']:
            # We grab the first one
            image_url = response['tracks']['items'][0]['album']['images'][1]['url']
    except IndexError:
        image_url = None
        
    return image_url

def return_image_from_url(image_url):
    if image_url is None:
        img = Image.open('assets/image-not-available-300x300.png')
    else:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
    
    return img

def get_preview_url(response):
    preview_url = response['tracks']['items'][0]['preview_url']

    return preview_url

def return_player_from_url(instance, preview_url):
    #Define VLC player
    player=instance.media_player_new()

    #Define VLC media
    media=instance.media_new(preview_url)

    #Set player media
    player.set_media(media)

    return player