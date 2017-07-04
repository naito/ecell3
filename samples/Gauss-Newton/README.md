Gause-Newton 法によるパラメータ最適化
==================================

- Gause-Newton法を用いたパラメータ推定のサンプル。
- 最適化対象データとして、モデル中の変数の時系列（ECDファイル）を用い、トレーニングデータを再現する最適なパラメータを探索する。
  - 時系列ECDデータは、任意の数用いることができる。
  - 最適化するパラメータは、任意の数選べる。ただし、最適化に用いるデータの点の数以下でなければならない（Gause-Newton法の制約）。

ファイル
--------
- `Gauss-Newton_osc.py`  セッションマネージャ スクリプト
- `osc_session.py`  セッション スクリプト（EMを内包している）
- `Data`  最適化対象データ格納ディレクトリ
  - `osc_s1.ecd`, `osc_s2.ecd`, `osc_s3.ecd`  最適化対象データ（ECDファイル）
- `generate_osc_data.py`  最適化対象データを生成するセッションスクリプト（EMを内包している）
- `osc.em`  モデルのEMファイル
- `Gauss-Newton_wo-ecell3.py`  E-Cell3を用いないセッションマネージャ スクリプト。Wikidediaの「[ガウス・ニュートン法](https://ja.wikipedia.org/wiki/ガウス・ニュートン法)」にある例と同じ問題を解く。
- `README.md`  このファイル


使い方
--------
```
$ ecell3-session-manager Gauss-Newton_osc.py
$ ecell3-session-manager -E Torque Gauss-Newton_osc.py
```


パラメータの設定方法
------------------
- すべて `Gauss-Newton_osc.py` 内で設定する。ファイル冒頭付近の〔(0) パラメータ設定〕に列挙してある。

- `ESS_FILE`  セッションスクリプトファイルの名称
  - セッションスクリプトは、シミュレーション結果を辞書に格納し、JSON形式で返す。
    - キー：`CURVE_DATA_DICT` と同一
    - 値：時系列のECDデータ。最適化対象データと同じタイムポイントを持つようにスクリプト内で調整される。

- `CURVE_DATA_DIR`  最適化対象データを格納するディレクトリ
- `CURVE_DATA_DICT`  最適化対象データに関する辞書
  - キー：FullPN
  - 値：時系列（ECD）ファイル名

- `T_START`：最適化に用いる最初の時点（Noneの場合、先頭のデータから）
- `T_END`：最適化に用いる最後の時点（Noneの場合、末尾のデータまで）
- `T_INTERVAL`：最適化に用いるデータの間隔（Noneの場合、すべてのデータポイント）

- `PARAMETERS`  最適化するパラメータに関する辞書
  - キー：FullPN
  - 値：初期値

- `MAX_GENERATION`  反復計算の最大回数
- `ENOUGH_S`  反復計算を打ち切る残差平方和Sの値
- `DELTA`  残差のヤコビアンを求める際のパラメータの差分の割合


反復計算で発生するjobの数
-----------------------
- 最適化対象の時系列データの点の数 _m_ は、おおむね次の値になる：<img src="https://latex.codecogs.com/gif.latex?m={N}_\mathtt{CURVE\_DATA\_DICT}\times\frac{\mathtt{T\_END}-\mathtt{T\_START}}{\mathtt{T\_INTERVAL}}" />
  - ただし、 <img src="https://latex.codecogs.com/gif.latex?m={N}_\mathtt{CURVE\_DATA\_DICT}" /> は `CURVE_DATA_DICT` の要素数。
- 最適化対象のパラメータ数 _n_ （`PARAMETERS`の要素数）は、 _m_ 以下でなければならない（Gause-Newton法の制約）。
- 反復計算の１世代あたり、_n_ + 1 個の job が発生する。モデルが小規模で _n_ が小さければ、ローカルで充分な速度が出る場合もあるだろう。
