import pygame
import random
import os
import time
import json
import threading
import urllib.error
import urllib.request

class ArcadeApiClient:
	def __init__(self):
		self.base_url = os.environ.get(
			"GPI_LAUNCHER_ARCADE_API_URL", "http://127.0.0.1:5055/api/v1"
		).rstrip("/")
		self.enabled = os.environ.get("GPI_LAUNCHER_CREDIT_MODE", "").lower() == "arcade"
		self._continue_granted = threading.Event()
		self._stop = threading.Event()

		if self.enabled:
			self._thread = threading.Thread(target=self._listen_for_events, daemon=True)
			self._thread.start()
		else:
			self._thread = None

	def close(self):
		self._stop.set()

	def get_credits(self):
		if not self.enabled:
			return 1

		try:
			with urllib.request.urlopen(f"{self.base_url}/credits", timeout=0.4) as response:
				payload = json.loads(response.read().decode("utf-8"))
				return int(payload.get("credits", 0))
		except (OSError, ValueError, urllib.error.URLError):
			return 0

	def spend_credit(self, amount=1):
		if not self.enabled:
			return True

		payload = self._post("/credits/spend", {"amount": amount})
		return bool(payload and payload.get("ok"))

	def request_continue(self, max_credits=1):
		if not self.enabled:
			self._continue_granted.set()
			return True

		payload = self._post("/continue/request", {"maxCredits": max_credits})
		return bool(payload and payload.get("ok"))

	def consume_continue_granted(self):
		if not self._continue_granted.is_set():
			return False

		self._continue_granted.clear()
		return True

	def _post(self, path, payload):
		request = urllib.request.Request(
			f"{self.base_url}{path}",
			data=json.dumps(payload).encode("utf-8"),
			headers={"Content-Type": "application/json"},
			method="POST",
		)

		try:
			with urllib.request.urlopen(request, timeout=0.5) as response:
				return json.loads(response.read().decode("utf-8"))
		except urllib.error.HTTPError as error:
			try:
				return json.loads(error.read().decode("utf-8"))
			except (OSError, ValueError):
				return None
		except (OSError, ValueError, urllib.error.URLError):
			return None

	def _listen_for_events(self):
		while not self._stop.is_set():
			try:
				request = urllib.request.Request(
					f"{self.base_url}/events", headers={"Accept": "text/event-stream"}
				)
				with urllib.request.urlopen(request, timeout=10) as response:
					event_name = "message"
					data_lines = []

					for raw_line in response:
						if self._stop.is_set():
							return

						line = raw_line.decode("utf-8").strip()
						if not line:
							self._handle_event(event_name, "\n".join(data_lines))
							event_name = "message"
							data_lines = []
							continue

						if line.startswith(":"):
							continue
						if line.startswith("event:"):
							event_name = line[6:].strip()
						elif line.startswith("data:"):
							data_lines.append(line[5:].strip())
			except (OSError, urllib.error.URLError):
				if not self._stop.is_set():
					time.sleep(1)

	def _handle_event(self, event_name, data):
		if event_name == "continueAccepted":
			self._continue_granted.set()

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
running_game = False
exit_game = False
dt = 0
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

#ZMIENNE DO API
session_active = False
waiting_for_credit = False
continue_requested = False
#ZMIENNE DO API

SCORE = 0
LIFE = 3
LIFE_UP_COUNTER = 0
LEVEL = 1
COMBO = 0
bricks_no_damaged = []
bricks_damaged = []
for i in range(len(os.listdir("assets/bricks_no_damage"))):
    bricks_no_damaged.append(pygame.image.load(f"assets/bricks_no_damage/lvl{i}.png"))

for i in range(len(os.listdir("assets/bricks_damage"))):
    bricks_damaged.append(pygame.image.load(f"assets/bricks_damage/damaged_lvl{i}.png"))

