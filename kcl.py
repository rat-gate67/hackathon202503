import streamlit as st
import math
import random
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ------------------------------------------------------
# （1）ダミーのモデル呼び出し関数
# ------------------------------------------------------
def get_recommended_papers(input_text):
    """
    入力されたテキスト(文章)をもとに、
    類似度の高い論文情報を10件返すダミー関数。
    戻り値: リスト[ {title, authors, university, relatedness}, ... ]
      - university: '東工大' or '九工大'
      - relatedness: 1～10 (小さいほど関連が強いとする)
    """
    dummy_data = []
    for i in range(10):
        paper = {
            "title": f"論文タイトル{i+1}",
            "authors": f"著者A{i+1}, 著者B{i+1}",
            "university": "東工大" if i % 2 == 0 else "九工大",
            "relatedness": i
            #random.randint(1, 10)  # 1〜10のランダム値
        }
        dummy_data.append(paper)
    return dummy_data


# ------------------------------------------------------
# （2）Plotlyでネットワーク風に可視化する関数
# ------------------------------------------------------
def create_network_figure(input_text, papers):
    """
    中心ノード(入力テキスト) + 周囲ノード(論文) を円状に配置し、
    Plotlyの散布図＋線でネットワーク風に可視化する。
    """
    # 中心ノードの座標
    center_x, center_y = 0, 0

    # 周囲ノードの座標を計算
    num_papers = len(papers)
    angle_unit = 2 * math.pi / max(num_papers, 1)
    base_radius = 100

    # Plotly用データを入れるリスト
    node_x = []       # 各ノードのX座標
    node_y = []       # 各ノードのY座標
    node_text = []    # ノードに表示するラベル(ホバー等)
    node_color = []   # ノードの色

    edge_x = []       # エッジ描画用X座標ペア
    edge_y = []       # エッジ描画用Y座標ペア

    # 1) まず中心ノードの情報をセット
    node_x.append(center_x)
    node_y.append(center_y)
    node_text.append(input_text if input_text else "入力文(空)")
    node_color.append("#999999")  # グレー

    # 2) 論文ノードとエッジを追加
    for i, paper in enumerate(papers):
        # 関連度が小さいほど近い、大きいほど遠い
        radius = base_radius + paper["relatedness"] * 20
        angle = angle_unit * i
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        # 大学による色分け
        color = "#0000FF" if paper["university"] == "東工大" else "#008000"

        label_text = f"{paper['title']}<br>{paper['authors']}<br>({paper['university']})"
        node_x.append(x)
        node_y.append(y)
        node_text.append(label_text)
        node_color.append(color)

        # エッジ: 中心(0,0) → ノード(x,y) を結ぶ線
        # Plotlyの "scatter" (mode='lines') 用に2点ずつ追加
        edge_x.extend([center_x, x, None])  # Noneで線分を区切る
        edge_y.extend([center_y, y, None])

    # ------------------------------------------------------
    # (A) エッジ用トレース (mode='lines')
    # ------------------------------------------------------
    edge_trace = go.Scatter(
        x=edge_x, 
        y=edge_y,
        mode='lines',
        line=dict(color='#cccccc', width=2),
        hoverinfo='none'  # 線にホバー情報は不要
    )

    # ------------------------------------------------------
    # (B) ノード用トレース (mode='markers')
    # ------------------------------------------------------
    node_trace = go.Scatter(
        x=node_x, 
        y=node_y,
        mode='markers+text',
        text=node_text,             # ラベル文字列
        textposition="bottom center",
        marker=dict(
            color=node_color,
            size=20,
            line=dict(width=2, color='#FFFFFF')  # ノード枠
        ),
        hoverinfo='text'  # ホバー時に上記のtextを表示
    )

    # ------------------------------------------------------
    # プロット領域のレイアウト設定
    # ------------------------------------------------------
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        xaxis=dict(
                            showgrid=False, # 背景グリッド非表示
                            zeroline=False, # X軸の線を消す
                        ),
                        yaxis=dict(
                            showgrid=False,
                            zeroline=False,
                        ),
                        # アスペクト比を1:1に
                        margin=dict(l=10, r=10, b=10, t=10),
                    )
    )

    # auto rangeにしておけば拡大縮小をPlotlyのUIから操作できる
    fig.update_layout(xaxis={'autorange': True}, yaxis={'autorange': True})

    return fig


# ------------------------------------------------------
# （3）メインのStreamlitアプリ
# ------------------------------------------------------
def main():
    st.title("論文レコメンド＆可視化デモ")

    st.write("文章を入力すると、その内容に関連の強い論文を10件、ネットワーク風に可視化します。")
    st.write("Plotlyのツールバーから「Reset Axes」ボタンを押すと初期表示近くに戻ります。")

    input_text = st.text_area("文章を入力:", value="", placeholder="ここに文章を入力...")

    if st.button("関連論文を検索"):
        papers = get_recommended_papers(input_text)
        # ネットワーク可視化のFigureを生成
        fig = create_network_figure(input_text, papers)
        # Streamlitで描画
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
