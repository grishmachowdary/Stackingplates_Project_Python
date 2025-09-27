  if current_screen == "name_prompt":
            if e.type == pygame.KEYDOWN:
                if input_active:
                    if e.key == pygame.K_RETURN:
                        if len(input_text.strip()) >= 2:
                            player_name = input_text.strip()
                            load_leaderboard()
                            current_screen = "home"
                        else:
                            input_error = "Name must be at least 2 characters"
                    elif e.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 20:
                            input_text += e.unicode

        elif e.type == pygame.MOUSEBUTTONDOWN:
            if current_screen == "home":
                for b in home_buttons:
                    if b.is_clicked(pos):
                        if b.text == "Play":
                            selected_level = 0
                            init_game(0)
                            current_screen = "game"
                        elif b.text == "Levels":
                            current_screen = "levels"
                        elif b.text == "Help":
                            current_screen = "help"
                        elif b.text == "Quit":
                            running = False
                        elif b.text == "Leaderboard":
                            current_screen = "leaderboard"