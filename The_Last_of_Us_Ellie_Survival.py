import random
from sys import exit
import pygame.time
from pygame import K_RIGHT, K_LEFT
import math

scale = [500, 200]

def save_highscore(highscore):
    with open("Save Games/highscore.txt", "w") as file:
        fetched_highscore = file.write(str(highscore))

    return fetched_highscore

def read_highscore():
    with open("Save Games/highscore.txt", "r") as file:
        saved_highscore = str(file.read())

        if not saved_highscore:
            saved_highscore = 0

        return int(saved_highscore)

def get_sine_speed(base_speed, score, period=50, amplitude=1.3):
    sine_value = math.sin(3 * math.pi * score / period)
    normalized_sine = (sine_value + 4)
    speed_factor = 1 + amplitude * (normalized_sine - 2.5)

    return base_speed * speed_factor

# Create temporary rects with scaling applied for collision detection
def get_scaled_rect(rect):
    return pygame.Rect(
        rect.x + scale[0],
        rect.y + scale[1],
        rect.width,
        rect.height
    )


def get_direction(sprite_rect, speed, time):
    # Create direction state object if not present as an attribute
    if not hasattr(get_direction, "moving_left"):
        get_direction.moving_left = False

    just_bounced = False

    # Check boundaries and update direction
    if sprite_rect.x <= 300:
        sprite_rect.x = 300

        if get_direction.moving_left:
            get_direction.moving_left = False
            just_bounced = True

    elif sprite_rect.x >= 900:
        sprite_rect.x = 900

        if not get_direction.moving_left:
            get_direction.moving_left = True
            just_bounced = True

    # Move based on direction
    if get_direction.moving_left:
        sprite_rect.x -= speed * time

    else:
        sprite_rect.x += speed * time

    return {
        'moving_left': get_direction.moving_left,
        'just_bounced': just_bounced
    }

