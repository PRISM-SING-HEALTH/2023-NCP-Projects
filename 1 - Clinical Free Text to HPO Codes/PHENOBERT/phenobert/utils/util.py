import torch
from torch.utils.data import Dataset, DataLoader
import json
import nltk
import re
import os
import numpy as np
import unicodedata
from nltk.tokenize import PunktSentenceTokenizer, TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

project_path = os.path.dirname(__file__)+"/"

# file path definition
hpo_json_path = project_path + "../data/hpo.json"
hpo_obo_path = project_path + "../data/hpo.obo"
GSCp_ann_path = project_path + "../data/GSC+/ann"
fasttext_model_path = project_path + "../embeddings/fasttext_pubmed.bin"
stopwords_file_path = project_path + "../data/stopwords.txt"
num2word_file_path = project_path + "../data/NUM.txt"
cnn_model_path = project_path + "../models/HPOModel_H/model_layer1.pkl"
bert_model_path = project_path + "../models/bert_model_max_triple.pkl"
device = torch.device("cuda:0" if torch.cuda.is_available() else torch.device("cpu"))
wnl = WordNetLemmatizer()

class HPO_class:
    """
    HPO节点类
    """

    def __init__(self, dic):
        # 解析dic
        self.id = dic["Id"]
        self.name = dic["Name"]
        self.alt_id = dic["Alt_id"]
        self.defination = dic["Def"]
        self.comment = dic["Comment"]
        self.synonym = dic["Synonym"]
        self.xref = dic["Xref"]
        self.is_a = dic["Is_a"]
        self.father = set(dic["Father"].keys())  # 祖先
        self.child = set(dic["Child"].keys())  # 子孙
        self.son = set(dic["Son"].keys())


class PhraseDataSet4trainCNN(Dataset):
    """
    构造HPOModel的L1层的DataSet；训练用
    """

    def __init__(self, file_path, fasttext_model, hpo_tree, num_class):
        self.data = []
        self.hpo_tree = hpo_tree
        self.max_seq_len = 30  # 整个数据集最长长度
        self.fasttext_model = fasttext_model
        self.embedding_dim = self.fasttext_model.get_dimension()
        self.num_class = num_class
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                inter = line.strip().split("\t")
                phrase = processStr(inter[0])
                self.data.append([phrase, inter[0], inter[1]])
        # print("We got max sequence length %d ." % self.max_seq_len)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # data: [[word1, word2, ... in phrase], hpo_num_idx]
        phrase, sentence, hpo_num = self.data[idx]
        # [len(phrase), embedding_dim]
        data = np.concatenate([self.fasttext_model.get_word_vector(word).reshape(1, -1) for word in phrase])
        pad_data = np.zeros(shape=(self.max_seq_len, data.shape[1]))
        pad_data[:data.shape[0]] = data
        seq_len = data.shape[0]
        # mask矩阵
        # mask = np.zeros((self.max_seq_len, self.expand_dim))
        # mask[data.shape[0]:]=np.ones_like(mask[data.shape[0]:])
        l1_indexs = [self.hpo_tree.getHPO2idx_l1(i) for i in self.hpo_tree.getLayer1HPOByHPO(hpo_num)]
        target = torch.zeros(self.num_class + 1).index_fill(0, torch.tensor(l1_indexs), torch.tensor(1).long())
        sample = {"data": pad_data, "seq_len": seq_len, "target": target, "phrase": sentence, "hpo_num": hpo_num}
        return sample


class PhraseDataSet4trainCNN_sub(Dataset):
    """
    构造HPOModel的L1以下子模型的DataSet；训练用
    """

    def __init__(self, file_path, fasttext_model, hpo2idx):
        self.data = []
        self.max_seq_len = 30  # 整个数据集最长长度
        self.fasttext_model = fasttext_model
        self.embedding_dim = self.fasttext_model.get_dimension()
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                inter = line.strip().split("\t")
                phrase = processStr(inter[0])
                if inter[1] in hpo2idx:
                    hpo_num_idx = hpo2idx[inter[1]]
                else:
                    hpo_num_idx = hpo2idx["None"]
                self.data.append([phrase, hpo_num_idx, inter[0]])
        # print("We got max sequence length %d ." % self.max_seq_len)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # data: [[word1, word2, ... in phrase], hpo_num_idx]
        phrase, hpo_num_idx, sentence = self.data[idx]
        # [len(phrase), embedding_dim]
        data = np.concatenate([self.fasttext_model.get_word_vector(word).reshape(1, -1) for word in phrase])
        pad_data = np.zeros(shape=(self.max_seq_len, data.shape[1]))
        pad_data[:data.shape[0]] = data
        seq_len = data.shape[0]
        sample = {"data": pad_data, "seq_len": seq_len, "target": hpo_num_idx, "phrase": sentence}
        return sample


class PhraseDataSet4predict(Dataset):
    """
    构造HPOModel的L1层的DataSet；预测用
    """

    def __init__(self, phrase_list, fasttext_model):
        self.data = []
        self.phrase_list = []
        self.max_seq_len = 30  # 整个数据集最长长度
        self.fasttext_model = fasttext_model
        self.embedding_dim = self.fasttext_model.get_dimension()

        for phrase_item in phrase_list:
            if isinstance(phrase_item, PhraseItem):
                p_phrase = processStr(phrase_item.toString())
            elif isinstance(phrase_item, str):
                p_phrase = processStr(phrase_item)
            else:
                p_phrase = ""
            if len(p_phrase) > 0:
                self.phrase_list.append(phrase_item)
                self.data.append(p_phrase)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        p_phrase = self.data[idx]
        # [len(phrase), embedding_dim]
        data = np.concatenate([self.fasttext_model.get_word_vector(word).reshape(1, -1) for word in p_phrase])
        pad_data = np.zeros(shape=(self.max_seq_len, data.shape[1]))
        pad_data[:data.shape[0]] = data
        seq_len = data.shape[0]
        sample = {"data": pad_data, "seq_len": seq_len}
        return sample


