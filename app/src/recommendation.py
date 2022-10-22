import numpy as np
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


def get_recommendations(n_recommendations, df, df_artist_track_features, arg_key, arg_bpm):
    df_filter = df.copy(deep=True)

    # We filter by key
    if arg_key:
        current_key = df_artist_track_features['key'][0]
        key_match_idx = df_filter['key'] == current_key

        df_filter = df_filter.loc[key_match_idx]

    if arg_bpm:
        # We fix the bpm for all artists
        all_bpm_list = np.array([round(float(x), 2) for x in df_filter['tempo']])

        bpm_match_idx = (all_bpm_list >= arg_bpm[0]) & (all_bpm_list <= arg_bpm[1])

        df_filter = df_filter.loc[bpm_match_idx]

    # We add the df_artist_track_features to the df_filter
    df_filter = pd.concat([df_filter, df_artist_track_features], axis=0)

    # We drop duplicates in case we add an already existing track
    df_filter.drop_duplicates(subset=['track_name'], inplace=True)

    ############# MODEL BASED APPROACH #############
    # Load the model
    # model = load_model()

    # # We get the features
    # X_selection = get_features(df_artist_track_features)
    # X_recommendations = get_features(df_filter)

    # # We get the prediction
    # y_selection = get_prediction(model, X_selection)
    # y_recommendations = get_prediction(model, X_recommendations)

    # # Only get the rows in df_filter where the prediction is the same as the selection
    # df_filter = df_filter.loc[y_selection == y_recommendations]

    # # Sort the df_filter by popularity and return the top n_recommendations
    # df_filter.sort_values(by=['track_pop'], ascending=False, inplace=True)

    ############# COSINE SIMILARITY APPROACH #############
    features = ['artist_pop', 'track_pop', 'key', 'mode', 'tempo', 'time_signature', 'energy', 'danceability', 'instrumentalness']
    X = df_filter[features]

    # We want to get pandas dummy variables for key, mode and time_signature
    X = pd.get_dummies(X, columns=['key', 'mode', 'time_signature'])

    # We scale the data with StandardScaler
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # We calculate the cosine similarity
    cosine_sim = cosine_similarity(X)

    # Create a pandas dataframe with multiindex
    df_cosine_sim = pd.DataFrame(cosine_sim, index=df_filter.track_name, columns=df_filter.track_name)

    # We get the track name of the selection
    track_name = df_artist_track_features['track_name'][0]

    # We get the top n_recommendations track name from the cosine similarity for the track_name
    top_n_recommendations = df_cosine_sim[track_name].sort_values(ascending=False)[1:n_recommendations+1].index

    # We get the top n_recommendations from the df_filter
    df_filter = df_filter.loc[df_filter['track_name'].isin(top_n_recommendations)]

    return (df_filter)


# Write a function which loads the model in model/ and prepares to do a prediction
def load_model():
    # Load the model from the file
    model = pickle.load(open('model/model.pkl', 'rb'))
    return model


def predict(model, df):
    # Make a prediction
    prediction = model.predict(df)
    return prediction


def get_features(df):
    features = ['artist_pop', 'track_pop', 'energy', 'danceability', 'instrumentalness']
    X = df[features]
    return X


def get_prediction(model, X):
    prediction = model.predict(X)
    return prediction
