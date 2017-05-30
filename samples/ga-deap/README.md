GA using DEAP
=============
- PythonのGAモジュール [DEAP](https://github.com/DEAP/deap) を利用した簡単なパラメータ推定のサンプル
- トレーニングデータとして、モデル中の変数の時系列（ECDファイル）を用い、トレーニングデータを再現する最適なパラメータを探索する。
  - トレーニングデータの時系列データは、任意の数用いることができる。
  - 最適化するパラメータは、任意の数選べる。

ファイル
--------
- `deap.py`  セッションマネージャ スクリプト
- `session.py`  セッション スクリプト（EMを内包している）
- `Data`  トレーニングデータ格納ディレクトリ
  - `P.ecd`, `S.ecd`  トレーニングデータ（ECDファイル）

使い方
--------
```
$ ecell3-session-manager deap.py
$ ecell3-session-manager -E Torque deap.py
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
- `POPULATION_SIZE`  集団のサイズ（個体数）
- `FINISH_CONDITION`  終了条件
 - 評価値は、`session.py` の末尾で標準出力に `print` される変数 `aDifference` の値
- `P_CX`  交叉確率
- `P_MUT`  個体の変異確率
- `P_MUT_IND`  各パラメータの変異確率
- `MUT_MU`  変異量（正規分布）のパラメータ μ
- `MUT_SIGMA`  変異量（正規分布）のパラメータ σ
