class_name Actor
extends AnimatedSprite2D
## Grid movement shared by the burger and the chefs. They always belong
## to one cell and slide over to the next, like in the Pygame version.

var game: Game
var cell := Vector2i.ZERO  ## the cell we stand on, or are walking to
var dir := Vector2i.RIGHT
var moving := false
var speed := 150.0  ## pixels per second


func place(c: Vector2i) -> void:
	cell = c
	position = Game.cell_center(c)


## Turns towards d and starts walking if that cell is free.
func try_move(d: Vector2i) -> void:
	if moving:
		return
	dir = d
	if game.is_free(cell + d):
		cell += d
		moving = true


## Moves towards the current cell. When it arrives it returns the time
## left over in this frame, so the next step can use it without a hitch.
func slide(delta: float) -> float:
	var target := Game.cell_center(cell)
	var step := speed * delta
	var dist := position.distance_to(target)
	if step >= dist:
		position = target
		moving = false
		return (step - dist) / speed
	position = position.move_toward(target, step)
	return 0.0


## Plays name_down, name_up or name_side for the current direction.
## Side frames are drawn facing one way and mirrored for the other.
func face(anim: String, side_faces_left := true) -> void:
	if dir.y != 0:
		play(anim + ("_down" if dir.y > 0 else "_up"))
		flip_h = false
	else:
		play(anim + "_side")
		flip_h = (dir.x > 0) == side_faces_left
