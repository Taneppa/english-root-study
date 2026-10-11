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

# --- プリセットデータ（API消費なしで即時表示する初期データ） ---
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

# --- セッション状態の初期化 ---
if "analysis_cache" not in st.session_state:
    st.session_state.analysis_cache = PRESET_ANALYSIS.copy()

if "current_word" not in st.session_state:
    st.session_state.current_word = random.choice(list(PRESET_ANALYSIS.keys()))


# 実在する標準モデル (gemini-2.5-flash) を使用した問い合わせ関数
def fetch_analysis(word: str) -> str:
    prompt = f"""
英単語「{word}」の語源・構造解析を以下のフォーマットで短く簡潔に解説してください。

### 📌 【{word}】の和訳と意味
- **和訳**: 
- **概要**: 

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: 
- **語根・語幹**: 
- **接尾辞**: 
- **全体の成り立ち**: 

### 🔗 共通パーツを持つ他の英単語
- **単語1** (和訳): 解説
- **単語2** (和訳): 解説
"""
    try:
        # 正しいモデル名 gemini-2.5-flash を指定
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except errors.APIError as e:
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            return (
                "⚠️ **APIの利用制限（429 Quota Exceeded）に達しました。**\n\n"
                "Google AI Studioの無料枠（Free Tier）の上限に達したため、現在通信が制限されています。\n"
                "- 数分〜時間を置いてから再度検索してください。\n"
                "- Google AI Studioで従量課金（Pay-as-you-go）を設定すると、無制限で利用可能になります。"
            )
        return f"⚠️ APIエラーが発生しました: {e}"
    except Exception as e:
        return f"⚠️ エラーが発生しました: {e}"


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

# 解析結果の表示 (キャッシュにあれば即表示、無ければAPI取得)
if word in st.session_state.analysis_cache:
    st.markdown(st.session_state.analysis_cache[word])
else:
    with st.spinner(f"「{word}」の構造を解析中..."):
        result_text = fetch_analysis(word)
        if not result_text.startswith("⚠️"):
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
