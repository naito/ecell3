SRES (Stochastic Ranking Evolution Strategy)
============================================
- Stochastic Rankingを用いた進化戦略によるパラメータ最適化を実装したサンプル

必要なモジュール
----------------
### DEAP
```
$ pip install deap
```

ファイル
--------
- `SRES.py`  セッションマネージャ スクリプト
- `session.py`  セッション スクリプト（EMを内包している）
- `Data`  トレーニングデータ格納ディレクトリ
  - `P.ecd`, `S.ecd`  トレーニングデータ（ECDファイル）

使い方
--------
```
$ ecell3-session-manager SRES.py
$ ecell3-session-manager -E Torque SRES.py
```

パラメータの設定方法
------------------
- すべて `deap.py` 内で設定する。ファイル冒頭の〔(0) パラメータ設定〕に列挙してある。
- `ESS_FILE`  セッションスクリプトファイルの名称
- `TRAINING_DATA_DIR`  トレーニングデータを格納するディレクトリ
- `TRAINING_DATA_DICT`  トレーニングデータに関する辞書
  - キー：FullPN
  - 値：時系列（ECD）ファイル名
- `PARAMETER_RANGES`  最適化するパラメータに関する辞書
  - キー：FullPN
  - 値：リスト [ 最小値, 最大値 ]
- `MAX_GENERATION`  GAを実行する最大世代数
- `LAMBDA`  集団のサイズ（個体数）
- `MU`  次世代に引き継がれる個体数（推奨値はLAMBDAの1/7）
- `FINISH_CONDITION`  終了条件
 - 評価値は、`session.py` の末尾で標準出力に `print` される変数 `aDifference` の値
- `P_CX`  交叉確率
- `TAU`  特別な理由がない限り書き換える必要はない
- `TAU_PRIME`  特別な理由がない限り書き換える必要はない
- `MUT_MAX_TRIAL`  発生させた値が値域を逸脱する場合に再試行する最大回数。最大回数に達すると、値域の最大値または最小値に設定される。
