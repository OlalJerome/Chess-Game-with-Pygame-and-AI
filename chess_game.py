import pygame
import chess
import chess.engine
import os
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 650  # Extra space for the timer
SQUARE_SIZE = WIDTH // 8
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
HIGHLIGHT_COLOR = (173, 216, 230)  # Light blue for highlighting moves

# Load piece images
PIECE_IMAGES = {}
for piece in chess.PIECE_TYPES:
    for color in [chess.WHITE, chess.BLACK]:
        piece_name = chess.piece_name(piece).capitalize()
        color_name = "White" if color == chess.WHITE else "Black"
        image_path = os.path.join("pieces", f"{color_name}_{piece_name}.png")
        PIECE_IMAGES[(piece, color)] = pygame.image.load(image_path)

# Load sound effects
pygame.mixer.init()
MOVE_SOUND = pygame.mixer.Sound("sounds/move.wav")
CAPTURE_SOUND = pygame.mixer.Sound("sounds/capture.mp3")
CHECKMATE_SOUND = pygame.mixer.Sound("sounds/checkmate.mp3")

# Initialize Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()

# Initialize chess board and engine
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci("stockfish")  # Update path to Stockfish

# Timer variables
WHITE_TIME = 600  # 10 minutes in seconds
BLACK_TIME = 600
last_time = time.time()

def draw_board(highlighted_squares=None):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else GREEN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    if highlighted_squares:
        for square in highlighted_squares:
            row, col = divmod(square, 8)
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            screen.blit(PIECE_IMAGES[(piece.piece_type, piece.color)], (col * SQUARE_SIZE, row * SQUARE_SIZE))

def draw_timer():
    font = pygame.font.SysFont("Arial", 30)
    white_time_text = font.render(f"White: {WHITE_TIME // 60}:{WHITE_TIME % 60:02}", True, BLACK)
    black_time_text = font.render(f"Black: {BLACK_TIME // 60}:{BLACK_TIME % 60:02}", True, BLACK)
    screen.blit(white_time_text, (10, HEIGHT - 40))
    screen.blit(black_time_text, (WIDTH - 150, HEIGHT - 40))

def draw_game_over():
    font = pygame.font.SysFont("Arial", 50)
    if board.is_checkmate():
        text = font.render("Checkmate!", True, BLACK)
    elif board.is_stalemate():
        text = font.render("Stalemate!", True, BLACK)
    else:
        text = font.render("Game Over!", True, BLACK)
    screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 25))

def get_square_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return chess.square(col, 7 - row)

def main():
    global WHITE_TIME, BLACK_TIME, last_time
    running = True
    selected_square = None
    highlighted_squares = []
    game_over = False

    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        if not game_over:
            if board.turn == chess.WHITE:
                WHITE_TIME -= dt
            else:
                BLACK_TIME -= dt

            if WHITE_TIME <= 0 or BLACK_TIME <= 0:
                game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Human player's move
            if not game_over and board.turn == chess.WHITE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    square = get_square_from_mouse(pygame.mouse.get_pos())
                    if selected_square is None:
                        selected_square = square
                        highlighted_squares = [move.to_square for move in board.legal_moves if move.from_square == square]
                    else:
                        move = chess.Move(selected_square, square)
                        if move in board.legal_moves:
                            board.push(move)
                            if board.is_capture(move):
                                CAPTURE_SOUND.play()
                            else:
                                MOVE_SOUND.play()
                        selected_square = None
                        highlighted_squares = []

        # AI's move
        if not game_over and board.turn == chess.BLACK and not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(time=0.1))
            board.push(result.move)
            if board.is_capture(result.move):
                CAPTURE_SOUND.play()
            else:
                MOVE_SOUND.play()

        # Check for game over
        if board.is_game_over():
            game_over = True
            if board.is_checkmate():
                CHECKMATE_SOUND.play()

        # Draw the board, pieces, and timer
        draw_board(highlighted_squares)
        draw_pieces()
        draw_timer()

        # Draw game over screen
        if game_over:
            draw_game_over()

        pygame.display.flip()
        clock.tick(FPS)

    engine.quit()
    pygame.quit()

if __name__ == "__main__":
    main()