#!/bin/sh
# 形式の検査と解答の実行をまとめて行う。引数に問題IDを渡すと、その問題の解答だけを実行する。
set -eu
cd "$(dirname "$0")/.."
: "${CODEDECK_DIR:?CodeDeckのチェックアウトを CODEDECK_DIR に指定してください}"
go -C "$CODEDECK_DIR/api" run ./cmd/codedeck content-validate --dir "$PWD"
python3 scripts/solutions.py check "$@"
