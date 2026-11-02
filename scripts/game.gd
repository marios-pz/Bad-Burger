class_name Game
extends Node2D
## One level: the kitchen floor, counters, furnaces, ice, fruit, the burgers
## and the chefs, with the score and timer on top.
##
## In local co-op (G.players == 2) a second burger joins. A caught burger
## is out until the next fruit wave, and the level is lost only when both
## burgers are caught.

const TILE := 32
const COLS := 20
const ROWS := 15
## Floor tiles: a checkerboard of two dirt tones with dark grout lines and
## a light top edge, so every cell of the grid is easy to see.
const FLOOR_A := Color8(96, 48, 24)
const FLOOR_B := Color8(84, 41, 20)
const FLOOR_GROUT := Color8(52, 24, 11)
const FLOOR_SHINE := Color8(112, 60, 32)
const TIME_LIMIT := 120.0
const ZOOM := 1.5  ## how close the camera is, 1.0 shows the whole kitchen
const END_DELAY := 2.0  ## seconds the win or lose animation plays before the popup
const FRUIT_POINTS := 25.0
const ICE_ALPHA := 180.0 / 255.0
const BLOCK_NAMES := {1: "ice", 2: "furnace", 3: "counter"}
const BREAK_ALPHA := 128.0 / 255.0
const P2_HUE := 0.06  ## how far player 2's colors are shifted, 0 to 1
const DIRS: Array[Vector2i] = [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]
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

var player: Actor  ## player 1, also the only burger in solo play
var players: Array[Actor] = []
var cam := Camera2D.new()
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
	var level: Dictionary = G.LEVELS[G.level - 1]
	for c in level.enemies:
		enemies.append(_spawn(EnemyScript, c))
	for c in level.get("green", []):
		enemies.append(_spawn(EnemyScript, c, {kind = "green"}))
	var coop := G.players == 2
	player = _spawn(PlayerScript, level.start, {controls = "p1_" if coop else ""})
	players.append(player)
	if coop:
		var p2 := _spawn(PlayerScript, free_cell_near(level.start), {controls = "p2_"})
		p2.material = ShaderMaterial.new()
		p2.material.shader = preload("res://assets/hue_shift.gdshader")
		p2.material.set_shader_parameter("hue_shift", P2_HUE)
		players.append(p2)
		_add_tag(player, "1")
		_add_tag(p2, "2")
	_add_camera()
	astar.region = Rect2i(0, 0, COLS, ROWS)
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	astar.default_compute_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
	astar.update()


func _draw() -> void:
	for y in ROWS:
		for x in COLS:
			var r := Rect2(x * TILE, y * TILE, TILE, TILE)
			draw_rect(r, FLOOR_A if (x + y) % 2 == 0 else FLOOR_B)
			draw_rect(Rect2(r.position + Vector2(1, 1), Vector2(TILE - 1, 1)), FLOOR_SHINE)
			draw_rect(Rect2(r.position, Vector2(TILE, 1)), FLOOR_GROUT)
			draw_rect(Rect2(r.position, Vector2(1, TILE)), FLOOR_GROUT)


func _process(delta: float) -> void:
	if Input.is_action_just_pressed("ui_cancel") and not over:
		_toggle_pause()
	if get_tree().paused:
		return
	time_left = maxf(time_left - delta, 0.0)
	_eat_fruit()
	_catch_burgers()
	_move_camera(delta)
	_update_hud()


## Burgers still in the game, the ones not caught yet.
func alive_players() -> Array[Actor]:
	return players.filter(func(p: Actor): return not p.out)


func _catch_burgers() -> void:
	if over:
		return
	for p in alive_players():
		if not _enemy_at(p.cell):
			continue
		if players.size() == 1:
			finish(false)
			return
		p.knock_out()
		if alive_players().is_empty():
			finish(false)
			return


## The free cell closest to c that no chef stands on. Used to place
## player 2 next to player 1, and to bring caught burgers back. Some
## levels start the burger sealed in ice, then this returns c itself
## and both burgers share the cell until they break out.
func free_cell_near(c: Vector2i) -> Vector2i:
	var seen := {c: true}
	var queue: Array[Vector2i] = [c]
	while not queue.is_empty():
		var current: Vector2i = queue.pop_front()
		for d in DIRS:
			var next := current + d
			if seen.has(next) or not is_free(next):
				continue
			if not _enemy_at(next):
				return next
			seen[next] = true
			queue.append(next)
	return c


