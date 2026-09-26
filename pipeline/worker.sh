#!/bin/bash
# synthesis worker: picks up finished scripts (marked by .done file) and makes mp3s
# SCRIPTS_DIR で台本の場所を変えられる（既定 ~/pod/scripts）。~/vv/venv があれば使う（Mac）
cd ~/vv; [ -e venv/bin/activate ] && . venv/bin/activate
S=${SCRIPTS_DIR:-~/pod/scripts}
mkdir -p ~/pod/up32 ~/pod/out ~/pod/parts ~/pod/logs
W=$1
while true; do
  did=0
  for s in "$S"/*.txt; do
    [ -e "$s" ] || continue
    b=$(basename "$s" .txt)
    [ -e "$S/$b.done" ] || continue
    [ -e ~/pod/out/$b.mp3 ] && continue
    mkdir ~/pod/parts/$b.lock 2>/dev/null || continue   # claim
    echo "$(date +%T) W$W start $b" >> ~/pod/logs/worker.log
    d=~/pod/parts/$b; mkdir -p $d
    python3 - "$s" "$d" <<'PY'
import sys,os
src,d=sys.argv[1],sys.argv[2]
lines=[l for l in open(src).read().split("\n")]
parts=[];cur=[];n=0
for l in lines:
    cur.append(l);n+=len(l)
    if n>=1900: parts.append(cur);cur=[];n=0
if any(x.strip() for x in cur): parts.append(cur)
for i,p in enumerate(parts):
    open(f"{d}/p{i:02d}.txt","w").write("\n".join(p))
PY
    : > $d/list.txt
    for p in $d/p*.txt; do
      m=${p%.txt}.mp3
      [ -e $m ] || python3 synth.py models/4.vvm 11 $p $m 1.0 >> ~/pod/logs/synth_$b.log 2>&1
      echo "file '$m'" >> $d/list.txt
    done
    ffmpeg -loglevel error -y -f concat -safe 0 -i $d/list.txt -c copy ~/pod/out/$b.tmp.mp3 && mv ~/pod/out/$b.tmp.mp3 ~/pod/out/$b.mp3
    ffmpeg -loglevel error -y -i ~/pod/out/$b.mp3 -ac 1 -b:a 32k ~/pod/up32/$b.mp3
    echo "$(date +%T) W$W done $b $(ffprobe -v error -show_entries format=duration -of csv=p=0 ~/pod/out/$b.mp3)" >> ~/pod/logs/worker.log
    did=1
  done
  [ -e ~/pod/STOP ] && exit 0
  [ $did = 0 ] && sleep 20
done
