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
    """The words of the animated end screen (finale.render_outro draws the card, badge and button under them):
    the channel's handle under its badge, "did you guess it?", comment, the button's SUBSCRIBE -> SUBSCRIBED, and
    thanks for watching. All in the middle of the frame, clear of the YouTube buttons at the bottom."""
    from .finale import BUTTON_IN, LAYOUT as L, TAP, THANKS_IN
    cx, y = width // 2, (lambda f: int(height * f))
    appear = lambda at: f"\\alpha&HFF&\\t({int(at * 1000)},{int(at * 1000) + 250},\\alpha&H00&)"
    lines = []
    if card.get("handle"):
        lines.append(_text(start, end, cx, y(L["name_y"]), int(size * 0.8), WHITE, card["handle"], appear(0.3)))
    if card.get("title"):
        lines.append(_text(start, end, cx, y(L["title_y"]), int(size * 1.0), YELLOW, card["title"], appear(0.45)))
    if card.get("sub"):
        lines.append(_text(start, end, cx, y(L["sub_y"]), int(size * 0.7), WHITE, card["sub"], appear(0.6)))
    tap = start + TAP + 0.05
    if end > start + BUTTON_IN:
        lines.append(_text(start + BUTTON_IN + 0.2, min(tap, end), cx, y(L["button_y"]), int(size * 0.88), WHITE,
                           card.get("button", "SUBSCRIBE"), "\\fad(120,0)"))
    if end > tap:
        lines.append(_text(tap, end, cx + int(width * 0.05), y(L["button_y"]), int(size * 0.8), WHITE,
                           card.get("done", "SUBSCRIBED"), ""))
    if card.get("thanks"):
        lines.append(_text(start, end, cx, y(L["thanks_y"]), int(size * 0.92), YELLOW, card["thanks"], appear(THANKS_IN)))
    if card.get("thanks_sub"):
        lines.append(_text(start, end, cx, y(L["thanks_sub_y"]), int(size * 0.62), WHITE, card["thanks_sub"],
                           appear(THANKS_IN + 0.15)))
    return lines


def write_ass(phrases: list, path: Path, width: int, height: int, font: str, vertical: bool,
              title: str = "", duration: float = 0.0, hook: str = "", end_text: str = "",
              end_sub: str = "", hook_seconds: float = 2.2, end_seconds: float = 2.6,
              title_style: str = "banner", hook_sub: str = "", countdown: tuple = None,
              reveal: tuple = None, hook_note: str = "", outro: tuple = None, count_label: str = "",
              clue_countdown: tuple = None, clue: tuple = None) -> None:
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
Style: Count,{font},{int(size * 3.3)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{outline},4,5,0,0,0,1
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
    rings = ([(*countdown, count_label)] if countdown else []) + ([clue_countdown] if clue_countdown else [])
    for start, seconds, label in rings:
        # a big 5, 4, 3, 2, 1 inside the countdown ring (finale.render_countdown), one per second
        from .finale import LAYOUT as L
        n = int(round(seconds))
        cy = int(height * L["ring_y"])
        for k in range(n):
            lines.append(f"Dialogue: 3,{_ass_time(start + k)},{_ass_time(start + k + 0.97)},Count,,0,0,0,,"
                         f"{{\\an5\\pos({width // 2},{cy})\\fscx135\\fscy135\\t(0,220,\\fscx100\\fscy100)\\fad(60,120)}}" + str(n - k))
        if label:
            lines.append(_text(start, start + seconds, width // 2, int(height * L["count_label_y"]), int(size * 0.8),
                               WHITE, label, "\\fad(200,0)"))
    if clue:  # the clue card's words: the heading in its gold pill, then each clue as the narrator reaches it
        from .finale import LAYOUT as L
        start, end, words, rows = clue
        lines.append(_text(start + 0.35, end, width // 2, int(height * L["clue_pill_y"]), int(size * 0.85),
                           "&H00180E08&", "க்ளூ!", "\\bord0\\shad0\\fad(120,0)"))
        # Each clue appears when the narrator starts it ("க்ளூ ஒண்ணு", "க்ளூ ரெண்டு"), else spread evenly.
        marks = [start + w[1] for w in words if w[0].startswith("க்ளூ")] if words else []
        for n, clue_rows in enumerate(rows):
            at = marks[n] if n < len(marks) else start + 0.5 + n * (end - start - 1.0) / max(len(rows), 1)
            y0 = height * L["clue_y"][min(n, len(L["clue_y"]) - 1)]
            for r, text in enumerate(clue_rows):  # the first row carries the clue's number, in gold
                text = (f"{{\\c{YELLOW}}}{n + 1}.{{\\c{WHITE}}} " if r == 0 else "") + _ass_escape(text)
                lines.append(f"Dialogue: 5,{_ass_time(at)},{_ass_time(end)},Card,,0,0,0,,{{\\an5\\pos({width // 2},"
                             f"{int(y0 + r * height * L['clue_row'])})\\fs{int(size * 0.78)}\\c{WHITE}\\fad(200,0)}}{text}")
        phrases = [p for p in phrases if not (start - 0.05 <= p[1] < end)]  # the card shows the words already
    if clue_countdown:
        phrases = [p for p in phrases if not (clue_countdown[0] - 0.05 <= p[1] < clue_countdown[0] + clue_countdown[1])]
    if reveal and reveal[1] and duration > reveal[0]:
        from .finale import BANNER_IN, LAYOUT as L
        at = reveal[0] + BANNER_IN + 0.3  # once the gold banner has slid in
        lines.append(_text(at, outro[0] if outro else duration, width // 2, int(height * L["banner_y"]),
                           int(size * 0.95), "&H00180E08&", reveal[1],
                           "\\bord0\\shad0\\fscx115\\fscy115\\t(0,200,\\fscx100\\fscy100)\\fad(100,0)"))
    if reveal:  # no captions over the poster: its title is usually at the bottom, and the answer is on screen
        phrases = [(text, s, min(e, reveal[0])) for text, s, e in phrases if s < reveal[0] - 0.05]
    if hook:  # keep the first half second clean: that frame is the thumbnail
        phrases = [(text, max(s, 0.5), e) for text, s, e in phrases]
    lines += [
        f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},Cap,,0,0,0,,{_ass_escape(text)}"
        for text, s, e in phrases if e > s
    ]
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
