extends Control
## Level select: 40 buns in a grid, the first 10 are real levels and
## the rest show a lock, just like the original jam build.

const SLOTS := 40
const SIZE := Vector2(41, 40)

var unlocked: Array[TextureButton] = []
var clock := 0.0


func _ready() -> void:
	size = Vector2(G.W, G.H)
	draw.connect(G.draw_tables.bind(self))
	G.image(self, "credits_bg", Rect2(0, 0, G.W, G.H))
	G.label(self, "level select", 50, Rect2(0, 35, G.W, 55))

	var pos := Vector2(124, 130)
	for i in SLOTS:
		var number := i + 1
		var open := number <= G.LEVELS.size()
		var b := G.button(self, Rect2(pos, SIZE), str(number), 30, Callable(), open)
		if open:
			b.pressed.connect(_play.bind(number))
			unlocked.append(b)
		else:
			b.disabled = true
			var lock := G.tex("lock")  # 22x32, shown 35 wide and peeking out the top
			G.image(b, "lock", Rect2(3, -10, 35, 35.0 * lock.get_height() / lock.get_width()))
		pos.x += SIZE.x + 10
		if pos.x >= 500:
			pos = Vector2(124, pos.y + SIZE.y + 10)

	G.button(self, Rect2(270, G.H - 100, 100, 40), "back", 30, G.go.bind("menu"))


func _process(delta: float) -> void:
	# Unlocked buns flicker between two hover frames while the mouse is on them.
	clock += delta
	var frame := G.FRAMES.get_frame_texture("level_hover", int(clock * 10) % 2)
	for b in unlocked:
		b.texture_hover = frame


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		G.go("menu")


func _play(number: int) -> void:
	G.level = number
	G.go("game")
