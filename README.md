# 🔤 英単語構造学習アプリ (English Word Structure Learning App)

🌐 **実際のアプリはこちらからお試しいただけます:** [https://chatbot-6uxnifrwjui.streamlit.app/](https://chatbot-6uxnifrwjui.streamlit.app/)

## 📌 アプリの概要

「英単語構造学習アプリ」は、英単語の意味を単に調べるだけでなく、**その単語の成り立ち（接頭辞・語幹/語根・接尾辞）を分解して解説する**学習サポートツールです。

「なぜその意味になるのか」というコアなニュアンスを理解し、さらに**共通するパーツを持つ別の英単語**もあわせて知ることで、通常の辞書を引くよりも深く、芋づる式に語彙力を伸ばすことを目的として設計されています。

## 📷 画面イメージ

<img width="1044" height="1504" alt="image" src="https://github.com/user-attachments/assets/c24f013a-4d42-4374-b453-e7afc766e316" />

## ✨ 主な機能

1. **構造の可視化と解説**

   * 入力された英単語を「接頭辞(Prefix)」「語根・語幹(Root/Stem)」「接尾辞(Suffix)」に分解。

   * 各パーツの意味と、それらがどう組み合わさって現在の意味（和訳）になっているかを分かりやすく解説します。

2. **関連単語の提示**

   * 調べた単語と同じ語根・接頭辞などを持つ他の英単語を例示し、関連づけて暗記できるようにサポートします。

3. **即時表示機能（プリセット）**

   * アプリ起動時には、あらかじめ登録されたいくつかの単語からランダムに1つ選ばれ、API通信を待たずに即座に解説が表示されます。

4. **検索とキャッシュ機能**

   * 任意の英単語を検索可能。一度調べた単語の結果はアプリ内にキャッシュされ、再検索時は瞬時に結果が表示されます。

## 📷 使用例

## 🛠 使用技術・要件

* **Python 3.x**

* **Streamlit**: Webアプリケーションフレームワーク

* **Google GenAI SDK**: Gemini APIを用いた単語構造の解析

* **Gemini 3.8 Flash**: テキスト生成モデル

### 必須ライブラリ

```
streamlit
google-genai

```

## 🚀 ローカルでの動かし方

1. **リポジトリのクローン**

   ```
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   
   ```

2. **必要なパッケージのインストール**

   ```
   pip install -r requirements.txt
   
   ```

3. **APIキーの設定**
   ローカルで動かす場合、`.streamlit/secrets.toml` ファイルを作成し、Gemini APIキーを設定してください。

   ```
   # .streamlit/secrets.toml
   GEMINI_API_KEY = "あなたのAPIキー"
   
   ```

4. **アプリの起動**

   ```
   streamlit run app.py
   
   ```

## ☁️ Streamlit Community Cloud へのデプロイ

1. GitHubにコード（`app.py` と `requirements.txt`）をプッシュします。

2. [Streamlit Community Cloud](https://streamlit.io/cloud) にログインし、「New app」を作成します。

3. 対象のリポジトリ、ブランチ、メインファイルパス（`app.py`）を指定します。

4. **Advanced settings** の **Secrets** に、APIキーを以下のように設定します。

   ```
   GEMINI_API_KEY = "あなたのAPIキー"
   
   ```

5. 「Deploy」をクリックして完了です。

## ⚠️ 注意事項

* 本アプリはGoogleのGemini APIを利用しています。利用頻度によってはAPIのレート制限（429エラーなど）に達する可能性があります。

* 安定した運用のために、Google AI Studioにて適切な課金設定（Pay-as-you-go等）を行うことをお勧めします。
