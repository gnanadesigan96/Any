"""Burned-in captions: groups timed words into short phrases and writes an ASS file."""

from pathlib import Path


def group_words(words: list, max_words: int = 5, max_span: float = 2.2) -> list:
    """words: [[text, start, end]] in absolute seconds -> [[phrase, start, end]].

    Phrases break on sentence punctuation, after max_words, or when they'd span too long,
    so each caption is short enough to read at a glance.
    """
    phrases, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or w[2] - cur[0][1] > max_span):
            phrases.append(cur)
            cur = []
        cur.append(w)
        if w[0][-1:] in ".?!;:" or (w[0][-1:] == "," and len(cur) >= 3):
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    out = []
    for i, p in enumerate(phrases):
        start, end = p[0][1], p[-1][2]
        if i + 1 < len(phrases):  # hold the caption until the next one starts (no flicker)
            end = max(end, min(phrases[i + 1][0][1], end + 0.6))
        out.append([" ".join(w[0] for w in p), start, end])
    return out


def _ass_time(t: float) -> str:
    t = max(t, 0.0)
    cs = int(round(t * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")


def write_ass(phrases: list, path: Path, width: int, height: int, font: str, vertical: bool,
              title: str = "", duration: float = 0.0, hook: str = "", end_text: str = "",
              end_sub: str = "", hook_seconds: float = 2.2, end_seconds: float = 2.6) -> None:
    """Captions, plus optional overlays: `title` at the top for the whole video, `hook` as a big
    punch-in card for the first seconds, and an end card (`end_text` / `end_sub`) at the end."""
    if vertical:
        size, margin_v, align, outline = int(height * 0.05), int(height * 0.30), 2, 7
    else:
        size, margin_v, align, outline = int(height * 0.062), int(height * 0.07), 2, 4
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},1,{align},{int(width * 0.08)},{int(width * 0.08)},{margin_v},1
Style: Title,{font},{int(size * 1.15)},&H0000D7FF,&H0000D7FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline + 1},1,8,{int(width * 0.07)},{int(width * 0.07)},{int(height * 0.12)},1
Style: Hook,{font},{int(size * 1.7)},&H0000D7FF,&H0000D7FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{outline + 3},2,5,{int(width * 0.06)},{int(width * 0.06)},0,1
Style: End,{font},{int(size * 1.6)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{outline + 3},2,5,{int(width * 0.06)},{int(width * 0.06)},0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    if title and duration > 0:
        lines.append(f"Dialogue: 1,{_ass_time(0)},{_ass_time(duration)},Title,,0,0,0,,{_ass_escape(title)}")
    if hook and duration > 0:
        # Punch-in: starts oversized and snaps to size, then fades out.
        lines.append(f"Dialogue: 2,{_ass_time(0)},{_ass_time(min(hook_seconds, duration))},Hook,,0,0,0,,"
                     "{\\fscx135\\fscy135\\t(0,220,\\fscx100\\fscy100)\\fad(0,250)}"
                     + _ass_escape(hook.upper()))
    if end_text and duration > end_seconds + 1:
        sub = (f"\\N{{\\fs{int(size * 0.85)}\\c&H0000D7FF&}}{_ass_escape(end_sub.upper())}" if end_sub else "")
        lines.append(f"Dialogue: 2,{_ass_time(duration - end_seconds)},{_ass_time(duration)},End,,0,0,0,,"
                     "{\\fad(200,0)\\fscx120\\fscy120\\t(0,200,\\fscx100\\fscy100)}"
                     + _ass_escape(end_text.upper()) + sub)
    lines += [
        f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},Cap,,0,0,0,,{_ass_escape(text)}"
        for text, s, e in phrases if e > s
    ]
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
