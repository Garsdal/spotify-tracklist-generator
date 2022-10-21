import pandas as pd
import streamlit as st
import json
import base64

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# audio
import vlc


@st.cache(suppress_st_warning=True)
def read_data(path):
    return pd.read_csv(path, sep=";", index_col=[0])


@st.cache(suppress_st_warning=True)
def load_config(path_config):
    with open(path_config, 'r') as f:
        config = json.load(f)

    return config


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def setup_spotify_credentials_manager(config):
    CLIENT_ID = config['CLIENT_ID']
    CLIENT_SECRET = config['CLIENT_SECRET']

    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    return sp


def set_up_audio_instance():
    instance = vlc.Instance('--input-repeat=-1', '--fullscreen')

    return instance


@st.cache(allow_output_mutation=True)
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_bg(png_file):
    # We remove the header of the page
    st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    # We add the background as base64
    bin_str = get_base64(png_file)
    page_bg_img = """
        <style>
        .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        }
        </style>
    """ % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)


def convert_fractional_time(length_minutes_decimal):
    minutes = length_minutes_decimal
    seconds = 60 * (minutes % 1)

    length_minutes_seconds = "%02d:%02d" % (minutes, seconds)

    return length_minutes_seconds
