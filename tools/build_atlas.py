"""Packs every sprite from art/sprites into one atlas for Godot.

Run it from the repo root:  python3 tools/build_atlas.py

It writes two files:
  assets/atlas.png    all images packed into a single texture
  assets/sprites.tres a SpriteFrames resource. Every animation and every
                      single image is an entry in it, so the game loads
                      one texture and one resource for all its art.

Only game art lives here. Buttons, boxes and other UI come from the
Godot theme in assets/ui_theme.tres.

Single images are stored as one frame animations. In GDScript you get
them with G.tex("name").
"""
import re
from pathlib import Path

from PIL import Image

SRC = Path("art/sprites")
OUT = Path("assets")
ATLAS_WIDTH = 1024
PAD = 2  # empty pixels between sprites so neighbours never bleed in

# name: (source folder or file, frames per second, loops, max frames)
ANIMATIONS = {
    "player_walk_down": ("walk_down", 13.33, True, None),
    "player_walk_up": ("walk_up", 13.33, True, None),
    "player_walk_side": ("walk_left", 13.33, True, None),  # faces left
    "player_idle_down": ("idle_down", 6.67, True, None),
    "player_idle_up": ("idle_up", 6.67, True, None),
    "player_idle_side": ("idle_left", 6.67, True, None),  # faces left
    "player_kick": ("attack", 16, True, None),
    "player_power_side": ("ability_side", 16, True, None),  # faces right
    "player_power_down": ("power_down", 18, True, None),
    "player_dying": ("player_dying", 13.33, False, None),
    "player_win": ("winning", 13.33, True, None),
    "enemy_down": ("enemy1_down", 14.29, True, None),
    "enemy_up": ("enemy1_up", 14.29, True, None),
    "enemy_side": ("enemy1_side", 14.29, True, None),  # faces left
    "ice_break": ("iceblock", 12, False, None),
    "clock": ("clock", 10, True, None),
    "menu_run": ("walk_right", 15, True, None),
}

STATICS = {
    "ice": "iceblock.png",
    "furnace": "furnace.png",
    "counter": "3t.png",
    "table": "table.png",
    "fruit_1": "fruits/banana.png",
    "fruit_2": "fruits/cherry.png",
    "fruit_3": "fruits/lemon.png",
    "fruit_4": "fruits/grape.png",
    "alert": "exlamation_point.png",
}


def natural_key(path: Path):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", path.name)]


def frames_of(folder: str, limit):
    files = sorted((SRC / folder).glob("*.png"), key=natural_key)
    if folder == "iceblock":
        # iceblock.png is the untouched block, the break starts at iceblock1
        files = [f for f in files if f.name != "iceblock.png"]
    return files[:limit] if limit else files


def pack(images):
    """Simple shelf packer: tallest first, fill rows left to right."""
    order = sorted(range(len(images)), key=lambda i: -images[i].height)
    spots = [None] * len(images)
    x = y = shelf = 0
    for i in order:
        w, h = images[i].size
        if x + w > ATLAS_WIDTH:
            x, y, shelf = 0, y + shelf + PAD, 0
        spots[i] = (x, y)
        x += w + PAD
        shelf = max(shelf, h)
    return spots, y + shelf


def main():
    entries = []  # (name, fps, loops, [image paths])
    for name, (folder, fps, loops, limit) in ANIMATIONS.items():
        entries.append((name, fps, loops, frames_of(folder, limit)))
    for name, file in STATICS.items():
        entries.append((name, 0, False, [SRC / file]))

    paths = [p for entry in entries for p in entry[3]]
    unique = list(dict.fromkeys(paths))
    images = [Image.open(p).convert("RGBA") for p in unique]
    spots, height = pack(images)

    atlas = Image.new("RGBA", (ATLAS_WIDTH, height), (0, 0, 0, 0))
    region = {}
    for path, img, spot in zip(unique, images, spots):
        atlas.paste(img, spot)
        region[path] = (*spot, *img.size)
    OUT.mkdir(exist_ok=True)
    atlas.save(OUT / "atlas.png")

    subs, anims = [], []
    ids = {path: f"r{i}" for i, path in enumerate(unique)}
    for path in unique:
        x, y, w, h = region[path]
        subs.append(
            f'[sub_resource type="AtlasTexture" id="{ids[path]}"]\n'
            f'atlas = ExtResource("atlas")\nregion = Rect2({x}, {y}, {w}, {h})\n'
        )
    for name, fps, loops, files in entries:
        frames = ", ".join(f'{{"duration": 1.0, "texture": SubResource("{ids[p]}")}}' for p in files)
        anims.append(
            f'{{\n"frames": [{frames}],\n"loop": {str(loops).lower()},\n'
            f'"name": &"{name}",\n"speed": {fps or 5.0}\n}}'
        )

    tres = (
        '[gd_resource type="SpriteFrames" format=3]\n\n'
        '[ext_resource type="Texture2D" path="res://assets/atlas.png" id="atlas"]\n\n'
        + "\n".join(subs)
        + "\n[resource]\nanimations = [" + ", ".join(anims) + "]\n"
    )
    (OUT / "sprites.tres").write_text(tres)
    print(f"atlas {ATLAS_WIDTH}x{height}, {len(unique)} images, {len(entries)} entries")


if __name__ == "__main__":
    main()
