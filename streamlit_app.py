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

# --- プリセットデータ（通信消費0で即時表示する初期データ：20単語） ---
PRESET_ANALYSIS = {
    "predict": """### 📌 【predict】の和訳と意味
- **和訳**: 予測する、予言する
- **概要**: あらかじめ（前に）言うことから、将来の出来事を「予測する」意味になります。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `pre-`（前に、あらかじめ）
- **語根・語幹**: `dict`（言う、伝える）
- **接尾辞**: なし
- **全体の成り立ち**: 「事前に（pre-）」「言う（dict）」＝「予測する」

### 🔗 共通パーツを持つ他の英単語
- **dictionary** (辞書): 語根 `dict`（言葉）を集めたもの
- **contradict** (矛盾する): 接頭辞 `contra-`（反対に）＋ `dict`（言う）""",

    "sympathy": """### 📌 【sympathy】の和訳と意味
- **和訳**: 同情、共感
- **概要**: 他人の感情を自分と同じように「共に感じる」心の状態。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `sym-`（共に）
- **語根・語幹**: `path`（感情、苦痛）
- **接尾辞**: `-y`（状態・性質を表す名詞化）
- **全体の成り立ち**: 「共に（sym-）」「感情（path）」を共有する状態（-y）＝「共感」

### 🔗 共通パーツを持つ他の英単語
- **empathy** (感情移入): `em-`（中に）＋ `path`（感情）
- **telepathy** (テレパシー): `tele-`（遠く）＋ `path`（感情）""",

    "transport": """### 📌 【transport】の和訳と意味
- **和訳**: 輸送する、交通機関
- **概要**: 物品や人をある場所から別の場所へ「越えて運ぶ」動き。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `trans-`（越えて、向こう側へ）
- **語根・語幹**: `port`（運ぶ、港）
- **接尾辞**: なし
- **全体の成り立ち**: 「向こう側へ（trans-）」「運ぶ（port）」＝「輸送する」

### 🔗 共通パーツを持つ他の英単語
- **export** (輸出する): `ex-`（外へ）＋ `port`（運ぶ）
- **import** (輸入する): `im-`（中に）＋ `port`（運ぶ）""",

    "preview": """### 📌 【preview】の和訳と意味
- **和訳**: 試写、下書き、事前に見る
- **概要**: 実際に公開・実行される「前に見る」こと。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `pre-`（前に、事前に）
- **語根・語幹**: `view`（見る）
- **接尾辞**: なし
- **全体の成り立ち**: 「事前に（pre-）」「見る（view）」＝「試写・下書き」

### 🔗 共通パーツを持つ他の英単語
- **review** (復習・再検討): `re-`（再び）＋ `view`（見る）
- **interview** (面接): `inter-`（お互いに）＋ `view`（見る）""",

    "invisible": """### 📌 【invisible】の和訳と意味
- **和訳**: 目に見えない
- **概要**: 視覚で捉えることができない状態。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `in-`（否定、〜ない）
- **語根・語幹**: `vis`（見る）
- **接尾辞**: `-ible`（〜できる：形容詞化）
- **全体の成り立ち**: 「見（vis）」「る事ができる（-ible）」「ない（in-）」＝「目に見えない」

### 🔗 共通パーツを持つ他の英単語
- **vision** (視覚、展望): `vis`（見る）＋ `-ion`（こと）
- **visible** (目に見える): `vis`（見る）＋ `-ible`（できる）""",

    "incredible": """### 📌 【incredible】の和訳と意味
- **和訳**: 信じられない、素晴らしい
- **概要**: あまりにすごくて「信じることができない」ほどの状態。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `in-`（否定、〜ない）
- **語根・語幹**: `cred`（信じる）
- **接尾辞**: `-ible`（〜できる：形容詞化）
- **全体の成り立ち**: 「信じ（cred）」「る事ができる（-ible）」「ない（in-）」＝「信じられない」

### 🔗 共通パーツを持つ他の英単語
- **credit** (信用、クレジット): `cred`（信じる）
- **credible** (信用できる): `cred`（信じる）＋ `-ible`（できる）""",

    "construct": """### 📌 【construct】の和訳と意味
- **和訳**: 建設する、組み立てる
- **概要**: 部品や材料を「共に積み上げて」形を作ること。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `con-`（共に、一緒に）
- **語根・語幹**: `struct`（建てる、積む）
- **接尾辞**: なし
- **全体の成り立ち**: 「共に（con-）」「建てる（struct）」＝「建設する」

### 🔗 共通パーツを持つ他の英単語
- **structure** (構造): `struct`（建てる）＋ `-ure`（名詞化）
- **destruct** (破壊する): `de-`（離れて・壊して）＋ `struct`（建てる）""",

    "extract": """### 📌 【extract】の和訳と意味
- **和訳**: 引き出す、抽出する
- **概要**: 中にあるものを「外へ引っ張り出す」こと。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `ex-`（外へ）
- **語根・語幹**: `tract`（引く）
- **接尾辞**: なし
- **全体の成り立ち**: 「外へ（ex-）」「引く（tract）」＝「抽出する」

### 🔗 共通パーツを持つ他の英単語
- **attract** (引きつける): `at-`（〜へ）＋ `tract`（引く）
- **contract** (契約する、縮小する): `con-`（共に）＋ `tract`（引く）""",

    "progress": """### 📌 【progress】の和訳と意味
- **和訳**: 前進する、進歩
- **概要**: 前に向かって歩みを進めること。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `pro-`（前へ）
- **語根・語幹**: `gress`（行く、歩む）
- **接尾辞**: なし
- **全体の成り立ち**: 「前へ（pro-）」「歩む（gress）」＝「前進・進歩」

### 🔗 共通パーツを持つ他の英単語
- **congress** (議会、会議): `con-`（共に）＋ `gress`（行く・集まる）
- **regress** (退歩する): `re-`（後ろへ）＋ `gress`（歩む）""",

    "reject": """### 📌 【reject】の和訳と意味
- **和訳**: 拒絶する、却下する
- **概要**: 受け入れずに「後ろへ投げ返す」こと。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `re-`（後ろへ、再び）
- **語根・語幹**: `ject`（投げる）
- **接尾辞**: なし
- **全体の成り立ち**: 「後ろへ（re-）」「投げる（ject）」＝「拒絶する」

### 🔗 共通パーツを持つ他の英単語
- **inject** (注射する、注入する): `in-`（中へ）＋ `ject`（投げる）
- **project** (計画、投影する): `pro-`（前へ）＋ `ject`（投げる）""",

    "inspect": """### 📌 【inspect】の和訳と意味
- **和訳**: 検査する、視察する
- **概要**: 中をよく「覗き見る」ことで調べること。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `in-`（中を）
- **語根・語幹**: `spect`（見る）
- **接尾辞**: なし
- **全体の成り立ち**: 「中を（in-）」「見る（spect）」＝「検査する」

### 🔗 共通パーツを持つ他の英単語
- **respect** (尊敬する): `re-`（再び・振り返って）＋ `spect`（見る）
- **spectator** (観客): `spect`（見る）＋ `-ator`（人）""",

    "autograph": """### 📌 【autograph】の和訳と意味
- **和訳**: サイン、自筆
- **概要**: 本人が「自分自身で書いた」署名。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `auto-`（自分自身、自動の）
- **語根・語幹**: `graph`（書くこと）
- **接尾辞**: なし
- **全体の成り立ち**: 「自分自身で（auto-）」「書いたもの（graph）」＝「サイン」

### 🔗 共通パーツを持つ他の英単語
- **automatic** (自動の): `auto-`（自分で動く）
- **biography** (伝記): `bio`（生命）＋ `graph`（書く）""",

    "monochrome": """### 📌 【monochrome】の和訳と意味
- **和訳**: 白黒の、単色の
- **概要**: 1つの色だけで描かれた状態。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `mono-`（１つの、単一の）
- **語根・語幹**: `chrome`（色）
- **接尾辞**: なし
- **全体の成り立ち**: 「１つの（mono-）」「色（chrome）」＝「単色の」

### 🔗 共通パーツを持つ他の英単語
- **monologue** (独白): `mono-`（１人）＋ `logue`（話す）
- **Google Chrome** (ブラウザ名): カラフルな「色（chrome）」が由来のひとつ""",

    "philosophy": """### 📌 【philosophy】の和訳と意味
- **和訳**: 哲学、人生観
- **概要**: 知恵や知識を「愛する」学問。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `philo-`（愛する）
- **語根・語幹**: `sophy`（知恵）
- **接尾辞**: なし
- **全体の成り立ち**: 「愛する（philo-）」「知恵を（sophy）」＝「哲学」

### 🔗 共通パーツを持つ他の英単語
- **philanthropy** (慈善活動): `philo-`（愛する）＋ `anthro`（人類）
- **sophomore** (大学2年生): `sopho`（賢い）＋ `more`（愚か）※賢ぶる時期の意味""",

    "submariner": """### 📌 【submariner】の和訳と意味
- **和訳**: 潜水艦乗組員
- **概要**: 海の下で活動する人。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `sub-`（下に）
- **語根・語幹**: `marin`（海）
- **接尾辞**: `-er`（〜する人）
- **全体の成り立ち**: 「海（marin）」「の下（sub-）」「の人（-er）」＝「潜水艦乗組員」

### 🔗 共通パーツを持つ他の英単語
- **submarine** (潜水艦): `sub-`（下）＋ `marine`（海）
- **subway** (地下鉄): `sub-`（下）＋ `way`（道）""",

    "biodiversity": """### 📌 【biodiversity】の和訳と意味
- **和訳**: 生物多様性
- **概要**: 様々な生命が豊かに存在している状態。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `bio-`（生命、生物）
- **語根・語幹**: `divers`（多様な）
- **接尾辞**: `-ity`（状態・性質を表す名詞化）
- **全体の成り立ち**: 「生物の（bio-）」「多様な（divers）」「状態（-ity）」＝「生物多様性」

### 🔗 共通パーツを持つ他の英単語
- **biology** (生物学): `bio`（生命）＋ `-logy`（学問）
- **diversity** (多様性): `divers`（多様な）＋ `-ity`（状態）""",

    "bisect": """### 📌 【bisect】の和訳と意味
- **和訳**: 二等分する
- **概要**: ２つに切り分けること。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `bi-`（２つの）
- **語根・語幹**: `sect`（切る）
- **接尾辞**: なし
- **全体の成り立ち**: 「２つに（bi-）」「切る（sect）」＝「二等分する」

### 🔗 共通パーツを持つ他の英単語
- **bicycle** (自転車): `bi-`（２つ）＋ `cycle`（車輪）
- **section** (部分、切ったもの): `sect`（切る）＋ `-ion`（こと）""",

    "triangle": """### 📌 【triangle】の和訳と意味
- **和訳**: 三角形
- **概要**: ３つの角を持つ図形。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `tri-`（３つの）
- **語根・語幹**: `angle`（角）
- **接尾辞**: なし
- **全体の成り立ち**: 「３つの（tri-）」「角（angle）」＝「三角形」

### 🔗 共通パーツを持つ他の英単語
- **tricycle** (三輪車): `tri-`（３つ）＋ `cycle`（車輪）
- **triple** (３倍の): `tri-`（３つ）を含む""",

    "uniform": """### 📌 【uniform】の和訳と意味
- **和訳**: 制服、均一な
- **概要**: 全員が「１つの形」に揃っていること。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: `uni-`（１つの）
- **語根・語幹**: `form`（形）
- **接尾辞**: なし
- **全体の成り立ち**: 「１つの（uni-）」「形（form）」＝「制服・均一」

### 🔗 共通パーツを持つ他の英単語
- **unicorn** (ユニコーン): `uni-`（１つ）＋ `corn`（角）
- **unique** (唯一の): `uni-`（１つ）を含む""",

    "flexible": """### 📌 【flexible】の和訳と意味
- **和訳**: 柔軟な、曲げやすい
- **概要**: 状況に合わせてしなやかに曲がることができる状態。

### 🧩 成り立ち（パーツ分解）
- **接頭辞**: なし
- **語根・語幹**: `flex`（曲げる）
- **接尾辞**: `-ible`（〜できる）
- **全体の成り立ち**: 「曲げる（flex）」「ことができる（-ible）」＝「柔軟な」

### 🔗 共通パーツを持つ他の英単語
- **reflect** (反射する): `re-`（後ろに・再び）＋ `flect`（曲げる）
- **reflex** (反射神経): 再び（re-）曲がる（flex）動き"""
}

