import os
import pandas as pd
import streamlit as st

from src.page_content import head_introduction, head_recommendations, sidebar, body_selection, body_recommendation
from src.utils import set_bg, read_data, load_config, setup_spotify_credentials_manager, set_up_audio_instance, get_artist_track_features
from src.processing import search_artist_track
from src.recommendation import get_recommendations

############### APP ################

# Set background
set_bg('assets/background.jpg')

# Get config
path_config = "config/config.json"
config = load_config(path_config)
key_mapping = load_config("config/mapping_key.json")
mode_mapping = load_config("config/mapping_mode.json")

# Setup credentials 
sp = setup_spotify_credentials_manager(config)

# Setup audio instance
instance = set_up_audio_instance()

# Load Data
path_data = os.path.join("data", "hypno_deep.csv")
df = read_data(path_data)

# We get the user inputs from the sidebar
n_recommendations, artist_selected, track_selected, arg_key, arg_bpm = sidebar(df)
df_artist_track_features = get_artist_track_features(df, artist_selected, track_selected) 

# We query the artist + track data from Spotify API
response = search_artist_track(sp, artist_selected, track_selected)

# We print the header
head_introduction()

# We show the user their selected track
body_selection(response, df_artist_track_features, key_mapping, mode_mapping)

# We print the header for the recommendations section
head_recommendations()

# We get recommendations
#df_recommendations = df.sample(n_recommendations)
df_recommendations = get_recommendations(n_recommendations, df, df_artist_track_features, arg_key, arg_bpm)

# We create columns to present the recommendations
columns_mapping = {1: 3,
                   3: 3,
                   5: 5}
columns = st.columns(columns_mapping[n_recommendations])

for cnt, artist in enumerate(df_recommendations.index):
    df_artist_track_features_recommendation = df_recommendations.loc[artist].to_frame().T
    artist_recommended = df_artist_track_features_recommendation.index[0]
    track_recommended = df_artist_track_features_recommendation['track_name'][0]

    df_artist_track_features_recommended = get_artist_track_features(df, artist_recommended, track_recommended) 

    response = search_artist_track(sp, artist_recommended, track_recommended)
    
    # If we only have a single recommendation we always use the middle columns
    if n_recommendations == 1:
        with columns[1]:
            body_recommendation(response, df_artist_track_features_recommended, key_mapping, mode_mapping)
    else:
        with columns[cnt]:
            body_recommendation(response, df_artist_track_features_recommended, key_mapping, mode_mapping)