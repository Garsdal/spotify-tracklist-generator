import os
import pandas as pd
import streamlit as st

from src.page_content import head_introduction, head_recommendations, head_tracklist, sidebar, body_selection, body_input_spotify_url, body_recommendation, body_tracklist
from src.utils import set_bg, read_data, load_config, setup_spotify_credentials_manager, set_up_audio_instance
from src.processing import api_call_get_track_from_artist_track, api_call_get_track_from_url, get_artist_track_features_from_response, get_artist_track_features_from_local_data
from src.recommendation import get_recommendations

############### APP ################

# Init
st.session_state['click'] = False

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
path_data = os.path.join("data", "track_audio_features.csv")
df = read_data(path_data)

# We get the user inputs from the sidebar
n_recommendations, arg_key, arg_bpm = sidebar()

# We print the header
head_introduction()

# We print the input body
track_url = body_input_spotify_url()

# We query a track
response_track = api_call_get_track_from_url(sp, track_url)

# We get the artist track features for the specific track
df_artist_track_features = get_artist_track_features_from_response(sp, response_track)

# We show the user their selected track
body_selection(response_track, df_artist_track_features, key_mapping, mode_mapping)

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

    df_artist_track_features_recommended = get_artist_track_features_from_local_data(df, artist_recommended, track_recommended) 

    response_track = api_call_get_track_from_artist_track(sp, artist_recommended, track_recommended)
    
    # If we only have a single recommendation we always use the middle columns
    if n_recommendations == 1:
        with columns[1]:
            click = body_recommendation(response_track, df_artist_track_features_recommended, key_mapping, mode_mapping)
    else:
        with columns[cnt]:
            click = body_recommendation(response_track, df_artist_track_features_recommended, key_mapping, mode_mapping)

# We get the user recommendation
artist_recommendation_selected = st.session_state['click']
print(artist_recommendation_selected)

# We print the header for the recommendations section
head_tracklist()