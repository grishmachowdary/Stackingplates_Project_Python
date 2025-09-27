if current_screen == "name_prompt":
        draw_text_center("Enter Your Name", BIG_FONT, BLACK, CONTENT_RECT.top + 40)
        pygame.draw.rect(screen, WHITE, name_input_box, 0, border_radius=10)
        pygame.draw.rect(screen, BLACK, name_input_box, 2, border_radius=10)
        name_surface = FONT.render(input_text, True, BLACK)
        screen.blit(name_surface, (name_input_box.x + 10, name_input_box.y + 10))
        if input_error:
            err_surface = SMALL_FONT.render(input_error, True, RED)
            screen.blit(err_surface, (CONTENT_RECT.centerx - err_surface.get_width()//2, name_input_box.bottom + 10))
        draw_text_center("Press Enter to Continue", SMALL_FONT, BLACK, CONTENT_RECT.bottom - 60)
