#!/bin/bash
# Lay a quiet music bed under a finished video, ducking under the voice.
#   mix_music.sh <video.mp4> <music.mp3> <out.mp4>
# Licence first: Mixkit's Stock Music Free License covers social media and online ads
# with no credit (https://mixkit.co/llm-info/). Keep it short-form only: on the long
# walkthrough a music bed competes with the voice.
set -eu  # not pipefail: ffmpeg -i exits 1 when only probing
FF="${FFMPEG:?set FFMPEG to an ffmpeg binary}"
VID=$1 MUS=$2 OUT=$3
DUR=$("$FF" -i "$VID" 2>&1 | grep -o "Duration: [0-9:.]*" | cut -d' ' -f2 | awk -F: '{print $1*3600+$2*60+$3}')
FADE=$(python3 -c "print(max(0,$DUR-2.5))")
"$FF" -y -loglevel error -i "$VID" -i "$MUS" -filter_complex \
  "[1:a]atrim=0:${DUR},asetpts=PTS-STARTPTS,volume=0.22,afade=t=in:d=0.6,afade=t=out:st=${FADE}:d=2.5[m];[0:a]asplit=2[v][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[md];[v][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "wrote $OUT"