def main():
    # For window scaling
    window_scale = [1120, 620]
    global scale
    sprite_scale = [window_scale[0] * 2, window_scale[1] * 2.6]

    # Initialize Pygame and the mixer for sounds
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # Window setup
    screen = pygame.display.set_mode((1930, 1050))
    pygame.display.set_caption("The Last of Us Ellie Survival")

    # Window icon
    icon = pygame.image.load("Graphics/icon.ico")
    pygame.display.set_icon(icon)

    # Clock for frame rate control
    clock = pygame.time.Clock()

    # Load score text font
    score = 0
    score_font = pygame.font.Font(None, 96)

    # Load images
    sky = pygame.image.load("Graphics/background.jpg").convert_alpha()
    sky_scaled = pygame.transform.scale(sky, (sprite_scale[0], sprite_scale[1]))

    death = pygame.image.load("Graphics/death.png").convert_alpha()
    death_scaled = pygame.transform.scale(death, (2000, 1000))

    # Load surfaces
    border = pygame.Surface((5, window_scale[0]))
    border.fill("#2d541e")

    rat_king_boss_health_bar = pygame.Surface((200,50))
    rat_king_boss_health_bar.fill("red")

    # Fonts and text
    game_over_font = pygame.font.Font(None, 80)
    game_over_text = game_over_font.render("You Died", False, "blue")
    death_text = game_over_font.render("Game over", False, "red")

    restart_button = pygame.Surface((800 + window_scale[0], 50))
    restart_button.fill("violet")
    restart_button_text = game_over_font.render("Press space to restart", False, "red")

    # Sounds
    bg_music = pygame.mixer.Sound("Sounds/bg_music.mp3")
    bg_music.set_volume(0.25)

    menu_music = pygame.mixer.Sound("Sounds/menu_music.mp3")
    menu_music.set_volume(1.5)

    death_sound = pygame.mixer.Sound("Sounds/death_sound.mp3")
    death_sound.set_volume(0.25)

    # Player setup
    ellie = pygame.image.load("Graphics/ellie.png").convert_alpha()
    ellie_rect = ellie.get_rect(midbottom=(1011, 1030))

    # Enemy setup
    runner = pygame.image.load("Graphics/runner.png").convert_alpha()
    runner_rect = runner.get_rect(midbottom=(random.randint(50, 750), 0))

    stalker = pygame.image.load("Graphics/stalker.png").convert_alpha()
    stalker_rect = stalker.get_rect(midbottom=(random.randint(50, 750), 0))

    clicker = pygame.image.load("Graphics/clicker.png").convert_alpha()
    clicker_rect = clicker.get_rect(midbottom=(random.randint(50, 750), 0))

    shambler = pygame.image.load("Graphics/shambler.png").convert_alpha()
    shambler_rect = shambler.get_rect(midbottom=(random.randint(50, 750), 0))

    bloater = pygame.image.load("Graphics/bloater.png").convert_alpha()
    bloater_rect = bloater.get_rect(midbottom=(random.randint(50, 750), 0))

    rat_king_boss = pygame.image.load("Graphics/rat_king.png").convert_alpha()
    rat_king_boss_rect = rat_king_boss.get_rect(midbottom=(random.randint(50, 750), 400))

    # Game variables
    game_active = True

    #last_multiple_of_10 = 0  # Track the last multiple of 10 for which speeds were increased
    high_score = read_highscore()

    # Main game loop
    while True:
        # Calculate delta time (time since last frame in seconds)
        delta_time = clock.tick(60) / 1000  # 60 FPS cap, convert milliseconds to seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Reset once game restarts
            if not game_active and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                score = 0

                # Reset player and enemy positions
                ellie_rect.x = 370  # Reset player position
                runner_rect.y = -100  # Reset enemy position
                stalker_rect.y = -100  # Reset enemy position
                clicker_rect.y = -100  # Reset enemy position
                shambler_rect.y = -100  # Reset enemy position
                bloater_rect.y = -100  # Reset enemy position

                # Set a new random X position for the enemy
                runner_rect.x = random.randint(50, 750)
                stalker_rect.x = random.randint(50, 750)
                clicker_rect.x = random.randint(50, 750)
                shambler_rect.x = random.randint(50, 750)
                bloater_rect.x = random.randint(50, 750)

        if game_active:

            #
            # Score logic
            #

            if score < 5:
                # Reset the speed
                runner_speed = 250
                stalker_speed = 225
                clicker_speed = 275
                shambler_speed = 200
                bloater_speed = 175
                player_speed = 200
            else:
                runner_speed = get_sine_speed(250, score)
                stalker_speed = get_sine_speed(225, score)
                clicker_speed = get_sine_speed(275, score)
                shambler_speed = get_sine_speed(200, score)
                bloater_speed = get_sine_speed(175, score)
                player_speed = get_sine_speed(200, score)

            # working on a boss battle
            #if score % 10 == 0:
            #    screen.blit(rat_king_boss, (rat_king_boss_rect.x, rat_king_boss_rect.y))
            #    screen.blit(rat_king_boss_health_bar, (0, window_scale[0]))

            # Update and load the score text
            score_text = score_font.render(f"Score: {score}", False, "cyan")

            # Update the highscore if necessary
            if high_score < score:
                high_score = score
                save_highscore(high_score)

            #
            # Display logic
            #

            # Draw the game elements
            screen.blit(sky_scaled, (0, -300))  # Draw the sky (500, 200)
            screen.blit(ellie, (ellie_rect.x, ellie_rect.y))  # Draw the player

            # Draw the enemy
            screen.blit(runner, (runner_rect.x + scale[0], runner_rect.y + scale[1]))
            screen.blit(stalker, (stalker_rect.x + scale[0], stalker_rect.y + scale[1]))
            screen.blit(clicker, (clicker_rect.x + scale[0], clicker_rect.y + scale[1]))
            screen.blit(shambler, (shambler_rect.x + scale[0], shambler_rect.y + scale[1]))
            screen.blit(bloater, (bloater_rect.x + scale[0], bloater_rect.y + scale[1]))

            # border displays
            screen.blit(border, (550, 0))
            screen.blit(border, (1350, 0))

            # Play the background music
            menu_music.stop()
            bg_music.play(-1)  # The -1 parameter makes the music loop indefinitely

            # Display the score
            screen.blit(score_text, (50, 50))

            #
            # Move the enemy logic
            #

            rat_king_boss_speed = 175

            runner_rect.y += runner_speed * delta_time
            stalker_rect.y += stalker_speed * delta_time
            clicker_rect.y += clicker_speed * delta_time
            shambler_rect.y += shambler_speed * delta_time
            bloater_rect.y += bloater_speed * delta_time
            rat_king_boss_rect.y += rat_king_boss_speed * delta_time

            # Reset enemy position when it goes off-screen
            spawn_point = -300

            if runner_rect.y >= 1013:
                runner_rect.y = spawn_point  # Reset Y position
                runner_rect.x = random.randint(50, 750)  # Set a new random X position
                score += 1

            if stalker_rect.y >= 1050:
                stalker_rect.y = spawn_point  # Reset Y position
                stalker_rect.x = random.randint(50, 750)  # Set a new random X position
                score += 1

            if clicker_rect.y >= 1050:
                clicker_rect.y = spawn_point  # Reset Y position
                clicker_rect.x = random.randint(50, 750)  # Set a new random X position
                score += 1

            if shambler_rect.y >= 1050:
                shambler_rect.y = spawn_point  # Reset Y position
                shambler_rect.x = random.randint(50, 750)  # Set a new random X position
                score += 1

            if bloater_rect.y >= 1050:
                bloater_rect.y = spawn_point  # Reset Y position
                bloater_rect.x = random.randint(50, 750)  # Set a new random X position
                score += 1

            if rat_king_boss_rect.y >= 1050:
                rat_king_boss_rect.y = -400
                rat_king_boss_rect.x = random.randint(50, 750)

            # Check if score is between X00 and X50 for any X >= 1
            #boss_active = (score >= 100 and score % 100 < 50 and score // 100 >= 1)

            #if boss_active:
            #    screen.blit(rat_king_boss, (rat_king_boss_rect.x, rat_king_boss_rect.y))
            #    screen.blit(rat_king_boss_health_bar, (1700, 50))
            #    get_direction(rat_king_boss_rect, rat_king_boss_speed, delta_time)

            # Set the player boundaries
            if ellie_rect.x <= 550:
                ellie_rect.x = 550

            if ellie_rect.x >= 1300:
                ellie_rect.x = 1300

            #
            # Key pressing logic
            #

            # Get the state of all keys
            keys = pygame.key.get_pressed()

            # Move the player based on delta time
            if keys[pygame.K_d] or keys[K_RIGHT]:
                ellie_rect.x += player_speed * delta_time  # Move right

            if keys[pygame.K_a] or keys[K_LEFT]:
                ellie_rect.x -= player_speed * delta_time  # Move left

            #
            # Collision logic
            #

            if (ellie_rect.colliderect(get_scaled_rect(runner_rect)) or
                ellie_rect.colliderect(get_scaled_rect(stalker_rect)) or
                ellie_rect.colliderect(get_scaled_rect(clicker_rect)) or
                ellie_rect.colliderect(get_scaled_rect(shambler_rect)) or
                ellie_rect.colliderect(get_scaled_rect(bloater_rect))): #or
                #boss_active and ellie_rect.colliderect(get_scaled_rect(rat_king_boss_rect)))):

                # Stop the background music and play the death sound
                bg_music.stop()
                death_sound.play()

                # Display the death screen
                screen.fill("black")
                screen.blit(death_scaled, (0, 0))
                screen.blit(death_text, (100, 50))

                # Update the display to show the death screen
                pygame.display.flip()
                pygame.time.wait(2000)

                game_active = False

        else:

            #
            # Display logic
            #

            # Game over state
            screen.fill("red")  # Clear the screen with red
            screen.blit(game_over_text, (350 + scale[0], 50 + scale[1]))  # Draw game over text
            screen.blit(restart_button, (0, 150 + scale[1]))  # Draw restart button
            screen.blit(restart_button_text, (250 + scale[0], 150 + scale[1]))  # Draw restart button text
            menu_music.play(-1)  # Play the music continuously

            # Show the final score
            final_score = score_font.render(f"Your final score was: {score}", False, "cyan")
            screen.blit(final_score, (225 + scale[0], 250 + scale[1]))

            # Show the high score
            highest_score = score_font.render(f"High score: {high_score}", False, "purple")
            screen.blit(highest_score, (300 + scale[0], 350 + scale[1]))

        # Update the display
        pygame.display.update()

if __name__ == "__main__":
    main()