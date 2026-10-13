"""Tamil subtitles: an .ass file to burn into the video and an .srt to upload to YouTube."""
import re

from PIL import ImageFont

from . import fonts

MAX_LINE_PX = 1500   # at 1080p with the subtitle font below
FONT_SIZE = 52


def _chunks(text):
    """Split narration into sentence-sized pieces."""
    parts = [p.strip() for p in re.split(r"(?<=[.!?।])\s+", text.replace("\n", " ")) if p.strip()]
    out = []
    for p in parts:
        if len(p) <= 95:
            out.append(p)
            continue
        cur = ""
        for piece in re.split(r"(?<=[,:;])\s+", p):
            if cur and len(cur) + len(piece) > 95:
                out.append(cur)
                cur = piece
            else:
                cur = f"{cur} {piece}".strip()
        if cur:
            out.append(cur)
    return out


def _lines(text, fnt):
    lines, cur = [], ""
    for w in text.split():
        trial = f"{cur} {w}".strip()
        if fnt.getlength(trial) <= MAX_LINE_PX or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def events(ep):
    fnt = ImageFont.truetype(fonts.path("NotoSansTamil-Bold.ttf"), FONT_SIZE,
                             layout_engine=ImageFont.Layout.RAQM)
    lead = float(ep.cfg["narration_lead"])
    evs = []
    for sc in ep.scenes:
        if not sc.text:
            continue
        pieces = []
        for ch in _chunks(sc.text):
            lines = _lines(ch, fnt)
            for i in range(0, len(lines), 2):
                pieces.append(lines[i:i + 2])
        total_chars = sum(len(" ".join(p)) for p in pieces) or 1
        t = sc.start + lead
        span = sc.narration_seconds
        for p in pieces:
            d = span * len(" ".join(p)) / total_chars
            evs.append((t, t + d - 0.05, p))
            t += d
    return evs


def _ass_time(t):
    cs = int(round(max(t, 0) * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _srt_time(t):
    ms = int(round(max(t, 0) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write(ep, ass_path, srt_path):
    evs = events(ep)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Tamil,Noto Sans Tamil,{FONT_SIZE},&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,0,0,1,3.2,1.5,2,120,120,64,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    body = []
    for a, b, lines in evs:
        txt = r"\N".join(l.replace("{", "(").replace("}", ")") for l in lines)
        body.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},Tamil,,0,0,0,,{{\\fad(120,120)}}{txt}")
    ass_path.write_text(head + "\n".join(body) + "\n", encoding="utf-8")
    srt = []
    for i, (a, b, lines) in enumerate(evs, 1):
        srt.append(f"{i}\n{_srt_time(a)} --> {_srt_time(b)}\n" + "\n".join(lines) + "\n")
    srt_path.write_text("\n".join(srt), encoding="utf-8")
    return len(evs)
