from kivy.config import Config

Config.set("graphics", "width", "900")
Config.set("graphics", "height", "400")

from kivy import platform
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout
from random import randint


class MainWidget(RelativeLayout):
    # import inside class to preserve pointers and calls to "self"
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    menu_widget = ObjectProperty()

    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button_title = StringProperty("START")
    score_txt = StringProperty("")

    V_NB_LINES = 15
    V_LINES_SPACING = 0.15       # Percentage in screen width
    vertical_lines = []         # list of lines

    H_NB_LINES = 15
    H_LINES_SPACING = 0.15  # Percentage in screen width
    horizontal_lines = []  # list of lines

    SPEED = 0
    SPEED_FACTOR = 80      # Larger is slower
    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 0
    SPEED_X_FACTOR = 80     # Larger is slower
    current_speed_x = 0
    current_offset_x = 0

    NB_TILES = 14
    tiles = []
    tile_coordinates = []

    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    state_game_started = False

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)

        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()

        # Only init keyboard if we're on desktop -- not for mobile
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0/60.0)  # Schedule frame update at 60fps
        self.sound_galaxy.play()

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_impact.volume = .25
        self.sound_gameover_voice.volume = .6
        self.sound_restart.volume = .25

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.score_txt = "SCORE: " + str(self.current_y_loop * 20)

        self.tile_coordinates = []
        self.prefill_tile_coordinates()
        self.generate_tile_coordinates()

        self.state_game_over = False

    def is_desktop(self):
        if platform in ("linux", "win", "macosx"):
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(0.26, 0.41, 0.88)      # Black
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width * 0.5
        base_y = self.height * self.SHIP_BASE_Y
        length = self.width * self.SHIP_WIDTH
        height = self.height * self.SHIP_HEIGHT
        #    2
        # 1     3
        self.ship_coordinates[0] = (center_x-length/2, base_y)
        self.ship_coordinates[1] = (center_x, base_y+height)
        self.ship_coordinates[2] = (center_x+length/2, base_y)

        # Transform function only applied AFTER logic calculations - transform is for display only
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(len(self.tile_coordinates)):
            tile_index_x, tile_index_y = self.tile_coordinates[i]
            if tile_index_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(tile_index_x, tile_index_y):
                # The ship is still on a tile
                return True
        return False

    def check_ship_collision_with_tile(self, tile_index_x, tile_index_y):
        xmin, ymin = self.get_tile_coordinates(tile_index_x, tile_index_y)
        xmax, ymax = self.get_tile_coordinates(tile_index_x+1, tile_index_y+1)

        for i in range(3):
            point_x, point_y = self.ship_coordinates[i]
            if xmin <= point_x <= xmax and ymin <= point_y <= ymax:
                # Atleast one point of the ship is within the tile
                return True
        return False    # No collision with tile detected

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[x1, y1, x2, y2])
            for i in range(self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.NB_TILES):
                self.tiles.append(Quad())

    def prefill_tile_coordinates(self):
        # 10 tiles in a straight line to start off the game
        for i in range(10):
            self.tile_coordinates.append((0, i))

    def generate_tile_coordinates(self):
        # Called once at init, and then every time current_y_loop exceeds the tile coordinates, for cleanup and
        # infinite generation.

        last_y = 0      # Keep track of the furthest block generated
        last_x = 0
        for i in range(len(self.tile_coordinates)-1, -1, -1):       # Loop backwards over list
            # when y coordinates are out of screen
            if self.tile_coordinates[i][1] < self.current_y_loop:
                del self.tile_coordinates[i]

        if len(self.tile_coordinates) > 0:
            # If there's something in the list, get the y of the last element and increment
            last_coordinates = self.tile_coordinates[-1]
            last_y = last_coordinates[1] + 1    # Increment to move forward
            last_x = last_coordinates[0]

        # Add some new tiles
        for i in range(len(self.tile_coordinates), self.NB_TILES):
            start_index = -int(self.V_NB_LINES * 0.5) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if last_x <= start_index:
                # if at left boundary, force right
                r = 1
            elif last_x >= end_index-1:
                # if at right boundary, force left
                r = 2
            else:
                r = randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            self.tile_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tile_coordinates.append((last_x, last_y))
                last_y += 1
                self.tile_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tile_coordinates.append((last_x, last_y))
                last_y += 1
                self.tile_coordinates.append((last_x, last_y))
            last_y += 1

    def get_line_x_from_index(self, index):
        center_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        # Offset position from center by half of spacing
        offset = index - 0.5
        line_x = center_line_x + offset*spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        # current_offset_y control movement behaviour -- called in "update" method
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, tile_index_x, tile_index_y):
        # This variable ensures that the tile keeps a "fixed" position and "moves down", instead of resetting to initial
        # position on every loop of the update method. Guarantees the tiles will move out of screen.
        tile_index_y = tile_index_y - self.current_y_loop

        x = self.get_line_x_from_index(tile_index_x)
        y = self.get_line_y_from_index(tile_index_y)
        return x, y

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES * 0.5) + 1
        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES * 0.5) + 1
        end_index = start_index+self.V_NB_LINES - 1
        # dependent on vertical line coordinates - get first and last vertical x-coordinates
        left_boundary = self.get_line_x_from_index(start_index)
        right_boundary = self.get_line_x_from_index(end_index)

        for i in range(self.H_NB_LINES):
            # line_y = i * spacing_y - self.current_offset_y
            line_y = self.get_line_y_from_index(i)

            x1, y1 = self.transform(left_boundary, line_y)
            x2, y2 = self.transform(right_boundary, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update_tiles(self):
        for i in range(self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tile_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)

            # 2     3
            #
            # 1     4
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update(self, dt):
        # dt (delta_time) is a variable that shows how much time elapsed between consecutive Clock.schedule calls
        # Here we can use it as a modifier to speed so that there is a consistent experience in the movement of the game
        # regardless if the time between function calls differ. I.e. slower calls will slightly speed up the game and
        # faster calls will slightly slow down the movement to achieve a balanced feel.
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        # Game in progress
        if not self.state_game_over and self.state_game_started:
            # Movement on y-axis
            self.SPEED = self.height / self.SPEED_FACTOR
            self.current_offset_y += self.SPEED * time_factor
            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "SCORE: " + str(self.current_y_loop * 20)
                self.generate_tile_coordinates()

            # Movement on x-axis
            self.current_offset_x += self.current_speed_x * time_factor

        # Game over trigger
        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.menu_button_title = "RESTART"
            self.menu_widget.opacity = 1
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_game_over_voice_sound, 2)
            print("GAME OVER")

    def play_game_over_voice_sound(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()

    def on_menu_button_pressed(self):
        print("START GAME")
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.reset_game()
        self.state_game_started = True
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    pass


GalaxyApp().run()
