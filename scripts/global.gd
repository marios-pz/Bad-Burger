extends Node
## Autoload "G". Holds what every screen shares: the sprite sheet,
## sound settings, level data and a few helpers to build UI from code.

const W := 640
const H := 480
const FRAMES: SpriteFrames = preload("res://assets/sprites.tres")
const SETTINGS_PATH := "user://settings.cfg"

const CREDITS := [
	"credits",
	"programing:",
	"emc235 | fkS | Mario | hk",
	"art:",
	"Mario | hk",
	"music:",
	"Mario | hk | fkS",
]

## Start cell, enemy spawn cells and the fruit waves of every level,
## copied from Pygame/src/levels.py. Waves are eaten in this order.
const LEVELS := [
	{start = Vector2i(2, 1), enemies = [Vector2i(19, 2)], waves = [1]},
	{start = Vector2i(2, 3), enemies = [Vector2i(3, 13), Vector2i(18, 3)], waves = [1]},
	{start = Vector2i(2, 2), enemies = [Vector2i(1, 12), Vector2i(17, 1)], waves = [1]},
	{start = Vector2i(10, 6), enemies = [Vector2i(2, 13), Vector2i(17, 1)], waves = [1, 2]},
	{start = Vector2i(7, 8), enemies = [Vector2i(2, 13), Vector2i(17, 1), Vector2i(12, 1)], waves = [2, 1]},
	{start = Vector2i(4, 5), enemies = [Vector2i(2, 13), Vector2i(15, 5)], waves = [1, 2, 3]},
	{start = Vector2i(7, 7), enemies = [Vector2i(17, 11), Vector2i(1, 5)], waves = [1, 2, 3]},
	{start = Vector2i(4, 5), enemies = [Vector2i(9, 12), Vector2i(17, 3)], waves = [1, 2]},
	{start = Vector2i(3, 1), enemies = [Vector2i(3, 13), Vector2i(16, 1), Vector2i(12, 7), Vector2i(16, 13)], waves = [1, 2]},
	{start = Vector2i(3, 6), enemies = [Vector2i(16, 3), Vector2i(8, 12), Vector2i(10, 2)], waves = [1, 2, 3]},
]

var level := 1  ## the level being played, starts at 1
var menu_opened := false  ## skip the "click to eat" screen after the first visit
var music_on := true
var sfx_on := true


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS  # sounds keep playing on pause screens
	var cfg := ConfigFile.new()
	if cfg.load(SETTINGS_PATH) == OK:
		music_on = cfg.get_value("sound", "music", true)
		sfx_on = cfg.get_value("sound", "sfx", true)


func save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("sound", "music", music_on)
	cfg.set_value("sound", "sfx", sfx_on)
	cfg.save(SETTINGS_PATH)


## Reads a level text file (map or fruit wave) into rows of numbers.
func read_grid(path: String) -> Array:
	var rows := []
	for line in FileAccess.get_file_as_string(path).split("\n"):
		line = line.replace(" ", "").strip_edges()
		if line.is_empty():
			continue
		var row := PackedByteArray()
		for ch in line:
			row.append(int(ch))
		rows.append(row)
	return rows


func level_file(name: String) -> String:
	return "res://assets/levels/level%d/%s.txt" % [level, name]


func go(scene: String) -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/%s.tscn" % scene)


# --- Sound ------------------------------------------------------------------

func sfx(name: String, volume := 1.0) -> void:
	if not sfx_on:
		return
	var p := AudioStreamPlayer.new()
	p.stream = load("res://assets/sfx/%s.wav" % name)
	p.volume_db = linear_to_db(volume)
	p.finished.connect(p.queue_free)
	add_child(p)
	p.play()


# --- UI helpers -------------------------------------------------------------

## One image (or the first frame of an animation) from the sprite sheet.
func tex(name: String) -> Texture2D:
	return FRAMES.get_frame_texture(name, 0)


func image(parent: Node, name: String, rect: Rect2) -> TextureRect:
	var t := TextureRect.new()
	t.texture = tex(name)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_SCALE
	t.position = rect.position
	t.size = rect.size
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(t)
	return t


## Black text centered inside rect (or aligned left/right with align).
func label(parent: Node, text: String, font_size: int, rect: Rect2,
		align := HORIZONTAL_ALIGNMENT_CENTER) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = align
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", Color.BLACK)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.position = rect.position
	l.size = rect.size
	parent.add_child(l)
	return l


## The burger bun button used everywhere, with an optional text on top.
func button(parent: Node, rect: Rect2, text := "", font_size := 30,
		on_press := Callable(), hover := true) -> TextureButton:
	var b := TextureButton.new()
	b.texture_normal = tex("button")
	b.texture_hover = tex("button_hover" if hover else "button")
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_SCALE
	b.position = rect.position
	b.size = rect.size
	if on_press.is_valid():
		b.pressed.connect(on_press)
	parent.add_child(b)
	if text:
		label(b, text, font_size, Rect2(Vector2.ZERO, rect.size))
	return b


## The orange kitchen table pattern behind the menus. Rows overlap by
## 4 pixels on purpose, just like the original.
func draw_tables(canvas: CanvasItem) -> void:
	var t := tex("table")
	for x in 21:
		for y in 18:
			canvas.draw_texture(t, Vector2(x * 32, y * 28))


## The small framed window used by the pause, win and lose screens.
## Returns the layer so the caller can free it.
func popup(parent: Node, title: String, buttons: Array) -> Control:
	var layer := Control.new()
	layer.size = Vector2(W, H)
	parent.add_child(layer)
	image(layer, "panel_bg", Rect2(160, 124, 320, 232))
	label(layer, title, 25, Rect2(0, 195, W, 30))
	for i in buttons.size():
		button(layer, Rect2(260, 240 + i * 40, 120, 35), buttons[i][0], 25, buttons[i][1])
	return layer
