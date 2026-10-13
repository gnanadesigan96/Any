"""Burned-in captions: groups timed words into short phrases and writes an ASS file."""

import unicodedata
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


def _round_rect(w: int, h: int, r: int) -> str:
    """An ASS vector drawing of a w x h box with rounded corners (drawn with \\p1)."""
    return (f"m {r} 0 l {w - r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h - r} b {w} {h} {w} {h} {w - r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h - r} l 0 {r} b 0 0 0 0 {r} 0")


def _box(start: float, end: float, x: int, y: int, w: int, h: int, colour: str, alpha: str, extra: str = "") -> str:
    return (f"Dialogue: 4,{_ass_time(start)},{_ass_time(end)},Box,,0,0,0,,"
            f"{{\\an5\\pos({x},{y})\\1c{colour}\\1a{alpha}{extra}\\p1}}{_round_rect(w, h, min(w, h) // 4)}{{\\p0}}")


def _text(start: float, end: float, x: int, y: int, size: int, colour: str, text: str, extra: str = "") -> str:
    return (f"Dialogue: 5,{_ass_time(start)},{_ass_time(end)},Card,,0,0,0,,"
            f"{{\\an5\\pos({x},{y})\\fs{size}\\c{colour}{extra}}}{_ass_escape(text)}")


YELLOW, WHITE, RED = "&H0000D7FF&", "&H00FFFFFF&", "&H001721E6&"


def intro_card(start: float, end: float, width: int, height: int, size: int, title: str, sub: str, note: str) -> list:
    """The opening card over the first picture: a soft dark panel with the title in English (e.g. "GUESS THE
    MOVIE" / "FROM THE STORY") and a line in the narration's language under it."""
    cx, cy = width // 2, int(height * 0.36)
    def fit(text, most):  # the biggest size that keeps the line on one line (Tamil vowel signs take no width of their own)
        letters = sum(1 for ch in text if not unicodedata.category(ch).startswith("M"))
        return int(min(size * most, width * 0.8 / (0.62 * max(letters, 1))))
    pop = "\\q2\\fscx90\\fscy90\\t(0,180,\\fscx100\\fscy100)\\fad(0,250)"
    lines = [_box(start, end, cx, cy, int(width * 0.9), int(height * (0.19 if note else 0.14)), "&H00000000&", "&H50&", pop),
             _text(start, end, cx, cy - int(height * (0.045 if note else 0.022)), fit(title, 1.3), YELLOW, title.upper(), pop)]
    if sub:
        lines.append(_text(start, end, cx, cy + int(height * (0.012 if note else 0.035)), fit(sub, 0.85), WHITE,
                           sub.upper(), pop))
    if note:
        lines.append(_text(start, end, cx, cy + int(height * 0.058), fit(note, 0.62), WHITE, note, pop))
    return lines


def outro_card(start: float, end: float, width: int, height: int, size: int, card: dict) -> list:
    """The closing screen: "did you guess it?", comment, a red SUBSCRIBE button with the channel's handle, and
    thanks for watching. Kept in the middle of the frame, clear of the YouTube buttons at the bottom."""
    cx = width // 2
    y = lambda f: int(height * f)
    fade = lambda k: f"\\fad({200 if k == 0 else 250},0)" if k == 0 else f"\\alpha&HFF&\\t({k * 250},{k * 250 + 250},\\alpha&H00&)"
    lines = [_box(start, end, cx, y(0.44), int(width * 0.88), y(0.46), "&H00000000&", "&H60&", fade(0))]
    k = 0
    if card.get("title"):
        lines.append(_text(start, end, cx, y(0.255), int(size * 1.15), YELLOW, card["title"], fade(k)))
    if card.get("sub"):
        k += 1
        lines.append(_text(start, end, cx, y(0.315), int(size * 0.78), WHITE, card["sub"], fade(k)))
    k += 1
    bw, bh = int(width * 0.64), y(0.078)
    pulse = "".join(f"\\t({t},{t + 200},\\fscx106\\fscy106)\\t({t + 200},{t + 400},\\fscx100\\fscy100)"
                    for t in (900, 1900, 2900))
    lines.append(_box(start, end, cx, y(0.415), bw, bh, RED, "&H00&", fade(k) + pulse))
    lines.append(_text(start, end, cx, y(0.415), int(size * 0.95), WHITE, card.get("button", "SUBSCRIBE"), fade(k) + pulse))
    if card.get("handle"):
        lines.append(_text(start, end, cx, y(0.49), int(size * 0.72), WHITE, card["handle"], fade(k)))
    if card.get("thanks"):
        k += 1
        lines.append(_text(start, end, cx, y(0.565), int(size * 0.9), YELLOW, card["thanks"], fade(k)))
    if card.get("thanks_sub"):
        lines.append(_text(start, end, cx, y(0.62), int(size * 0.62), WHITE, card["thanks_sub"], fade(k)))
    return lines


