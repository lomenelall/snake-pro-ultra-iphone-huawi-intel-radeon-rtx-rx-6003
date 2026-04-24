import random
import asyncio
from nicegui import ui

class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = (random.randint(0, 19), random.randint(0, 19))
        self.score = 0
        self.is_running = False
        self.is_game_over = False

    def step(self):
        if not self.is_running or self.is_game_over: return
        
        self.direction = self.next_direction
        # Проход сквозь стенки (% 20 делает телепорт)
        new_head = (
            (self.snake[0][0] + self.direction[0]) % 20,
            (self.snake[0][1] + self.direction[1]) % 20
        )

        if new_head in self.snake[:-1]:
            self.is_game_over = True
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            self.food = (random.randint(0, 19), random.randint(0, 19))
        else:
            self.snake.pop()

game = SnakeGame()

@ui.page('/')
def main_page():
    ui.dark_mode().enable()
    
    ui.add_head_html('''
        <style>
            body { background: #000; margin: 0; display: flex; justify-content: center; }
            .grid { 
                display: grid; grid-template-columns: repeat(20, 1fr); 
                width: 90vw; height: 90vw; max-width: 400px; max-height: 400px;
                background: #111; border: 2px solid #333; 
            }
            .cell { width: 100%; height: 100%; border: 0.1px solid rgba(255,255,255,0.02); }
            .h { background: #00ff88 !important; box-shadow: 0 0 10px #00ff88; }
            .b { background: #008855 !important; }
            .f { background: #ff0055 !important; border-radius: 50%; box-shadow: 0 0 10px #ff0055; }
            .btn { width: 80px; height: 80px; background: #222 !important; color: white !important; font-size: 30px !important; }
        </style>
    ''')

    with ui.column().classes('items-center w-full gap-4 pt-4'):
        with ui.row().classes('w-full justify-around items-center'):
            ui.label('SNAKE').classes('text-2xl font-black italic text-green-500')
            score_label = ui.label('0').classes('text-3xl font-mono text-white')

        grid_el = ui.html('').classes('grid')

        # Кнопки управления
        with ui.column().classes('items-center gap-2'):
            ui.button('▲', on_click=lambda: set_dir(0, -1)).classes('btn')
            with ui.row().classes('gap-2'):
                ui.button('◀', on_click=lambda: set_dir(-1, 0)).classes('btn')
                ui.button('▼', on_click=lambda: set_dir(0, 1)).classes('btn')
                ui.button('▶', on_click=lambda: set_dir(1, 0)).classes('btn')
            
            ui.button('RESET', on_click=lambda: restart()).classes('mt-4 w-full bg-red-800')

    def set_dir(dx, dy):
        if (dx, -dy) == game.direction or (-dx, dy) == game.direction: return
        game.next_direction = (dx, dy)
        game.is_running = True

    def restart():
        game.reset()
        update_grid()

    def update_grid():
        score_label.set_text(str(game.score))
        cells = []
        for y in range(20):
            for x in range(20):
                cls = "cell"
                if (x, y) == game.snake[0]: cls += " h"
                elif (x, y) in game.snake: cls += " b"
                elif (x, y) == game.food: cls += " f"
                cells.append(f'<div class="{cls}"></div>')
        grid_el.content = "".join(cells)

    async def loop():
        while True:
            if game.is_running and not game.is_game_over:
                game.step()
                update_grid()
            await asyncio.sleep(0.08) # Высокая скорость

    ui.timer(0.1, loop, once=True)
    update_grid()

ui.run(native=True, window_size=(450, 800), title='Snake')
