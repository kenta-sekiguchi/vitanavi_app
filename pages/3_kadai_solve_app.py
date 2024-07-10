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
# オリジナル関数のimport
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
import function

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

vita_navi_client = VitaNaviClient()

st.title('ライフケア～適度に不健康を楽しもう～')


#----------------------------
# 入力属性
# ----------------------------

st.markdown("""
## あなたの基本属性を入力して下さい
            """)

height = st.number_input('身長', step=0.1)
weight = st.number_input('体重', step=0.1)
age = st.number_input('年齢', step=1)
sex = st.selectbox('性別', ['男性', '女性'])
if sex == '男性':
    sex = 'M'
else:
    sex ='F'

nervous = st.selectbox('緊張しやすい', [label['label'] for label in vita_navi_attribute_def_map['AABAK']['selectOptions']])
nervous_label = function.get_value_from_label(nervous, vita_navi_attribute_def_map["AABAK"]['selectOptions'])

morning = st.selectbox('朝が弱い夜型人間だ ', [label['label'] for label in vita_navi_attribute_def_map['AABAF']['selectOptions']])
morning_label = function.get_value_from_label(morning, vita_navi_attribute_def_map["AABAF"]['selectOptions'])

average_input_vector = {
                '性別' : sex, 
                '年齢' : age, 
                '身長' : height, 
                # '体重' : weight, 
                function.id2name('AABAK'):nervous_label, 
                function.id2name('AABAF'):morning_label
                }

user_input_vector = {
                '性別' : sex, 
                '年齢' : age, 
                '身長' : height, 
                # '体重':weight,
                function.id2name('AABAK'):nervous_label, 
                function.id2name('AABAF'):morning_label
                }


#----------------------------
# 譲れない条件
# ----------------------------
st.markdown("""
### あなたが譲れない条件を入力して下さい
            """)

choose_id_list = ['AADMJ', 'AAAED', 'AAAID', 'AAEDQ', 'AAAEP', 'AABQE', 'AABOS']
other_id_list = ['AACPO']

# 睡眠は入れるべきかな
# 体重入れても面白い？
option = st.selectbox(
                'あなたが通したいわがままは？',
                ['タバコを吸いたい', 'お酒を飲みたい', '運動はしたくない', 'カフェインとりたい', 
                 '夜食をしたい', '塩分は気にしたくない', '糖質制限はしたくない', '特になし']
                )

# 歯科衛生質問票_喫煙_1日あたり●本 (AADMJ)
if option == 'タバコを吸いたい':
    num_smoke = st.number_input('1日当たりに吸う本数は？', step=1)
    user_input_vector[function.id2name('AADMJ')] = num_smoke
    choose_id_list.remove('AADMJ')

# 飲酒量 (AAAED)
elif option == 'お酒を飲みたい':
    amount_alc = st.selectbox('1日当たりのお酒を飲む量', [label['label'] for label in vita_navi_attribute_def_map['AAAED']['selectOptions']])
    st.info("""
    **【1合の目安】**\n
    ・ビール中瓶1本(約500ml)\n
    ・焼酎35度(80ml)\n
    ・ワイン2杯(240ml))\n
    ・ウイスキーダブル一杯(60ml)
            """)

    alc_label = function.get_value_from_label(amount_alc, vita_navi_attribute_def_map["AAAED"]['selectOptions'])
    user_input_vector[function.id2name('AAAED')] = alc_label
    choose_id_list.remove('AAAED')

# 平均歩数 (AAAID)
elif option == '運動はしたくない':
    exc = st.number_input('1日当たりの歩数は？(歩)', step=1)
    user_input_vector[function.id2name('AAAID')] = exc
    choose_id_list.remove('AAAID')

# コーヒーポリフェノール (AAEDQ)
# なんかおかしい気がする
elif option == 'カフェインとりたい':
    coffee = st.number_input('1日あたりに飲むコーヒーの量は？(ml)', step=50)
    pol = coffee * 2
    user_input_vector[function.id2name('AAEDQ')] = pol
    choose_id_list.remove('AAEDQ')

# 食べ方3(夜食/間食) (AAAEP)
elif option == '夜食をしたい':
    yashoku = st.number_input('週に何回夜食をしますか？(回)', step=1)

    if yashoku >= 3:
        user_input_vector[function.id2name('AAAEP')] = 1
    else:
        user_input_vector[function.id2name('AAAEP')] = 2

    choose_id_list.remove('AAAEP')

