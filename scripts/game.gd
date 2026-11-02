class_name Game
extends Node2D
## One level: the kitchen floor, counters, furnaces, ice, fruit, the burger
## and the chefs, with the score and timer on top.

const TILE := 32
const COLS := 20
const ROWS := 15
const FLOOR := Color8(80, 38, 19)
const TIME_LIMIT := 120.0
const END_DELAY := 2.0  ## seconds the win or lose animation plays before the popup
const FRUIT_POINTS := 25.0
const ICE_ALPHA := 180.0 / 255.0
const BLOCK_NAMES := {1: "ice", 2: "furnace", 3: "counter"}
const BREAK_ALPHA := 128.0 / 255.0
const PlayerScript := preload("res://scripts/player.gd")
const EnemyScript := preload("res://scripts/enemy.gd")

var grid := []  ## grid[y][x] is 1 when the cell is blocked
var blocks := {}  ## Vector2i -> AnimatedSprite2D (counter, furnace or ice)
var fruits := {}  ## Vector2i -> Sprite2D, only the wave being eaten
var waves: Array = []  ## fruit kind (1 to 4) of every wave
var wave := 0
var score := 0.0
var time_left := TIME_LIMIT
var over := false  ## true once the level is won or lost

var player: Actor
var enemies: Array[Actor] = []
var astar := AStarGrid2D.new()

var fruit_layer := Node2D.new()
var world := Node2D.new()  ## everything that stands on the floor, sorted by height
var hud := CanvasLayer.new()
var overlay := CanvasLayer.new()  ## pause and end popups, still runs while paused
var popup: Control
var score_label: Label
var time_label: Label
var clock_anim: AnimatedSprite2D
var wave_box: ReferenceRect
var wave_icons: Array[Sprite2D] = []


func _ready() -> void:
	# The level root keeps running while paused so Escape can resume, the
	# board and HUD below it freeze.
	process_mode = Node.PROCESS_MODE_ALWAYS
	for layer in [fruit_layer, world, hud]:
		layer.process_mode = Node.PROCESS_MODE_PAUSABLE
		add_child(layer)
	world.y_sort_enabled = true
	overlay.layer = 2
	add_child(overlay)
	_start_music()
	_load_map()
	_build_hud()
	_load_wave()
	player = _spawn(PlayerScript, G.LEVELS[G.level - 1].start)
	for c in G.LEVELS[G.level - 1].enemies:
		enemies.append(_spawn(EnemyScript, c))
	astar.region = Rect2i(0, 0, COLS, ROWS)
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	astar.default_compute_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
	astar.update()


func _draw() -> void:
	draw_rect(Rect2(0, 0, COLS * TILE, ROWS * TILE), FLOOR)


func _process(delta: float) -> void:
	if Input.is_action_just_pressed("ui_cancel") and not over:
		_toggle_pause()
	if get_tree().paused:
		return
	time_left = maxf(time_left - delta, 0.0)
	_eat_fruit()
	if not over and _enemy_at(player.cell):
		finish(false)
	_update_hud()


func _spawn(script: Script, c: Vector2i) -> Actor:
	var a: Actor = script.new()
	a.game = self
	a.place(c)
	world.add_child(a)
	return a


## Ends the level once. The win or lose animation plays right away.
func finish(won: bool) -> void:
	if over:
		return
	over = true
	player.finish(won)
	if won:
		G.sfx("win")
	await get_tree().create_timer(END_DELAY, false).timeout
	var last := G.level >= G.LEVELS.size()
	var next := ["levels" if last else "next level", _next_level]
	popup = G.popup(overlay, "You Won !" if won else "You Lost !",
		[next if won else ["restart", G.go.bind("game")], ["quit", G.go.bind("menu")]])
	get_tree().paused = true


func _toggle_pause() -> void:
	get_tree().paused = not get_tree().paused
	if get_tree().paused:
		popup = G.popup(overlay, "GAME PAUSED", [["resume", _toggle_pause], ["quit", G.go.bind("menu")]])
	else:
		popup.queue_free()


## After the last level there is no next one, so go back to the list.
func _next_level() -> void:
	if G.level >= G.LEVELS.size():
		G.go("level_select")
	else:
		G.level += 1
		G.go("game")


func _start_music() -> void:
	if not G.music_on:
		return
	var music := AudioStreamPlayer.new()
	music.stream = preload("res://assets/sfx/boil.wav")
	music.volume_db = linear_to_db(0.2)
	music.finished.connect(music.play)  # loop
	add_child(music)
	music.play()


# --- Grid -------------------------------------------------------------------

static func cell_center(c: Vector2i) -> Vector2:
	return Vector2(c * TILE) + Vector2(TILE, TILE) / 2.0


func in_grid(c: Vector2i) -> bool:
	return c.x >= 0 and c.y >= 0 and c.x < COLS and c.y < ROWS


## Inside the outer ring of the kitchen, the ring itself is never walkable.
func _inside(c: Vector2i) -> bool:
	return c.x >= 1 and c.y >= 1 and c.x <= COLS - 2 and c.y <= ROWS - 2


