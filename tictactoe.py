import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import os
import json

def main():
    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load("assets/audio_files/Relaxed Scene.mp3")
    pygame.mixer.music.play(-1)  # Loop the music indefinitely

    def start_game():
        for widget in root.winfo_children():
            widget.destroy()


        # Open the image using Pillow
        image = Image.open("assets/settingupgamebg.png")
        
        # Get the root window dimensions
        root_width = root.winfo_screenwidth()
        root_height = root.winfo_screenheight()
        
        # Calculate the scaling factor to ensure the entire image fits within the window
        scale_factor = 1.7
        
        # Calculate new dimensions
        new_width = int(image.width / scale_factor)
        new_height = int(image.height / scale_factor)
        
        # Resize the image
        image = image.resize((new_width, new_height), Image.LANCZOS)
        root.bg_image = ImageTk.PhotoImage(image)  # Keep a reference to the image

        # Set the resized image as the background
        bg_label = tk.Label(root, image=root.bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')  # Center the image
        
        tk.Label(root, text="Game Settings", font=("Helvetica", 25), fg='white', bg='black').pack(pady=10)
        
        tk.Label(root, text="Player 1 Name (1-7 chars):", font=("Helvetica", 15), fg='white', bg='black').pack(pady=5)
        player1_entry = tk.Entry(root, font=("Helvetica", 15))
        player1_entry.pack(pady=5)
        
        tk.Label(root, text="Player 2 Name (1-7 chars):", font=("Helvetica", 15), fg='white', bg='black').pack(pady=5)
        player2_entry = tk.Entry(root, font=("Helvetica", 15))
        player2_entry.pack(pady=5)
        
        tk.Label(root, text="Board Size (N x N):", font=("Helvetica", 15), fg='white', bg='black').pack(pady=5)
        board_size_entry = tk.Entry(root, font=("Helvetica", 15))
        board_size_entry.insert(0, "3")  # Default value
        board_size_entry.pack(pady=5)
        
        def start_actual_game():
            import csv
            import os

            def set_image(image_path, subsample_factor):
                image = tk.PhotoImage(file=image_path)
                return image.subsample(subsample_factor, subsample_factor)

            def check_winner(board, player):
                # Check rows, columns, and diagonals for a win
                for i in range(board_size):
                    if all([cell == player for cell in board[i]]):  # Check row
                        return True
                    if all([board[j][i] == player for j in range(board_size)]):  # Check column
                        return True
                if all([board[i][i] == player for i in range(board_size)]):  # Check main diagonal
                    return True
                if all([board[i][board_size - i - 1] == player for i in range(board_size)]):  # Check anti-diagonal
                    return True
                return False

            def update_scores(winner):
                # Update scores in the CSV file
                file_path = 'game_data/data.csv'
                if not os.path.exists(file_path):
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Player', 'Score'])

                scores = {player1_name: 0, player2_name: 0}
                with open(file_path, 'r', newline='') as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip header
                    for row in reader:
                        scores[row[0]] = int(row[1])

                if winner:
                    scores[winner] += 1

                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Player', 'Score'])
                    for player, score in scores.items():
                        writer.writerow([player, score])

                # Update the score labels
                player1_score_label.config(text=f"{player1_name}'s score: {scores[player1_name]}")
                player2_score_label.config(text=f"{player2_name}'s score: {scores[player2_name]}")

            def end_game(winner):
                # Display game over message and handle continuation or exit
                game_over_canvas = tk.Canvas(root, width=500, height=200, bg='black')
                game_over_canvas.place(relx=0.5, rely=0.5, anchor='center')

                def continue_game():
                    game_over_canvas.destroy()
                    update_scores(winner)
                    
                    # Clear the board and reset game state
                    nonlocal board, current_player, moves_made
                    board = [['' for _ in range(board_size)] for _ in range(board_size)]
                    current_player = 'X'
                    moves_made = 0

                    # Clear the canvas
                    canvas.delete("all")

                    # Redraw the background image
                    canvas.create_image(0, 0, image=root.bg_image, anchor='nw')
                    
                    # Redraw the grid lines
                    for i in range(1, board_size):
                        canvas.create_line(i * cell_size, 0, i * cell_size, 500, fill='white')
                        canvas.create_line(0, i * cell_size, 500, i * cell_size, fill='white')

                    # Restart the game
                    start_actual_game()

                def exit_game():
                    if os.path.exists('game_data/data.csv'):
                        os.remove('game_data/data.csv')
                    show_main_menu()

                # Create buttons inside the game over canvas
                continue_button = tk.Button(root, text="Continue", command=continue_game, width=10, fg='white', bg='green')
                exit_button = tk.Button(root, text="Exit", command=exit_game, width=10, fg='white', bg='red')

                if winner:
                    game_over_canvas.create_text(250, 25, text=f"Game Over!\n{winner} wins!", fill='white', font=("Helvetica", 15))
                else:
                    game_over_canvas.create_text(250, 25, text="Game Over!\nTie!", fill='white', font=("Helvetica", 15))

                # Place buttons on the canvas
                game_over_canvas.create_window(200, 100, window=continue_button)
                game_over_canvas.create_window(300, 100, window=exit_button)

                

            player1_name = player1_entry.get().strip()
            player2_name = player2_entry.get().strip()
            board_size = board_size_entry.get().strip()

            if not player1_name or not player2_name or not board_size:
                messagebox.showerror("Error", "All fields must be filled!")
                return

            try:
                board_size = int(board_size)
                if board_size < 3 or board_size > 5:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Board size must be an integer between 3 and 5.")
                return

            root.geometry("800x475")
            for widget in root.winfo_children():
                widget.destroy()

            # Open the image using Pillow
            image = Image.open("assets/space.png")
            
            # Get the root window dimensions
            root_width = root.winfo_screenwidth()
            root_height = root.winfo_screenheight()
            
            # Calculate the scaling factor to ensure the entire image fits within the window
            scale_factor = 1.7
            
            # Calculate new dimensions
            new_width = int(image.width / scale_factor)
            new_height = int(image.height / scale_factor)
            
            # Resize the image
            image = image.resize((new_width, new_height), Image.LANCZOS)
            root.bg_image = ImageTk.PhotoImage(image)  # Keep a reference to the image
            
            # Create the game board with the background image
            canvas = tk.Canvas(root, width=new_width, height=new_height)
            canvas.pack(side='left', anchor='nw')  # Align the canvas to the left
            canvas.create_image(0, 0, image=root.bg_image, anchor='nw')

            
            cell_size = 500 // board_size
            for i in range(1, board_size):
                # Draw vertical lines (excluding outer borders)
                canvas.create_line(i * cell_size, 0, i * cell_size, 500, fill='white')
                # Draw horizontal lines (excluding outer borders)
                canvas.create_line(0, i * cell_size, 500, i * cell_size, fill='white')

            board = [['' for _ in range(board_size)] for _ in range(board_size)]
            current_player = 'X'
            moves_made = 0
            
            def get_winning_line(board, player):
                # Check rows
                for i in range(board_size):
                    if all([cell == player for cell in board[i]]):
                        return (0, i * cell_size + cell_size // 2, 500, i * cell_size + cell_size // 2)
                # Check columns
                for i in range(board_size):
                    if all([board[j][i] == player for j in range(board_size)]):
                        return (i * cell_size + cell_size // 2, 0, i * cell_size + cell_size // 2, 500)
                # Check main diagonal
                if all([board[i][i] == player for i in range(board_size)]):
                    return (0, 0, 500, 500)
                # Check anti-diagonal
                if all([board[i][board_size - i - 1] == player for i in range(board_size)]):
                    return (0, 500, 500, 0)
                return None

            def make_move(event):
                nonlocal current_player, moves_made
                x, y = event.x // cell_size, event.y // cell_size
                if board[y][x] == '':
                    board[y][x] = current_player
                    # Load the image for the current player
                    player_image = set_image(f"assets/{current_player}.png", 5)
                    # Place the image on the canvas
                    canvas.create_image(x * cell_size + cell_size // 2, y * cell_size + cell_size // 2, image=player_image)
                    # Keep a reference to avoid garbage collection
                    if not hasattr(canvas, 'images'):
                        canvas.images = []
                    canvas.images.append(player_image)
                    moves_made += 1
                    if check_winner(board, current_player):

                        # Determine the winning line
                        winning_line = get_winning_line(board, current_player)
                        if winning_line:
                            x1, y1, x2, y2 = winning_line
                            # Calculate the number of steps for the animation
                            steps = 50
                            dx = (x2 - x1) / steps
                            dy = (y2 - y1) / steps

                            def animate_line(step=0):
                                if step <= steps:
                                    # Draw a line segment
                                    canvas.create_line(x1, y1, x1 + step * dx, y1 + step * dy, fill='red', width=3)
                                    # Schedule the next segment
                                    root.after(10, animate_line, step + 1)

                            # Start the animation
                            animate_line()

                        end_game(player1_name if current_player == 'X' else player2_name)
                    elif moves_made == board_size * board_size:
                        end_game(None)
                    else:
                        current_player = 'O' if current_player == 'X' else 'X'
                        root.turn_image = set_image(f"assets/{current_player}.png", 5)
                        image_label.config(image=root.turn_image)

            canvas.bind("<Button-1>", make_move)
            # Check if the game_settings directory and color_mode.json file exist
            color_mode = "dark"  # Default color mode
            color_mode_path = 'game_settings/color_mode.json'
            
            if os.path.exists('game_settings') and os.path.isfile(color_mode_path):
                with open(color_mode_path, 'r') as f:
                    try:
                        color_mode_data = json.load(f)
                        color_mode = color_mode_data.get('color_mode', 'default')
                    except json.JSONDecodeError:
                        print("Error decoding JSON from color_mode.json")
            
            color_modes = {
                "light": {
                    "text_color": "black",
                    "bg_color": "white"
                },
                "dark": {
                    "text_color": "white",
                    "bg_color": "#2f2f2f"
                },
                "contrast": {
                    "text_color": "yellow",
                    "bg_color": "black"
                }
            }

            font_size = "small"  # Default font size
            font_size_path = 'game_settings/font_size.json'
            
            if os.path.exists('game_settings') and os.path.isfile(font_size_path):
                with open(font_size_path, 'r') as f:
                    try:
                        font_size_data = json.load(f)
                        font_size = font_size_data.get('font_size', 'big')
                    except json.JSONDecodeError:
                        print("Error decoding JSON from font_size.json")
            
            font_size_dict = {
                "small": 0,
                "big": 3
            }

            # Create a sidebar on the right
            sidebar = tk.Frame(root, width=300, bg=color_modes[color_mode]["bg_color"]) # DARKLIGHTCONTRASTMODE
            sidebar.place(relx=1.0, rely=0.0, anchor='ne', relheight=1.0)

            # Add some placeholder buttons or labels to the sidebar
            sidebar_label = tk.Label(sidebar, text="Tic-Tac-Toe", font=("Helvetica", 20 + font_size_dict[font_size]), fg=color_modes[color_mode]["text_color"], bg=color_modes[color_mode]["bg_color"]) # DARKLIGHTCONTRASTMODE
            sidebar_label.place(relx=0.5, rely=0.1, anchor='center')

            turn_label = tk.Label(sidebar, text="Turn:", font=("Helvetica", 15 + font_size_dict[font_size]), fg=color_modes[color_mode]["text_color"], bg=color_modes[color_mode]["bg_color"]) # DARKLIGHTCONTRASTMODE
            turn_label.place(relx=0.1, rely=0.3, anchor='w')  # Added padding to move it right

            # Load the initial image for X and shrink it
            root.turn_image = set_image("assets/X.png", 5)  # Store the image in the root object

            # Create a label to display the shrunken image
            image_label = tk.Label(sidebar, image=root.turn_image, bg=color_modes[color_mode]["bg_color"])  # Use the stored image # DARKLIGHTCONTRASTMODE
            image_label.place(relx=0.3, rely=0.3, anchor='w')

            # Add two rectangles with black fill and white outline
            sidebar_canvas = tk.Canvas(sidebar, width=280, height=220, bg=color_modes[color_mode]["bg_color"], highlightthickness=0)  # Increased height # DARKLIGHTCONTRASTMODE
            sidebar_canvas.place(relx=0.5, rely=0.6, anchor='center')
            sidebar_canvas.create_rectangle(10, 40, 270, 90, fill='black', outline='white')  # Adjusted position

            # Shrink the image further to fit inside the rectangle
            x_image = set_image("assets/X.png", 14)  # Increase subsample factor to shrink more
            # Create a label to display the shrunken image inside the first rectangle
            x_image_label = tk.Label(sidebar_canvas, image=x_image, bg='black')
            x_image_label.image = x_image  # Keep a reference to avoid garbage collection
            x_image_label.place(x=30, y=43)  # Adjust position to fit inside the rectangle
            scores = {player1_name : 0, player2_name: 0}
            # Add a text label for Player 1's score
            player1_score_label = tk.Label(sidebar_canvas, text=f"{player1_name}'s score: {scores[player1_name]}", font=("Helvetica", 10 + font_size_dict[font_size]), fg='white', bg='black')
            player1_score_label.place(x=80, y=50)  # Position the label inside the first rectangle

            sidebar_canvas.create_rectangle(10, 110, 270, 160, fill='black', outline='white')  # Adjusted position

            # Shrink the O image to fit inside the second rectangle
            o_image = set_image("assets/O.png", 14)  # Use the same subsample factor as X
            # Create a label to display the shrunken O image inside the second rectangle
            o_image_label = tk.Label(sidebar_canvas, image=o_image, bg='black')
            o_image_label.image = o_image  # Keep a reference to avoid garbage collection
            o_image_label.place(x=30, y=113)  # Adjust position to fit inside the rectangle

            # Add a text label for Player 2's score
            player2_score_label = tk.Label(sidebar_canvas, text=f"{player2_name}'s score: {scores[player2_name]}", font=("Helvetica", 10 + font_size_dict[font_size]), fg='white', bg='black')
            player2_score_label.place(x=80, y=120)  # Position the label inside the second rectangle

            # Create a red "Exit" button at the bottom right corner of the sidebar
            exit_button = tk.Button(sidebar, text="Exit→", command=show_main_menu, width=10, fg='white', bg='red')
            exit_button.place(relx=0.9, rely=0.9, anchor='se')


            
        def create_gradient_image(width, height, start_color, end_color):
            image = Image.new("RGB", (width, height))
            start_r, start_g, start_b = start_color
            end_r, end_g, end_b = end_color

            for y in range(height):
                r = int(start_r + (end_r - start_r) * y / height)
                g = int(start_g + (end_g - start_g) * y / height)
                b = int(start_b + (end_b - start_b) * y / height)
                for x in range(width):
                    image.putpixel((x, y), (r, g, b))

            return ImageTk.PhotoImage(image)
        
        # Create gradient images
        normal_gradient = create_gradient_image(200, 30, (255, 0, 0), (0, 0, 255))
        hover_gradient = create_gradient_image(200, 30, (255, 100, 100), (100, 100, 255))
            
        def create_gradient_button(canvas, text, command, x, y):
            button = tk.Label(canvas, image=normal_gradient, text=text, compound='center', fg='white', font=("Helvetica", 10))
            button.bind("<Enter>", lambda e: button.config(image=hover_gradient))
            button.bind("<Leave>", lambda e: button.config(image=normal_gradient))
            button.bind("<Button-1>", lambda e: command())
            button.place(relx=x, rely=y, anchor='center')
        
        create_gradient_button(root, "Start Game", start_actual_game, 0.5, 0.7)
        create_gradient_button(root, "Back to Main Menu", show_main_menu, 0.5, 0.8)
    
    def show_main_menu():
        
        for widget in root.winfo_children():
            widget.destroy()
        root.geometry("600x600")
        # Open the image using Pillow
        image = Image.open("assets/menu_bg.png")
        
        # Get the root window dimensions
        root_width = root.winfo_screenwidth()
        root_height = root.winfo_screenheight()
        
        # Calculate the scaling factor to ensure the entire image fits within the window
        scale_factor = 1.7
        
        # Calculate new dimensions
        new_width = int(image.width / scale_factor)
        new_height = int(image.height / scale_factor)
        
        # Resize the image
        image = image.resize((new_width, new_height), Image.LANCZOS)
        root.bg_image = ImageTk.PhotoImage(image)  # Keep a reference to the image

        # Set the resized image as the background
        bg_label = tk.Label(root, image=root.bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')  # Center the image

        def draw_gradient(canvas, width, height, start_color, end_color):
            # Convert hex color to RGB
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

            # Calculate color step
            start_rgb = hex_to_rgb(start_color)
            end_rgb = hex_to_rgb(end_color)
            steps = height
            delta_r = (end_rgb[0] - start_rgb[0]) / steps
            delta_g = (end_rgb[1] - start_rgb[1]) / steps
            delta_b = (end_rgb[2] - start_rgb[2]) / steps

            # Draw gradient
            for i in range(steps):
                r = int(start_rgb[0] + (delta_r * i))
                g = int(start_rgb[1] + (delta_g * i))
                b = int(start_rgb[2] + (delta_b * i))
                color = f'#{r:02x}{g:02x}{b:02x}'
                canvas.create_line(0, i, width, i, fill=color)

        # Create a canvas for the buttons and rectangle with curved edges
        button_canvas = tk.Canvas(root, width=300, height=150, highlightthickness=0)
        button_canvas.place(relx=0.5, rely=0.8, anchor='center')

        # Draw gradient background
        draw_gradient(button_canvas, 300, 150, '#ff0000', '#0000ff')  # From red to blue
        def create_gradient_image(width, height, start_color, end_color):
            image = Image.new("RGB", (width, height))
            start_r, start_g, start_b = start_color
            end_r, end_g, end_b = end_color

            for y in range(height):
                r = int(start_r + (end_r - start_r) * y / height)
                g = int(start_g + (end_g - start_g) * y / height)
                b = int(start_b + (end_b - start_b) * y / height)
                for x in range(width):
                    image.putpixel((x, y), (r, g, b))

            return ImageTk.PhotoImage(image)

        # Create gradient images
        normal_gradient = create_gradient_image(200, 30, (255, 0, 0), (0, 0, 255))
        hover_gradient = create_gradient_image(200, 30, (255, 100, 100), (100, 100, 255))

        # Function to create a button with text overlay
        def create_gradient_button(canvas, text, command, x, y):
            button = tk.Label(canvas, image=normal_gradient, text=text, compound='center', fg='white', font=("Helvetica", 10))
            button.bind("<Enter>", lambda e: button.config(image=hover_gradient))
            button.bind("<Leave>", lambda e: button.config(image=normal_gradient))
            button.bind("<Button-1>", lambda e: command())
            button.place(relx=x, rely=y, anchor='center')

        # Place buttons on the canvas
        create_gradient_button(button_canvas, "Start Game", start_game, 0.5, 0.2)
        create_gradient_button(button_canvas, "Settings", show_settings, 0.5, 0.5)
        create_gradient_button(button_canvas, "Exit", root.quit, 0.5, 0.8)

    def show_settings():
        def create_gradient_image(width, height, start_color, end_color):
            image = Image.new("RGB", (width, height))
            start_r, start_g, start_b = start_color
            end_r, end_g, end_b = end_color

            for y in range(height):
                r = int(start_r + (end_r - start_r) * y / height)
                g = int(start_g + (end_g - start_g) * y / height)
                b = int(start_b + (end_b - start_b) * y / height)
                for x in range(width):
                    image.putpixel((x, y), (r, g, b))

            return ImageTk.PhotoImage(image)

        # Create gradient images
        normal_gradient = create_gradient_image(200, 30, (255, 0, 0), (0, 0, 255))
        hover_gradient = create_gradient_image(200, 30, (255, 100, 100), (100, 100, 255))

        # Function to create a button with text overlay
        def create_gradient_button(canvas, text, command, x, y):
            button = tk.Label(canvas, image=normal_gradient, text=text, compound='center', fg='white', font=("Helvetica", 10))
            button.bind("<Enter>", lambda e: button.config(image=hover_gradient))
            button.bind("<Leave>", lambda e: button.config(image=normal_gradient))
            button.bind("<Button-1>", lambda e: command())
            button.place(relx=x, rely=y, anchor='center')

        for widget in root.winfo_children():
            widget.destroy()

        # Open the image using Pillow
        image = Image.open("assets/debate.png")
        
        # Get the root window dimensions
        root_width = root.winfo_screenwidth()
        root_height = root.winfo_screenheight()
        
        # Calculate the scaling factor to ensure the entire image fits within the window
        scale_factor = 1.7
        
        # Calculate new dimensions
        new_width = int(image.width / scale_factor)
        new_height = int(image.height / scale_factor)
        
        # Resize the image
        image = image.resize((new_width, new_height), Image.LANCZOS)
        root.bg_image = ImageTk.PhotoImage(image)  # Keep a reference to the image

        # Set the resized image as the background
        bg_label = tk.Label(root, image=root.bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')  # Center the image
        
        tk.Label(root, text="Settings Menu", font=("Helvetica", 25), fg='white', bg='black').pack(pady=10)
        
        # Create gradient buttons
        def update_font_size(size):
            # Ensure the game_settings directory exists
            if not os.path.exists('game_settings'):
                os.makedirs('game_settings')
            
            font_size_path = 'game_settings/font_size.json'
            font_size_data = {'font_size': size}
            
            # Write the font size to the json file
            with open(font_size_path, 'w') as f:
                json.dump(font_size_data, f)
            
            messagebox.showinfo("Settings", f"Font size set to {size}")

        create_gradient_button(root, "Big Font Size", lambda: update_font_size("big"), 0.5, 0.3)
        create_gradient_button(root, "Small Font Size", lambda: update_font_size("small"), 0.5, 0.4)
        
        

        # Ensure the game_settings directory exists
        if not os.path.exists('game_settings'):
            os.makedirs('game_settings')

        # Function to update color mode in color_mode.json
        def update_color_mode(mode):
            color_mode_path = 'game_settings/color_mode.json'
            color_mode_data = {'color_mode': mode}
            with open(color_mode_path, 'w') as f:
                json.dump(color_mode_data, f)
            messagebox.showinfo("Update", f"Color mode updated to {mode}")

        create_gradient_button(root, "Light Mode", lambda: update_color_mode("light"), 0.5, 0.5)
        create_gradient_button(root, "Dark Mode", lambda: update_color_mode("dark"), 0.5, 0.6)
        create_gradient_button(root, "High Contrast Mode", lambda: update_color_mode("contrast"), 0.5, 0.7)
        create_gradient_button(root, "Back to Main Menu", show_main_menu, 0.5, 0.9)

    root = tk.Tk()
    root.title("TicTacToe-SanjayK")
    root.geometry("600x600")
    root.configure(bg='black')
    root.resizable(False, False)
    
    show_main_menu()
    
    root.mainloop()

if __name__ == "__main__":
    main()
