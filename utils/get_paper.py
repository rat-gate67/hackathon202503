import os

from pinecone import Pinecone
from utils.get_vec import text_to_vector
from dotenv import load_dotenv

load_dotenv()


# 環境変数からAPIキーを取得
api_key = os.getenv('PINECONE_API_KEY')
if not api_key:
    raise ValueError("環境変数 'PINECONE_API_KEY' が設定されていません。.envファイルを確認してください。")


pc = Pinecone(api_key=api_key)
pinecone_index = pc.Index("vector-db")
print(pc.list_indexes())

def get_n_near_papers(input_text, n=10):
    vector = text_to_vector(input_text)
    vector_list = vector.tolist()
    results = pinecone_index.query(
        vector=vector_list,  # Pass the list instead of ndarray
        top_k=n,  # 引数 n を使用
        include_metadata=True
    )

    return results

if __name__ == "__main__":
    
    text = "生物の脳神経ネットワークにおける情報処理をアルゴリズムとして抽出した「ニューラルネットワーク」は，ネットワーク内の「重み」を巧みに調節することで，様々な入出力関係を持つ関数を学習により獲得することができる。本研究では，DNAコンピューティングの理論と技術を発展させ，反応拡散系として分子的に実装されたニューラルネットワークシステムを開発し，マイクロ流体デバイスにて実験レベルで検証する。"
    papers = get_n_near_papers(text)  # 関数名を修正
    print(papers)
    
    # Pinecone の結果を正しく処理する例
    if hasattr(papers, 'matches'):
        for match in papers.matches:
            print(f"ID: {match.id}, Score: {match.score}")
            if hasattr(match, 'metadata'):
                print(f"Metadata: {match.metadata}")