## Walkable means inside the ring and not blocked.
func is_free(c: Vector2i) -> bool:
	return _inside(c) and grid[c.y][c.x] == 0


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


## Shortest walk from a to b, or an empty list. With through_ice the
## chefs plan as if ice was not there. This replaces pathfinder.py.
func find_path(a: Vector2i, b: Vector2i, through_ice: bool) -> Array[Vector2i]:
	for y in ROWS:
		for x in COLS:
			var c := Vector2i(x, y)
			astar.set_point_solid(c, not (is_free(c) or (through_ice and is_ice(c) and _inside(c))))
	astar.set_point_solid(a, false)  # level 1 spawns its chef inside a furnace
	astar.set_point_solid(b, false)
	return astar.get_id_path(a, b)


# --- Ice --------------------------------------------------------------------

func _enemy_at(c: Vector2i) -> bool:
	return enemies.any(func(e: Actor): return e.cell == c)


## Freezes floor cells from c onwards until something is in the way.
## Each block shows up 0.1 seconds after the one before it.
func ice_line(c: Vector2i, d: Vector2i) -> int:
	var count := 0
	while in_grid(c) and grid[c.y][c.x] == 0 and not _enemy_at(c):
		add_block(c, "ice", 0.1 + count * 0.1)
		count += 1
		c += d
	return count


## Breaks every ice block in a row from c onwards, one after another.
func break_line(c: Vector2i, d: Vector2i) -> int:
	var count := 0
	while is_ice(c):
		break_ice(c, count * 0.1)
		count += 1
		c += d
	return count


## Plays the shatter animation after delay and removes the block 0.5
## seconds later. Chefs smash ice with free_now so they can walk in at once.
func break_ice(c: Vector2i, delay: float, free_now := false) -> void:
	if not is_ice(c) or blocks[c].get_meta("breaking", false):
		return
	var b: AnimatedSprite2D = blocks[c]
	b.set_meta("breaking", true)
	if free_now:
		set_cell(c, 0)
	var t := b.create_tween()
	t.tween_interval(delay)
	t.tween_callback(func():
		b.show()
		b.modulate.a = BREAK_ALPHA
		b.play("ice_break"))
	t.tween_interval(0.5)
	t.tween_callback(func():
		if blocks.get(c) == b:  # a new block may already sit here
			blocks.erase(c)
			set_cell(c, 0)
		b.queue_free()
		G.sfx("ice_smash", 0.2))


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
## Fruit is eaten as soon as the burger starts walking into its cell.
## After the clock runs out every fruit is worth half.
func _eat_fruit() -> void:
	if fruits.has(player.cell):
		fruits[player.cell].queue_free()
		fruits.erase(player.cell)
		score += FRUIT_POINTS * (1.0 if time_left > 0 else 0.5)
		G.sfx("fruit_pickup")
	if fruits.is_empty() and not over:
		if wave < waves.size() - 1:
			wave += 1
			_load_wave()
		else:
			finish(true)


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
	# Score in a box at the top, fruit waves in a box at the bottom.
	G.panel(ui, Rect2(250, 3, 140, 32), "HudPanel")
	G.panel(ui, Rect2(250, 440, 140, 36), "HudPanel")
	score_label = G.label(ui, "", 24, Rect2(250, 3, 140, 30))

	for file_number in G.LEVELS[G.level - 1].waves:
		waves.append(_first_fruit_kind(file_number))
	for i in waves.size():
		var icon := _fruit_sprite(waves[i])
		icon.scale *= 0.8
		icon.position = Vector2(320 - (floori(waves.size() / 2.0) - i) * 32, 456)
		ui.add_child(icon)
		wave_icons.append(icon)
	wave_box = ReferenceRect.new()
	wave_box.editor_only = false
	wave_box.border_color = Color(0.784, 0.271, 0.227)
	wave_box.border_width = 2
	ui.add_child(wave_box)

	# Countdown clock in the top right corner.
	G.panel(ui, Rect2(532, 3, 104, 32), "HudPanel")
	clock_anim = AnimatedSprite2D.new()
	clock_anim.sprite_frames = G.FRAMES
	clock_anim.centered = false
	clock_anim.position = Vector2(537, 5)
	clock_anim.play("clock")
	ui.add_child(clock_anim)
	time_label = G.label(ui, "", 20, Rect2(560, 3, 70, 30), HORIZONTAL_ALIGNMENT_RIGHT)


func _update_wave_box() -> void:
	if wave_box == null:
		return
	# Same size box for every fruit, centered on the icon.
	wave_box.size = Vector2(30, 28)
	wave_box.position = wave_icons[wave].position - wave_box.size / 2.0


func _update_hud() -> void:
	score_label.text = "%05d" % int(score)
	var t := floori(time_left)
	time_label.text = "%02d:%02d" % [floori(t / 60.0), t % 60]
	if time_left <= 0:
		clock_anim.stop()
