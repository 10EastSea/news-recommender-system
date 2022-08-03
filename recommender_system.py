import sys
import os
import numpy as np
from tqdm import tqdm
import tensorflow as tf

tf.get_logger().setLevel('ERROR')  # only show error messages

from recommenders.models.deeprec.deeprec_utils import download_deeprec_resources
from recommenders.models.newsrec.newsrec_utils import prepare_hparams
from recommenders.models.newsrec.models.nrms import NRMSModel
from recommenders.models.newsrec.io.mind_iterator import MINDIterator
from recommenders.models.newsrec.newsrec_utils import get_mind_data_set
from recommenders.models.newsrec.newsrec_utils import word_tokenize


# add_to_user_history(news, mind_iterator=model.test_iterator)
def add_to_user_history(nid, mind_iterator):
    history = mind_iterator.histories[0]
    history = list(filter(lambda x: x != 0, history))
    history.append(mind_iterator.nid2index[nid])

    history = [0] * (mind_iterator.his_size - len(history)) + history[
                                                              -mind_iterator.his_size :
                                                              ]
    mind_iterator.histories[0] = history


def init_model(data_path, impr_file) -> NRMSModel:
    epochs = 5
    seed = 42
    batch_size = 32

    # Options: demo, small, large
    MIND_type = 'large'

    train_news_file = os.path.join(data_path, 'train', r'news.tsv')
    train_behaviors_file = os.path.join(data_path, 'train', r'behaviors.tsv')
    user_behaviors_file = os.path.join(data_path, r'user_behaviors.csv')
    valid_news_file = os.path.join(data_path, 'valid', r'news.tsv')
    valid_behaviors_file = os.path.join(data_path, 'valid', r'behaviors.tsv')
    wordEmb_file = os.path.join(data_path, "utils", "embedding.npy")
    userDict_file = os.path.join(data_path, "utils", "uid2index.pkl")
    wordDict_file = os.path.join(data_path, "utils", "word_dict.pkl")
    yaml_file = os.path.join(data_path, "utils", r'nrms.yaml')

    mind_url, mind_train_dataset, mind_dev_dataset, mind_utils = get_mind_data_set(MIND_type)

    if not os.path.exists(train_news_file):
        download_deeprec_resources(mind_url, os.path.join(data_path, 'train'), mind_train_dataset)

    if not os.path.exists(valid_news_file):
        download_deeprec_resources(mind_url, os.path.join(data_path, 'valid'), mind_dev_dataset)

    if not os.path.exists(yaml_file):
        download_deeprec_resources(r'https://recodatasets.z20.web.core.windows.net/newsrec/',
                                   os.path.join(data_path, 'utils'), mind_utils)

    hparams = prepare_hparams(yaml_file,
                              wordEmb_file=wordEmb_file,
                              wordDict_file=wordDict_file,
                              userDict_file=userDict_file,
                              batch_size=batch_size,
                              epochs=epochs,
                              show_step=10)

    iterator = MINDIterator

    model = NRMSModel(hparams, iterator, seed=seed)
    model_data_path = os.path.join(data_path, 'models', r'nrms_ckpt')
    model.model.load_weights(model_data_path)

    model.test_iterator.init_news(train_news_file)
    model.test_iterator.init_behaviors(user_behaviors_file)
    change_impr(model, data_path, impr_file)

    news_vecs = model.run_news(train_news_file)

    return model, news_vecs


# it returns top 10 news from news candidates pool.
def get_recommendation(model: NRMSModel, news_vecs, data_path):
    train_news_file = os.path.join(data_path, 'train', r'news.tsv')
    user_behaviors_file = os.path.join(data_path, r'user_behaviors.csv')

    group_impr_indexes, group_labels, group_preds = model.run_fast_eval(train_news_file, user_behaviors_file, news_vecs)

    import time
    start = time.time()
    for impr_index, preds in tqdm(zip(group_impr_indexes, group_preds)):
        pred_rank = (np.argsort(np.argsort(preds)[::-1]) + 1).tolist()
        recommendation = [None] * 10

        for i, rank in enumerate(pred_rank):
            if rank < 11:
                news_idx = model.test_iterator.imprs[0][i]
                recommendation[rank - 1] = model.test_iterator.index2nid[news_idx]

    
    print(time.time() - start)
    print(recommendation)
    return recommendation

def change_impr(model, data_path, file_name):
    impr_file = os.path.join(data_path, 'result_11to15', file_name)
    impr = []

    with open(impr_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            impr.append(model.test_iterator.nid2index[line.strip()])

    label = [0] * len(impr)

    model.test_iterator.imprs[0] = impr
    model.test_iterator.labels[0] = label


# data_path = './recommenders/MIND_dataset'
# model, news_vecs = init_model(data_path, impr_file='2019-11-11.tsv')
# get_recommendation(model, news_vecs, data_path)
# change_impr(model, data_path, file_name='2019-11-12.tsv')
# get_recommendation(model, news_vecs, data_path)
# add_to_user_history('N25434', model.test_iterator)
# add_to_user_history('N97703', model.test_iterator)
# get_recommendation(model, news_vecs, data_path)

