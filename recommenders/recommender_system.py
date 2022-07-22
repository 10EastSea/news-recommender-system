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

print("System version: {}".format(sys.version))
print("Tensorflow version: {}".format(tf.__version__))


# # news는 dict 형식으로 주어야 함
def add_to_news_candidate(news, mind_iterator):
    nid = news['nid']
    title = news['title']

    if nid in mind_iterator.nid2index:
        return

    mind_iterator.nid2index[nid] = len(mind_iterator.nid2index) + 1
    title = word_tokenize(title)

    news_title_vector = np.zeros(
        (1, mind_iterator.title_size), dtype="int32"
    )

    mind_iterator.news_title_index = np.concatenate((mind_iterator.news_title_index, news_title_vector))
    news_index = len(mind_iterator.news_title_index) - 1

    for word_index in range(min(mind_iterator.title_size, len(title))):
        if title[word_index] in mind_iterator.word_dict:
            mind_iterator.news_title_index[news_index, word_index] = mind_iterator.word_dict[
                title[word_index].lower()
            ]


def add_to_user_history(news, mind_iterator):
    history = mind_iterator.histories[0]
    history = list(filter(lambda x: x != 0, history))
    history.append(mind_iterator.nid2index[news['nid']])

    history = [0] * (mind_iterator.his_size - len(history)) + history[
                                                              : mind_iterator.his_size
                                                              ]

    mind_iterator.histories[0] = history


epochs = 5
seed = 42
batch_size = 32

# Options: demo, small, large
MIND_type = 'large'
data_path = './MIND_dataset'

train_news_file = os.path.join(data_path, 'train', r'news.tsv')
train_behaviors_file = os.path.join(data_path, 'train', r'behaviors.tsv')
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
model_data_path = './MIND_dataset/models/nrms_ckpt'
model.model.load_weights(model_data_path)

test_behaviors_file = './test_behaviors.csv'
model.test_iterator.init_news(train_news_file)
news_vecs = model.run_news(train_news_file)

model.test_iterator.init_behaviors(test_behaviors_file)

# news = {
#     'nid': 'N311233',
#     'title': 'The Brands Queen Elizabeth, Prince Charles, and Prince Philip Swear By',
# }

# add_to_news_candidate(news, mind_iterator=model.test_iterator)
# add_to_user_history(news, mind_iterator=model.test_iterator)
# model.test_iterator.imprs[0].append(model.test_iterator.nid2index[news['nid']])

group_impr_indexes, group_labels, group_preds = model.run_fast_eval(valid_news_file, test_behaviors_file, news_vecs)

with open(os.path.join('./', 'prediction.txt'), 'w') as f:
    for impr_index, preds in tqdm(zip(group_impr_indexes, group_preds)):
        impr_index += 1
        pred_rank = (np.argsort(np.argsort(preds)[::-1]) + 1).tolist()
        pred_rank = '[' + ','.join([str(i) for i in pred_rank]) + ']'
        f.write(' '.join([str(impr_index), pred_rank]) + '\n')
