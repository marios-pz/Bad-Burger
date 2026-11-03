extends Node
## Autoload "G". Holds what every screen shares: the sprite sheet,
## sound settings, level data and a few helpers to build UI from code.

const W := 640
const H := 480
const FRAMES: SpriteFrames = preload("res://assets/sprites.tres")
const SETTINGS_PATH := "user://settings.cfg"

const CREDITS := [
	"credits",
	"programming:",
	"emc235 | fkS | Mario | hk",
	"art:",
	"Mario | hk",
	"music:",
	"Mario | hk | fkS",
]

## Every level is a scene in levels/: level_01.tscn, level_02.tscn and so
## on. Saving the next number there adds a level, no code change needed.
var level_count := 0
var level := 1  ## the level being played, starts at 1
var players := 1  ## 1 for solo, 2 for local co-op
var menu_opened := false  ## skip the "click to eat" screen after the first visit
var music_on := true
var sfx_on := true


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS  # sounds keep playing on pause screens
	var cfg := ConfigFile.new()
	if cfg.load(SETTINGS_PATH) == OK:
		music_on = cfg.get_value("sound", "music", true)
		sfx_on = cfg.get_value("sound", "sfx", true)
	while ResourceLoader.exists(level_path(level_count + 1)):
		level_count += 1


func save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("sound", "music", music_on)
	cfg.set_value("sound", "sfx", sfx_on)
	cfg.save(SETTINGS_PATH)


## How many screen pixels one game pixel takes up, always a whole number
## because the project uses the "integer" stretch scale mode.
func window_scale() -> float:
	var size := get_window().size
	return maxf(1.0, floorf(minf(size.x / float(W), size.y / float(H))))


func level_path(n: int) -> String:
	return "res://levels/level_%02d.tscn" % n


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


## A framed box from the UI theme (assets/ui_theme.tres). variation can be
## "HudPanel" for the slimmer HUD boxes or "KeyCap" / "KeyCapOn" for keys.
func panel(parent: Node, rect: Rect2, variation := "") -> Panel:
	var p := Panel.new()
	p.theme_type_variation = variation
	p.position = rect.position
	p.size = rect.size
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(p)
	return p


## Text centered inside rect (or aligned left/right with align).
## The color comes from the theme.
func label(parent: Node, text: String, font_size: int, rect: Rect2,
		align := HORIZONTAL_ALIGNMENT_CENTER) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = align
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.add_theme_font_size_override("font_size", font_size)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.position = rect.position
	l.size = rect.size
	parent.add_child(l)
	# A label that is too short for its font grows downwards, which pushes
	# the text below the middle of rect. Grow it evenly up and down instead.
	var extra := l.get_minimum_size().y - rect.size.y
	if extra > 0:
		l.position.y -= extra / 2.0
	return l


## A themed button. Hover, pressed, disabled and keyboard focus looks
## all come from assets/ui_theme.tres.
func button(parent: Node, rect: Rect2, text: String, font_size := 42,
		on_press := Callable()) -> Button:
	var b := Button.new()
	b.text = text
	b.add_theme_font_size_override("font_size", font_size)
	b.position = rect.position
	b.size = rect.size
	if on_press.is_valid():
		b.pressed.connect(on_press)
	parent.add_child(b)
	return b


## The orange kitchen table pattern behind the menus. Rows overlap by
## 4 pixels on purpose, just like the original.
func draw_tables(canvas: CanvasItem) -> void:
	var t := tex("table")
	for x in 21:
		for y in 18:
			canvas.draw_texture(t, Vector2(x * 32, y * 28))


## The small window used by the pause, win and lose screens. The game
## behind it is dimmed. The first button gets keyboard and gamepad focus.
## Returns the layer so the caller can free it.
## With an empty title it is only a small box of buttons, placed lower so
## a banner can sit above it.
func popup(parent: Node, title: String, buttons: Array) -> Control:
	var layer := ColorRect.new()
	layer.color = Color(0, 0, 0, 0.45)
	layer.size = Vector2(W, H)
	parent.add_child(layer)
	var top := 214
	if title:
		panel(layer, Rect2(180, 140, 280, 200))
		label(layer, title, 42, Rect2(180, 158, 280, 40))
	else:
		top = 270
		panel(layer, Rect2(220, top - 14, 200, buttons.size() * 52 + 22))
	for i in buttons.size():
		var b := button(layer, Rect2(240, top + i * 52, 160, 42), buttons[i][0], 31, buttons[i][1])
		if i == 0:
			b.grab_focus.call_deferred()
	return layer
