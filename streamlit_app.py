import random
import streamlit as st
from google import genai
from google.genai import errors

# ページ基本設定 (必ず一番上に書く必要があります)
st.set_page_config(
    page_title="英単語構造学習アプリ",
    page_icon="🔤",
    layout="centered"
)

# 初回ランダム表示用のサンプル単語リスト
SAMPLE_WORDS = [
    "predict", "sympathy", "transport", "autograph", "contradict",
    "spectacular", "submariner", "philosophy", "monochrome", "biodiversity"
]

# APIキーの取得とクライアント初期化
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=gemini_api_key)
except KeyError:
    st.error("APIキーが設定されていません。StreamlitのSecretsに 'GEMINI_API_KEY' を設定してください。")
    st.stop()


# 英単語の構造解析を行う関数
def analyze_word(word: str) -> str:
    prompt = f"""
英単語 「{word}」 について、語源や構造（語幹・接頭辞・接尾辞など）を学習するための解説を作成してください。

以下のフォーマットに従って、わかりやすい日本語のマークダウン形式で出力してください：

### 📌 【{word}】の和訳と意味
- **和訳**: （主な和訳）
- **概要**: （簡単な意味やコアなニュアンスの説明）

### 🧩 成り立ち（パーツ分解）
- **接頭辞 (Prefix)**: （該当する場合：パーツ名と意味。なければ「なし」）
- **語根・語幹 (Root/Stem)**: （パーツ名と意味）
- **接尾辞 (Suffix)**: （該当する場合：パーツ名と品詞・機能。なければ「なし」）
- **全体の成り立ち**: （各パーツがどう組み合わさって現在の意味になっているかの説明）

### 🔗 共通パーツを持つ他の英単語
- **単語1** (和訳): 共通パーツ（例：語根 -xxx）と解説
- **単語2** (和訳): 共通パーツと解説
- **単語3** (和訳): 共通パーツと解説
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",  # 指定通り gemini-3.8-flash を使用
            contents=prompt,
        )
        return response.text
    except errors.APIError as e:
        return f"⚠️ APIエラーが発生しました: {e}"
    except Exception as e:
        return f"⚠️ エラーが発生しました: {e}"

# ==========================================
# ここからUIの描画 (先に画面を表示させる)
# ==========================================
st.title("🔤 英単語構造学習アプリ")
st.caption("接頭辞・語根・接尾辞の成り立ちから英単語のコア意味を学びます。")

# セッション状態の初期化 (単語のみ先に決定)
if "current_word" not in st.session_state:
    st.session_state.current_word = random.choice(SAMPLE_WORDS)

# --- メイン表示エリア ---
st.subheader(f"📖 表示中の単語: `{st.session_state.current_word}`")

# ランダム切替ボタン
if st.button("🎲 別のランダム単語を見る"):
    st.session_state.current_word = random.choice(SAMPLE_WORDS)
    # 結果を一度リセットして再取得させる
    if "analysis_result" in st.session_state:
        del st.session_state.analysis_result
    st.rerun()

# ⚠️ UIを表示した「後」で、解析結果がない場合のみAPI通信を実行する
if "analysis_result" not in st.session_state:
    with st.spinner(f"「{st.session_state.current_word}」の構造を解析中..."):
        st.session_state.analysis_result = analyze_word(st.session_state.current_word)

# 解析結果表示
st.markdown(st.session_state.analysis_result)

st.divider()

# --- ページ下部：検索エリア ---
st.subheader("🔎 英単語を検索する")

with st.form(key="search_form", clear_on_submit=True):
    search_input = st.text_input("調べたい英単語を入力してください（半角英字）", placeholder="例: preview, bisect, incredible")
    submit_button = st.form_submit_button("構造を解析する")

if submit_button:
    target_word = search_input.strip().lower()
    if target_word:
        st.session_state.current_word = target_word
        with st.spinner(f"「{target_word}」の構造を解析中..."):
            st.session_state.analysis_result = analyze_word(target_word)
        st.rerun()
    else:
        st.warning("英単語を入力してください。")
