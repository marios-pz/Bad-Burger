@tool
class_name LevelSpawn
extends Marker2D
## Where the burger or a chef starts in a level scene. Drag it onto a
## cell in the editor, any spot inside the cell works. It shows the
## sprite in the editor only, the game reads its cell when the level
## loads and creates the real burger or chef there.

enum What { BURGER, RED_CHEF, GREEN_CHEF }

const FRAMES := preload("res://assets/sprites.tres")

@export var what := What.RED_CHEF:
	set(value):
		what = value
		queue_redraw()


## The grid cell this marker sits in.
func cell() -> Vector2i:
	return Vector2i((position / 32.0).floor())


func _draw() -> void:
	if not Engine.is_editor_hint():
		return
	var tex := FRAMES.get_frame_texture("player_idle_down" if what == What.BURGER else "enemy_down", 0)
	var tint := Color(0.55, 1.0, 0.45) if what == What.GREEN_CHEF else Color.WHITE
	draw_texture(tex, -tex.get_size() / 2.0, tint)
