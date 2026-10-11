import random
import time
import streamlit as st
from google import genai
from google.genai import errors

# ページ基本設定
st.set_page_config(
    page_title="英単語構造学習アプリ",
    page_icon="🔤",
    layout="centered"
)

# --- プリセットデータ（初期表示・高速表示用） ---
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

# 実在するモデル候補（flashで制限超過・通信不調が発生した場合はproに自動切換）
MODEL_CANDIDATES = [
    "gemini-3.8-flash",
    "gemini-3.8-pro",
]

# APIキー取得とクライアント初期化
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=gemini_api_key)
except KeyError:
    st.error("APIキーが設定されていません。Streamlit Secretsに 'GEMINI_API_KEY' を設定してください。")
    st.stop()

# セッションステート初期化
if "analysis_cache" not in st.session_state:
    st.session_state.analysis_cache = PRESET_ANALYSIS.copy()

if "current_word" not in st.session_state:
    st.session_state.current_word = random.choice(list(PRESET_ANALYSIS.keys()))


def fetch_analysis(word: str) -> str:
    prompt = f"""
英単語「{word}」の語源・構造解析を以下のフォーマットに従って簡潔に解説してください。

### 📌 【{word}】の和訳と意味
- **和訳**: 
- **概要**: 

### 🧩 成り立ち（パーツ分解）
- **接頭辞 (Prefix)**: 
- **語根・語幹 (Root/Stem)**: 
- **接尾辞 (Suffix)**: 
- **全体の成り立ち**: 

### 🔗 共通パーツを持つ他の英単語
- **単語1** (和訳): 解説
- **単語2** (和訳): 解説
"""
    last_error_details = ""

    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
        except errors.APIError as e:
            err_msg = str(e)
            last_error_details = err_msg
            # 429(制限超過)、503(混雑)、404(未存在) の場合は次の候補モデルへ自動フォールバック
            if any(code in err_msg for code in ["429", "RESOURCE_EXHAUSTED", "503", "404", "NOT_FOUND"]):
                continue
            else:
                return f"⚠️ APIエラーが発生しました ({model_name}): {e}"
        except Exception as e:
            return f"⚠️ 予期せぬエラーが発生しました: {e}"

    return (
        "⚠️ **Gemini APIの利用制限（429 Quota Exceeded）または高負荷状態です。**\n\n"
        "- 無料枠（Free Tier）の制限に達しているため、時間を置いて再度お試しください。\n"
        "- Google AI Studioで従量課金（Pay-as-you-go）を設定することで制限なく即座にご利用可能です。\n"
        f"（詳細: {last_error_details}）"
    )


# UI表示
st.title("🔤 英単語構造学習アプリ")
st.caption("接頭辞・語根・接尾辞の成り立ちから英単語のコア意味を学びます。")

word = st.session_state.current_word

st.subheader(f"📖 表示中の単語: `{word}`")

if st.button("🎲 別のランダム例を見る"):
    st.session_state.current_word = random.choice(list(PRESET_ANALYSIS.keys()))
    st.rerun()

if word in st.session_state.analysis_cache:
    st.markdown(st.session_state.analysis_cache[word])
else:
    with st.spinner(f"「{word}」の構造を解析中..."):
        result_text = fetch_analysis(word)
        if not result_text.startswith("⚠️"):
            st.session_state.analysis_cache[word] = result_text
    st.markdown(result_text)

st.divider()

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