# APIキー取得とクライアント初期化
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=gemini_api_key)
except KeyError:
    st.error("APIキーが設定されていません。")
    st.stop()

# セッションステート初期化
if "analysis_cache" not in st.session_state:
    st.session_state.analysis_cache = PRESET_ANALYSIS.copy()

if "current_word" not in st.session_state:
    st.session_state.current_word = random.choice(list(PRESET_ANALYSIS.keys()))


# API問い合わせ関数（エラーメッセージを簡略化）
def fetch_analysis(word: str) -> str:
    prompt = f"""
英単語「{word}」の語源・構造解析を以下のフォーマットに従って簡潔に解説してください。

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
    max_retries = 3
    delay = 2

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )
            return response.text
        except errors.APIError as e:
            err_msg = str(e)
            if "503" in err_msg or "UNAVAILABLE" in err_msg:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                return "⚠️ サーバーが混雑しています。少し待ってから再度お試しください。"
            elif "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                return "⚠️ APIリクエストの上限に達しました。しばらく時間をおいてから再度お試しください。"
            else:
                return f"⚠️ APIエラーが発生しました: {e}"
        except Exception as e:
            return f"⚠️ エラーが発生しました: {e}"


# --- UI表示 ---
st.title("🔤 英単語構造学習アプリ")
st.caption("接頭辞・語根・接尾辞の成り立ちから英単語のコア意味を学びます。")

word = st.session_state.current_word

st.subheader(f"📖 表示中の単語: `{word}`")

# ランダム切替ボタン
if st.button("🎲 別のランダム例を見る"):
    st.session_state.current_word = random.choice(list(PRESET_ANALYSIS.keys()))
    st.rerun()

# 解析結果の表示
if word in st.session_state.analysis_cache:
    st.markdown(st.session_state.analysis_cache[word])
else:
    with st.spinner(f"「{word}」の構造を解析中..."):
        result_text = fetch_analysis(word)
        if not result_text.startswith("⚠️"):
            st.session_state.analysis_cache[word] = result_text
    st.markdown(result_text)

st.divider()

# 検索エリア
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