def PhraseDataSet4predictFunc(phrase_item, fasttext_model, max_seq_len=30):
    """
    构造HPOModel的L1以下子模型的DataSet；预测用
    :param phrase_item:
    :param fasttext_model:
    :param max_seq_len:
    :return:
    """
    if isinstance(phrase_item, PhraseItem):
        p_phrase = processStr(phrase_item.toString())
    elif isinstance(phrase_item, str):
        p_phrase = processStr(phrase_item)
    else:
        p_phrase = ""
    if len(p_phrase) == 0:
        return None
    data = np.concatenate([fasttext_model.get_word_vector(word).reshape(1, -1) for word in p_phrase])
    pad_data = np.zeros(shape=(max_seq_len, data.shape[1]))
    pad_data[:data.shape[0]] = data
    return [torch.tensor(pad_data).unsqueeze(0).float().to(device), None]


class PhraseDataSet4trainBERT(Dataset):
    """
    产生HPOModel的Training的DataSet；适用BERT Encoder
    """

    def __init__(self, file_path, hpo2idx):
        self.data = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                inter = line.strip().split("\t")
                phrase = inter[0]
                hpo_num_idx = hpo2idx[inter[1]]
                self.data.append([phrase, hpo_num_idx])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        phrase, hpo_num_idx = self.data[idx]
        sample = {"phrase": phrase, "target": hpo_num_idx}
        return sample


class WordItem:
    """
    英文单词的包装类
    """
    # 用于lemmatize
    lemma_dict = {}
    def __init__(self, text, start, end):
        self.text = text.lower()
        self.start = start
        self.end = end

def getNum2Word(file_path):
    Num2Word = {}
    with open(file_path, encoding="utf-8") as file:
        for line in file:
            inter = line.strip().split("\t")
            Num2Word[inter[0]] = inter[1]
    return Num2Word

class PhraseItem:
    """
    英文短语的包装类，包含了文本信息和起止点信息
    """

    Num2Word = getNum2Word(num2word_file_path)
    StopWords = stopwords.words("english")

    def __init__(self, word_items):
        self.word_items = word_items
        self.simple_items = []
        self.simplify()
        self.locs_set = set([i.start for i in word_items])
        self.start_loc = self.word_items[0].start
        self.end_loc = self.word_items[-1].end
        self.no_flag = False


    def simplify(self):
        """
        对phrase_item进行简化，去除常用词以及替换数字
        :return:
        """
        for word_item in self.word_items:
            if word_item.text in PhraseItem.Num2Word:
                self.simple_items.append(WordItem(PhraseItem.Num2Word[word_item.text], word_item.start, word_item.end))
            elif word_item.text in PhraseItem.StopWords or isNum(word_item.text):
                continue
            else:
                self.simple_items.append(word_item)


    def toString(self):
        return " ".join([i.text for i in self.word_items])

    def toSimpleString(self):
        return " ".join([i.text for i in self.simple_items])

    def include(self, phrase_item):
        if self.locs_set.issubset(phrase_item.locs_set) or self.locs_set.issuperset(phrase_item.locs_set):
            return True
        return False

    def issubset(self, phrase_item):
        if self.locs_set.issubset(phrase_item.locs_set):
            return True
        return False

    def set_no_flag(self):
        self.no_flag = True

    def __len__(self):
        return len(self.word_items)


