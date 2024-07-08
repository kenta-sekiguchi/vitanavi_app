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

st.title('ライフケア～適度に不健康を楽しもう～')


#----------------------------
# 入力属性
# ----------------------------

st.markdown("""
## あなたの基本属性を入力して下さい
            """)

height = st.number_input('身長', step=0.1)
age = st.number_input('年齢', step=1)
sex = st.selectbox('性別', ['男性', '女性'])
if sex == '男性':
    sex = 'M'
else:
    sex ='F'

average_input_vector = {
                '性別' : sex, 
                '年齢' : age, 
                '身長' : height, 
                # '体重' : weight
                }
user_input_vector = {
                '性別' : sex, 
                '年齢' : age, 
                '身長' : height, 
                }


#----------------------------
# 譲れない条件
# ----------------------------
st.markdown("""
### あなたが譲れない条件を入力して下さい
            """)

choose_id_list = ['AADMJ', 'AAAED', 'AAAID', 'AAEDQ', 'AAAEP']

# 睡眠は入れるべきかな
# 体重入れても面白い？
option = st.selectbox(
                'あなたが通したいわがままは？',
                ['タバコを吸いたい', 'お酒を飲みたい', '運動はしたくない', 'カフェインとりたい', '夜食をしたい', '特になし']
                )

# 歯科衛生質問票_喫煙_1日あたり●本 (AADMJ)
if option == 'タバコを吸いたい':
    num_smoke = st.number_input('1日当たりに吸う本数は？', step=1)
    user_input_vector[id2name('AADMJ')] = num_smoke
    choose_id_list.remove('AADMJ')

# 飲酒量 (AAAED)
elif option == 'お酒を飲みたい':
    amount_alc = st.selectbox('お酒の量', [label['label'] for label in vita_navi_attribute_def_map['AAAED']['selectOptions']])
    alc_label = get_value_from_label(amount_alc, vita_navi_attribute_def_map["AAAED"]['selectOptions'])
    user_input_vector[id2name('AAAED')] = alc_label
    choose_id_list.remove('AAAED')

# 平均歩数 (AAAID)
elif option == '運動はしたくない':
    exc = st.number_input('1日当たりの歩数は？', step=1)
    user_input_vector[id2name('AAAID')] = exc
    choose_id_list.remove('AAAID')

# コーヒーポリフェノール (AAEDQ)
# なんかおかしい気がする
elif option == 'カフェインとりたい':
    coffee = st.number_input('1日あたりに飲むコーヒーの量は？(ml)', step=50)
    pol = coffee * 2
    user_input_vector[id2name('AAEDQ')] = pol
    choose_id_list.remove('AAEDQ')

# 食べ方3(夜食/間食) (AAAEP)
elif option == '夜食をしたい':
    yashoku = st.number_input('週に何回夜食をしますか？', step=1)

    if yashoku >= 3:
        user_input_vector[id2name('AAAEP')] = 1
    else:
        user_input_vector[id2name('AAAEP')] = 2

    choose_id_list.remove('AAAEP')

elif option == '特になし':
    pass

choose_name_list = [id2name(id) for id in choose_id_list]

#----------------------------
# 任意の選択
# ----------------------------

st.markdown("""
### あてはまるものを選択してください
            """)

# 頭痛->AACVX
if st.checkbox('頭痛持ち'):
    average_input_vector[id2name('AACVX')] = 2

# 腰痛 -> AACWF
if st.checkbox('腰痛持ち'):
    average_input_vector[id2name('AACWF')] = 2



#----------------------------
# プロセス
# ----------------------------
if st.button('実行'):
    average_response_data = vita_navi_client.prediction(
                            input_vector = average_input_vector, 
                            model="musica",  
                            api_version = 'v4'
                            )
    
    # '''
    # -------ここの処理は後で変更---------------
    # '''
    musica_columns = average_response_data.vector_as_dataframe_with_attribute_name_jp.columns
    id_list = []
    way_list = []
    field_list = []
    descrioption_list = []

    for column in musica_columns:
        
        id = vita_navi_attribute_def_map_by_attribute_name_jp[column]['attributeId']
        way = vita_navi_attribute_def_map_by_attribute_name_jp[column]['categoryMethod']
        field = vita_navi_attribute_def_map_by_attribute_name_jp[column]['categoryField']

        try:
            description = vita_navi_attribute_def_map_by_attribute_name_jp[column]['descriptionJp']
        except:
            description = ''
        
        id_list.append(id)
        way_list.append(way)
        field_list.append(field)
        descrioption_list.append(description)
    
    df_info_column = pd.DataFrame({'id':id_list, 
                               'name':musica_columns,
                               'way':way_list, 
                               'field':field_list, 
                               'description':descrioption_list})
    
    sick_id = df_info_column[(df_info_column['field']=='既往歴・服薬（アンケート、レセプト発行回数）') & (df_info_column['way']=='レセプト')]['id'].values
    # '''
    # -----------------------------------------
    # '''

    # ユーザと同属性の人の病気にかかる回数
    # ユーザの健康習慣を推定するのに使用
    input_sick = average_response_data.get_vector_as_dataframe()[sick_id]
    st.dataframe(input_sick)
    input_sick_dict = input_sick.to_dict(orient='records')[0]

    # ユーザの入力とマージ
    user_input_vector = user_input_vector | input_sick_dict

    # vita-naviを使用
    user_response_data = vita_navi_client.prediction(
                            input_vector = user_input_vector, 
                            model="musica",  
                            api_version = 'v4'
                            )
    
    user_df = user_response_data.get_vector_as_dataframe()[choose_id_list]

    st.markdown("""
### あなたが払う犠牲
            """)

    for id in choose_id_list:
        # タバコ
        if id == 'AADMJ':
            st.write(f'吸って良いたばこの本数：{int(user_df[id].iloc[0])}')
        
        # 酒
        elif id == 'AAAED':
            label = get_label_from_value(user_df[id].iloc[0], vita_navi_attribute_def_map["AAAED"]['selectOptions'])
            st.write(f'飲んでよいお酒の上限：{label}')

        # 運動
        elif id == 'AAAID':
            st.write(f'1日あたりの歩数：{int(user_df[id].iloc[0])}')

        # カフェイン
        elif id == 'AAEDQ':
            st.write(f'コーヒー上限：{int(user_df[id].iloc[0]/2)} ml')
        
        # 夜食
        elif id == 'AAAEP':
            value = user_df[id].iloc[0]
            if value == 1:
                st.write('週3回以上の夜食OK !!')

            elif value ==2:
                st.write('夜食は週2回までにしましょう')

