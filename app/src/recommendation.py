import numpy as np

def get_recommendations(n_recommendations, df, df_artist_track_features, arg_key, arg_bpm):
    df_filter = df.copy(deep = True)

    # We filter by key
    if arg_key:
        current_key = df_artist_track_features['key'][0]
        key_match_idx = df_filter['key'] == current_key

        df_filter = df_filter.loc[key_match_idx]
    
    if arg_bpm:
        # We fix the bpm for all artists
        all_bpm_list = np.array([round(float("".join(x.split(".")[0:1])), 2) for x in df_filter['tempo']])

        bpm_match_idx = (all_bpm_list >= arg_bpm[0]) & (all_bpm_list <= arg_bpm[1])
        
        df_filter = df_filter.loc[bpm_match_idx]

    # We sort by popularity
    return(df_filter.head(n_recommendations))