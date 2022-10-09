import pandas as pd
import numpy as np
import streamlit as st
import time
import requests
from io import BytesIO

from src.processing import search_artist_track, get_image_url, get_preview_url, return_image_from_url, return_player_from_url
from src.utils import get_artist_tracks, convert_fractional_time, load_config

def sidebar(df):
    st.sidebar.write(f"## Artist info")
    artist_selected = st.sidebar.selectbox("Please select an artist to begin:", np.unique(df.sort_index().index))
    artist_tracks = get_artist_tracks(df, artist_selected)

    track_selected = st.sidebar.selectbox("Please select a track to begin:", artist_tracks)

    st.sidebar.write(f"## Recommendation info")

    # We get number of recommendations
    n_recommendations = st.sidebar.selectbox("Number of recommendations", (1, 3, 5))

    # We check if the key must be the same
    arg_key = st.sidebar.checkbox("Keep key the same")

    # We get a specific bpm range
    col_left, col_right = st.columns(2)
    with col_left:
        bpm_minimum = st.sidebar.number_input("Minimum BPM", value = 120)
    with col_right:
        bpm_maximum = st.sidebar.number_input("Maximum BPM", value = 130)
    arg_bpm = (bpm_minimum, bpm_maximum)

    return(n_recommendations, artist_selected, track_selected, arg_key, arg_bpm)

def head_introduction():
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: -35px;'>
        Tracklist Generator
        </h1>
    """, unsafe_allow_html=True
    )
    
    st.caption("""
        <p style='text-align: center'>
        by <a href='https://github.com/garsdal'>Garsdal</a>
        </p>
    """, unsafe_allow_html=True
    )
    
def head_recommendations():
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: -35px;'>
        Recommendations
        </h1>
    """, unsafe_allow_html=True
    )

    st.caption("""
        <p style='text-align: center'>
        Generated by AI Machine Learning AlphaRecommender
        </p>
    """, unsafe_allow_html=True
    )

def body_selection(response, df_artist_track_features, key_mapping, mode_mapping):
    artist_name = df_artist_track_features.index[0]
    track_name = df_artist_track_features["track_name"][0]

    # We grab the track image and display it
    image_url = get_image_url(response)
    img = return_image_from_url(image_url)

    # We print the track_features
    f1,f2,f3,f4,f5 = st.columns(5)

    with f1:
        key_numeric = int(df_artist_track_features['key'])
        key_string = key_mapping[str(key_numeric)]
        st.metric("Key:", key_string)
    with f2:
        mode_numeric = int(df_artist_track_features['mode'])
        mode_string = mode_mapping[str(mode_numeric)]
        st.metric("Mode:", mode_string)
    with f3:
        # BPM can come in the format 120.99 and 120.99.00
        bpm_list = df_artist_track_features['tempo'].values[0].split(".")
        bpm = "".join(bpm_list[0:1])

        st.metric("BPM:", round(float(bpm), 1))
    with f4:
        length_minutes_decimal = int(df_artist_track_features['duration_ms'].values[0])/(60*1000)
        length_minutes_seconds = convert_fractional_time(length_minutes_decimal)
        st.metric("Length:", length_minutes_seconds)
    with f5:
        energy = df_artist_track_features['energy'].values[0].replace(",", ".").strip()
        st.metric("Energy:", round(float(energy), 2))

    # We grab the track preview and play it
    preview_url = get_preview_url(response)

    # # We get the data
    response_audio = requests.get(preview_url)
    audio_bytesIO = BytesIO(response_audio.content)
    
    # # We create a audio player
    _,col_audio_mid,_ = st.columns(3)
    with col_audio_mid:
        st.audio(audio_bytesIO)

    # We print the image
    _, col_mid, _ = st.columns(3)
    with col_mid:
        #st.caption(f' {artist_name} - {track_name}')
        st.image(img, caption=f' {artist_name} - {track_name}')

def body_recommendation(response, df_artist_track_features, key_mapping, mode_mapping):
    artist_name = df_artist_track_features.index[0]
    track_name = df_artist_track_features["track_name"][0]

    # We get the most important features (COULD BE PUT IN UTILS FCT)
    key_numeric = int(df_artist_track_features['key'])
    key_string = key_mapping[str(key_numeric)]

    mode_numeric = int(df_artist_track_features['mode'])
    mode_string = mode_mapping[str(mode_numeric)]

    # BPM can come in the format 120.99 and 120.99.00
    bpm_list = df_artist_track_features['tempo'].values[0].split(".")
    bpm = "".join(bpm_list[0:1])

    # We grab the track image and display it
    image_url = get_image_url(response)
    img = return_image_from_url(image_url)

    # We grab the preview and provide an audio player
    preview_url = get_preview_url(response)

    # We get the data
    response_audio = requests.get(preview_url)
    audio_bytesIO = BytesIO(response_audio.content)

    # We show the user the player
    st.audio(audio_bytesIO)

    # We show the user the image
    st.image(img, caption=f' {artist_name} - {track_name} | {key_string} | {mode_string} | {bpm}')