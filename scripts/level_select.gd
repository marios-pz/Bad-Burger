extends Control
## Level select: one button for every level in G.LEVELS, five per row.

const PER_ROW := 5
const SIZE := Vector2(64, 56)
const GAP := 16


func _ready() -> void:
	size = Vector2(G.W, G.H)
	draw.connect(G.draw_tables.bind(self))
	G.panel(self, Rect2(96, 24, 448, 432))
	G.label(self, "level select", 56, Rect2(96, 40, 448, 50))

	var row_width := PER_ROW * SIZE.x + (PER_ROW - 1) * GAP
	var origin := Vector2((G.W - row_width) / 2.0, 130)
	var buttons: Array[Button] = []
	for i in G.LEVELS.size():
		var spot := Vector2(i % PER_ROW, floorf(i / float(PER_ROW)))
		var b := G.button(self, Rect2(origin + spot * (SIZE + Vector2(GAP, GAP)), SIZE),
			str(i + 1), 42, _play.bind(i + 1))
		buttons.append(b)
	G.label(self, "watch out, green chefs from level 5 on!", 25, Rect2(96, 290, 448, 30))

	G.button(self, Rect2(250, 386, 140, 40), "back", 34, G.go.bind("menu"))
	buttons[0].grab_focus.call_deferred()  # so keyboard and gamepad can pick a level


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		G.go("menu")


func _play(number: int) -> void:
	G.level = number
	G.go("game")
