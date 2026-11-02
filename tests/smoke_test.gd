extends Node
## Quick check that every level loads and the core rules still work.
## Run it with:  godot --headless --path . res://tests/smoke_test.tscn
## It prints PASS and exits with code 0, or prints what broke.

var failures := 0


func check(ok: bool, what: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", what)


func press(key: Key, down: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = key
	e.pressed = down
	Input.parse_input_event(e)


func load_level(n: int) -> Game:
	G.level = n
	var game: Game = load("res://scenes/game.tscn").instantiate()
	add_child(game)
	return game


func _ready() -> void:
	G.sfx_on = false
	G.music_on = false

	for n in range(1, G.LEVELS.size() + 1):
		var game := load_level(n)
		check(game.is_free(game.player.cell), "level %d: burger starts on a free cell" % n)
		check(not game.fruits.is_empty(), "level %d: has fruit" % n)
		check(game.enemies.size() == G.LEVELS[n - 1].enemies.size(), "level %d: all chefs spawned" % n)
		for e in game.enemies:
			var path := game.find_path(e.cell, game.player.cell, true)
			check(path.size() >= 2, "level %d: chef at %s can reach the burger through ice" % [n, e.cell])
		game.free()

	# Level 1: the burger starts at (2, 1), below it are two floor cells
	# and then an ice block.
	var game := load_level(1)
	check(game.ice_line(Vector2i(2, 2), Vector2i.DOWN) == 2, "ice line stops at the first block")
	check(game.is_ice(Vector2i(2, 3)) and not game.is_free(Vector2i(2, 3)), "new ice blocks the cell")
	check(game.break_line(Vector2i(6, 2), Vector2i.RIGHT) == 8, "kick breaks the whole row of 8")
	game.free()

	# Pressing D (WASD) walks the burger one cell to the right.
	game = load_level(1)
	game.enemies[0].place(Vector2i(17, 13))  # keep the chef out of the way
	var start: Vector2i = game.player.cell
	press(KEY_D, true)
	await get_tree().process_frame
	await get_tree().process_frame
	press(KEY_D, false)
	check(game.player.cell == start + Vector2i.RIGHT, "the D key walks right")
	game.free()

	# Pressing A halfway through a step to the right turns straight back,
	# even with D still held, because the newest key wins.
	game = load_level(1)
	game.enemies[0].place(Vector2i(17, 13))
	start = game.player.cell
	press(KEY_D, true)
	await get_tree().process_frame
	await get_tree().process_frame
	press(KEY_A, true)
	await get_tree().process_frame
	await get_tree().process_frame
	press(KEY_A, false)
	press(KEY_D, false)
	check(game.player.cell == start and game.player.dir == Vector2i.LEFT, "turning back mid-step returns to the start cell")
	game.free()

	# A chef standing next to an idle burger catches it.
	game = load_level(1)
	game.enemies[0].place(game.player.cell + Vector2i.RIGHT)
	for i in 120:
		await get_tree().process_frame
		if game.over:
			break
	check(game.over and game.player.done, "a chef next to the burger ends the level")
	game.free()

	print("PASS" if failures == 0 else "%d check(s) failed" % failures)
	get_tree().quit(1 if failures else 0)
