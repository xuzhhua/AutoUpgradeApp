# AutoUpgradeApp.py（日本語）

**他の言語版 / Other Languages / 其他语言版本:**
- [中文](README.md)
- [English](README_EN.md)

このスクリプトは、Windows パッケージマネージャー winget を利用して、Windows アプリの自動チェックとアップグレードを行います。
多言語出力、ユーザー定義の除外・強制更新リスト、更新活動の記録に対応しています。
スクリプトは常駐型で、24時間ごとに自動で更新をチェックします。

## モジュール

- `subprocess`：winget コマンドの実行
- `time`：定期的なチェック
- `os`：ファイルとパスの操作
- `keyboard`：更新前後にホットキーを送信
- `datetime`：更新タイムスタンプの記録
- `unicodedata`：多言語文字の表示幅処理
- `json`：言語パックの読み込み
- `locale`：システム言語の検出

## 主な関数

- **load_lang_pack()**  
  `lang.json` から言語パックを読み込み、システム言語に応じたローカライズ文字列辞書を返します。

- **get_default_excluded_apps()**  
  デフォルトの除外アプリ名と表ヘッダーを返します。

- **load_excluded_apps(file_path)**  
  ファイルから除外・強制更新リストを読み込み、2つのリストを返します。

- **check_and_update_apps()**  
  winget で利用可能な更新をチェックします。  
  除外リストにあるアプリ（強制更新リストを除く）をスキップし、更新を実行して結果を記録します。  
  **新機能：wingetアップグレードプロセスのリアルタイム出力表示。**

- **substr_by_display_width(s, start, length)**  
  表示幅で文字列を抽出し、全角文字にも対応します。

- **get_display_width(s)**  
  文字列の表示幅を計算します（全角文字対応）。

- **monitor_updates()**  
  メインループで24時間ごとに更新チェックを実行。  

- **get_current_datetime_string()**  
  現在の日付と時刻をフォーマットして返します。

## 使い方

1. スクリプトを直接実行すると、自動更新監視が開始されます。
2. `lang.json`、`update_policy.txt`、`proxy.txt`（オプション）、および `check_interval.txt`（オプション）を同じディレクトリに配置し、言語、除外設定、プロキシ設定、およびチェック間隔設定を行ってください。

## 注意事項

1. winget がインストールされ、システムの PATH に設定されていることを確認してください。
2. 更新操作を行うため、管理者権限でスクリプトを実行してください。
3. 必要に応じて `update_policy.txt`、`lang.json`、`proxy.txt`、および `check_interval.txt` の内容を調整してください。
   特に lang.json の英語・日本語の `titles` と `all_latest` の設定はシステム制限により未検証です。必要に応じて修正してください。
4. 更新をダウンロードするため、スクリプト実行中はネットワーク接続を維持してください。
5. 中国本土で使用する場合、特別な理由で魔法が必要な場合があります。

## update_policy.txt の使い方

- 各行に自動更新から除外したいアプリ名を記載します（ID、表示名など、あいまい一致・大文字小文字無視に対応）。
- 行頭に感嘆符 `!` を付けると「強制更新」アプリとなり、除外リストにあっても必ず更新されます。
- パスの後に `|admin` を追加することで、アプリを管理者権限で起動するかどうかを指定できます。
- 空行や空白のみの行は無視されます。
- 特殊ルール：
  - 単独一行 `*` は「強制更新対象のみを更新し、他のすべてのアプリをスキップする」ことを意味し、スキップされたすべてのアプリの情報がコンソールに表示されます。

### 例：

```
# 強制更新対象のみを更新し、他のすべてのアプリをスキップ
*
!AppID1=C:\Path\To\App1.exe|admin
!AppID2=C:\Path\To\App2.exe
AppID3
AppID4
!AppID3
```

上記の例では：
- AppID1 と AppID2 のみが強制的にアップデートされ（設定に従って指定アプリも起動）、AppID3 も強制的にアップデートされます。AppID4 およびその他すべてのアプリはスキップされ、スキップ情報がコンソールに表示されます。
- `!AppID3` は AppID3 を強制的にアップデートし、指定されたアプリを起動しないことを意味します。
- `|admin` は管理者権限で起動することを意味します。

### 互換性の注意事項
- `*` が設定されていない場合、通常の除外/強制更新ルールが適用されます。
- `*` が設定されている場合、強制更新対象のみが処理され、他のすべてがスキップされ、プロンプトが表示されます。

## プロキシサーバー設定

プロキシサーバーを介してネットワークにアクセスする必要がある場合は、`proxy.txt` ファイルを作成してプロキシを設定できます。

### proxy.txt 設定フォーマット

```text
# プロキシサーバー設定ファイル
# 以下のフォーマットをサポートします：
http://proxy.example.com:8080
https://proxy.example.com:8080
proxy.example.com:8080  # 自動的に http:// を追加

# 例：
http://127.0.0.1:8080
192.168.1.100:8080
```

