import time
import random
import streamlit as st
from google import genai
from google.genai import errors

# ページ基本設定
st.set_page_config(
    page_title="英単語構造学習アプリ",
    page_icon="🔤",
    layout="centered"
)

# --- プリセットデータ（最初から即時表示できる単語） ---
PRESET_ANALYSIS = {
    "predict": """### 📌 【predict】の和訳と意味
- **和訳**: 予測する、予言する
- **概要**: あらかじめ（前に）言うことから、将来の出来事を「予測する」意味になります。

### 🧩 成り立ち（パーツ分解）
- **接頭辞 (Prefix)**: `pre-`（前に、あらかじめ）
- **語根・語幹 (Root/Stem)**: `dict`（言う、伝える）
- **接尾辞 (Suffix)**: なし
- **全体の成り立ち**: 「事前に（pre-）」「言う（dict）」＝「予測する」

### 🔗 共通パーツを持つ他の英単語
- **dictionary** (辞書): 語根 `dict`（言葉・言うこと）をまとめた本
- **contradict** (矛盾する、反論する): 接頭辞 `contra-`（反対に）＋ `dict`（言う）""",

    "sympathy": """### 📌 【sympathy】の和訳と意味
- **和訳**: 同情、共感、思いやり
- **概要**: 他人の感情を自分と同じように「共に感じる」心の状態を表します。

### 🧩 成り立ち（パーツ分解）
- **接頭辞 (Prefix)**: `sym-` / `syn-`（共に、一緒に）
- **語根・語幹 (Root/Stem)**: `path`（感情、苦痛）
- **接尾辞 (Suffix)**: `-y`（名詞を作る接尾辞：状態・性質）
- **全体の成り立ち**: 「共に（sym-）」「感情（path）」を共有する状態（-y）＝「同情・共感」

### 🔗 共通パーツを持つ他の英単語
- **empathy** (共感、感情移入): 接頭辞 `em-`（中に）＋ `path`（感情）
- **telepathy** (テレパシー): 接頭辞 `tele-`（遠く離れた）＋ `path`（感情）""",

    "transport": """### 📌 【transport】の和訳と意味
- **和訳**: 輸送する、運ぶ、交通機関
- **概要**: 物品や人をある場所から別の場所へ「越えて運ぶ」動きを示します。

### 🧩 成り立ち（パーツ分解）
- **接頭辞 (Prefix)**: `trans-`（越えて、向こう側へ）
- **語根・語幹 (Root/Stem)**: `port`（運ぶ、港）
- **接尾辞 (Suffix)**: なし
- **全体の成り立ち**: 「向こう側へ（trans-）」「運ぶ（port）」＝「輸送する」

### 🔗 共通パーツを持つ他の英単語
- **export** (輸出する): 接頭辞 `ex-`（外へ）＋ `port`（運ぶ）
- **import** (輸入する): 接頭辞 `im-`（中に）＋ `port`（運ぶ）"""
}

# APIキーの取得とクライアント初期化
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=gemini_api_key)
except KeyError:
    st.error("APIキーが設定されていません。StreamlitのSecrets設定を確認してください。")
    st.stop()

# --- セッション状態（キャッシュ）の初期化 ---
# 検索結果を蓄積する辞書。初期値としてPRESET_ANALYSISをコピーしておく。
if "analysis_cache" not in st.session_state:
    st.session_state.analysis_cache = PRESET_ANALYSIS.copy()

# 現在表示している単語
if "current_word" not in st.session_state:
    st.session_state.current_word = random.choice(list(PRESET_ANALYSIS.keys()))

# --- UI構成 ---
st.title("🔤 英単語構造学習アプリ")
st.caption("接頭辞・語根・接尾辞の成り立ちから英単語のコア意味を学びます。")

word = st.session_state.current_word

# メイン表示エリア
st.subheader(f"📖 表示中の単語: `{word}`")

# ランダム切替ボタン
if st.button("🎲 別のランダム例を見る"):
    st.session_state.current_word = random.choice(list(PRESET_ANALYSIS.keys()))
    st.rerun()

# --- 解析結果の表示 (キャッシュにあれば即表示、なければストリーミング生成) ---
if word in st.session_state.analysis_cache:
    # キャッシュ済み（またはプリセット）の場合は0秒で即表示
    st.markdown(st.session_state.analysis_cache[word])
else:
    # 未知の単語の場合は、APIを呼び出して文字を少しずつ表示（ストリーミング）
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
    - **単語1** (和訳): 共通パーツと解説
    - **単語2** (和訳): 共通パーツと解説
    """

    def stream_generator():
        max_retries = 3
        delay = 2
        for attempt in range(max_retries):
            try:
                # 必ず gemini-3.8-flash を使用
                response_stream = client.models.generate_content_stream(
                    model="gemini-3.8-flash",
                    contents=prompt,
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                return  # 正常終了
            except errors.APIError as e:
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
                        continue
                    else:
                        yield "⚠️ 現在Googleのサーバーが混雑しています（503エラー）。時間を置いて再度検索してください。"
                        return
                elif "429" in err_str:
                    yield "⚠️ APIの利用制限に達しました。時間を置いてお試しください。"
                    return
                else:
                    yield f"**APIエラー:** {e}"
                    return
            except Exception as e:
                yield f"**予期せぬエラーが発生しました:** {e}"
                return

    # st.write_streamで文字をパラパラと表示し、結果を変数に受け取る
    result_text = st.write_stream(stream_generator)
    
    # 完了後、結果をキャッシュに保存（2回目以降の検索を高速化）
    st.session_state.analysis_cache[word] = result_text

st.divider()

# --- ページ下部：検索エリア ---
st.subheader("🔎 英単語を検索する")

with st.form(key="search_form", clear_on_submit=True):
    search_input = st.text_input("調べたい英単語を入力してください（半角英字）", placeholder="例: preview, bisect, incredible")
    submit_button = st.form_submit_button("構造を解析する")

# フォームが送信されたときの処理
if submit_button:
    target_word = search_input.strip().lower()
    if target_word:
        # 現在の単語を更新して、画面を一番上から再描画（rerun）させる
        st.session_state.current_word = target_word
        st.rerun()
    else:
        st.warning("英単語を入力してください。")
