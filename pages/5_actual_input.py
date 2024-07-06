import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import streamlit as st
# モジュールから必要なクラス及びオブジェクトを読み込む
from vitanaviclient import VitaNaviClient
from vitanaviclient.vector import apply_styles, apply_unordinary_mask
from vitanaviclient.params import vita_navi_available_model_name_list
# 属性マスタの参照
from vitanaviclient.params import vita_navi_attribute_def_map, vita_navi_attribute_def_map_by_attribute_name_jp

try:
    # 環境変数を本Notebookと同じ場所に置いた.envファイルから注入します
    from dotenv import load_dotenv

    load_dotenv(verbose=True)

except:
    # .envファイルが存在しないか、ライブラリpython-dotenvが見つかりませんでした
    # 注意: 必要なライブラリは `pip install python-dotenv` です。 `pip install dotenv` ではありません(別の不動ライブラリが入ります)。
    warnings.warn(
        "Cannot load environment values from .env file. If you need please run `pip install python-dotenv`",
    )

# 適宜名前変換用の関数を作成しておくと便利
def id2name(id):
    return vita_navi_attribute_def_map[id]["attributeNameJp"]


def name2id(name):
    return vita_navi_attribute_def_map_by_attribute_name_jp[name]["attributeId"]

# 日本語の解説があるものはその説明が出てくる
def id2description(id):
    return vita_navi_attribute_def_map[id]["descriptionJp"]

# 'label'から'value'を取得する関数
def get_value_from_label(label, data_list):
    for item in data_list:
        if item['label'] == label:
            return item['value']
    return None  # ラベルが見つからない場合はNoneを返す

# 'value'から'label'を取得する関数
def get_label_from_value(value, data_list):
    for item in data_list:
        if item['value'] == value:
            return item['label']
    return None  # ラベルが見つからない場合はNoneを返す

vita_navi_client = VitaNaviClient()

st.title('〇〇ポイントを算出するよ!!')

st.markdown("""
## あなたの基本属性を入力して下さい
            """)

height = st.number_input('身長', step=0.1)
weight = st.number_input('体重', step=0.1)
age = st.number_input('年齢', step=1)
sex = st.selectbox('性別', ['男性', '女性'])

average_input_vector = {
                '性別' : sex, 
                '年齢' : age, 
                '身長' : height, 
                # '体重' : weight
                }

# こっちには体重を入れていることに注意
user_input_vector = {
                '性別' : sex, 
                '年齢' : age, 
                '身長' : height, 
                '体重':weight
                }

st.markdown("""
## あなたの今週の成果を入力してね！
            """)

choose_id_list = ['AADMJ', 'AAAED', 'AAAID', 'AAEDQ', 'AAAEP']


# 歯科衛生質問票_喫煙_1日あたり●本 (AADMJ)
num_smoke = st.number_input('タバコを1日平均で何本吸いましたか？', step=1)
user_input_vector[id2name('AADMJ')] = num_smoke

# 飲酒量 (AAAED)
amount_alc = st.selectbox('お酒を1日平均でどのくらい飲みましたか？', [label['label'] for label in vita_navi_attribute_def_map['AAAED']['selectOptions']])
alc_label = get_value_from_label(amount_alc, vita_navi_attribute_def_map["AAAED"]['selectOptions'])
user_input_vector[id2name('AAAED')] = alc_label

# 平均歩数 (AAAID)
exc = st.number_input('1日当たりの平均歩数は？', step=1)
user_input_vector[id2name('AAAID')] = exc

# コーヒーポリフェノール (AAEDQ)
# なんかおかしい気がする
coffee = st.number_input('コーヒーを1日平均でどのくらい飲みましたか？(ml)', step=50)
pol = coffee * 2
user_input_vector[id2name('AAEDQ')] = pol

# 食べ方3(夜食/間食) (AAAEP)
yashoku = st.number_input('週に何回夜食をしますか？', step=1)

if yashoku >= 3:
    user_input_vector[id2name('AAAEP')] = 1
else:
    user_input_vector[id2name('AAAEP')] = 2

