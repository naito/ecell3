定常状態を探索するサンプルスクリプト
===============================
- モデルの定常状態を探索し、EMLファイルを出力するサンプルスクリプト

ファイル
--------
- `identify_steady_state.py`  セッションスクリプト
- `Arkin95_model.py`  モデルファイル
- `README.md`  このファイル

使い方
--------
```
$ ecell3-session identify_steady_state.py
```

出力
--------
- `MAX_TIME` 以内に定常状態に達すると、その状態をEMLモデル "`モデル名-steady.eml`"として出力する。

パラメータの設定方法
------------------

### モデルファイル
- `name` ：モデル名
- `em` ：EM文字列。Stepperには、`ODEStepper` のように極端に大きな `StepInterval` を取りうるものは用いない方がよい。

### セッションスクリプト
- `THRESHOLD` ：定常状態を判定する閾値。すべてのVariableについて、`Velocity / Value` の値が `THRESHOLD` を下回った状態を定常状態とみなす。
- `MAX_TIME` ：シミュレーションを実行する最大時間。`MAX_TIME` に達しても定常状態に至らない場合には、ファイルを出力せずに処理を終了する。

