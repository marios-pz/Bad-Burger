extends Actor
## The burger. Arrow keys or WASD walk one cell at a time. Space shoots a line of
## ice in front of it, or kicks away the line of ice it is facing.

const CAST_MS := 500  ## the cast animation, the burger can not walk meanwhile

var casting_until := 0
var cooldown_until := 0
var cooldown_dir := Vector2i.ZERO
var done := false  ## the level is over, only the win or lose animation plays


func _ready() -> void:
	sprite_frames = G.FRAMES
	face("player_idle")


func _process(delta: float) -> void:
	if done:
		return
	var now := Time.get_ticks_msec()
	if casting_until and now >= casting_until:
		casting_until = 0
		G.sfx("ability", 0.2)
	if moving:
		slide(delta)
	if casting_until:
		return

	if Input.is_action_just_pressed("cast") and not moving and _can_cast(now):
		_cast(now)
		return
	var held := _held_direction()
	if held != Vector2i.ZERO:
		try_move(held)
	face("player_walk" if moving or held != Vector2i.ZERO else "player_idle")


## Same priority as the original: left, right, down, up.
## Arrow keys, WASD and the gamepad d-pad all work (see Project Settings, Input Map).
static func _held_direction() -> Vector2i:
	if Input.is_action_pressed("move_left"):
		return Vector2i.LEFT
	if Input.is_action_pressed("move_right"):
		return Vector2i.RIGHT
	if Input.is_action_pressed("move_down"):
		return Vector2i.DOWN
	if Input.is_action_pressed("move_up"):
		return Vector2i.UP
	return Vector2i.ZERO


## After a cast you wait a bit before the next one in the same direction.
## Turning around skips the wait.
func _can_cast(now: int) -> bool:
	return now >= cooldown_until or dir != cooldown_dir


func _cast(now: int) -> void:
	var first := cell + dir
	if not game.in_grid(first):
		return
	var breaking := game.is_ice(first)
	var count := game.break_line(first, dir) if breaking else game.ice_line(first, dir)
	casting_until = now + CAST_MS
	cooldown_until = now + count * 100 + (500 if breaking else 100)
	cooldown_dir = dir
	if breaking:
		play("player_kick")
		flip_h = false
	elif dir.y != 0:
		play("player_power_down")
		flip_h = false
	else:
		play("player_power_side")
		flip_h = dir.x < 0  # these frames face right
	set_frame_and_progress(0, 0.0)


func finish(won: bool) -> void:
	done = true
	moving = false
	flip_h = false
	play("player_win" if won else "player_dying")
	if not won:
		G.sfx("death", 0.3)