# 塩分（AABQE）
elif option == '塩分は気にしたくない':
    salt_amount = st.number_input('1日当たりの食塩摂取量は？(g)', step=0.1)
    user_input_vector[function.id2name('AABQE')] = salt_amount
    choose_id_list.remove('AABQE')

# 炭水化物（AABOS）
elif option == '糖質制限はしたくない':
    carb_amount = st.number_input('1日当たりの炭水化物摂取量は？(g)', step=1)

    st.info("""
                        
        **【炭水化物量の目安】**\n
        ・お茶碗1杯のご飯(160g)の炭水化物量：約60g\n
        ・食パン1枚あたり(6枚切り)の炭水化物量：約30g\n
        ・パスタスタ1人前(乾麺90g)あたりの炭水化物量：約66g
                    """)
    
    user_input_vector[function.id2name('AABOS')] = carb_amount
    choose_id_list.remove('AABOS')

elif option == '特になし':
    pass

choose_name_list = [function.id2name(id) for id in choose_id_list]

#----------------------------
# 任意の選択
# ----------------------------

st.markdown("""
### あてはまるものを選択してください
            """)

# 頭痛->AACVX
if st.checkbox('頭痛持ち'):
    average_input_vector[function.id2name('AACVX')] = 2

# 腰痛 -> AACWF
if st.checkbox('腰痛持ち'):
    average_input_vector[function.id2name('AACWF')] = 2



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
    # st.dataframe(input_sick)
    input_sick_dict = input_sick.to_dict(orient='records')[0]

    # ユーザの入力とマージ
    user_input_vector = user_input_vector | input_sick_dict

    # vita-naviを使用
    user_response_data = vita_navi_client.prediction(
                            input_vector = user_input_vector, 
                            model="musica",  
                            api_version = 'v4'
                            )
    
    user_df = user_response_data.get_vector_as_dataframe()

    st.markdown("""
### あなたが払う犠牲
            """)

    all_id_list = choose_id_list + other_id_list

    for id in all_id_list:
        # タバコ
        if id == 'AADMJ':
            st.markdown('**【吸ってよいたばこの上限】**')
            st.write(f'{int(user_df[id].iloc[0])} 本')
        
        # 酒
        elif id == 'AAAED':
            label = function.get_label_from_value(user_df[id].iloc[0], vita_navi_attribute_def_map["AAAED"]['selectOptions'])
            st.markdown('**【飲んでよいお酒の上限】**')
            st.write(f'{label}')
            st.info("""
                    **【1合の目安】**\n
                    ・ビール中瓶1本(約500ml)\n
                    ・焼酎35度(80ml)\n
                    ・ワイン2杯(240ml))\n
                    ・ウイスキーダブル一杯(60ml)
                            """)

        # 運動
        elif id == 'AAAID':
            st.markdown('**【1日当たりの歩数】**')
            st.write(f'{int(user_df[id].iloc[0])} 歩')

        # カフェイン
        elif id == 'AAEDQ':
            st.markdown('**【1日に飲んでよいコーヒーの上限】**')
            st.write(f'{int(user_df[id].iloc[0]/2)} ml')
        
        # 夜食
        elif id == 'AAAEP':
            st.markdown('**【夜食の回数】**')
            value = user_df[id].iloc[0]
            if value == 1:
                st.write('週3回以上の夜食OK !!')

            elif value ==2:
                st.write('夜食は週2回までにしましょう')
        
        # 塩分
        elif id == 'AABQE':
            st.markdown('**【塩分摂取量】**')
            st.write(f'{user_df[id].iloc[0]:.1f} g')
            st.warning('※日本人の平均塩分摂取量は約10gです')

        # 炭水化物量
        elif id == 'AABOS':
            st.markdown('**【炭水化物摂取量】**')
            st.write(f'炭水化物摂取量：{user_df[id].iloc[0]:.1f} g')

            st.info("""         
            **【炭水化物量の目安】**\n
            ・お茶碗1杯のご飯(160g)の炭水化物量：約60g\n
            ・食パン1枚あたり(6枚切り)の炭水化物量：約30g\n
            ・パスタスタ1人前(乾麺90g)あたりの炭水化物量：約66g
                        """)


        elif id == 'AACPO':
            st.markdown('**【推奨睡眠時間（最低）】**')
            st.write(f'{((user_df[id].iloc[0])/60):.1f}時間')
            

