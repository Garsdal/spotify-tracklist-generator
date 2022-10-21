import numpy as np
import pickle


def get_recommendations(n_recommendations, df, df_artist_track_features, arg_key, arg_bpm):
    df_filter = df.copy(deep=True)

    # Load the model
    model = load_model()

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

    # We get the features
    X_selection = get_features(df_artist_track_features)
    X_recommendations = get_features(df_filter)

    # We get the prediction
    y_selection = get_prediction(model, X_selection)
    y_recommendations = get_prediction(model, X_recommendations)

    # Only get the rows in df_filter where the prediction is the same as the selection
    df_filter = df_filter.loc[y_selection == y_recommendations]

    # Sort the df_filter by popularity and return the top n_recommendations
    df_filter.sort_values(by=['track_pop'], ascending=False, inplace=True)

    return (df_filter.head(n_recommendations))


# Write a function which loads the model in model/ and prepares to do a prediction
def load_model():
    # Load the model from the file
    model = pickle.load(open('model/model.pkl', 'rb'))
    return model

# Write a function which takes in the model and the data and returns a prediction


def predict(model, df):
    # Make a prediction
    prediction = model.predict(df)
    return prediction

# Write a function which takes in a dataframe with audio features and returns X


def get_features(df):
    features = ['artist_pop', 'track_pop', 'energy', 'danceability', 'instrumentalness']
    X = df[features]
    return X

# Write a function which takes in features X and returns a prediction


def get_prediction(model, X):
    prediction = model.predict(X)
    return prediction
