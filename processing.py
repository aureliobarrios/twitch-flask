import json
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.metrics import pairwise_distances
# from scipy.spatial.distance import cosine

data = pd.read_csv("data/twitch_data.csv")


def calculate_mode(number_list):

    twitter_handles = []

    names_list = list(data['twitter_handle'])
    twitter_list = list(data['lower_handles'])
    twitch_list = list(data['lower_channel'])

    for name in number_list:
        name = name.lower()
        curr_index = 0
        if name.lower() in twitter_list:
            #means given twitter handle
            curr_index = twitter_list.index(name)
        elif name.lower() in twitch_list:
            #means given twitch channel
            curr_index = twitch_list.index(name)

        twitter_name = names_list[curr_index]

        if twitter_name not in twitter_handles:
            twitter_handles.append(twitter_name)

    streamer_data = [twitter_handles] + json.load(open('data/connections.json'))

    streamers = sorted(list(data['twitter_handle']))

    def build_vector(streamer_list):
        return np.array([1 if streamer in streamer_list else 0 for streamer in streamers])

    streamer_matrix = np.array(list((map(build_vector, streamer_data))))

    item_matrix = np.array([[streams_followed[i] for streams_followed in streamer_matrix]
                  for i, _ in enumerate(streamers)])

    items = 1 - pairwise_distances(item_matrix, metric='cosine')

    def get_similar_items(curr_item):
        item_pairs = [(streamers[other_item], similarity)
                     for other_item, similarity in enumerate(items[curr_item])
                     if curr_item != other_item and similarity > 0]
        return sorted(item_pairs, key=lambda x: x[1], reverse=True)

    def recommend_item(curr_user, add_self_items=False, num_rec=5):
        rec_streamers = defaultdict(float)
        curr_user_streamers = streamer_matrix[curr_user]
        for curr_item, follows in enumerate(curr_user_streamers):
            if follows:
                similar_streams = get_similar_items(curr_item)
                for streamer, similarity in similar_streams:
                    rec_streamers[streamer] += similarity
        rec_streamers = sorted(rec_streamers.items(), key=lambda x: x[1], reverse=True)
        if add_self_items:
            return [streamer for streamer, _ in rec_streamers][:num_rec]
        else:
            return [streamer for streamer, _ in rec_streamers
                   if streamer not in streamer_data[curr_user]][:num_rec]

    recommended = recommend_item(0)

    img_df = pd.read_csv('data/profile_img.csv')
    image_list = []
    for handle in recommended:
        curr_df = img_df[img_df['twitter_handle'] == handle]
        other_df = data[data['twitter_handle'] == handle]
        image_list.append([handle, curr_df.iloc[0].profile_img_original, other_df.iloc[0].channel])

    return image_list
    # return "The streamers we recommend you follow are: {}".format(' '.join(recommended))



