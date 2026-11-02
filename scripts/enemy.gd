extends Actor
## A chef. Wanders around until the burger comes within 5 cells, then
## shows a blinking "!" and chases it. If the burger hides behind ice,
## the chef smashes its way through.

const SIGHT := 5
const WANDER_SPEED := 45.0
const CHASE_SPEED := 67.5  ## 50% faster while chasing
const SMASH_PAUSE_MS := 600
const DIRECTIONS: Array[Vector2i] = [Vector2i.DOWN, Vector2i.RIGHT, Vector2i.LEFT, Vector2i.UP]

var resting_until := 0
var saw_player := false
var alert := Sprite2D.new()


func _ready() -> void:
	sprite_frames = G.FRAMES
	animation = "enemy_down"
	alert.texture = G.tex("alert")
	alert.hide()
	add_child(alert)


func _process(delta: float) -> void:
	var now := Time.get_ticks_msec()
	var sees := sees_player()
	if sees and not saw_player:
		G.sfx("detect", 0.2)
	saw_player = sees
	alert.visible = sees and (now / 250) % 2 == 0

	if now < resting_until:
		return
	if moving:
		slide(delta)
	else:
		_think(sees, now)
	if moving:
		face("enemy")
	else:
		pause()


func sees_player() -> bool:
	var gap: Vector2i = (game.player.cell - cell).abs()
	return maxi(gap.x, gap.y) <= SIGHT


func _think(sees: bool, now: int) -> void:
	if not sees:
		speed = WANDER_SPEED
		# Keep walking straight, pick a random way when blocked.
		try_move(dir if game.is_free(cell + dir) else DIRECTIONS.pick_random())
		return

	speed = CHASE_SPEED
	var path: Array[Vector2i] = game.find_path(cell, game.player.cell, false)
	if path.size() >= 2:
		try_move(path[1] - cell)
		return
	# No open way: plan a route through ice and smash the first block.
	path = game.find_path(cell, game.player.cell, true)
	if path.size() < 2:
		return
	var step := path[1] - cell
	if game.is_free(cell + step):
		try_move(step)
	else:
		dir = step
		game.break_ice(cell + step, 0.0, true)
		resting_until = now + SMASH_PAUSE_MS
