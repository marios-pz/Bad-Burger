extends Control
## Main menu. Four pages share the same table background:
## "click to eat" title, the main buttons, help and credits.

const RUNNERS := 7
const RUN_SPEED := 300.0  # pixels per second
const JUMP_TIME := 0.7
const JUMP_HEIGHT := 192.0
const SHOWCASE := [["player_walk_down", false, 0.0], ["player_walk_side", false, 90.0],
	["player_walk_up", false, 180.0], ["player_walk_side", true, -90.0]]

var runners: Array[AnimatedSprite2D] = []
var logo: TextureRect
var title_page: Control
var main_page: Control
var help_page: Control
var credits_page: Control
var sound_buttons: Control
var showcase: AnimatedSprite2D
var arrow: Sprite2D
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
	add_child(sound_buttons)
	_sound_button(Vector2(G.W - 35, 5), "music")
	_sound_button(Vector2(G.W - 67, 4), "sfx")

	title_page = _page()
	G.button(title_page, Rect2(235, 295, 170, 40), "click to eat", 30, _open_main)

	main_page = _page()
	G.button(main_page, Rect2(270, 295, 100, 40), "play", 30, G.go.bind("level_select"))
	G.button(main_page, Rect2(265, 340, 110, 40), "help", 30, _show.bind("help"))
	G.button(main_page, Rect2(250, 385, 140, 40), "credits", 30, _show.bind("credits"))
	G.button(main_page, Rect2(270, 430, 100, 40), "quit", 30, get_tree().quit)

	credits_page = _page()
	G.image(credits_page, "credits_bg", Rect2(0, 0, 640, 464))
	var line_h := 30
	var top := 50 + (380 - line_h * G.CREDITS.size()) / 2
	for i in G.CREDITS.size():
		G.label(credits_page, G.CREDITS[i], 30, Rect2(0, top + i * line_h, G.W, line_h))
	G.button(credits_page, Rect2(270, 350, 100, 40), "back", 30, _show.bind("main"))

	help_page = _page()
	G.image(help_page, "credits_bg", Rect2(0, 0, 640, 464))
	G.image(help_page, "panel_bg", Rect2(160, 94, 320, 232))
	G.label(help_page, "moving", 40, Rect2(0, 155, G.W, 45))
	G.label(help_page, "arrows or wasd: move\nspace: make or break ice", 15,
		Rect2(212, 246, 216, 52))
	showcase = AnimatedSprite2D.new()
	showcase.sprite_frames = G.FRAMES
	showcase.position = Vector2(G.W / 2.0, 216)
	help_page.add_child(showcase)
	arrow = Sprite2D.new()
	arrow.texture = G.tex("arrow")
	arrow.scale = Vector2(2, 2)
	arrow.position = Vector2(350, 215)
	help_page.add_child(arrow)
	G.button(help_page, Rect2(270, 350, 100, 40), "back", 30, _show.bind("main"))
	# Two empty buns next to "back", kept from the original layout.
	G.button(help_page, Rect2(220, 350, 40, 40))
	G.button(help_page, Rect2(380, 350, 40, 40))

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
		arrow.rotation_degrees = step[2]


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and (help_page.visible or credits_page.visible):
		_show("main")


func _page() -> Control:
	var page := Control.new()
	page.size = size
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(page)
	return page


func _show(page: String) -> void:
	title_page.visible = page == "title"
	main_page.visible = page == "main"
	help_page.visible = page == "help"
	credits_page.visible = page == "credits"
	sound_buttons.visible = page in ["title", "main"]


func _open_main() -> void:
	G.menu_opened = true
	_show("main")


func _sound_button(pos: Vector2, kind: String) -> void:
	var b := TextureButton.new()
	b.position = pos
	sound_buttons.add_child(b)
	var refresh := func():
		var on: bool = G.music_on if kind == "music" else G.sfx_on
		b.texture_normal = G.tex("%s_%s" % [kind, "on" if on else "off"])
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