### プロキシ設定の注意事項

- プロキシが不要な場合は、`proxy.txt` ファイルを削除するか、すべての行をコメントアウトしてください。
- HTTP および HTTPS プロキシプロトコルをサポートします。
- `host:port` 形式のみが提供された場合、`http://` プレフィックスが自動的に追加されます。
- プロキシ設定はすべての winget ネットワークリクエストに適用されます。
- 設定の変更は次のサイクルで自動的に再読み込みされます。

## チェック間隔設定

`check_interval.txt` ファイルでアップデートチェックの時間間隔をカスタマイズできます。

### check_interval.txt 設定フォーマット

```text
# チェック間隔設定ファイル
# サポートされている形式:
# - 数字 + h/H: 時間
# - 数字 + m/M: 分  
# - 数字 + s/S: 秒
# - 数字のみ: 秒

# 例:
24h     # 24時間
12h     # 12時間
6h      # 6時間
30m     # 30分
3600s   # 3600秒
86400   # 86400秒（24時間）
```

### チェック間隔設定の注意事項

- ファイルが存在しない場合、デフォルトの24時間間隔が使用されます。
- `1.5h`（1.5時間）や `90m`（90分）など小数点をサポートします。
- 設定の変更は次のサイクルで自動的に再読み込みされます。
- 過度に頻繁なチェックを避けるため、最小間隔は30分以上を推奨します。

## リアルタイム表示機能

**新機能：wingetアップグレードプロセスのリアルタイム表示**

アプリのアップグレード時に、wingetの出力情報をリアルタイムで表示し、ユーザーがアップグレードの進行状況とステータスをすぐに把握できるようにします。

### リアルタイム表示の特徴

- ✅ **リアルタイム出力**: アップグレードプロセス中にwingetのすべての出力情報をリアルタイムで表示
- ✅ **多言語対応**: 中国語、英語、日本語のリアルタイム出力インジケーターをサポート
- ✅ **エラー処理**: エンコーディング問題と例外状況の智能的な処理
- ✅ **互換性維持**: 既存機能の完全性を維持し、既存ロジックに影響しません
- ✅ **明確なフォーマット**: セパレーターとインデントを使用してリアルタイム出力コンテンツを明確に識別

### リアルタイム表示の例

```
Microsoft.VisualStudioCode のアップグレードを開始、リアルタイム出力:
==================================================
  Found Microsoft Visual Studio Code [Microsoft.VisualStudioCode] Version 1.85.0
  This application is licensed to you by its owner.
  Downloading https://github.com/microsoft/vscode/releases/download/1.85.1/VSCodeSetup-x64-1.85.1.exe
  ██████████████████████████████  32.0 MB / 32.0 MB
  Successfully verified installer hash
  Starting package install...
  Successfully installed
==================================================
更新成功: Microsoft.VisualStudioCode [1.85.1]
```

### 技術実装

- `subprocess.Popen` を使用してノンブロッキングプロセスを作成
- `readline()` を通じて出力ストリームをリアルタイム読み取り
- WindowsシステムのGBKエンコーディングを自動処理
- 智能的エラー処理と例外キャッチ

## コマンドライン引数と高度な使い方

- `--dry-run`：アップグレード対象アプリをプレビューのみ行い、実際のアップグレードや起動は行いません（テストや定期タスクのプレビューに最適）。
- `--once`：アップグレードチェックを一度だけ実行し、24時間ループには入りません（定期タスクや手動実行に適しています）。

### 例：

```bash
python AutoUpgradeApp.py --dry-run
python AutoUpgradeApp.py --once
python AutoUpgradeApp.py --dry-run --once
```

## 業務プロセス構成

- メインエントリ `main()` は引数解析、権限チェック、メインループの調整を担当します。
- `monitor_updates()` は定期ループまたは単回実行に対応します。
- `check_and_update_apps()` はアップグレード可能なアプリを巡回し、ポリシーに従ってアップグレードを判断・実行します。
- `process_upgrade_item()` は個々のアプリのアップグレード／スキップ／強制／除外などの業務ロジックを処理します。
- `launch_app_by_id()` はアップグレード後に指定アプリの自動起動をサポートします。

## 起動アプリの出力動作

- `launch_app_by_id()` で起動されたアプリの標準出力とエラー出力はリダイレクトされ、現在のコンソールウィンドウには表示されません。これにより、メインスクリプトのログや出力に干渉しません。
- この動作は、管理者権限で起動されるかどうかに関わらず、アップグレード後に自動的に起動されるすべてのアプリに適用されます。
- 起動されたアプリの出力を確認するには、対応するプログラムを手動で実行してください。

## よくある質問（FAQ）

**Q1: アップグレード後に自動起動したアプリの出力がないのはなぜですか？**
A: `launch_app_by_id()` で起動されたアプリの標準出力とエラー出力はリダイレクトされ、現在のコンソールウィンドウには表示されません。これにより、メインスクリプトのログに干渉しません。出力を確認するには、手動で対応するプログラムを実行してください。

