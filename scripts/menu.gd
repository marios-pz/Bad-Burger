extends Control
## Main menu. Four pages share the same table background:
## "click to eat" title, the main buttons, help and credits.

const RUNNERS := 7
const RUN_SPEED := 300.0  # pixels per second
const JUMP_TIME := 0.7
const JUMP_HEIGHT := 192.0
## The help page burger walks down, left, up, right and the matching key lights up.
const SHOWCASE := [["player_walk_down", false, "S"], ["player_walk_side", false, "A"],
	["player_walk_up", false, "W"], ["player_walk_side", true, "D"]]
const ROLE_COLOR := Color(0.784, 0.271, 0.227)

var runners: Array[AnimatedSprite2D] = []
var logo: TextureRect
var title_page: Control
var main_page: Control
var help_page: Control
var credits_page: Control
var sound_buttons: Control
var showcase: AnimatedSprite2D
var keys := {}  ## letter -> key cap Panel on the help page
var clock := 0.0


func _ready() -> void:
	size = Vector2(G.W, G.H)
	draw.connect(G.draw_tables.bind(self))
	_add_runners()

	logo = TextureRect.new()
	logo.texture = preload("res://assets/logo.png")
	logo.position.x = (G.W - logo.texture.get_width()) / 2.0
	logo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(logo)

	sound_buttons = Control.new()
	sound_buttons.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(sound_buttons)
	_sound_button(Rect2(G.W - 220, 8, 112, 30), "music")
	_sound_button(Rect2(G.W - 102, 8, 94, 30), "sfx")

	title_page = _page()
	G.button(title_page, Rect2(215, 300, 210, 48), "click to eat", 36, _open_main)

	main_page = _page()
	G.button(main_page, Rect2(240, 288, 160, 40), "play", 34, G.go.bind("level_select"))
	G.button(main_page, Rect2(240, 334, 160, 40), "help", 34, _show.bind("help"))
	G.button(main_page, Rect2(240, 380, 160, 40), "credits", 34, _show.bind("credits"))
	G.button(main_page, Rect2(240, 426, 160, 40), "quit", 34, get_tree().quit)

	credits_page = _dimmed_page()
	G.panel(credits_page, Rect2(140, 40, 360, 400))
	G.label(credits_page, G.CREDITS[0], 48, Rect2(140, 54, 360, 44))
	for i in range(1, G.CREDITS.size()):
		var line := G.label(credits_page, G.CREDITS[i], 31, Rect2(140, 80 + i * 36, 360, 32))
		if G.CREDITS[i].ends_with(":"):
			line.add_theme_color_override("font_color", ROLE_COLOR)
	G.button(credits_page, Rect2(250, 376, 140, 40), "back", 34, _show.bind("main"))

	help_page = _dimmed_page()
	G.panel(help_page, Rect2(110, 40, 420, 400))
	G.label(help_page, "how to play", 45, Rect2(110, 52, 420, 40))
	showcase = AnimatedSprite2D.new()
	showcase.sprite_frames = G.FRAMES
	showcase.position = Vector2(220, 146)
	showcase.scale = Vector2(2, 2)
	help_page.add_child(showcase)
	for k in [["W", 400, 102], ["A", 360, 142], ["S", 400, 142], ["D", 440, 142]]:
		keys[k[0]] = _key(Rect2(k[1], k[2], 36, 36), k[0])
	G.label(help_page, "walk with wasd or the arrow keys", 22, Rect2(110, 190, 420, 24))
	_key(Rect2(150, 228, 120, 32), "space")
	G.label(help_page, "make or break ice", 22, Rect2(284, 228, 230, 32), HORIZONTAL_ALIGNMENT_LEFT)
	_key(Rect2(150, 272, 120, 32), "esc")
	G.label(help_page, "pause", 22, Rect2(284, 272, 230, 32), HORIZONTAL_ALIGNMENT_LEFT)
	G.label(help_page, "eat all the fruit and dodge the chefs!", 22, Rect2(130, 316, 380, 40))
	G.button(help_page, Rect2(250, 376, 140, 40), "back", 34, _show.bind("main"))

	_show("main" if G.menu_opened else "title")


func _process(delta: float) -> void:
	clock += delta
	logo.position.y = -5 + sin(clock * 5) * 5
	for r in runners:
		_move_runner(r, delta)
	if help_page.visible:
		var step: Array = SHOWCASE[int(clock / 0.8) % 4]
		showcase.play(step[0])
		showcase.flip_h = step[1]
		for letter in keys:
			keys[letter].theme_type_variation = "KeyCapOn" if letter == step[2] else "KeyCap"


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and (help_page.visible or credits_page.visible):
		_show("main")


func _page() -> Control:
	var page := Control.new()
	page.size = size
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(page)
	return page


## A page that darkens the menu behind it, used by help and credits.
func _dimmed_page() -> Control:
	var page := ColorRect.new()
	page.color = Color(0, 0, 0, 0.45)
	page.size = size
	add_child(page)
	return page


## A keyboard key drawn as a small box with its name on it.
func _key(rect: Rect2, text: String) -> Panel:
	var cap := G.panel(help_page, rect, "KeyCap")
	G.label(cap, text, 25, Rect2(Vector2(0, -1), rect.size))
	return cap


func _show(page: String) -> void:
	title_page.visible = page == "title"
	main_page.visible = page == "main"
	help_page.visible = page == "help"
	credits_page.visible = page == "credits"
	sound_buttons.visible = page in ["title", "main"]


func _open_main() -> void:
	G.menu_opened = true
	_show("main")


## Small on/off switch for music or sound effects, saved right away.
func _sound_button(rect: Rect2, kind: String) -> void:
	var b := G.button(sound_buttons, rect, "", 22)
	var refresh := func():
		var on: bool = G.music_on if kind == "music" else G.sfx_on
		b.text = "%s: %s" % [kind, "on" if on else "off"]
	refresh.call()
	b.pressed.connect(func():
		if kind == "music":
			G.music_on = not G.music_on
		else:
			G.sfx_on = not G.sfx_on
		G.save_settings()
		refresh.call())


# --- Burgers running across the screen ---------------------------------------

func _add_runners() -> void:
	for i in RUNNERS:
		var r := AnimatedSprite2D.new()
		r.sprite_frames = G.FRAMES
		r.centered = false
		r.scale = Vector2(2, 2)
		r.position = Vector2(-100 * i, randi_range(270, 370))
		r.set_meta("ground", r.position.y)
		r.set_meta("jump", -1.0)  # time spent in the air, below 0 means on the ground
		r.play("menu_run")
		r.frame = randi() % 8
		add_child(r)
		runners.append(r)


func _move_runner(r: AnimatedSprite2D, delta: float) -> void:
	r.position.x += RUN_SPEED * delta
	if r.position.x >= G.W + 50:
		r.position.x = 0
	var t: float = r.get_meta("jump")
	if t < 0:
		# The original rolled a 10% chance every frame at 30 fps.
		if r.position.x >= 0 and randf() < 1.0 - pow(0.9, delta * 30):
			t = 0.0
	else:
		t += delta
		if t >= JUMP_TIME:
			t = -1.0
	r.set_meta("jump", t)
	var lift := 0.0 if t < 0 else 4.0 * JUMP_HEIGHT * t * (JUMP_TIME - t) / (JUMP_TIME * JUMP_TIME)
	r.position.y = r.get_meta("ground") - lift
