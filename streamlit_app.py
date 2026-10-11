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

# --- プリセットデータ（トップ画面用：通信ゼロで即時0秒表示） ---
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
- **contradict** (矛盾する、反論する): 接頭辞 `contra-`（反対に）＋ `dict`（言う）
- **preview** (予告、下書き): 接頭辞 `pre-`（事前に）＋ `view`（見る）""",

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
- **telepathy** (テレパシー): 接頭辞 `tele-`（遠く離れた）＋ `path`（感情）
- **symphony** (交響曲): 接頭辞 `sym-`（共に）＋ `phon`（音）""",

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
- **import** (輸入する): 接頭辞 `im-`（中に）＋ `port`（運ぶ）
- **translate** (翻訳する): 接頭辞 `trans-`（越えて・変えて）＋ `late`（運ばれた）""",

    "autograph": """### 📌 【autograph】の和訳と意味
- **和訳**: （有名人などの）サイン、自筆の署名
- **概要**: 本人が「自分自身で書いた」文字や署名を指します。

### 🧩 成り立ち（パーツ分解）
- **接頭辞 (Prefix)**: `auto-`（自分自身、自動の）
- **語根・語幹 (Root/Stem)**: `graph`（書くこと、記録、図）
- **接尾辞 (Suffix)**: なし
- **全体の成り立ち**: 「自分自身で（auto-）」「書いたもの（graph）」＝「サイン」

### 🔗 共通パーツを持つ他の英単語
- **automatic** (自動の): 接頭辞 `auto-`（自分で動く）
- **biography** (伝記): `bio`（生命・人生）＋ `graph`（書かれたもの）
- **telegraph** (電信): `tele`（遠くへ）＋ `graph`（書く・送る）""",

    "contradict": """### 📌 【contradict】の和訳と意味
- **和訳**: 矛盾する、否定する、反論する
- **概要**: 相手の言ったことに対して「反対の言葉を言う」ことから生じる意味です。

### 🧩 成り立ち（パーツ分解）
- **接頭辞 (Prefix)**: `contra-`（反対に、対立して）
- **語根・語幹 (Root/Stem)**: `dict`（言う、宣言する）
- **接尾辞 (Suffix)**: なし
- **全体の成り立ち**: 「反対に（contra-）」「言う（dict）」＝「矛盾する・反論する」

### 🔗 共通パーツを持つ他の英単語
- **contrast** (対比、対照): `contra-`（反対）
- **dictator** (独裁者): `dict`（言う人・命令する人）
- **predict** (予測する): `pre-`（前に）＋ `dict`（言う）"""
}

# サンプル単語リスト
SAMPLE_WORDS = list(PRESET_ANALYSIS.keys())

# APIクライアントを取得する関数（セッションキャッシュ）
@st.cache_resource
def get_gemini_client():
    try:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=gemini_api_key)
    except KeyError:
        return None

# 新規単語用API問い合わせ（検索結果をキャッシュして2回目の検索を高速化）
@st.cache_data(show_spinner=False)
def fetch_from_gemini(word: str) -> str:
    client = get_gemini_client()
    if not client:
        return "⚠️ APIキーが設定されていません。StreamlitのSecretsに 'GEMINI_API_KEY' を設定してください。"

    prompt = f"""
英単語 「{word}」 について、語源や構造（語幹・接頭辞・接尾辞など）を学習するための解説を作成してください。

以下のフォーマットに従って、わかりやすい日本語のマークダウン形式で出力してください：

### 📌 【{word}】の和訳と意味
- **