class HPOTree:
    """
    构造HPO有向无环图结构的类；默认以HP:0000118为根节点
    """

    def __init__(self):
        with open(hpo_json_path, encoding="utf-8") as json_file:
            self.data = json.loads(json_file.read())

        # # 统计phenotypic abnomality下的分布
        # tmp_list = [[HPO_class(self.data[i]).name, len(HPO_class(self.data[i]).child)] for i in
        #             HPO_class(self.data["HP:0000118"]).son]
        # tmp_list = sorted(tmp_list, key=lambda x: x[1], reverse=True)
        # print(tmp_list)

        # print(HPO_class(self.data["HP:0000001"]).father)
        # print("HP:0000001" in HPO_class(self.data["HP:0000001"]).child)

        self.root = "HP:0000118"
        self.phenotypic_abnormality = HPO_class(self.data[self.root]).child
        # 没有root的HPO表型异常节点集合
        self.phenotypic_abnormalityNT = set(list(self.phenotypic_abnormality))
        self.phenotypic_abnormality.add(self.root)
        # get MIN node depth in HP:0000118(0) （due to a concept may has multi-inheritance）
        self.hpo_list = sorted(list(self.phenotypic_abnormality))
        self.n_concept = len(self.hpo_list)
        self.hpo2idx = {hpo: idx for idx, hpo in enumerate(self.hpo_list)}
        # Add None
        self.hpo2idx["None"] = len(self.hpo_list)
        self.idx2hpo = {self.hpo2idx[hpo]: hpo for hpo in self.hpo2idx}
        self.alt_id_dict = {}
        self.p_phrase2HPO = {}  # 用于短语的直接对应
        self.depth = 0  # 根节点深度为0
        self.layer1 = sorted(list(HPO_class(self.data[self.root]).son))  # 所有的layer1
        self.layer1_set = set(self.layer1)
        self.n_concept_l1 = len(self.layer1)
        self.hpo2idx_l1 = {hpo: idx for idx, hpo in enumerate(self.layer1)}
        # Add None
        self.hpo2idx_l1["None"] = len(self.layer1)
        self.idx2hpo_l1 = {self.hpo2idx_l1[hpo]: hpo for hpo in self.hpo2idx_l1}

        for hpo_name in self.data:
            struct = HPO_class(self.data[hpo_name])
            alt_ids = struct.alt_id
            for sub_alt_id in alt_ids:
                self.alt_id_dict[sub_alt_id] = hpo_name
            phrases = getNames(struct)
            for phrase in phrases:
                key = " ".join(sorted(processStr(phrase)))
                self.p_phrase2HPO[key] = hpo_name

    def buildHPOTree(self):
        """
        用BFS构建深度哈希对应表
        """

        self.depth_dict = {}
        queue = {self.root}
        visited = {self.root}
        depth = 0
        while len(queue) > 0:
            tmp = set()
            for node in queue:
                self.depth_dict[node] = depth
                son = HPO_class(self.data[node]).son
                for sub_node in son:
                    if sub_node not in visited:
                        visited.add(sub_node)
                        tmp.add(sub_node)
            queue = tmp
            depth += 1
        self.depth = depth - 1

    def getNameByHPO(self, hpo_num):
        """
        根据HPO号获得Concept Name
        :param hpo_num:
        :return:
        """
        return HPO_class(self.data[hpo_num]).name[0].lower()

    def getFatherHPOByHPO(self, hpo_num):
        """
        根据HPO号获得Concept的直属父节点的HPO号
        :param hpo_num:
        :return:
        """
        if hpo_num not in self.phenotypic_abnormalityNT:
            return None
        return HPO_class(self.data[hpo_num]).is_a

    def getLayer1HPOByHPO(self, hpo_num):
        """
        根据HPO号获得Concept的L1层祖先节点的HPO号
        :param hpo_num:
        :return:
        """
        if hpo_num not in self.phenotypic_abnormalityNT:
            return ["None"]
        if hpo_num in self.layer1_set:
            return [hpo_num]
        return list(self.layer1_set & HPO_class(self.data[hpo_num]).father)

    def getAllFatherHPOByHPO(self, hpo_num):
        """
        根据HPO号获得Concept的所有祖先节点的HPO号
        :param hpo_num:
        :return:
        """
        if hpo_num not in self.phenotypic_abnormalityNT:
            return set()
        return HPO_class(self.data[hpo_num]).father

    def getPhrasesByHPO(self, hpo_num):
        """
        根据HPO号获得Concept的Name & Synonyms
        :param hpo_num:
        :return:
        """
        return [i.lower() for i in getNames(HPO_class(self.data[hpo_num]))]

    def getAllPhrasesAbnorm(self):
        """
        获得所有表型异常Concept的Name & Synonyms
        :return:
        """
        phrases_list = []
        for hpo_name in self.hpo_list:
            names = getNames(HPO_class(self.data[hpo_name]))
            phrases_list.extend(names)
        return phrases_list

    def matchPhrase2HPO(self, phrase):
        """
        给定短语获得可能对应的HPO号；在注释用于直接的字典对应方式
        :param phrase:
        :return:
        """
        p_phrase = " ".join(sorted(processStr(phrase)))
        p_l_phrase = " ".join([WordItem.lemma_dict[i] if i in WordItem.lemma_dict else i for i in p_phrase.split()])
        if p_phrase in self.p_phrase2HPO:
            return self.p_phrase2HPO[p_phrase]
        elif p_l_phrase in self.p_phrase2HPO:
            return self.p_phrase2HPO[p_l_phrase]
        return ""

    def getHPO2idx(self, hpo_num):
        """
        返回hpo_num在表型异常根节点下对应的idx
        """
        return self.hpo2idx[hpo_num]

    def getHPO2idx_l1(self, hpo_num):
        """
        返回hpo_num在layer1节点中的对应的idx
        """
        return self.hpo2idx_l1[hpo_num]

    def getIdx2HPO(self, idx):
        """
        返回idx在在表型异常根节点下对应的hpo_num
        """
        return self.idx2hpo[idx]

    def getIdx2HPO_l1(self, idx):
        """
        返回idx在layer1节点中的对应的hpo_num
        """
        return self.idx2hpo_l1[idx]

    def getMaterial4L1(self, root_l1):
        """
        返回给定的L1的hpo_num，获得以该L1节点为根节点所构建DAG的各项对应表
        :param root_l1:
        :return:
        """
        root_idx = self.getHPO2idx_l1(root_l1)
        hpo_list = HPO_class(self.data[root_l1]).child
        hpo_list.add(root_l1)
        hpo_list = sorted(hpo_list)
        n_concept = len(hpo_list)
        hpo2idx = {hpo: idx for idx, hpo in enumerate(hpo_list)}
        # Add None
        hpo2idx["None"] = len(hpo_list)
        idx2hpo = {hpo2idx[hpo]: hpo for hpo in hpo2idx}
        return root_idx, hpo_list, n_concept, hpo2idx, idx2hpo


    def getNodeSimilarityByID(self, hpoNum1, hpoNum2):
        """
        计算hpoNum1和hpoNum2的节点相似性，基于edge和information content
        默认采用基于edge的方式
        """
        # Use phenotypic abnomality only; ensure score >= 0.0
        if hpoNum1 not in self.phenotypic_abnormality or hpoNum2 not in self.phenotypic_abnormality:
            return 0.0
        if hpoNum1 == self.root and hpoNum2 == self.root:
            return 1.0
        # depth in HPO Tree
        depth1 = self.depth_dict[hpoNum1]
        # print(depth1)    # HP:0000118 depth 0
        depth2 = self.depth_dict[hpoNum2]
        struct1 = HPO_class(self.data[hpoNum1])
        struct2 = HPO_class(self.data[hpoNum2])
        # get LCS
        father1 = struct1.father
        father1.add(hpoNum1)
        father2 = struct2.father
        father2.add(hpoNum2)
        ancestor = father1 & father2
        LCS = \
            sorted([[a, self.depth_dict[a]] for a in ancestor if a in self.phenotypic_abnormality], key=lambda x: x[1],
                   reverse=True)[0][0]
        depth3 = self.depth_dict[LCS]
        struct3 = HPO_class(self.data[LCS])
        # Edge-based score
        eb_score = 2 * depth3 / (depth1 + depth2)
        return eb_score

        # # Info-based score
        # pc1=(len(struct1.child)+1)/len(self.phenotypic_abnormality)
        # pc2=(len(struct2.child)+1)/len(self.phenotypic_abnormality)
        # pc3=(len(struct3.child)+1)/len(self.phenotypic_abnormality)
        # ib_score = 2*math.log2(pc3)/(math.log2(pc1)+math.log2(pc2))
        # return ib_score


    def getHPO_set_similarity_max(self, hpo_set1, hpo_set2):
        """
        计算HPO集合之间的相似性；使用最大值计算方式
        :param hpo_set1:
        :param hpo_set2:
        :return:
        """
        if len(hpo_set1) == 0 and len(hpo_set2) == 0:
            return 1.0
        if len(hpo_set1) == 0 or len(hpo_set2) == 0:
            return 0.0
        part1 = 0.0
        for hpo_num1 in hpo_set1:
            if hpo_num1 in hpo_set2:
                continue
            tmp = 0
            for hpo_num2 in hpo_set2:
                s_score = self.getNodeSimilarityByID(hpo_num1, hpo_num2)
                if s_score > tmp:
                    tmp = s_score
            part1 += 1 - tmp

        part2 = 0.0
        for hpo_num2 in hpo_set2:
            if hpo_num2 in hpo_set1:
                continue
            tmp = 0
            for hpo_num1 in hpo_set1:
                s_score = self.getNodeSimilarityByID(hpo_num1, hpo_num2)
                if s_score > tmp:
                    tmp = s_score
            part2 += 1 - tmp

        return 1 - ((part1 + part2) / len(hpo_set1 | hpo_set2))


    def getAdjacentMatrixAncestors(self, root_l1, num_nodes):
        """
        产生考虑所有祖先节点的邻接矩阵
        self.getAdjacentMatrixAncestorsAssist为辅助函数
        """
        import scipy.sparse as ss
        root_idx, hpo_list, n_concept, hpo2idx, idx2hpo = self.getMaterial4L1(root_l1)
        ancestors_weight = {}
        for hpo_num in hpo_list:
            concept_id = hpo2idx[hpo_num]
            self.getAdjacentMatrixAncestorsAssist(ancestors_weight, concept_id, hpo2idx, idx2hpo)
        sparse_indexes = []
        sparse_values = []
        for concept_id in ancestors_weight:
            sparse_indexes.extend([[concept_id, ancestor_id] for ancestor_id in ancestors_weight[concept_id]])
            sparse_values.extend([ancestors_weight[concept_id][ancestor_id]
                                  for ancestor_id in ancestors_weight[concept_id]])

        indices = np.array(sparse_indexes)
        A = ss.coo_matrix((np.array(sparse_values), (indices[:, 0], indices[:, 1])),
                          shape=(num_nodes, num_nodes), dtype=np.float)
        return A.tocoo()

    def getAdjacentMatrixAncestorsAssist(self, ancestors_weight, concept_id, hpo2idx, idx2hpo):
        if concept_id in ancestors_weight:
            return ancestors_weight[concept_id].keys()
        ancestors_weight[concept_id] = {concept_id: 1.0}
        fathers = [i for i in HPO_class(self.data[idx2hpo[concept_id]]).is_a if i in hpo2idx]
        for father_hpo_num in fathers:
            father_id = hpo2idx[father_hpo_num]
            ancestors = self.getAdjacentMatrixAncestorsAssist(ancestors_weight, father_id, hpo2idx, idx2hpo)
            for ancestor_id in ancestors:
                if ancestor_id not in ancestors_weight[concept_id]:
                    ancestors_weight[concept_id][ancestor_id] = 0.0
                ancestors_weight[concept_id][ancestor_id] += ancestors_weight[father_id][ancestor_id] / len(fathers)
        return ancestors_weight[concept_id].keys()


