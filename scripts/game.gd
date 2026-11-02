class_name Game
extends Node2D
## One level: the kitchen floor, counters, furnaces, ice, fruit, the burger
## and the chefs, with the score and timer on top.

const TILE := 32
const COLS := 20
const ROWS := 15
const FLOOR := Color8(80, 38, 19)
const TIME_LIMIT := 120.0
const FRUIT_POINTS := 25.0
const ICE_ALPHA := 180.0 / 255.0
const BLOCK_NAMES := {1: "ice", 2: "furnace", 3: "counter"}

var grid := []  ## grid[y][x] is 1 when the cell is blocked
var blocks := {}  ## Vector2i -> AnimatedSprite2D (counter, furnace or ice)
var fruits := {}  ## Vector2i -> Sprite2D, only the wave being eaten
var waves: Array = []  ## fruit kind (1 to 4) of every wave
var wave := 0
var score := 0.0
var time_left := TIME_LIMIT

var fruit_layer := Node2D.new()
var world := Node2D.new()  ## everything that stands on the floor, sorted by height
var hud := CanvasLayer.new()
var score_label: Label
var time_label: Label
var clock_anim: AnimatedSprite2D
var wave_box: ReferenceRect
var wave_icons: Array[Sprite2D] = []


func _ready() -> void:
	world.y_sort_enabled = true
	add_child(fruit_layer)
	add_child(world)
	add_child(hud)
	_load_map()
	_build_hud()
	_load_wave()


func _draw() -> void:
	draw_rect(Rect2(0, 0, COLS * TILE, ROWS * TILE), FLOOR)


func _process(delta: float) -> void:
	time_left = maxf(time_left - delta, 0.0)
	_update_hud()


# --- Grid -------------------------------------------------------------------

static func cell_center(c: Vector2i) -> Vector2:
	return Vector2(c * TILE) + Vector2(TILE, TILE) / 2.0


func in_grid(c: Vector2i) -> bool:
	return c.x >= 0 and c.y >= 0 and c.x < COLS and c.y < ROWS


## Walkable means inside the outer ring of the kitchen and not blocked.
func is_free(c: Vector2i) -> bool:
	return c.x >= 1 and c.y >= 1 and c.x <= COLS - 2 and c.y <= ROWS - 2 and grid[c.y][c.x] == 0


func set_cell(c: Vector2i, value: int) -> void:
	grid[c.y][c.x] = value


func is_ice(c: Vector2i) -> bool:
	return blocks.has(c) and blocks[c].get_meta("kind") == "ice"


func _load_map() -> void:
	var rows := G.read_grid(G.level_file("map"))
	for y in ROWS:
		grid.append(PackedByteArray())
		grid[y].resize(COLS)
		for x in COLS:
			var kind: int = rows[y][x]
			if BLOCK_NAMES.has(kind):
				add_block(Vector2i(x, y), BLOCK_NAMES[kind])


## Places a counter, furnace or ice block. Blocks are 40 pixels tall and
## sit on the bottom of their cell, so they overlap the row above a bit.
func add_block(c: Vector2i, kind: String, show_after := 0.0) -> AnimatedSprite2D:
	var b := AnimatedSprite2D.new()
	b.sprite_frames = G.FRAMES
	b.animation = kind
	b.offset.y = -4
	b.position = cell_center(c)
	b.set_meta("kind", kind)
	if kind == "ice":
		b.modulate.a = ICE_ALPHA
	world.add_child(b)
	blocks[c] = b
	set_cell(c, 1)
	if show_after > 0:
		b.hide()
		b.create_tween().tween_callback(b.show).set_delay(show_after)
	return b


# --- Fruit ------------------------------------------------------------------

func _load_wave() -> void:
	for f in fruits.values():
		f.queue_free()
	fruits.clear()
	var rows := G.read_grid(G.level_file("fruits_%d" % G.LEVELS[G.level - 1].waves[wave]))
	for y in rows.size():
		for x in rows[y].size():
			if rows[y][x] != 0:
				var f := _fruit_sprite(rows[y][x])
				f.position = cell_center(Vector2i(x, y))
				fruit_layer.add_child(f)
				fruits[Vector2i(x, y)] = f
	_update_wave_box()


## Fruit drawn a bit smaller than a tile, the grape is squeezed to 24x24.
static func _fruit_sprite(kind: int) -> Sprite2D:
	var f := Sprite2D.new()
	f.texture = G.tex("fruit_%d" % kind)
	var s := f.texture.get_size()
	f.scale = Vector2(24, 24) / s if kind == 4 else (s * 0.9).floor() / s
	f.set_meta("kind", kind)
	return f


func _first_fruit_kind(file_number: int) -> int:
	for row in G.read_grid("res://assets/levels/level%d/fruits_%d.txt" % [G.level, file_number]):
		for kind in row:
			if kind != 0:
				return kind
	return 1


# --- HUD --------------------------------------------------------------------

func _build_hud() -> void:
	var ui := Control.new()
	ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(ui)
	# Score on a bar at the top, fruit waves on a bar at the bottom.
	G.image(ui, "fruit_bar", Rect2(192, 0, 256, 33))
	G.image(ui, "fruit_bar", Rect2(192, 442, 256, 33))
	score_label = G.label(ui, "", 25, Rect2(192, 2, 256, 30))

	for file_number in G.LEVELS[G.level - 1].waves:
		waves.append(_first_fruit_kind(file_number))
	for i in waves.size():
		var icon := _fruit_sprite(waves[i])
		icon.scale *= 0.8
		icon.position = Vector2(320 - (floori(waves.size() / 2.0) - i) * 32, 458.5)
		ui.add_child(icon)
		wave_icons.append(icon)
	wave_box = ReferenceRect.new()
	wave_box.editor_only = false
	wave_box.border_color = Color.BLACK
	wave_box.border_width = 2
	ui.add_child(wave_box)

	# Countdown clock in the top right corner.
	G.image(ui, "clock_ui", Rect2(538, 5, 97, 28))
	clock_anim = AnimatedSprite2D.new()
	clock_anim.sprite_frames = G.FRAMES
	clock_anim.centered = false
	clock_anim.position = Vector2(544, 6)
	clock_anim.play("clock")
	ui.add_child(clock_anim)
	time_label = G.label(ui, "", 20, Rect2(500, 7, 123, 24), HORIZONTAL_ALIGNMENT_RIGHT)


func _update_wave_box() -> void:
	if wave_box == null:
		return
	var icon := wave_icons[wave]
	var half := icon.texture.get_size() * icon.scale / 2.0
	wave_box.position = icon.position - half - Vector2(2, 2)
	wave_box.size = half * 2 + Vector2(4, 4)


func _update_hud() -> void:
	score_label.text = "%05d" % int(score)
	var t := floori(time_left)
	time_label.text = "%02d:%02d" % [floori(t / 60.0), t % 60]
	if time_left <= 0:
		clock_anim.stop()
