import requests
import pandas as pd
import numpy as np

# images
from PIL import Image
from io import BytesIO

def api_call_get_track_from_artist_track(sp, artist, track):
    response_search = sp.search(q="artist:" + artist + " track:" + track, type="track")
    
    response_track = response_search['tracks']['items'][0]

    return response_track

def api_call_get_track_from_url(sp, track_url):
    response_track = sp.track(track_url)

    return response_track

def get_artist_track_features_from_response(sp, response_track):
    keys = ["artist_name", "artist_pop", "track_name", "track_pop", "album", "key", "mode", "tempo", "duration_ms", "time_signature", "energy", "danceability", "instrumentalness"]
    artist_keys = ["artist_name", "artist_pop", "track_name", "track_pop", "album"]
    audio_keys = ["key", "mode", "tempo", "duration_ms", "time_signature", "energy", "danceability", "instrumentalness"]
    dict_data = {key: np.array([]) for key in keys}

    #Track name
    track_name = response_track['name']
    track_uri = response_track['uri']

    #Main Artist
    artist_uri = response_track["artists"][0]["uri"]
    artist_info = sp.artist(artist_uri)

    #Name, popularity, genre
    artist_name = response_track["artists"][0]["name"]
    artist_pop = artist_info["popularity"]
    artist_genres = artist_info["genres"]

    #Album
    album = response_track["album"]["name"]

    #Popularity of the track
    track_pop = response_track["popularity"]

    # We get audio features
    audio_features = sp.audio_features(track_uri)[0]

    # We look for the preview url
    preview_url = response_track['preview_url']

    # We get the cover url
    cover_url = response_track['album']['images'][0]['url']

    # We save the results
    dict_data["artist_name"] = np.append(dict_data["artist_name"], artist_name)
    dict_data["artist_pop"] = np.append(dict_data["artist_pop"], artist_pop)
    dict_data["track_name"] = np.append(dict_data["track_name"], track_name)
    dict_data["track_pop"] = np.append(dict_data["track_pop"], track_pop)
    dict_data["album"] = np.append(dict_data["album"], album)

    for audio_key in audio_keys:
        dict_data[audio_key] = np.append(dict_data[audio_key], audio_features[audio_key])

    df = pd.DataFrame(dict_data)
    df.set_index("artist_name", inplace = True)

    return df

def get_artist_tracks_from_local_data(df, artist_selected):
    artist_tracks = df.loc[artist_selected, 'track_name']

    # We have to consider if only a single track or multiple tracks are returned
    if isinstance(artist_tracks, str):
        artist_tracks = [artist_tracks]
    else:
        artist_tracks = artist_tracks.values

    return artist_tracks

def get_artist_track_features_from_local_data(df, artist_selected, track_selected):
    df_artist = df.loc[artist_selected]
    
    # We have to consider if only a single track or multiple tracks are returned
    if isinstance(df_artist, pd.Series):
        df_artist_track_features = df_artist.to_frame().T
    else:
        idx = df_artist['track_name'] == track_selected
        df_artist_track_features = df_artist.loc[idx]

    return df_artist_track_features

def get_image_url(response_track):
    # If there are images in the response
    try:
        if response_track['album']['images']:
            # We grab the first one
            image_url = response_track['album']['images'][1]['url']
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

def get_preview_url(response_track):
    preview_url = response_track['preview_url']

    return preview_url

def return_player_from_url(instance, preview_url):
    #Define VLC player
    player=instance.media_player_new()

    #Define VLC media
    media=instance.media_new(preview_url)

    #Set player media
    player.set_media(media)

    return player