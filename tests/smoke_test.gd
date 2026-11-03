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


## How many chef markers a level scene has.
func chef_markers(n: int) -> int:
	var scene: Node = load(G.level_path(n)).instantiate()
	var count := 0
	for spawn in scene.get_node("Spawns").get_children():
		if spawn is LevelSpawn and spawn.what != LevelSpawn.What.BURGER:
			count += 1
	scene.free()
	return count


func load_level(n: int) -> Game:
	G.level = n
	var game: Game = load("res://scenes/game.tscn").instantiate()
	add_child(game)
	return game


func _ready() -> void:
	G.sfx_on = false
	G.music_on = false
	check(G.level_count >= 10, "all level scenes are found")

	for n in range(1, G.level_count + 1):
		var game := load_level(n)
		check(game.is_free(game.player.cell), "level %d: burger starts on a free cell" % n)
		check(not game.fruits.is_empty(), "level %d: has fruit" % n)
		check(game.enemies.size() == chef_markers(n), "level %d: all chefs spawned" % n)
		var greens := game.enemies.filter(func(e): return e.kind == "green").size()
		check((greens > 0) == (n >= 5), "level %d: green chefs only from level 5 on" % n)
		for e in game.enemies:
			if e.kind == "green":
				check(not e.sees_player(), "level %d: the green chef does not see the burger at the start" % n)
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

	# Co-op: player 2 starts on a free cell next to player 1 on every level.
	G.players = 2
	for n in range(1, G.level_count + 1):
		game = load_level(n)
		var p1: Actor = game.players[0]
		var p2: Actor = game.players[1]
		var sealed := not Game.DIRS.any(func(d): return game.is_free(p1.cell + d))
		check(game.is_free(p2.cell) and not game._enemy_at(p2.cell) and (p2.cell != p1.cell or sealed),
			"level %d: player 2 starts on a free cell next to player 1" % n)
		game.free()

	# Co-op rule: a caught burger is out until the next wave, the level is
	# lost only when both are caught. Level 4 has two fruit waves.
	game = load_level(4)
	var p1: Actor = game.players[0]
	var p2: Actor = game.players[1]
	game.enemies[0].place(p2.cell)
	await get_tree().process_frame
	check(p2.out and not game.over, "co-op: one caught burger does not end the level")
	for f in game.fruits.values():
		f.free()
	game.fruits.clear()
	await get_tree().process_frame
	check(game.wave == 1 and not p2.out, "co-op: the next fruit wave brings the caught burger back")
	game.enemies[0].place(p1.cell)
	game.enemies[1].place(p2.cell)
	await get_tree().process_frame
	check(game.over and p1.out and p2.out, "co-op: catching both burgers ends the level")
	game.free()
	G.players = 1

	print("PASS" if failures == 0 else "%d check(s) failed" % failures)
	get_tree().quit(1 if failures else 0)
