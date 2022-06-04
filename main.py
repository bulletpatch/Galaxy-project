from kivy.config import Config
Config.set("graphics", "width", "900")
Config.set("graphics", "height", "400")

from kivy import platform
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget


class MainWidget(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 12
    V_LINES_SPACING = 0.25       # Percentage in screen width
    vertical_lines = []         # list of lines

    H_NB_LINES = 12
    H_LINES_SPACING = 0.1  # Percentage in screen width
    horizontal_lines = []  # list of lines

    SPEED = 2
    current_offset_y = 0

    SPEED_X = 12
    current_speed_x = 0
    current_offset_x = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("On_Init Width: " + str(self.width) + "  Height: " + str(self.height))

        self.init_vertical_lines()
        self.init_horizontal_lines()

        # Only init keyboard if we're on desktop -- not for mobile
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0/60.0)  # Schedule frame update at 60fps

    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard.unbind(on_key_up=self.on_keyboard_up)
        self._keyboard = None

    def is_desktop(self):
        if platform in ("linux", "win", "macosx"):
            return True
        return False

    def on_parent(self, widget, parent):
        # print("On_Parent Width: " + str(self.width) + "  Height: " + str(self.height))
        pass

    def on_size(self, *args):
        # print("On_Size Width: " + str(self.width) + "  Height: " + str(self.height))
        # self.perspective_point_x = self.width * 0.5
        # self.perspective_point_y = self.height * 0.75
        # self.update_vertical_lines()
        # self.update_horizontal_lines()
        pass

    def on_perspective_point_x(self, widget, value):
        print("Px: " + str(value))

    def on_perspective_point_y(self, widget, value):
        print("Py: " + str(value))

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[100, 0, 100, 100])
            for i in range(self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        center_line_x = int(self.width * 0.5)            # Find the middle
        spacing = self.V_LINES_SPACING * self.width
        # Offset position from center; start on left (negative). Add .5 so that line shifts - track in middle, not line
        offset = -int(self.V_NB_LINES * 0.5) + 0.5

        for i in range(self.V_NB_LINES):
            line_x = center_line_x + (offset * spacing) + self.current_offset_x

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

            offset += 1

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        # dependent on vertical line coordinates - get first and last vertical x-coordinates
        left_boundary = self.vertical_lines[0].points[0]
        right_boundary = self.vertical_lines[-1].points[0]
        spacing_y = self.H_LINES_SPACING * self.height
        '''
        center_line_x = int(self.width * 0.5)
        spacing = self.V_LINES_SPACING * self.width
        offset = -int(self.V_NB_LINES * 0.5) + 0.5
        left_boundary = center_line_x + offset * spacing + self.current_offset_x
        right_boundary = center_line_x - offset * spacing + self.current_offset_x
        '''
        for i in range(self.H_NB_LINES):
            # current_offset_y control movement behaviour -- called in "update" method
            line_y = i * spacing_y - self.current_offset_y

            x1, y1 = self.transform(left_boundary, line_y)
            x2, y2 = self.transform(right_boundary, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def transform(self, x, y):
        # return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def transform_2D(self, x, y):
        return x, y

    def transform_perspective(self, x, y):
        linear_y = y * self.perspective_point_y / self.height    # equal to: y * 0.75
        if linear_y > self.perspective_point_y:                  # perspective_y is the limit; cannot be greater
            linear_y = self.perspective_point_y

        # transformed y is a simply a proportion of the perspective_y limit
        # transformed x is calculated proportional to the position on the (new) y-axis: it is basically asking what is
        # the new x-coordinate based on how high up we are on the slope? [ m=(y2-y1)/(x2-x1) ]
        #   if pro_y == 0, tr_x = input_x; if pro_y == 1, tr_x = offset
        '''
        # my code
        proportion_y = 1 - (linear_y / self.perspective_point_y)
        offset = self.perspective_point_x
        transformed_x = offset + (x - offset) * proportion_y

        transformed_y = 0
        '''
        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - linear_y
        factor_y = diff_y / self.perspective_point_y
        factor_y = pow(factor_y, 3)      # This creates weird behaviour when used inline in "transformed_y"

        transformed_x = self.perspective_point_x + diff_x * factor_y
        transformed_y = self.perspective_point_y - (factor_y * self.perspective_point_y)

        # take care to use int's for coordinates - floats create weird behaviour
        return int(transformed_x), int(transformed_y)

    def on_touch_down(self, touch):
        if touch.x < self.width * 0.5:
            print("left-side touch")
            self.current_speed_x = self.SPEED_X
        else:
            print("right-side touch")
            self.current_speed_x = -self.SPEED_X

    def on_touch_up(self, touch):
        print("UP")
        self.current_speed_x = 0

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == "left":
            self.current_speed_x = self.SPEED_X
        elif keycode[1] == "right":
            self.current_speed_x = -self.SPEED_X
        return True

    def on_keyboard_up(self, keyboard, keycode):
        self.current_speed_x = 0
        return True

    def update(self, dt):
        # dt (delta_time) is a variable that shows how much time elapsed between consecutive Clock.schedule calls
        # Here we can use it as a modifier to speed so that there is a consistent experience in the movement of the game
        # regardless if the time between function calls differ. I.e. slower calls will slightly speed up the game and
        # faster calls will slightly slow down the movement to achieve a balanced feel.
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()

        # Movement on y-axis
        self.current_offset_y += self.SPEED * time_factor
        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y

        # Movement on x-axis
        self.current_offset_x += self.current_speed_x * time_factor


class GalaxyApp(App):
    pass


GalaxyApp().run()
