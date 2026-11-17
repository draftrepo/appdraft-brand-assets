# Builds voice.wav from the long take plus the re-recorded "get the most" line (fix/line_raw.wav).
import subprocess, json
segs=[(0,40.35,51.35),(0,53.6,96.3),(0,103.9,117.2),(0,134.6,147.4),(0,159.55,190.3),(0,195.6,219.2),
      (0,227.55,237.7),(0,242.75,258.95),(0,297.1,314.7),(0,331.45,339.45),(0,355.1,363.1),
      (1,15.75,19.6),(0,367.25,372.2)]
json.dump(segs, open("cutlist.json","w"))
fc=[]
for i,(src,a,b) in enumerate(segs):
    fc.append(f"[{src}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={b-a-0.04}:d=0.04[s{i}]")
fc.append("".join(f"[s{i}]" for i in range(len(segs)))+f"concat=n={len(segs)}:v=0:a=1,highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=9[out]")
subprocess.run(["/usr/local/bin/ffmpeg","-loglevel","error","-y","-i","voice_raw.wav","-i","fix/line_raw.wav","-filter_complex",";".join(fc),"-map","[out]","-ar","48000","voice.wav"],check=True)
print("total", round(sum(b-a for _,a,b in segs),1), "s")