class SpanTokenizer:
    """
    基于NLTK工具包，自定义一个详细版本的Tokenizer
    """

    def __init__(self):
        self.tokenizer_big = PunktSentenceTokenizer()
        self.tokenizer_small = TreebankWordTokenizer()

    def tokenize(self, text):
        result = []
        sentences_span = self.tokenizer_big.span_tokenize(text)
        for start, end in sentences_span:
            sentence = text[start:end]
            tokens_span = self.tokenizer_small.span_tokenize(sentence)
            for token_start, token_end in tokens_span:
                result.append([start + token_start, start + token_end])
        return result


class ModelSaver:
    """
    保存整个模型/仅保存模型参数
    """

    def __init__(self, model_save_path):
        self.model_save_path = model_save_path

    def save(self, model, params_only=False):
        if params_only:
            torch.save(model.state_dict(), self.model_save_path)
        else:
            torch.save(model, self.model_save_path)
        print("Model saved.")


class ModelLoader:
    """
    加载整个模型/仅加载模型参数
    """

    def __init__(self):
        pass

    def load_params(self, empty_model, model_save_path):
        empty_model.load_state_dict(torch.load(model_save_path))
        print("Model saved.")

    def load_all(self, model_save_path):
        if torch.cuda.is_available():
            return torch.load(model_save_path)
        return torch.load(model_save_path, map_location=torch.device('cpu'))


class EarlyStopping:
    """
    Early stops the training if validation loss doesn't improve after a given patience.
    Change from  https://github.com/Bjarten/early-stopping-pytorch/blob/master/pytorchtools.py
    """

    def __init__(self, patience=7, verbose=False, delta=0, path='checkpoint.pt'):
        """
        Args:
            patience (int): How long to wait after last time validation loss improved.
                            Default: 7
            verbose (bool): If True, prints a message for each validation loss improvement.
                            Default: False
            delta (float): Minimum change in the monitored quantity to qualify as an improvement.
                            Default: 0
            path (str): Path for the checkpoint to be saved to.
                            Default: 'checkpoint.pt'
        """
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
        self.path = path
        self.flag = False

    def __call__(self, score, model):

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(score, model)
        elif score < self.best_score + self.delta:
            self.counter += 1
            print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(score, model)
            self.counter = 0

    def save_checkpoint(self, score, model):
        """
        Saves model when validation loss decrease.
        """
        if self.verbose:
            print(f'Validation loss decreased ({self.best_score:.4f} --> {score:.4f}).  Saving model ...')
        torch.save(model, self.path)


