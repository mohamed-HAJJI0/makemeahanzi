import json
from pathlib import Path

BASE = Path(__file__).parent
OUT = BASE / "export"
OUT.mkdir(exist_ok=True)

STROKE_TIME = 0.8   # seconds per stroke
PAUSE = 1.5         # pause before the loop restarts

# paste your JSON between the triple quotes
DATA = '''
{"character":"⺀","strokes":["M 323 706 Q 325 699 328 694 Q 334 686 367 671 Q 474 619 574 561 Q 600 545 617 543 Q 627 545 631 559 Q 641 576 613 621 Q 575 684 334 717 Q 321 719 323 706 Z","M 312 541 Q 314 535 316 531 Q 320 524 347 512 Q 455 461 563 397 Q 588 380 606 380 Q 615 382 619 396 Q 629 414 602 457 Q 564 519 321 554 Q 320 555 319 555 Q 310 555 312 541 Z"],"medians":[[[336,704],[450,666],[554,620],[587,595],[614,558]],[[317,548],[347,531],[455,496],[543,456],[578,430],[602,395]]]}
'''

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="400" height="400">'
BG = '<rect width="1024" height="1024" fill="#fff"/>'
OPEN_G = '<g transform="scale(1, -1) translate(0, -900)">'


def static_svg(entry):
    paths = "\n".join(f'    <path fill="#111" d="{s}"/>' for s in entry["strokes"])
    return f"{HEAD}\n  {BG}\n  {OPEN_G}\n{paths}\n  </g>\n</svg>"


def animated_svg(entry):
    strokes, medians = entry["strokes"], entry["medians"]
    n = len(strokes)
    total = n * STROKE_TIME + PAUSE

    css, defs, ghost, anim = [], [], [], []
    for i, (stroke, median) in enumerate(zip(strokes, medians)):
        start = i * STROKE_TIME / total * 100
        end = (i + 1) * STROKE_TIME / total * 100
        css.append(
            f"@keyframes k{i}{{0%{{stroke-dashoffset:1}}{start:.2f}%{{stroke-dashoffset:1}}"
            f"{end:.2f}%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}"
            f"#m{i}{{animation:k{i} {total:.2f}s linear infinite}}"
        )
        defs.append(f'<clipPath id="c{i}"><path d="{stroke}"/></clipPath>')
        ghost.append(f'    <path fill="#ddd" d="{stroke}"/>')
        points = " L ".join(f"{x} {y}" for x, y in median)
        anim.append(
            f'    <g clip-path="url(#c{i})"><path id="m{i}" d="M {points}" '
            f'fill="none" stroke="#111" stroke-width="150" stroke-linecap="round" '
            f'pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></g>'
        )

    return (
        f"{HEAD}\n  <style>{''.join(css)}</style>\n  <defs>{''.join(defs)}</defs>\n"
        f"  {BG}\n  {OPEN_G}\n" + "\n".join(ghost) + "\n" + "\n".join(anim) + "\n  </g>\n</svg>"
    )


entry = json.loads(DATA)
name = entry["character"]
(OUT / "character.svg").write_text(static_svg(entry), encoding="utf-8")
(OUT / "character_animated.svg").write_text(animated_svg(entry), encoding="utf-8")
print("saved export/character.svg and export/character_animated.svg")