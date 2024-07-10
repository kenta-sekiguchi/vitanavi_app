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