def getNames(struct):
    """
    返回某一hpo结构中的name+synonym，并简单处理
    """
    # 训练集中同义词部分
    names = struct.name
    synonyms = struct.synonym
    # all name + synonym
    names.extend(synonyms)
    # 去重
    names = list(set(names))
    return names


def strip_accents(s):
    """
    去除口音化，字面意思
    :param s:
    :return:
    """
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def processStr(string):
    """
    输入字符串，返回经过符号处理的小写的word list
    :param string:
    :return:
    """
    string = re.sub("(?<=[A-Z])-(?=[\d])", "", string)  # 统一类型表述
    string = strip_accents(string.lower())
    string = re.sub("[-_\"\'\\\\\t\r\n‘’]", " ", string)
    all_text = string.strip().split()
    return all_text


def isNum(strings):
    """
    判断给定字符串是否为数字
    :param strings:
    :return:
    """
    try:
        float(strings)
        return True
    except ValueError:
        return False


def containNum(strings):
    """
    判断给定字符串是否包含数字
    :param strings:
    :return:
    """
    for c in strings:
        if c.isdigit():
            return True
    return False


def getStopWords():
    """
    返回stopwords_file_path给定的stop words
    :return:
    """
    stopwords = set()
    with open(stopwords_file_path, encoding="utf-8") as file:
        for line in file:
            stopwords.add(line.strip())
    return stopwords


def getSpliters():
    """
    用于分割短句的分割词
    :return:
    """
    spliters = set([word for word, pos in nltk.pos_tag(stopwords.words('english')) if pos in {'CC', 'WP', 'TO', 'WDT'}]+[',', '.', ':', ';', '(', ')', '[', ']', '/'])
    return spliters


def getNegativeWords():
    negatives = {"no", "not", "none", "negative", "non", "never", "few", "lower", "fewer", "less", "barely",
                           "normal"}
    return negatives


def produceCandidateTriple(Candidate_hpos_sub_total, model, threshold):
    """
    使用BERT判断Candidate_phrases中哪个与raw_phrase语义最接近；基于最大值方式；适用于批量处理
    :param Candidate_hpos_sub_total: 输出的短语及候选HPO嵌套列表
    :param model:
    :param threshold: 用作该模型输出阈值
    :return:
    """
    from fastNLP.core.utils import _move_dict_value_to_device
    from fastNLP.core.utils import _get_model_device
    from fastNLP import DataSet
    from fastNLP import DataSetIter
    from my_bert_match import addWordPiece, addSeqlen, addWords, processItem, processNum
    p_Candidate_phrases = []
    phrase_nums_per_hpo = []
    Candidate_hpos = []
    for raw_phrase, Candidate_phrase, Candidate_hpos_sub in Candidate_hpos_sub_total:
        p_Candidate_phrases.extend([raw_phrase + "::" + item for item in Candidate_phrase])
        phrase_nums_per_hpo.append(len(Candidate_phrase))
        Candidate_hpos.append(Candidate_hpos_sub)
    Candidate_dataset = DataSet({"raw_words": p_Candidate_phrases})
    Candidate_dataset.apply(addWords, new_field_name="p_words")
    Candidate_dataset.apply(addWordPiece, new_field_name="t_words")
    Candidate_dataset.apply(processItem, new_field_name="word_pieces")
    Candidate_dataset.apply(processNum, new_field_name="word_nums")
    Candidate_dataset.apply(addSeqlen, new_field_name="seq_len")
    Candidate_dataset.field_arrays["word_pieces"].is_input = True
    Candidate_dataset.field_arrays["seq_len"].is_input = True
    Candidate_dataset.field_arrays["word_nums"].is_input = True
    test_batch = DataSetIter(batch_size=128, dataset=Candidate_dataset, sampler=None)

    outputs = []
    for batch_x, batch_y in test_batch:
        _move_dict_value_to_device(batch_x, batch_y, device=_get_model_device(model))
        outputs.append(model.forward(batch_x["word_pieces"], batch_x["word_nums"], batch_x["seq_len"])['pred'])
    outputs = torch.cat(outputs)
    outputs = torch.nn.functional.softmax(outputs, dim=1).cpu().detach().numpy()
    # print(outputs.size)
    results_2 = np.array([item[2] for item in outputs])
    results_1 = np.array([item[1] for item in outputs])

    # 按短语分组
    count = 0
    index = 0
    ans = []
    for group_num in phrase_nums_per_hpo:
        g_results_2 = results_2[index:index+group_num]
        g_results_1 = results_1[index:index+group_num]
        Candidate_hpos_sub = Candidate_hpos[count]
        index += group_num
        count += 1
        # 如果这里已经能找到精确匹配的就直接输出
        if max(g_results_2) >= threshold:
            ans.append([Candidate_hpos_sub[int(np.argmax(g_results_2))], max(g_results_2), "2"])
            continue
        # 找近似关系
        if max(g_results_1) >= threshold:
            ans.append([Candidate_hpos_sub[int(np.argmax(g_results_1))], max(g_results_1), "1"])
            continue
        ans.append(["None", None, "0"])
    return ans

