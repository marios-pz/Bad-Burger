extends Actor
## The burger. Arrow keys or WASD walk one cell at a time. Space shoots a line of
## ice in front of it, or kicks away the line of ice it is facing.
##
## In co-op each burger reads its own keys: controls "p1_" is WASD and
## space, "p2_" is the arrow keys and enter (see Project Settings, Input
## Map). Solo play uses "", which listens to all of them.

const CAST_MS := 500  ## the cast animation, the burger can not walk meanwhile
const BUFFER_MS := 150  ## a key pressed this long before the burger is ready still counts
const MOVES := {
	"move_left": Vector2i.LEFT, "move_right": Vector2i.RIGHT,
	"move_up": Vector2i.UP, "move_down": Vector2i.DOWN,
}

var casting_until := 0
var cooldown_until := 0
var cooldown_dir := Vector2i.ZERO
var controls := ""  ## input action prefix: "", "p1_" or "p2_", set before spawning
var done := false  ## the level is over, only the win or lose animation plays
var out := false  ## caught by a chef in co-op, waits for the next fruit wave
var held: Array[Vector2i] = []  ## directions being held, the newest one last
var queued_dir := Vector2i.ZERO  ## last direction pressed, kept for a moment
var queued_at := -BUFFER_MS
var cast_at := -BUFFER_MS  ## when space was last pressed


func _ready() -> void:
	sprite_frames = G.FRAMES
	face("player_idle")


func _process(delta: float) -> void:
	if done:
		return
	var now := Time.get_ticks_msec()
	_read_input(now)
	if casting_until and now >= casting_until:
		casting_until = 0
		G.sfx("ability", 0.2)

	var want: Vector2i = held.back() if held else Vector2i.ZERO
	var spare := 0.0
	if moving:
		# Turning around halfway through a step is allowed right away.
		if want == -dir and game.is_free(cell - dir):
			cell -= dir
			dir = want
		spare = slide(delta)
	if casting_until:
		return  # keep the cast animation
	if moving:
		face("player_walk")
		return

	if now - cast_at < BUFFER_MS and _can_cast(now):
		cast_at = -BUFFER_MS
		_cast(now)
		return
	if want == Vector2i.ZERO and now - queued_at < BUFFER_MS:
		want = queued_dir  # a quick tap that ended before the burger was ready
	if want != Vector2i.ZERO:
		queued_at = -BUFFER_MS
		try_move(want)
		if moving and spare > 0:
			slide(spare)  # keep the leftover from the last step, no hitch
	face("player_walk" if moving else "player_idle")


## Keeps a list of held directions so the newest key always wins, and
## remembers taps and space presses for a short moment.
func _read_input(now: int) -> void:
	for move in MOVES:
		var d: Vector2i = MOVES[move]
		var action: String = controls + move
		if Input.is_action_just_pressed(action):
			held.erase(d)
			held.append(d)
			queued_dir = d
			queued_at = now
		elif not Input.is_action_pressed(action):
			held.erase(d)
	if Input.is_action_just_pressed(controls + "cast"):
		cast_at = now


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


## Caught in co-op: plays the dying animation and stays on the floor,
## faded, until the next fruit wave brings it back.
func knock_out() -> void:
	finish(false)
	out = true
	modulate.a = 0.5


## Back in the game on cell c, ready to walk.
func revive(c: Vector2i) -> void:
	done = false
	out = false
	modulate.a = 1.0
	casting_until = 0
	held.clear()
	place(c)
	face("player_idle")