## A small "1" or "2" floating over a burger in co-op.
func _add_tag(p: Actor, text: String) -> void:
	var tag := G.label(p, text, 18, Rect2(-20, -36, 40, 16))
	tag.add_theme_color_override("font_color", Color(0.965, 0.906, 0.784))
	tag.add_theme_color_override("font_outline_color", Color(0.169, 0.102, 0.071))
	tag.add_theme_constant_override("outline_size", 6)


## The camera stops at the kitchen walls so nothing outside shows.
## Solo: it follows the burger, zoomed in. Co-op: it sits between the
## burgers and zooms out as far as needed to keep both on screen.
func _add_camera() -> void:
	cam.zoom = Vector2(ZOOM, ZOOM)
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = COLS * TILE
	cam.limit_bottom = ROWS * TILE
	cam.position_smoothing_enabled = true
	cam.position_smoothing_speed = 8.0
	world.add_child(cam)
	_move_camera(0.0)
	cam.reset_smoothing()


func _move_camera(delta: float) -> void:
	var group := alive_players()
	if group.is_empty():
		group = players
	var box := Rect2(group[0].position, Vector2.ZERO)
	for p in group:
		box = box.expand(p.position)
	cam.position = box.get_center()
	# Keep about 3 cells of room around the burgers on every side.
	var room := box.size + Vector2(6, 6) * TILE
	var fit := minf(G.W / room.x, G.H / room.y)
	var target := clampf(fit, 1.0, ZOOM)
	cam.zoom = Vector2.ONE * (target if delta == 0.0 else lerpf(cam.zoom.x, target, 1.0 - exp(-4.0 * delta)))


## Creates the burger or a chef on cell c. props are set before it
## enters the level, for example {kind = "green"} for a green chef.
func _spawn(script: Script, c: Vector2i, props := {}) -> Actor:
	var a: Actor = script.new()
	a.game = self
	for key in props:
		a.set(key, props[key])
	a.place(c)
	world.add_child(a)
	return a


## Ends the level once. The win or lose animation plays right away.
func finish(won: bool) -> void:
	if over:
		return
	over = true
	for p in alive_players():
		p.finish(won)
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


func _burger_at(c: Vector2i) -> bool:
	return alive_players().any(func(p: Actor): return p.cell == c)


## Freezes floor cells from c onwards until something is in the way,
## a block, a chef or the other burger.
## Each block shows up 0.1 seconds after the one before it.
func ice_line(c: Vector2i, d: Vector2i) -> int:
	var count := 0
	while in_grid(c) and grid[c.y][c.x] == 0 and not _enemy_at(c) and not _burger_at(c):
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


## Fruit is eaten as soon as a burger starts walking into its cell.
## After the clock runs out every fruit is worth half. A new wave brings
## caught burgers back next to a teammate.
func _eat_fruit() -> void:
	for p in alive_players():
		if fruits.has(p.cell):
			fruits[p.cell].queue_free()
			fruits.erase(p.cell)
			score += FRUIT_POINTS * (1.0 if time_left > 0 else 0.5)
			G.sfx("fruit_pickup")
	if fruits.is_empty() and not over:
		if wave < waves.size() - 1:
			wave += 1
			_load_wave()
			_revive_burgers()
		else:
			finish(true)


func _revive_burgers() -> void:
	var standing := alive_players()
	for p in players:
		if p.out and not standing.is_empty():
			p.revive(free_cell_near(standing[0].cell))


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
	# Score in a box at the top, fruit waves in a box at the bottom.
	G.panel(ui, Rect2(250, 3, 140, 32), "HudPanel")
	G.panel(ui, Rect2(250, 440, 140, 36), "HudPanel")
	score_label = G.label(ui, "", 34, Rect2(250, 3, 140, 30))

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
	time_label = G.label(ui, "", 28, Rect2(560, 3, 70, 30), HORIZONTAL_ALIGNMENT_RIGHT)


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