def produceCandidateTripleSlow(raw_phrase, Candidate_phrases, model, Candidate_hpos_sub, threshold):
    """
    使用BERT判断Candidate_phrases中哪个与raw_phrase语义最接近；基于最大值方式；适用于单个处理
    """
    from fastNLP.core.utils import _move_dict_value_to_device
    from fastNLP.core.utils import _get_model_device
    from fastNLP import DataSet
    from fastNLP import DataSetIter
    from my_bert_match import addWordPiece, addSeqlen, addWords, processItem, processNum
    p_Candidate_phrases = [raw_phrase + "::" + item for item in Candidate_phrases]
    Candidate_dataset = DataSet({"raw_words": p_Candidate_phrases})
    Candidate_dataset.apply(addWords, new_field_name="p_words")
    Candidate_dataset.apply(addWordPiece, new_field_name="t_words")
    Candidate_dataset.apply(processItem, new_field_name="word_pieces")
    Candidate_dataset.apply(processNum, new_field_name="word_nums")
    Candidate_dataset.apply(addSeqlen, new_field_name="seq_len")
    Candidate_dataset.field_arrays["word_pieces"].is_input = True
    Candidate_dataset.field_arrays["seq_len"].is_input = True
    Candidate_dataset.field_arrays["word_nums"].is_input = True
    test_batch = DataSetIter(batch_size=10, dataset=Candidate_dataset, sampler=None)

    outputs = []
    for batch_x, batch_y in test_batch:
        _move_dict_value_to_device(batch_x, batch_y, device=_get_model_device(model))
        outputs.append(model.forward(batch_x["word_pieces"], batch_x["word_nums"], batch_x["seq_len"])['pred'])
    outputs = torch.cat(outputs)
    outputs = torch.nn.functional.softmax(outputs, dim=1).cpu().detach().numpy()

    results_2 = np.array([item[2] for item in outputs])
    results_1 = np.array([item[1] for item in outputs])

    # 如果这里已经能找到精确匹配的就直接输出
    if max(results_2) >= threshold:
        return Candidate_hpos_sub[int(np.argmax(results_2))], max(results_2), "2"

    if max(results_1) >= threshold:
        return Candidate_hpos_sub[int(np.argmax(results_1))], max(results_1), "1"

    return "None", None, "0"

def process_text2phrases(text, clinical_ner_model):
    """
    用于从文本中提取Clinical Text Segments
    :param text:自由文本
    :param clinical_ner_model: Stanza提供的预训练NER模型
    :return: List[PhraseItem]
    """
    tokenizer = SpanTokenizer()
    spliters = getSpliters()
    stopwords = getStopWords()
    # 将文本处理成正常的小写形式
    text = strip_accents(text.lower())
    text = re.sub("[-_\"\'\\\\\t‘’]", " ", text)
    # 对于换行符替换为句号，后续作为分割词
    text = re.sub("(?<=[\w])[\r\n]", ".", text)

    clinical_docs = clinical_ner_model(text)
    sub_sentences = []

    for sent_c in clinical_docs.sentences:
        clinical_tokens = sent_c.tokens

        # Stanza
        flag = False
        curSentence = []
        tmp = set()
        for i in range(len(clinical_tokens)):
            wi = WordItem(clinical_tokens[i].text, clinical_tokens[i].start_char, clinical_tokens[i].end_char)
            if "PROBLEM" in clinical_tokens[i].ner and wi.text not in {',', '.', ':', ';', '(', ')', '[', ']'}:
                curSentence.append(wi)
            else:
                if len(curSentence) > 0:
                    phrase_item = PhraseItem(curSentence)
                    sub_sentences.append(phrase_item)
                    tmp.update(phrase_item.locs_set)
                    flag = True
                curSentence = []

        if len(curSentence) > 0:
            phrase_item = PhraseItem(curSentence)
            sub_sentences.append(phrase_item)
            tmp.update(phrase_item.locs_set)
            flag = True

        # phrase segmentation
        # 只有Stanza标记的句子才作补充
        if not flag:
            continue
        curSentence = []
        for i in range(len(clinical_tokens)):
            wi = WordItem(clinical_tokens[i].text, clinical_tokens[i].start_char, clinical_tokens[i].end_char)
            # 用于后续lemma比对
            text_lemma = wnl.lemmatize(clinical_tokens[i].text)
            if clinical_tokens[i].text not in WordItem.lemma_dict:
                WordItem.lemma_dict[clinical_tokens[i].text] = text_lemma
            if clinical_tokens[i].text in spliters:
                if len(curSentence) > 0:
                    phrase_item = PhraseItem(curSentence)
                    # 只有不与Stanza重叠的部分才加入
                    if len(phrase_item.locs_set & tmp) == 0:
                        sub_sentences.append(phrase_item)
                curSentence = []
            else:
                curSentence.append(wi)

        if len(curSentence) > 0:
            phrase_item = PhraseItem(curSentence)
            if len(phrase_item.locs_set & tmp) == 0:
                sub_sentences.append(phrase_item)

    # 否定检测
    for phrase_item in sub_sentences:
        flag = False
        for token in phrase_item.word_items:
            if token.text.lower() in {"no", "not", "none", "negative", "non", "never", "few", "lower", "fewer", "less",
                                      "normal"}:
                flag = True
                break
        if flag:
            phrase_item.set_no_flag()

    # 省略恢复
    sub_sentences_ = []
    for idx, pi in enumerate(sub_sentences):
        # 将含有and, or, / 的短句用tokenize进行拆分
        sub_locs = [[i + pi.start_loc, j + pi.start_loc] for i, j in
                    tokenizer.tokenize(text[pi.start_loc:pi.end_loc])]
        sub_phrases = []
        curr_phrase = []
        # 把以and, or, / 分割的短语提出
        for loc in sub_locs:
            wi = WordItem(text[loc[0]:loc[1]], loc[0], loc[1])
            if wi.text in {"and", "or", "/"}:
                if len(curr_phrase) > 0:
                    sub_phrases.append(PhraseItem(curr_phrase))
                    sub_phrases[-1].no_flag = pi.no_flag
                curr_phrase = []
            else:
                curr_phrase.append(wi)
        if len(curr_phrase) > 0:
            sub_phrases.append(PhraseItem(curr_phrase))
            sub_phrases[-1].no_flag = pi.no_flag

        # 首先把原始分割的短语都加进去
        for item in sub_phrases:
            sub_sentences_.append(item)

        # 只考虑A+B形式的恢复
        if len(sub_phrases) == 2:
            if len(sub_phrases[0]) >= 1 and len(sub_phrases[1]) == 1:
                tmp = sub_phrases[0].word_items[:-1][:]
                tmp.extend(sub_phrases[1].word_items)
                sub_sentences_.append(PhraseItem(tmp))
                sub_sentences_[-1].no_flag = pi.no_flag
            elif len(sub_phrases[0]) == 1 and len(sub_phrases[1]) >= 1:
                tmp = sub_phrases[0].word_items[:]
                tmp.extend(sub_phrases[1].word_items[1:])
                sub_sentences_.append(PhraseItem(tmp))
                sub_sentences_[-1].no_flag = pi.no_flag

    sub_sentences = sub_sentences_

    # print([i.toSimpleString() for i in sub_sentences])

    # 穷举短语 删除纯数字
    phrases_list = []
    for pi in sub_sentences:
        tmp = pi.toSimpleString()
        if isNum(tmp) or len(tmp) <= 1:
            continue
        for i in range(len(pi.simple_items)):
            for j in range(10):
                if i + j == len(pi.simple_items):
                    break
                if len(pi.simple_items[i:i + j + 1]) == 1:
                    tmp_str = pi.simple_items[i:i + j + 1][0].text
                    if tmp_str in stopwords or isNum(tmp_str):
                        continue
                phrases_list.append(PhraseItem(pi.simple_items[i:i + j + 1]))
                phrases_list[-1].no_flag = pi.no_flag

    # print(len(phrases_list))
    # print([i.toString() for i in phrases_list])
    return phrases_list