**Q2: どうすれば一部のアプリのみをアップグレードしたり、特定のアプリを除外できますか？**
A: `update_policy.txt` を編集し、除外と強制更新対象をルールに従って記入してください。`*` ルールを使用して強制更新対象のみをアップグレードし、他はすべてスキップできます。

**Q3: スクリプトはなぜ管理者権限が必要ですか？**
A: winget のほとんどのアプリアップグレード操作は管理者権限を必要とします。そうしないと、失敗したり部分的に無効になることがあります。

**Q4: ログファイルはどこにありますか？カスタマイズは可能ですか？**
A: ログファイルのパスと形式は `output.py` で調整可能で、すべての info/warn/error レベルのログが記録されます。

**Q5: 英語/日本語インターフェースで一部のプロンプトが不完全なのはなぜですか？**
A: システム制限により、`lang.json` の英語と日本語の `titles`、`all_latest` などのフィールドは完全にテストされていません。実際の出力に基づいて調整することをお勧めします。

**Q6: Windows タスクスケジューラや CI/CD と統合するには？**
A: `--once` または `--dry-run --once` パラメータを使用し、定期的にトリガーするためにスケジュールされたタスクと組み合わせることをお勧めします。詳細は「コマンドライン引数と高度な使い方」セクションを参照してください。

**Q7: どの Windows バージョンがサポートされていますか？**
A: Windows 10/11 のみサポートされており、winget 1.3+ と Python 3.7+ が事前にインストールされている必要があります。

**Q8: プロキシサーバーを設定するにはどうすればよいですか？**
A: `proxy.txt` ファイルを作成し、プロキシサーバーのアドレス（例：`http://proxy.example.com:8080`）を入力してください。プロキシが不要な場合はファイルを削除してください。設定は次のサイクルで自動的に再読み込みされます。

**Q9: アップデートチェックの時間間隔を変更するにはどうすればよいですか？**
A: `check_interval.txt` ファイルを作成または編集して、希望する時間間隔を設定してください。`24h`（24時間）、`30m`（30分）、`3600s`（3600秒）、または `86400`（数字のみ秒）などの形式をサポートします。

**Q10: "AttributeError: '_io.TextIOWrapper' object has no attribute 'mode'" エラーが発生した場合はどうすればよいですか？**
A: これは初期バージョンのテキストモード検出の問題で、最新バージョンで修正済みです。最新バージョンに更新することで解決できます。問題が続く場合は、完全なコードを再ダウンロードしてください。

**Q11: なぜ「ユーザー指定の更新をスキップ: 明示的ターゲットがアップグレードに必要です」のようなメッセージがまだ表示されるのですか？**
A: これはwingetのプロンプト情報行で、実際のアプリケーション更新項目ではありません。最新バージョンでは解析ロジックが改善され、このような異常な形式のプロンプト行を自動的にフィルタリングし、誤検出を回避します。

## 主な変更点とベストプラクティス

- update_policy.txt の `*` ルールに対応し、強制対象のみアップデートし、それ以外はすべてスキップします。
- 多言語・設定の読み込みを分離し、カスタマイズや国際化が容易です。
- ユーティリティ関数とメイン処理を分離し、構造が明確で保守しやすくなっています。
- dry-run プレビューや単回実行に対応し、自動運用やテストに最適です。
- Windows タスクスケジューラと組み合わせて `--once` や `--dry-run --once` の定期実行を推奨します。

## プロジェクト構成とモジュールの役割

- `AutoUpgradeApp.py`：メインエントリ。引数解析、権限チェック、メインループの調整のみ担当。
- `upgrade.py`：アップグレード・巡回・起動などのコア業務ロジック。
- `config.py`：設定・多言語読み込み、ポリシーファイル解析。
- `utils.py`：汎用ユーティリティ関数（文字幅、時刻処理など）。
- `output.py`：統一出力・ログ。info/warn/error 各レベルとログファイル対応。

## 型アノテーションとドキュメント

- すべての関数・主要変数に型アノテーションを付与し、型安全性と可読性を向上。
- すべてのモジュールに詳細なドキュメント文字列を追加し、IDEや自動化ツールとの連携や二次開発に最適。

## ログ・出力メカニズム

- すべての出力は output.py でラップされ、info/warn/error 各レベルに対応。
- ログファイル記録に対応し、トラブルシューティングや自動運用に便利。
- コンソール出力とログを分離し、カスタマイズや統合が容易。

## 例外処理と自動化統合

- すべての主要例外で詳細なスタックトレースを出力し、問題解析を容易に。
- メイン処理や upgrade.py の主要例外で sys.exit(1)/sys.exit(0) により自動化に優しい終了コードを返却。
- Windows タスクスケジューラや CI/CD などの自動化ツールと組み合わせ、`--once` や `--dry-run --once` の定期実行を推奨。
