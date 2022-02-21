DETAIL_FILE = "詳細はhttps://github.com/Kdy0115/agent-simulation-system を参照して下さい。"

ENV_ERROR = """Error：実行環境エラー
マルチプロセスと非バッチ処理は対応していません。マルチプロセスを行う場合はバッチ処理に設定してください。
./controllers/env.pyの実行環境設定ファイルを編集してください。
{}""".format(DETAIL_FILE)

FILE_NOT_FIND_ERROR = """ファイルが正しく読み込まれませんでした。正しいパス名を選択してください。
./config/config.ini内のパスを正しい値に編集してください。
{}""".format(DETAIL_FILE)

SPACE_DEFINITION_ERROR = """シミュレーション空間定義に問題があります。
レイアウト情報、熱源情報、model.py内の空間定義アルゴリズムを見直してください。
{}""".format(DETAIL_FILE)

DATA_CLUMN_NAME_REFFERENCE_ERROR = """カラム名の対応が間違っています。
読み込みデータを確認するかカラム名に対応したプログラムに書き換えて下さい。
{}
""".format(DETAIL_FILE)