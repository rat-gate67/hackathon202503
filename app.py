import streamlit as st
import math
import random
import plotly.graph_objects as go
from st_cytoscape import cytoscape
from dotenv import load_dotenv
import os

import pandas as pd

load_dotenv()

# # 相対インポートを絶対インポートに変更
# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path)
# from utils.get_paper import get_n_near_papers

from utils.get_paper import get_n_near_papers

st.set_page_config(layout="wide")

# (1) ダミーの論文リスト生成関数
def get_recommended_papers(input_text, n=10):
    """
    入力されたテキスト(文章)をもとに、
    類似度の高い論文情報を10件返すダミー関数。
    戻り値: リスト[ {title, authors, university, relatedness}, ... ]
      - university: '東工大' or '九工大'
      - relatedness: 1～10 (小さいほど関連が強いとする)
    """

    ret = []
    papers = get_n_near_papers(input_text,n)

    if hasattr(papers, 'matches'):
        for i, match in enumerate(papers.matches):
            if hasattr(match, 'metadata'):
                metadata = match.metadata
                school = metadata.get("school", "")
                id = metadata.get("id", "")
                # クラスラベルをcsvから取得
                if school == "九州工業大学":
                    df = pd.read_csv("data/予測クラス_九州工業大学.csv.csv")
                    class_label = df[df['id'] == id]['label1'].values[0] 
                elif school == "東京工業大学":
                    df = pd.read_csv("data/予測クラス_東京工業大学.csv")
                    class_label = df[df['id'] == id]['label1'].values[0] 
                else:
                    class_label = None

                ret.append({
                    "title": metadata.get("title", "タイトルなし"),
                    # "authors": metadata.get("authors", ""),
                    "url": metadata.get("url", "#"),
                    "university": metadata.get("school", "不明"),
                    "relatedness": i * 2,  # スコアを関連度として使用
                    "class_label": class_label
                })

    random.shuffle(ret)  # Shuffle the papers randomly
    return ret

# (2) 円形配置でノード・エッジを作成
def build_cy_elements(input_text, papers):
    """
    円状にノードを配置し、'preset' レイアウトで描画できるように
    positionを持った要素リストを作る。
    """
    elements = []

    # 中心ノード
    center_node = {
        "data": {
            "id": "center",
            "label": ""
        },
        "position": {"x": 0, "y": 0},  # 円の中心(0,0)
    }
    elements.append(center_node)

    # 周囲ノードを円状に計算
    num_papers = len(papers)
    angle_unit = 2 * math.pi / max(num_papers, 1)
    base_radius = 100

    for i, paper in enumerate(papers):
        node_id = f"paper_{i}"
        label_text = f"{paper['title']})"
        # label_text = f"{paper['title']}\n{paper['url']}\n({paper['university']})"

        # 関連度が1に近いほど中心に近い位置に
        radius = base_radius + paper["relatedness"] * 20
        angle = angle_unit * i
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        # 大学で色分け (東工大→青, 九工大→緑)
        color = "#0000FF" if paper["university"] == "九州工業大学" else "#008000"

        node = {
            "data": {
                "id": node_id, 
                "label": label_text,
                "title": f"{paper['title']}\n{paper['url']}\n({paper['university']})",
                "url": paper['url'],
                "university": paper['university'],
                "class_label": paper['class_label']
                },
            "position": {"x": x, "y": y},  # 'preset' 用の座標指定
            "style": {"background-color": color}
        }
        elements.append(node)

        # エッジ (中心ノード 'center' → 各paperノード)
        edge = {
            "data": {
                "id": f"edge_center_{node_id}",
                "source": "center",
                "target": node_id
            }
        }
        elements.append(edge)

    return elements

def main():
    st.title("論文レコメンド＆可視化デモ (継続表示対応)")

    st.write("文章を入力→「検索」ボタンを押すと、その内容に関連する論文を円状に可視化します。")
    input_text = st.text_area("文章を入力:", value="", placeholder="ここに文章を入力...")

    # ----------------------
    # 検索ボタンで論文情報を取得・保存
    # ----------------------
    with st.expander("オプション設定"):
        near_n = st.slider("検索する論文数:", min_value=1, max_value=50, value=10)
        boost = st.slider("検索のboost:", min_value=1, max_value=5, value=1)
    if st.button("検索"):
        papers = get_recommended_papers(input_text*boost, near_n)
        # セッションステートに保存
        st.session_state["papers"] = papers
        st.session_state["input_text"] = input_text  # 後でラベル表示に使う

    # ----------------------
    # セッションステートにデータがあればグラフを描画
    # ----------------------
    if "papers" in st.session_state:
        papers = st.session_state["papers"]
        saved_text = st.session_state.get("input_text", "")  # 入力文のラベル用

        # ノード・エッジの作成
        elements = build_cy_elements(saved_text, papers)

        # Cytoscape 用のスタイル設定
        stylesheet = [
            {
                "selector": "node",
                "style": {
                    "label": "data(label)",
                    "text-wrap": "wrap",
                    "text-max-width": "100px",
                    "font-size": "12px",
                    "color": "#333",
                    "width": "30px",
                    "height": "30px"

                }
            },
            {
                "selector": "node:selected",
                    "style": {
                        "background-color": "#FF0000",  # 選択されたノードは赤色に
                        "border-color": "#FFF",
                        "border-width": "2px",
                    }
                },
            {
                "selector": "edge",
                "style": {
                    "width": 2,
                    "line-color": "#ccc",
                    "target-arrow-shape": "triangle",
                    "target-arrow-color": "#ccc",
                    "curve-style": "bezier"
                }
            },
        ]
        layout = {"name": "preset"}

        
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write("### 検索結果のネットワーク:")
            st.write("---")
            with st.container(border=True):
                selected = cytoscape(
                elements,
                stylesheet,
                height="1000px",  # 600pxの高さ
                layout=layout,
                key="graph",  # コンポーネントのキー
                )

        with col2:
            # st.write("選択されたノードやエッジの情報:", selected)
            # selected
            st.write("### 選択されたノードやエッジの情報:")
            st.write("---")
            if selected:
                selected_node = selected["nodes"]
                if selected_node:
                    for node in selected_node:
                        for e in elements:
                            if e["data"]["id"] == node and node != "center":
                                st.write(f"タイトル: {e['data']['label']}")
                                st.write(f"関連順位: {papers[int(node.split('_')[1])]['relatedness'] / 2 + 1}") 
                                st.write(f"大学: {papers[int(node.split('_')[1])]['university']}")
                                st.write(f"URL: {papers[int(node.split('_')[1])]['url']}")
                                st.write("---")
                                break

        # st.write(elements)  

if __name__ == "__main__":
    main()