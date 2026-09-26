#!/bin/bash
# VOICEVOX core をLinux(x64)に入れる。公式ダウンローダーはGitHub APIのレート制限で落ちるので直接取得する。
set -e
cd ~ && mkdir -p vv/models vv/ort && cd vv
curl -sLO https://github.com/VOICEVOX/voicevox_core/releases/download/0.17.0/voicevox_core-0.17.0-cp310-abi3-manylinux_2_34_x86_64.whl
pip install ./voicevox_core-0.17.0-cp310-abi3-manylinux_2_34_x86_64.whl --break-system-packages
curl -sL https://github.com/VOICEVOX/onnxruntime-builder/releases/download/voicevox_onnxruntime-1.17.3/voicevox_onnxruntime-linux-x64-1.17.3.tgz -o ort.tgz && tar xzf ort.tgz -C ort
curl -sL -o models/4.vvm https://github.com/VOICEVOX/voicevox_vvm/releases/download/0.16.4/4.vvm   # 玄野武宏を含む
pip install pyopenjtalk --break-system-packages
python3 -c "import pyopenjtalk; pyopenjtalk.g2p('テスト')"
cp "$(dirname "$0")/synth.py" ~/vv/
echo "OK: python3 ~/vv/synth.py models/4.vvm 11 台本.txt 出力.mp3 1.0（~/vv で実行）"
