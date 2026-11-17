#!/bin/bash
# Final assembly. Run from the working folder that holds the rendered parts.
#
#   compose.sh long  <main.mp4> <intro_frames_dir> <outro_frames_dir> <captions.ass> <fonts_dir> <out.mp4>
#   compose.sh short <main.mp4> <banner_frames_dir> <outro_frames_dir> <captions.ass> <fonts_dir> <out.mp4>
#
# long:  intro card, the 16:9 walkthrough, end card; captions offset by the intro length
#        (make the captions with captions_long.py <intro seconds>). Intro rendered at LEN=4.5.
# short: 1080x1080. Banner card (rendered with banner=1, 2s) animates in then holds at the top,
#        the walkthrough fills the width beneath it, word captions under that, a teal progress
#        bar along the top, then the square end card.
set -eu  # not pipefail: ffmpeg -i exits 1 when only probing
FF="${FFMPEG:?set FFMPEG to an ffmpeg binary}"
MODE=$1 MAIN=$2 OPEN=$3 OUTRO=$4 CAPS=$5 FONTS=$6 OUT=$7
DUR=$("$FF" -i "$MAIN" 2>&1 | grep -o "Duration: [0-9:.]*" | cut -d' ' -f2 | awk -F: '{print $1*3600+$2*60+$3}')
OUTRO_LEN=$(python3 -c "import os;print(len([f for f in os.listdir('$OUTRO') if f.endswith('.png')])/30)")
FG=$(mktemp)

if [ "$MODE" = "long" ]; then
  INTRO_LEN=$(python3 -c "import os;print(len([f for f in os.listdir('$OPEN') if f.endswith('.png')])/30)")
  TOTAL=$(python3 -c "print($INTRO_LEN+$DUR+$OUTRO_LEN)")
  DELAY=$(python3 -c "print(int($INTRO_LEN*1000))")
  cat > "$FG" <<EOF
[0:v]format=yuv420p,setsar=1[a];[1:v]setsar=1[b];[2:v]format=yuv420p,setsar=1[c];
[a][b][c]concat=n=3:v=1:a=0[cat];[cat]subtitles=filename='${CAPS}':fontsdir='${FONTS}'[v];
[1:a]adelay=${DELAY}:all=1,apad,atrim=0:${TOTAL}[au]
EOF
  "$FF" -y -loglevel error -framerate 30 -i "$OPEN/%04d.png" -i "$MAIN" -framerate 30 -i "$OUTRO/%04d.png" \
    -/filter_complex "$FG" -map "[v]" -map "[au]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
else
  TOTAL=$(python3 -c "print($DUR+$OUTRO_LEN)")
  LIST=$(mktemp).ffconcat
  { echo "ffconcat version 1.0"; for i in $(seq 0 58); do printf "file '%s/%04d.png'\nduration 0.033333\n" "$OPEN" "$i"; done
    printf "file '%s/0059.png'\nduration %s\nfile '%s/0059.png'\n" "$OPEN" "$DUR" "$OPEN"; } > "$LIST"
  cat > "$FG" <<EOF
[0:v]fps=30,format=yuv420p,trim=0:${DUR},setpts=PTS-STARTPTS[bg];
[1:v]scale=1080:608:flags=lanczos[vid];
[bg][vid]overlay=x=0:y=226[c1];
color=c=0x3cd6bf:s=1080x8:r=30:d=${DUR}[bar];
[c1][bar]overlay=x='-W+W*t/${DUR}':y=0:shortest=1[c2];
[c2]subtitles=filename='${CAPS}':fontsdir='${FONTS}'[main];
[2:v]format=yuv420p,fps=30[out];
[main][out]concat=n=2:v=1:a=0[v];
[1:a]apad,atrim=0:${TOTAL}[au]
EOF
  "$FF" -y -loglevel error -f concat -safe 0 -i "$LIST" -i "$MAIN" -framerate 30 -i "$OUTRO/%04d.png" \
    -/filter_complex "$FG" -map "[v]" -map "[au]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
fi
"$FF" -i "$OUT" 2>&1 | grep Duration
