# Bad Burger

You are a burger. The chefs want to cook you. Eat all the fruit before they catch you.

Bad Burger started as our entry for the Pygame Summer Team Jam, made by the Greco-France Alliance. Years later I ported it to Godot 4, mostly for the fun of it and so I can upload it to my itch.io page again. If you want the original Pygame code, it's still in the git history, just before the commit that removed it.

## How to play

| Key | What it does |
| --- | --- |
| Arrow keys or WASD | Walk |
| Space | Shoot a line of ice, or kick away the ice in front of you |
| Escape | Pause |

A gamepad works too: the d-pad walks and the bottom face button (A on Xbox, Cross on PlayStation) casts ice.

- Eat every fruit to clear a wave. Some levels have two or three waves.
- Chefs wander around. If you get close they spot you and run after you.
- Ice blocks the chefs, but if they can't reach you they'll smash through it.
- You have 2 minutes. After that, fruit is only worth half the points.

## Running the Godot version

1. Install [Godot 4.7](https://godotengine.org/download).
2. Open this folder in Godot (pick `project.godot`).
3. Press F5.

To check nothing is broken, run the smoke test:

```sh
godot --headless --path . res://tests/smoke_test.tscn
```

It loads all 10 levels, tries the main rules and prints `PASS`.

## What changed in the port

The game should feel the same. Under the hood a few things got simpler:

- All the game sprites (about 130 PNG files) are packed into one sheet, `assets/atlas.png`. The original images live in `art/sprites/`. If you change them, run `python3 tools/build_atlas.py` to rebuild the sheet.
- The menus, popups and HUD use a Godot theme, `assets/ui_theme.tres`, instead of drawn images. Open it in the Godot editor to change colors, borders or fonts everywhere at once. Menus also work with a keyboard or a gamepad now.
- The chefs find their way with Godot's built in pathfinding instead of our own.
- The camera follows the burger, zoomed in 1.5 times so the kitchen feels closer. Change `ZOOM` at the top of `scripts/game.gd` to zoom in or out, 1.0 shows the whole kitchen like the original.
- Walking feels smoother: the newest key wins, quick taps are never lost, you can turn back halfway through a step, and there is no tiny stop on every cell.
- The floor is a checkerboard of dirt tiles, so you can see the grid you walk on.
- Pausing really freezes everything now, ice timers included.
- The music and sound buttons in the menu actually work, and the game remembers your choice.
- A few old bugs are gone. "Next level" on level 9 now opens level 10, and the chefs no longer crash the game when they can't find a path.

## Project layout

| Folder | What's inside |
| --- | --- |
| `scenes/` | The three screens: menu, level select and the game |
| `scripts/` | All the game code. `global.gd` is shared by every screen |
| `assets/` | The sprite sheet, UI theme, font, sounds and the level maps |
| `tests/` | The smoke test |
| `tools/` | The script that builds the sprite sheet |
| `art/sprites/` | The separate game sprite images, used to build the sheet |

The level maps are plain text, one number per cell. In `map.txt`, `0` is floor, `1` is ice, `2` is a furnace and `3` is a counter. In the `fruits_*.txt` files, `1` to `4` are banana, cherry, lemon and grape.

## Building for itch.io

`export_presets.cfg` has Web, Windows and Linux presets. You can export from the Godot editor (Project, Export), or run the "Godot Build" workflow by hand from the GitHub Actions tab and download the builds it makes.

## Credits

- Programming: emc235, fkS, Mario, hk
- Art: Mario, hk
- Music: Mario, hk, fkS
- Font: [Jersey 10](https://github.com/scfried/soft-type-jersey) by The Soft Type Project Authors, under the SIL Open Font License 1.1 (see `assets/fonts/OFL.txt`)

## License

The game is GPL 3.0, see [LICENSE](LICENSE). The font keeps its own license, the SIL Open Font License 1.1.
