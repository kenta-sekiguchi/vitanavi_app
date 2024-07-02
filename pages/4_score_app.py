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


vita_navi_client = VitaNaviClient()

st.title('健康スコアを算出するよ！')


#----------------------------
# 入力属性
# ----------------------------
smoke_id = 'AAADZ'
drink_id = 'AAAEB'
smoke = st.selectbox('喫煙している', [label['label'] for label in vita_navi_attribute_def_map[smoke_id]['selectOptions']])
drink = st.selectbox('飲酒', [label['label'] for label in vita_navi_attribute_def_map[drink_id]['selectOptions']])

if smoke == 'はい':
    smoke = 1
elif smoke == 'いいえ':
    smoke = 2

if drink == '毎日':
    drink = 1
elif drink == '時々':
    drink = 2
elif drink == 'ほとんど飲まない':
    drink = 3

# input_vector = {
#                 '性別' : sex, 
#                 '年齢' : age, 
#                 '身長' : height, 
#                 '体重' : weight, 
#                 id2name(kadai_code):2
#                 }



#----------------------------
# プロセス
# ----------------------------
if st.button('実行'):
    score = smoke + drink
    st.write('あなたの健康スコア：', score)
    # response_data = vita_navi_client.prediction(
    #                     input_vector = input_vector, 
    #                     model="musica",  
    #                     api_version = 'v4'
    #                         )

    # ans = response_data.vector_as_dataframe_with_attribute_name_jp[taisaku][0]

    # if kadai == '腰痛':
    #     st.write(kadai, 'がない人の', taisaku, '：', ans)
    # elif kadai == '頭痛':
    #     st.write(kadai, 'がない人の平均睡眠時間：', vita_navi_attribute_def_map["AADGW"]['selectOptions'][int(ans-1)]['label'])