def write_ass(phrases: list, path: Path, width: int, height: int, font: str, vertical: bool,
              title: str = "", duration: float = 0.0, hook: str = "", end_text: str = "",
              end_sub: str = "", hook_seconds: float = 2.2, end_seconds: float = 2.6,
              title_style: str = "banner", hook_sub: str = "", countdown: tuple = None,
              reveal: tuple = None, hook_note: str = "", outro: tuple = None) -> None:
    """Captions, plus optional overlays: `title` at the top for the whole video ("banner": big yellow text;
    "tag": a small, neat label on a soft dark box), `hook` as a big punch-in card for the first seconds,
    and an end card (`end_text` / `end_sub`) at the end. With `hook_note` the opening is a panel card (intro_card);
    `outro` = (start, card) replaces the end card with a closing screen (outro_card)."""
    if vertical:
        size, margin_v, align, outline = int(height * 0.05), int(height * 0.30), 2, 7
    else:
        size, margin_v, align, outline = int(height * 0.062), int(height * 0.07), 2, 4
    if title_style == "tag":
        title_line = (f"Style: Title,{font},{int(size * 0.5)},&H00FFFFFF,&H00FFFFFF,&H5A000000,&H00000000,-1,0,0,0,"
                      f"100,100,0,0,3,{max(6, size // 5)},0,8,0,0,{int(height * 0.06)},1")  # no letter spacing: it splits Tamil letters
    else:
        title_line = (f"Style: Title,{font},{int(size * 1.15)},&H0000D7FF,&H0000D7FF,&H00000000,&H80000000,-1,0,0,0,"
                      f"100,100,0,0,1,{outline + 1},1,8,{int(width * 0.07)},{int(width * 0.07)},{int(height * 0.12)},1")
    # With a poster reveal the end card sits low, under the poster, instead of covering it.
    end_align, end_margin = (2, int(height * 0.035)) if reveal else (5, 0)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},1,{align},{int(width * 0.08)},{int(width * 0.08)},{margin_v},1
{title_line}
Style: Hook,{font},{int(size * 1.7)},&H0000D7FF,&H0000D7FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{outline + 3},2,5,{int(width * 0.06)},{int(width * 0.06)},0,1
Style: End,{font},{int(size * 1.6)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{outline + 3},2,{end_align},{int(width * 0.06)},{int(width * 0.06)},{end_margin},1
Style: Count,{font},{int(size * 5)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{outline + 6},3,5,0,0,0,1
Style: Box,{font},{size},&H00000000,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Card,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{max(2, outline - 3)},1,5,0,0,0,1
Style: Reveal,{font},{int(size * 1.3)},&H0000D7FF,&H0000D7FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{outline + 3},2,8,{int(width * 0.06)},{int(width * 0.06)},{int(height * 0.04)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    if title and duration > 0:
        lines.append(f"Dialogue: 1,{_ass_time(0)},{_ass_time(duration)},Title,,0,0,0,,{_ass_escape(title)}")
    if hook and hook_note and duration > 0:
        lines += intro_card(0, min(max(hook_seconds, 3.0), duration), width, height, size, hook, hook_sub, hook_note)
    elif hook and duration > 0:
        # Crisp from the very first frame (so that frame works as the thumbnail), then fades out.
        sub = f"\\N{{\\fs{int(size * 0.8)}\\c&H00FFFFFF&}}{_ass_escape(hook_sub)}" if hook_sub else ""
        lines.append(f"Dialogue: 2,{_ass_time(0)},{_ass_time(min(hook_seconds, duration))},Hook,,0,0,0,,"
                     "{\\fad(0,250)}" + _ass_escape(hook.upper()) + sub)
    if outro and duration > outro[0]:
        lines += outro_card(outro[0], duration, width, height, size, outro[1])
    elif end_text and duration > end_seconds + 1:
        sub = (f"\\N{{\\fs{int(size * 0.85)}\\c&H0000D7FF&}}{_ass_escape(end_sub.upper())}" if end_sub else "")
        lines.append(f"Dialogue: 2,{_ass_time(duration - end_seconds)},{_ass_time(duration)},End,,0,0,0,,"
                     "{\\fad(200,0)\\fscx120\\fscy120\\t(0,200,\\fscx100\\fscy100)}"
                     + _ass_escape(end_text if reveal else end_text.upper()) + sub)  # a channel name keeps its case
    if countdown:  # a big 5, 4, 3, 2, 1 over the blurred poster, one per second
        start, seconds = countdown
        n = int(round(seconds))
        for k in range(n):
            lines.append(f"Dialogue: 3,{_ass_time(start + k)},{_ass_time(start + k + 0.95)},Count,,0,0,0,,"
                         "{\\fscx160\\fscy160\\t(0,180,\\fscx100\\fscy100)\\fad(0,150)}" + str(n - k))
    if reveal and reveal[1] and duration > reveal[0]:
        lines.append(f"Dialogue: 3,{_ass_time(reveal[0])},{_ass_time(outro[0] if outro else duration)},Reveal,,0,0,0,,"
                     "{\\fad(150,0)\\fscx120\\fscy120\\t(0,220,\\fscx100\\fscy100)}" + _ass_escape(reveal[1]))
    if reveal:  # no captions over the poster: its title is usually at the bottom, and the answer is on screen
        phrases = [(text, s, min(e, reveal[0])) for text, s, e in phrases if s < reveal[0] - 0.05]
    if hook:  # keep the first half second clean: that frame is the thumbnail
        phrases = [(text, max(s, 0.5), e) for text, s, e in phrases]
    lines += [
        f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},Cap,,0,0,0,,{_ass_escape(text)}"
        for text, s, e in phrases if e > s
    ]
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