obraz = pygame.image.load("heart.png").convert_alpha()
obraz = pygame.transform.scale(obraz, (30, 30))
colors = [ (0, 129, 72), #zielony
           (8, 117, 82),
           (17, 106, 93),
           (25, 94, 103),
           (33, 82, 113),
           (42, 71, 124),
           (50, 59, 134)] #niebieski

y = screen.get_height()
x = screen.get_width()

#paddle parameters
paddle_width = 150
paddle_height = 20

#ball parameters
ballSpeed_x = 0.0
ballSpeed_y = 0.0

#brick parameters
first_brick_x = 85
first_brick_y = 60
brick_width = 100
brick_height = 30
brick_padding = 10 #łącznie 90

ball_radius = 20
paddle = pygame.Rect(x/2 - 75, y - 30, paddle_width, paddle_height)
ball = pygame.Rect(x/2 - ball_radius/2, y - 30 -ball_radius,ball_radius, ball_radius)
wall_left = pygame.Rect(0,0,10,y)
wall_right = pygame.Rect(x-10,0,10,y)
wall_up = pygame.Rect(10,0,x-20,10)
pygame.display.set_caption("Arcanoid")

score_font = pygame.font.Font("PressStart2P-Regular.ttf", 30)
start_font = pygame.font.Font("PressStart2P-Regular.ttf", 20)

dzwiek_odbicia = pygame.mixer.Sound("ball.wav")
notofication = pygame.mixer.Sound("notification.wav")

def generate_bricks():
    iterator = 0
    _bricks = []
    _bricks_lvl_matrix = []
    _brick_hit_counter = []
    for i in range(7):
        brick_layer = [pygame.Rect(first_brick_x + j * (brick_width + brick_padding),
                                   first_brick_y + i * (brick_height + brick_padding),
                                   brick_width, brick_height) for j in range(10)]
        bricks_lvl_matrix_layer = [1 for _ in range(10)]
        brick_hit_counter_layer = [0 for _ in range(10)]
        _bricks.append(brick_layer)
        _bricks_lvl_matrix.append(bricks_lvl_matrix_layer)
        _brick_hit_counter.append(brick_hit_counter_layer)


    while iterator < LEVEL * 10:
        if (LEVEL >= 63):
            for m in range(len(_bricks_lvl_matrix)):
                for n in range(len(_bricks_lvl_matrix[m])):
                    _bricks_lvl_matrix[m][n] = 10
            break

        k = random.randint(0,6)
        l = random.randint(0,9)
        if _bricks_lvl_matrix[k][l] < 10:
            _bricks_lvl_matrix[k][l] += 1
            iterator += 1
    return _bricks, _bricks_lvl_matrix, _brick_hit_counter

bricks, bricks_lvl_matrix, brick_hit_counter = generate_bricks()

def ball_brick_side_collision(ball, brick, _ballSpeed_x, _ballSpeed_y):
    overlap_left = ball.right - brick.left
    overlap_right = brick.right - ball.left
    overlap_top = ball.bottom - brick.top
    overlap_bottom = brick.bottom - ball.top

    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

    if min_overlap == overlap_top:
        _ballSpeed_y = -abs(_ballSpeed_y)  # Odbicie w górę
    elif min_overlap == overlap_bottom:
        _ballSpeed_y = abs(_ballSpeed_y)  # Odbicie w dół
    elif min_overlap == overlap_left:
        _ballSpeed_x = -abs(_ballSpeed_x)  # Odbicie w lewo
    elif min_overlap == overlap_right:
        _ballSpeed_x = abs(_ballSpeed_x)  # Odbicie w prawo

    return _ballSpeed_x, _ballSpeed_y

def ball_paddle_start():
    ball.x = x / 2 - ball_radius / 2
    ball.y = y - 30 - ball_radius
    paddle.x = x / 2 - 75
    paddle.y = y - 30

wider_paddle_enabled = False
def wider_paddle_powerup():
    start_powerup = time.time()
    paddle.width += 100
    return start_powerup, True
def wider_paddle_stop():
    paddle.width -= 100
    return False