def annotate_phrases(text, phrases_list, hpo_tree, fasttext_model, cnn_model, bert_model,
                     output_file_path, device, param1, param2, param3, use_longest, use_step_3):
    """
    注释一段文字
    :param text: 自由文本
    :param phrases_list: 经过短语提取后得到的短语列表，注意一般是去掉常用词后的k-mer形式
    :param hpo_tree: HPO Ontology的封装类
    :param fasttext_model: fastText预训练模型
    :param cnn_model: Layer1的CNN预训练模型
    :param bert_model: 用于判断Sentence Match的预训练模型
    :param output_file_path: 注释后的输出位置/返回字符串
    :param device: cpu or gpu
    :param use_longest: 是否只输出最具体的概念
    :param use_step_3: 是否增加Sentence Match步骤
    :return: None
    """

    result_list = []
    if output_file_path is not None:
        output_file = open(output_file_path, "w", encoding="utf-8")
    else:
        output_file = ""

    next_phrases_list = []
    for phrase_item in phrases_list:
        raw_phrase = phrase_item.toString()

        # Step 1: 字典对应；对于一个短语对应多个的情况我们给出任意一个
        d_match = hpo_tree.matchPhrase2HPO(raw_phrase)
        if d_match != "" and d_match in hpo_tree.phenotypic_abnormalityNT:  # 注意这里由于HPO版本不同，可能d_match!=tag
            # print(phrase_item.toString(), d_match)
            result_list.append([phrase_item, d_match, 1.0])
        else:
            # 如果已经由Step 1找出，则其内部短语均跳过
            flag = True
            for known_phrase_item, _, _ in result_list:
                if phrase_item.issubset(known_phrase_item):
                    flag = False
                    break
            if flag:
                next_phrases_list.append(phrase_item)

    # print([i.toString() for i in next_phrases_list])

    dataset = PhraseDataSet4predict(next_phrases_list, fasttext_model)
    dataloader = DataLoader(dataset, batch_size=256, shuffle=False)

    total_hpo_list = []
    total_hpo2idx = []
    total_idx2hpo = []
    total_model = []
    total_l1_root = hpo_tree.layer1
    for sub_l1_root in total_l1_root:
        # get idx2hpo hpo2idx for given HPO
        root_idx, hpo_list, n_concept, hpo2idx, idx2hpo = hpo_tree.getMaterial4L1(sub_l1_root)
        total_hpo_list.append(hpo_list)
        total_hpo2idx.append(hpo2idx)
        total_idx2hpo.append(idx2hpo)
        sub_model_save_path = f"PHENOBERT/phenobert/models/HPOModel_H/model_l1_{root_idx}.pkl"
        loader = ModelLoader()
        sub_model = loader.load_all(sub_model_save_path)
        sub_model.eval()
        total_model.append(sub_model)

    samples = 0

    with torch.no_grad():
        cnn_model.eval()
        bert_model.eval()

        for data in dataloader:
            # CNN input
            input_data = [data["data"].float().to(device), data["seq_len"].int().to(device)]
            batch_num = input_data[0].size(0)
            y = cnn_model(input_data)
            phrase_items = dataset.phrase_list[samples:samples + batch_num]
            samples += batch_num

            # Step 2: 基于显著性的Concept Generation

            if not use_step_3:

                # 按升序排序
                prediction = y.argsort().tolist()
                scores_p = y.sort()[0] >= param1
                Candidate_hpos = [
                    set([hpo_tree.getIdx2HPO_l1(prediction[idx1][idx2]) for idx2 in range(len(prediction[idx1])) if
                         scores_p[idx1][idx2]]) for idx1 in range(len(prediction))]
                for i, j in zip(phrase_items, Candidate_hpos):
                    if len(j) > 0 and "None" not in j:
                        Candidate_hpos_sub = []
                        for l1_hpo in j:
                            l1_idx = hpo_tree.getHPO2idx_l1(l1_hpo)
                            y_sub = total_model[l1_idx](PhraseDataSet4predictFunc(i, fasttext_model)).squeeze()
                            prediction_sub = y_sub.topk(5)[1].tolist()
                            scores_p_sub = torch.softmax(y_sub, dim=0).topk(5)[0].tolist()
                            Candidate_hpos_sub.extend(
                                [[total_idx2hpo[l1_idx][prediction_sub[idx]], scores_p_sub[idx]] for idx in
                                 range(len(prediction_sub)) if scores_p_sub[idx] >= param2])
                        Candidate_hpos_sub.sort(key=lambda x: x[1], reverse=True)
                        if len(Candidate_hpos_sub) != 0 and Candidate_hpos_sub[0][0] != "None":
                            result_list.append([i, Candidate_hpos_sub[0][0], Candidate_hpos_sub[0][1]])
            else:
                # 按升序排序
                prediction = y.argsort().tolist()
                scores_p = y.sort()[0]
                # 挑选每个短语超过阈值的L1层的HPO，超过0.8的我们才认为是预测正确的L1层
                Candidate_hpos = [
                    set([hpo_tree.getIdx2HPO_l1(prediction[idx1][idx2]) for idx2 in range(len(prediction[idx1])) if
                         scores_p[idx1][idx2] >= param1]) for idx1 in range(len(prediction))]

                Candidate_hpos_sub_total = []
                next_phrase_items = []
                for phrase_item, j in zip(phrase_items, Candidate_hpos):
                    # print(phrase_item.toString(), j)
                    if len(j) > 0 and "None" not in j:
                        Candidate_hpos_sub = set()
                        for l1_hpo in j:
                            l1_idx = hpo_tree.getHPO2idx_l1(l1_hpo)
                            y_sub = total_model[l1_idx](
                                PhraseDataSet4predictFunc(phrase_item, fasttext_model)).squeeze()
                            if y_sub.size(0) > 10:
                                prediction_sub = y_sub.topk(10)[1].tolist()
                                scores_p_sub = torch.softmax(y_sub, dim=0).topk(10)[0].tolist()
                            else:
                                prediction_sub = y_sub.topk(y_sub.size(0))[1].tolist()
                                scores_p_sub = torch.softmax(y_sub, dim=0).topk(y_sub.size(0))[0].tolist()
                            Candidate_hpos_sub.update(
                                [total_idx2hpo[l1_idx][prediction_sub[idx]] for idx in range(len(prediction_sub)) if
                                 scores_p_sub[idx] >= param2])

                            # for idx in range(len(prediction_sub)):
                            #     print(phrase_item.toString(), total_idx2hpo[l1_idx][prediction_sub[idx]], scores_p_sub[idx])

                        # print(phrase_item.toString(), Candidate_hpos_sub)

                        # Step 3: 基于BERT语义模型进行假阳性过滤
                        if len(Candidate_hpos_sub) != 0 and "None" not in Candidate_hpos_sub:
                            Candidate_hpos_sub = list(Candidate_hpos_sub)
                            candidate_phrase = [hpo_tree.getNameByHPO(item) for item in Candidate_hpos_sub]
                            raw_phrase = phrase_item.toString()
                            # print(raw_phrase, candidate_phrase)
                            Candidate_hpos_sub_total.append([raw_phrase, candidate_phrase, Candidate_hpos_sub])
                            next_phrase_items.append(phrase_item)
                if len(Candidate_hpos_sub_total) > 0:
                    ans = produceCandidateTriple(Candidate_hpos_sub_total, bert_model, param3)
                    for sub_ans, phrase_item in zip(ans, next_phrase_items):
                        if sub_ans[0] != "None":
                            result_list.append([phrase_item, sub_ans[0], sub_ans[1]])

        # 过滤结果/取长的短语
        idx_to_remove = set()

        for idx1 in range(len(result_list)):
            if idx1 in idx_to_remove:
                continue
            for idx2 in range(idx1 + 1, len(result_list)):
                if idx2 in idx_to_remove:
                    continue
                if result_list[idx1][0].include(result_list[idx2][0]):
                    if use_longest:
                        if len(result_list[idx1][0]) > len(result_list[idx2][0]):
                            idx_to_remove.add(idx2)
                        else:
                            idx_to_remove.add(idx1)
                    else:
                        if result_list[idx1][1] == result_list[idx2][1]:
                            if len(result_list[idx1][0]) > len(result_list[idx2][0]):
                                idx_to_remove.add(idx1)
                            else:
                                idx_to_remove.add(idx2)

        result_list = sorted([result_list[idx] for idx in range(len(result_list)) if idx not in idx_to_remove],
                             key=lambda x: x[0].start_loc)
		
		# 输出结果
        for item in result_list:
            if not item[0].no_flag:
                if output_file_path is not None:
                    output_file.write(
                        f"{item[0].start_loc}\t{item[0].end_loc}\t{text[item[0].start_loc:item[0].end_loc]}\t{item[1]}\t{'%.2f' % (item[2])}\n")
                else:
                    output_file += f"{item[0].start_loc}\t{item[0].end_loc}\t{text[item[0].start_loc:item[0].end_loc]}\t{item[1]}\t{'%.2f' % (item[2])}\n"
            else:
                if output_file_path is not None:
                    output_file.write(
                        f"{item[0].start_loc}\t{item[0].end_loc}\t{text[item[0].start_loc:item[0].end_loc]}\t{item[1]}\t{'%.2f' % (item[2])}\tNeg\n")
                else:
                    output_file += f"{item[0].start_loc}\t{item[0].end_loc}\t{text[item[0].start_loc:item[0].end_loc]}\t{item[1]}\t{'%.2f' % (item[2])}\tNeg\n"
        
        for term in result_list:
            term.append(hpo_tree.getNameByHPO(term[1]))

        if output_file_path is not None:
            output_file.close()
            return None
        else:
            return output_file, result_list