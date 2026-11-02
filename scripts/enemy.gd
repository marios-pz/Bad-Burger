extends Actor
## A chef. Wanders around until the burger comes close, then shows a
## blinking "!" and chases it. If the burger hides behind ice, the chef
## smashes its way through.
##
## There are two kinds. The red chef is the original one. The green chef
## shows up from level 5 on: it spots the burger from further away, moves
## faster (still slower than the burger) and smashes ice quicker.

const KINDS := {
	"red": {sight = 5, wander_speed = 45.0, chase_speed = 67.5, smash_pause_ms = 600},
	"green": {sight = 8, wander_speed = 60.0, chase_speed = 95.0, smash_pause_ms = 250},
}
const GREEN_LOOK := preload("res://assets/hue_shift.gdshader")
const DIRECTIONS: Array[Vector2i] = [Vector2i.DOWN, Vector2i.RIGHT, Vector2i.LEFT, Vector2i.UP]

var kind := "red"  ## set before the chef is added to the level
var sight: int
var wander_speed: float
var chase_speed: float
var smash_pause_ms: int
var resting_until := 0
var saw_player := false
var alert := Sprite2D.new()


func _ready() -> void:
	for stat in KINDS[kind]:
		set(stat, KINDS[kind][stat])
	if kind == "green":
		# Same frames as the red chef, recolored on the fly.
		material = ShaderMaterial.new()
		material.shader = GREEN_LOOK
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
	return maxi(gap.x, gap.y) <= sight


func _think(sees: bool, now: int) -> void:
	if not sees:
		speed = wander_speed
		# Keep walking straight, pick a random way when blocked.
		try_move(dir if game.is_free(cell + dir) else DIRECTIONS.pick_random())
		return

	speed = chase_speed
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
		resting_until = now + smash_pause_ms
