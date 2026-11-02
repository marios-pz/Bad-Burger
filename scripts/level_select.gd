extends Control
## Level select: 40 buttons in a grid. Levels 1 to 10 can be played,
## the rest are greyed out, just like the original jam build.

const SLOTS := 40
const SIZE := Vector2(41, 40)


func _ready() -> void:
	size = Vector2(G.W, G.H)
	draw.connect(G.draw_tables.bind(self))
	G.panel(self, Rect2(96, 24, 448, 432))
	G.label(self, "level select", 56, Rect2(96, 40, 448, 50))

	var pos := Vector2(124, 116)
	var first: Button
	for i in SLOTS:
		var number := i + 1
		var b := G.button(self, Rect2(pos, SIZE), str(number), 31)
		if number <= G.LEVELS.size():
			b.pressed.connect(_play.bind(number))
			first = first if first else b
		else:
			b.disabled = true
		pos.x += SIZE.x + 10
		if pos.x >= 500:
			pos = Vector2(124, pos.y + SIZE.y + 10)

	G.button(self, Rect2(250, 386, 140, 40), "back", 34, G.go.bind("menu"))
	first.grab_focus.call_deferred()  # so keyboard and gamepad can pick a level


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		G.go("menu")


func _play(number: int) -> void:
	G.level = number
	G.go("game")
