from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self.on_keyboard_down)
    self._keyboard.unbind(on_key_up=self.on_keyboard_up)
    self._keyboard = None


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    self.SPEED_X = self.width / self.SPEED_X_FACTOR
    if keycode[1] == "left":
        self.current_speed_x = self.SPEED_X
    elif keycode[1] == "right":
        self.current_speed_x = -self.SPEED_X
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0
    return True


def on_touch_down(self, touch):
    self.SPEED_X = self.width / self.SPEED_X_FACTOR

    if not self.state_game_over and self.state_game_started:
        if touch.x < self.width * 0.5:
            # print("left-side touch")
            self.current_speed_x = self.SPEED_X
        else:
            # print("right-side touch")
            self.current_speed_x = -self.SPEED_X
    # This method overrides the default behaviour - this is why the menu's button press does not register. But by
    # returning the MainWidget's parent class and calling its on_touch method we can propagate the touch event to the
    # default behaviour and get the correct action.
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    # print("UP")
    self.current_speed_x = 0
