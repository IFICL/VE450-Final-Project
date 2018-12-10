import json
import tensorflow as tf
import numpy as np
import jieba
import jieba.posseg as pseg

modelPath = "models/model_iter1543910047-14.meta"
dataInfoAddr = "data/data_info.txt"
jsonAddr = "data/output.json"


aspect_word = {"环境": ["环境", "卫生", "厕所", "条件", "厕所", "被子", "空气", "小院", "房间",
                    "隔音", "枕头", "设施", "床铺", "设备", "住宿", "民宿", "人员", "旅馆",
                    "卫生间", "被套", "氛围", "气氛", "网络信号", "信号", "充电", "公共区域", "网速",
                    "网络", "舍友", "房子", "室内", "旅社"],
                "服务": ["老板", "服务", "阿姨", "大叔", "大婶", "小姐姐", "房东", "态度", "姐姐",
                    "老板娘", "安全", "房主", "店主", "管理", "餐饮", "店家", "小哥哥"],
                "地点": ["位置", "交通", "公交", "地点"],
                "性价比": ["价格", "性价比", "价位"]}


def get_data_info(save_fname):
    word2id, max_sentence_len, max_aspect_len = {}, 0, 0
    word2id['<pad>'] = 0
    with open(save_fname, 'r') as f:
        for line in f:
            content = line.strip().split()
            if len(content) == 3:
                max_sentence_len = int(content[1])
                max_aspect_len = int(content[2])
            else:
                word2id[content[0]] = int(content[1])
    return word2id, max_sentence_len, max_aspect_len


def commentTag(text, sess, sentences, aspects, sentence_lens, sentence_locs, labels, dropout_keep_prob, predict_label):
    aspectTerm = []
    aspectMain = []
    aspectSentiment = []
    words = pseg.cut(text)

    for word, flag in words:
        if(flag == "n" or flag == "vn" or flag == "v"):
            if word in aspect_word["环境"] and word not in aspectTerm:
                aspectMain.append("环境")
                aspectTerm.append(word)
            if word in aspect_word["服务"] and word not in aspectTerm:
                aspectMain.append("服务")
                aspectTerm.append(word)
            if word in aspect_word["性价比"] and word not in aspectTerm:
                aspectMain.append("性价比")
                aspectTerm.append(word)
            if word in aspect_word["地点"] and word not in aspectTerm:
                aspectMain.append("地点")
                aspectTerm.append(word)

    for aspectTermItem in aspectTerm:
        sentence, aspect, sentence_len, sentence_loc = process(text, aspectTermItem)
        feed = {
            sentences: [sentence],
            aspects: [aspect],
            sentence_lens: [sentence_len],
            sentence_locs: [sentence_loc],
            labels: [[0, 0, 0]],
            dropout_keep_prob: 1.0,
        }
        aspectSentiment.append(sess.run(predict_label, feed_dict=feed))

    js = {}
    js["items"] = []
    for i in range(len(aspectTerm)):
        abstractInfo = {}
        abstractInfo["prop"] = aspectMain[i]
        abstractInfo["detail"] = aspectTerm[i]
        abstractInfo["sentiment"] = aspectSentiment[i].tolist()[0]
        js["items"].append(abstractInfo)
    #js = json.dumps(js, ensure_ascii=False)
    return js


def process(text, aspectTerm):
    word2id, max_sentence_len, max_aspect_len = \
                                    get_data_info(dataInfoAddr)
    jieba.del_word('价格便宜')
    jieba.del_word('服务态度')
    jieba.del_word('地理位置')
    jieba.del_word('环境差')
    sptoks = jieba.cut(text, cut_all=False)
    sptoks = [sp for sp in sptoks]
    ids = []
    if len(sptoks) != 0:
        for sptok in sptoks:
            if sptok in word2id:
                ids.append(word2id[sptok])
    sentence = ids + [0] * (max_sentence_len - len(ids))
    aspect = [word2id[aspectTerm]]
    index = sptoks.index(aspectTerm)
    sentence_lens = len(sptoks)
    sentence_locs = [0]*index + [1] + [0]*(max_sentence_len-index-1)

    return sentence, aspect, sentence_lens, sentence_locs


def load_model():
    sess = tf.Session()
    print("load model")
    saver = tf.train.import_meta_graph(modelPath)
    saver.restore(sess, tf.train.latest_checkpoint('models/'))

    print("load graph")
    graph = tf.get_default_graph()
    #for op in graph.get_operations():
    #    print(op.name)
    sentences = graph.get_tensor_by_name("inputs/sentences:0")
    aspects = graph.get_tensor_by_name("inputs/aspects:0")
    sentence_lens = graph.get_tensor_by_name("inputs/sentence_lens:0")
    sentence_locs = graph.get_tensor_by_name("inputs/sentence_locs:0")
    labels = graph.get_tensor_by_name("inputs/labels:0")
    dropout_keep_prob = graph.get_tensor_by_name("inputs/dropout_keep_prob:0")
    predict_label = graph.get_tensor_by_name("predict/predict_label:0")

    return sess, sentences, aspects, sentence_lens, sentence_locs, labels, dropout_keep_prob, predict_label


if __name__ == "__main__":
    #text = "交通方便，你是猪，我也是猪。"
    #text2 = "我觉得这个交通很差，离地铁站很远"
    #text3 = "The food is really bad. However, the car is excellent."
    #text4 = "The sushi is very good."

    sess, sentences, aspects, sentence_lens, sentence_locs, labels, dropout_keep_prob, predict_label = load_model()


    while(1):
        text = input("input your comment: ")
        if text == "exit":
            break
        js = json.loads(commentTag(text, sess, sentences, aspects, sentence_lens, sentence_locs, labels, dropout_keep_prob, predict_label))
        for i in js["items"]:
            print(i)
