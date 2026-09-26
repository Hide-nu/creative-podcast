import sys, re, io, wave, numpy as np, subprocess, time, glob
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
import pyopenjtalk
DIC = pyopenjtalk.OPEN_JTALK_DICT_DIR.decode()
# Linux は .so、Mac（setup_voicevox_mac.sh）は .dylib
ORT_LIB = (glob.glob("ort/*/lib/libvoicevox_onnxruntime.so.*") + glob.glob("ort/*/lib/libvoicevox_onnxruntime.*.dylib"))[0]
ort = Onnxruntime.load_once(filename=ORT_LIB)
syn = Synthesizer(ort, OpenJtalk(DIC))
vvm, style, src, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
speed = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
with VoiceModelFile.open(vvm) as m:
    syn.load_voice_model(m)
REPL = {"Airbnb": "エアビーアンドビー", "Yコンビネーター": "ワイコンビネーター",
        "一箱": "ひと箱", "SNS": "エスエヌエス", "一割半": "いちわりはん"}
text = open(src).read()
for k, v in REPL.items():
    text = text.replace(k, v)
chunks = []; sr = 24000; t = time.time()
for para in text.split("\n"):
    for s in re.split(r'(?<=[。！？])', para):
        s = s.strip()
        if not s: continue
        q = syn.create_audio_query(s, style)
        q.speed_scale = speed
        q.intonation_scale = 1.15
        q.post_phoneme_length = 0.12
        w = syn.synthesis(q, style)
        with wave.open(io.BytesIO(w)) as wf:
            sr = wf.getframerate()
            a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        chunks += [a, np.zeros(int(sr * 0.25), dtype=np.int16)]
    chunks.append(np.zeros(int(sr * 0.35), dtype=np.int16))
a = np.concatenate(chunks)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(sr), "-ac", "1",
                "-i", "-", "-b:a", "64k", out], input=a.tobytes(), check=True)
print(out, round(len(a) / sr, 1), "s audio,", round(time.time() - t, 1), "s compute")