more_balls = False
def more_balls_powerup(current_ballx,current_bally):
    ball1 = pygame.Rect(current_ballx, current_bally, ball_radius, ball_radius)
    ball2 = pygame.Rect(current_ballx, current_bally, ball_radius, ball_radius)

def request_launcher_continue():
    global running_game, waiting_for_credit, continue_requested

    if continue_requested:
        return

    running_game = False
    waiting_for_credit = True
    continue_requested = True
    arcade_api.request_continue(max_credits=0)


def start_session_with_credit():
    global running_game, session_active
    global waiting_for_credit, continue_requested
    global ballSpeed_x, ballSpeed_y

    if arcade_api.spend_credit(1):
        session_active = True
        waiting_for_credit = False
        continue_requested = False
        running_game = True

        # Uruchom piłkę przy rozpoczęciu sesji.
        if ballSpeed_x == 0 and ballSpeed_y == 0:
            ballSpeed_y = -5
    else:
        request_launcher_continue()

arcade_api = ArcadeApiClient()
print("Arcade mode:", arcade_api.enabled)
print("API URL:", arcade_api.base_url)
while running:
    if waiting_for_credit and arcade_api.consume_continue_granted():
        continue_requested = False
        start_session_with_credit()
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and exit_game:
            running = False

    screen.fill("black")

    pygame.draw.rect(screen, "red", ball, border_radius = 15)
    pygame.draw.rect(screen, "blue", paddle,border_radius=10)
    for i in range(len(bricks)):
        for j in range(len(bricks[i])):
            if bricks[i][j]:
                if(brick_hit_counter[i][j]<=0):
                    screen.blit(bricks_no_damaged[bricks_lvl_matrix[i][j]-1],bricks[i][j])
                else:
                    screen.blit(bricks_damaged[bricks_lvl_matrix[i][j]-1],bricks[i][j])
                #pygame.draw.rect(screen,colors[i] if bricks_lvl_matrix[i][j] <= 1 else "yellow", bricks[i][j])
            if bricks[i][j] and ball.colliderect(bricks[i][j]):
                if (paddle.width <= 150 and (random.randint(0,100)<=5)):
                    wider_paddle_timer, wider_paddle_enabled = wider_paddle_powerup()
                COMBO += 1
                dzwiek_odbicia.play()
                ballSpeed_x,ballSpeed_y = ball_brick_side_collision(ball,bricks[i][j],ballSpeed_x,ballSpeed_y)
                brick_hit_counter[i][j] += 1
                if(bricks_lvl_matrix[i][j] == brick_hit_counter[i][j]):
                    SCORE += 100 * bricks_lvl_matrix[i][j] + (COMBO * 50)
                    LIFE_UP_COUNTER += 100 * bricks_lvl_matrix[i][j] + (COMBO * 50)
                    bricks[i][j] = None
                    bricks_lvl_matrix[i][j] = 0

    keys = pygame.key.get_pressed()
    text_score = score_font.render(f"SCORE {SCORE}", True, (255, 255, 255))
    text_level = score_font.render(f"LEVEL {LEVEL}", True, (255, 255, 255))
    text_life = score_font.render("LIFE ", True, (255, 255, 255))
    lives = score_font.render(f"x{LIFE} ", True, (255, 255, 255))
    screen.blit(text_score, (5, 5))
    screen.blit(text_level, (x/2 - 100, 10))
    if (LIFE<=3):
        screen.blit(text_life, (1050, 5))
        for i in range(LIFE):
            screen.blit(obraz, (1175+i*35, 4))
    else:
        screen.blit(text_life, (1000, 5))
        screen.blit(lives, (1150, 5))
        screen.blit(obraz, (1240, 4))

    if (LIFE_UP_COUNTER >= 10000):
        LIFE += int(LIFE_UP_COUNTER/10000)
        LIFE_UP_COUNTER -= 10000

    text_combo = score_font.render(f"COMBO x{COMBO} ", True, (255, 255, 255))
    if (COMBO>1):
        screen.blit(text_combo, (40, 570))

    # GAME START STOP
    if running_game == False and not exit_game and LIFE>=1:
        #screen.blit(start_font.render("Press Space to start", True, (255, 255, 255)), (x/2 - 200, y/2))
        if not session_active and not exit_game and LIFE >= 1:
            if waiting_for_credit:
                message = "Waiting for coin"
            else:
                message = "Press Space to start"

            screen.blit(
                start_font.render(message, True, (255, 255, 255)),
                (x / 2 - 200, y / 2)
            )

    if all(brick == 0 for layer in bricks_lvl_matrix for brick in layer):
        notofication.play()
        LEVEL += 1
        ballSpeed_y = 0
        ballSpeed_x = 0
        ball_paddle_start()
        running_game = False
        bricks, bricks_lvl_matrix, brick_hit_counter = generate_bricks()

    ## SCREEN MANAGEMENT
    if keys[pygame.K_RETURN]:
        screen = pygame.display.set_mode(
            (1280, 720),
            pygame.FULLSCREEN | pygame.SCALED
        )
    if keys[pygame.K_ESCAPE]:
        screen = pygame.display.set_mode((1280, 720))

    ## PADDLE MOVEMENT
    if running_game:
        if keys[pygame.K_a]:
            #player_pos.x -= 300 * dt
            if paddle.x > 10:
                paddle.x -= 500 * dt
        if keys[pygame.K_d]:
            if paddle.x < x-paddle.width-10:
                paddle.x += 500 * dt

    ## BALL MOVEMENT
    if keys[pygame.K_SPACE] and not exit_game:
        if session_active:
            running_game = True
            if ballSpeed_x==0 and ballSpeed_y==0:
                ballSpeed_y = -5
        elif not waiting_for_credit:
            # Nowa sesja wymaga jednego kredytu.
            start_session_with_credit()

    if ball.colliderect(paddle):
        COMBO = 0
        dzwiek_odbicia.play()
        if ball.centerx == paddle.x:
            ballSpeed_y = -abs(ballSpeed_y)
        else:
            ballSpeed_y = -abs(ballSpeed_y)
            ballSpeed_x = (2 * abs((ball.x + 75 - paddle.x + 75)/(paddle_width/2))) * abs(ballSpeed_x+0.00001)/(ballSpeed_x+0.00001)

    if ball.centery > paddle.y:
        ballSpeed_y = 0
        ballSpeed_x = 0
        ball_paddle_start()
        LIFE -= 1
        running_game = False

    #ball gameboard movement
    ball.y += ballSpeed_y
    ball.x += ballSpeed_x
    if ball.colliderect(wall_left):
        ballSpeed_x = abs(ballSpeed_x)
        dzwiek_odbicia.play()
    if ball.colliderect(wall_right):
        ballSpeed_x = -abs(ballSpeed_x)
        dzwiek_odbicia.play()
    if ball.colliderect(wall_up):
        ballSpeed_y = abs(ballSpeed_y)
        dzwiek_odbicia.play()

    if (LIFE <= 0):
        ballSpeed_y = 0
        ballSpeed_x = 0
        ball_paddle_start()
        screen.blit(start_font.render("Game Over!", True, (255, 255, 255)), (x / 2 - 100, y / 2))
        screen.blit(start_font.render("Press any button to leave", True, (255, 255, 255)), (x / 2 - 230, y / 2 + 30))
        running_game = False
        exit_game = True
        session_active = False


    #POWERUP MANAGEMENT
    if(wider_paddle_enabled):
        stop_powerup = time.time()
        if (stop_powerup - wider_paddle_timer >= 10):
            wider_paddle_enabled = wider_paddle_stop()
        wider_paddle_notification = start_font.render(f"Wider paddle {10 - round(stop_powerup - wider_paddle_timer)}", True, (255, 255, 255))
        screen.blit(wider_paddle_notification, (40, 500))

    pygame.display.flip()
    dt = clock.tick(60) / 1000

arcade_api.close()
pygame.quit()