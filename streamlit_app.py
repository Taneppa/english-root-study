数分間待っても結果が出ずフリーズしてしまう原因は、Streamlit Cloudの通信環境において**ストリーミング処理（`generate_content_stream`）がタイムアウト設定なしで呼び出され、通信の応答待ちで処理が無限ブロック（フリーズ）していたため**です。

以下の対策を施した完全な全体コードに差し替えてください。

### 修正のポイント

1. **15秒のタイムアウト設定を追加**: `HttpOptions(timeout=15000)` を設定し、万が一Googleのサーバーからの応答が遅い場合でも数分間待たされず、15秒で即座にエラー/再試行へ切り替わるようにしました。
2. **一括取得（`generate_content`）に変更**: Streamlit Cloud環境で動作が不安定になりがちなストリーミングから、確実に一括で受け取る方式に変更しました。
3. **`st.form` の撤去**: フォーム送信による画面のレンダリング遅延を防ぐため、通常のボタン・入力欄構成に修正しました。

---

### 全体コード (`app.py` または `streamlit_app.py`)

```python
import random
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# ページ基本設定
st.set_page_config(
    page_title="英単語構造学習アプリ",
    page_icon="🔤",
    layout="centered"
)

# --- プリセットデータ（最初から即時0秒で表示できる単語） ---
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

# APIキーの取得とクライアント初期化（15秒のタイムアウトを設定）
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(
        api_key=gemini_api_key,
        http_options=types.HttpOptions(timeout=15000)  # 15秒応答がなければタイムアウト
    )
except KeyError:
    st.error("APIキーが設定されていません。StreamlitのSecrets設定を確認してください。")
    st.stop()

# --- セッション状態（キャッシュ）の初期化 ---
if "analysis_cache" not in st.session_state:
    st.session_state.analysis_cache = PRESET_ANALYSIS.copy()

if "current_word" not in st.session_state:
    st.session_state.current_word = random.choice(list(PRESET_ANALYSIS.keys()))


# Gemini APIから単語の構造解析を取得する関数
def fetch_analysis(word: str) -> str:
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
    try:
        # 指定モデル gemini-3.8-flash を使用して一括取得
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        return response.text
    except errors.APIError as e:
        return f"⚠️ APIエラーが発生しました: {e}"
    except Exception as e:
        return f"⚠️ 応答タイムアウトまたはエラーが発生しました (15秒超過): {e}"


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

# 解析結果の表示 (キャッシュにあれば即表示、なければ新規取得)
if word in st.session_state.analysis_cache:
    st.markdown(st.session_state.analysis_cache[word])
else:
    with st.spinner(f"「{word}」の構造を Gemini API で解析中（最大15秒）..."):
        result_text = fetch_analysis(word)
        st.session_state.analysis_cache[word] = result_text
    st.markdown(result_text)

st.divider()

# --- ページ下部：検索エリア ---
st.subheader("🔎 英単語を検索する")

search_input = st.text_input(
    "調べたい英単語を入力してください（半角英字）",
    key="search_term",
    placeholder="例: preview, bisect, incredible"
)

if st.button("構造を解析する", type="primary"):
    target_word = search_input.strip().lower()
    if target_word:
        st.session_state.current_word = target_word
        st.rerun()
    else:
        st.warning("英単語を入力してください。")

```
