import pygame
from constants import (
    WIDTH, HEIGHT,
    TITLE_START_BTN, TITLE_LEADERBOARD_BTN, TITLE_HOWTOPLAY_BTN,
    LEADERBOARD_BACK_BTN, HOWTOPLAY_BACK_BTN
)
import assets
import state
from state import trigger_screen_shake, update_screen_shake

def draw_title_screen(screen=None):
    if screen is None:
        screen = pygame.display.get_surface()
    if screen and assets.TITLE_BG_IMAGE:
        screen.blit(assets.TITLE_BG_IMAGE, (0, 0))
    if screen and assets.TITLE_MENU_SURFACE:
        screen.blit(assets.TITLE_MENU_SURFACE, (WIDTH // 2 - 150, 300))
    if screen and assets.TITLE_START_TEXT:
        screen.blit(assets.TITLE_START_TEXT, (WIDTH // 2 - assets.TITLE_START_TEXT.get_width() // 2, 320))
        screen.blit(assets.TITLE_LEADERBOARD_TEXT, (WIDTH // 2 - assets.TITLE_LEADERBOARD_TEXT.get_width() // 2, 370))
        screen.blit(assets.TITLE_HOWTOPLAY_TEXT, (WIDTH // 2 - assets.TITLE_HOWTOPLAY_TEXT.get_width() // 2, 420))
    return TITLE_START_BTN, TITLE_LEADERBOARD_BTN, TITLE_HOWTOPLAY_BTN

def draw_leaderboard(screen=None):
    if screen is None:
        screen = pygame.display.get_surface()
    if screen and assets.TITLE_BG_IMAGE:
        screen.blit(assets.TITLE_BG_IMAGE, (0, 0))

    panel_rect = pygame.Rect(WIDTH // 2 - 310, 100, 620, 340)
    if screen and assets.LEADERBOARD_PANEL_SURFACE:
        screen.blit(assets.LEADERBOARD_PANEL_SURFACE, panel_rect.topleft)

    label_font = assets.CUSTOM_FONT_BOLD or pygame.font.Font(None, 18)
    entry_font = assets.CUSTOM_FONT_REGULAR or pygame.font.Font(None, 16)
    small_font = assets.CUSTOM_FONT_SMALL or pygame.font.Font(None, 12)
    white = (255, 255, 255)
    yellow = (255, 220, 100)

    if screen:
        leaderboard_title = label_font.render("LEADERBOARD:", True, white)
        screen.blit(leaderboard_title, (WIDTH // 2 - leaderboard_title.get_width() // 2, 120))

        rank_text = small_font.render("RANK", True, white)
        name_text = small_font.render("NAME", True, white)
        wave_text = small_font.render("TOTAL WAVE", True, white)
        screen.blit(rank_text, (panel_rect.x + 60, 170))
        screen.blit(name_text, (panel_rect.x + 200, 170))
        screen.blit(wave_text, (panel_rect.x + 400, 170))

    if assets.cached_leaderboard is None:
        assets.refresh_leaderboard_data()

    if screen:
        if not assets.cached_leaderboard:
            no_scores_text = label_font.render("No scores yet!", True, (200, 200, 200))
            screen.blit(no_scores_text, (WIDTH // 2 - no_scores_text.get_width() // 2, HEIGHT // 2 - 20))
        else:
            start_y = 210
            for i, entry in enumerate(assets.cached_leaderboard[:5], start=1):
                name = entry[0]
                wave = entry[1]
                color = yellow if i == 1 else white

                rank_render = entry_font.render(f"{i}", True, color)
                name_render = entry_font.render(f"{name}", True, color)
                wave_render = entry_font.render(f"Wave {wave}", True, color)

                screen.blit(rank_render, (panel_rect.x + 80, start_y))
                screen.blit(name_render, (panel_rect.x + 200, start_y))
                screen.blit(wave_render, (panel_rect.x + 400, start_y))
                
                if i == 1 and assets.CROWN_IMAGE:
                    crown_x = panel_rect.x + 200 + name_render.get_width() + 10
                    crown_y = start_y + (name_render.get_height() - assets.CROWN_IMAGE.get_height()) // 2
                    screen.blit(assets.CROWN_IMAGE, (crown_x, crown_y))
                
                start_y += 45

        if assets.BACK_BUTTON_SURFACE:
            screen.blit(assets.BACK_BUTTON_SURFACE, LEADERBOARD_BACK_BTN.topleft)

        back_text = label_font.render("BACK TO MENU", True, white)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 432))

    return LEADERBOARD_BACK_BTN

def draw_how_to_play(screen=None):
    if screen is None:
        screen = pygame.display.get_surface()
    if screen and assets.TITLE_BG_IMAGE:
        screen.blit(assets.TITLE_BG_IMAGE, (0, 0))

    if screen and assets.HOWTOPLAY_PANEL_SURFACE:
        screen.blit(assets.HOWTOPLAY_PANEL_SURFACE, (WIDTH // 2 - 350, 80))

    if screen and assets.HOWTOPLAY_TITLE_TEXT:
        screen.blit(assets.HOWTOPLAY_TITLE_TEXT, (WIDTH // 2 - assets.HOWTOPLAY_TITLE_TEXT.get_width() // 2, 100))

    if screen:
        y = 180
        for text in assets.HOWTOPLAY_INSTRUCTION_TEXTS:
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 40

        if assets.HOWTOPLAY_BACK_BTN_SURFACE:
            screen.blit(assets.HOWTOPLAY_BACK_BTN_SURFACE, HOWTOPLAY_BACK_BTN.topleft)

        if assets.HOWTOPLAY_BACK_TEXT:
            screen.blit(assets.HOWTOPLAY_BACK_TEXT, (WIDTH // 2 - assets.HOWTOPLAY_BACK_TEXT.get_width() // 2, 450))

    return HOWTOPLAY_BACK_BTN

def draw_name_entry(screen=None):
    if screen is None:
        screen = pygame.display.get_surface()
    if not screen:
        return pygame.Rect(0, 0, 0, 0), pygame.Rect(0, 0, 0, 0)

    screen.fill((20, 20, 30))
    
    title_font = assets.CUSTOM_FONT_TITLE or pygame.font.Font(None, 32)
    score_font = assets.CUSTOM_FONT_BOLD or pygame.font.Font(None, 18)
    name_font = assets.CUSTOM_FONT_REGULAR or pygame.font.Font(None, 16)
    instr_font = assets.CUSTOM_FONT_SMALL or pygame.font.Font(None, 12)
    
    title_text = title_font.render("GAME OVER", True, (255, 50, 50))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
    
    wave_text = score_font.render(f"Wave Reached: {state.final_wave}", True, (255, 255, 255))
    score_text = score_font.render(f"Final Score: {state.final_score}", True, (255, 255, 255))
    
    screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, 150))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 200))
    
    prompt_text = name_font.render("Enter your name:", True, (200, 200, 255))
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, 270))
    
    input_box = pygame.Rect(WIDTH // 2 - 200, 320, 400, 60)
    pygame.draw.rect(screen, (50, 50, 70), input_box, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 200), input_box, 3, border_radius=10)
    
    name_surface = name_font.render(state.player_name, True, (255, 255, 255))
    screen.blit(name_surface, (input_box.x + 20, input_box.y + 15))
    
    if pygame.time.get_ticks() % 1000 < 500:
        cursor_x = input_box.x + 20 + name_surface.get_width() + 2
        pygame.draw.line(screen, (255, 255, 255), (cursor_x, input_box.y + 15), 
                         (cursor_x, input_box.y + input_box.height - 15), 3)
    
    submit_button = pygame.Rect(WIDTH // 2 - 100, 410, 200, 50)
    submit_color = (50, 150, 50) if len(state.player_name) > 0 else (80, 80, 80)
    pygame.draw.rect(screen, submit_color, submit_button, border_radius=10)
    pygame.draw.rect(screen, (100, 255, 100) if len(state.player_name) > 0 else (120, 120, 120), 
                     submit_button, 3, border_radius=10)
    
    submit_text = name_font.render("SUBMIT", True, (255, 255, 255))
    screen.blit(submit_text, (submit_button.centerx - submit_text.get_width() // 2, 
                             submit_button.centery - submit_text.get_height() // 2))
    
    instr_text = instr_font.render("Press ENTER to submit, BACKSPACE to delete", True, (150, 150, 150))
    screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, 480))
    
    return input_box, submit_button
