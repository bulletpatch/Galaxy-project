from kivy.lang.builder import Builder
from kivy.uix.relativelayout import RelativeLayout


Builder.load_file("menu.kv")


class MenuWidget(RelativeLayout):

    def on_touch_down(self, touch):
        # If menu has been hidden, do nothing on button click -> else propagate event
        if self.opacity == 0:
            return False
        return super(RelativeLayout, self).on_touch_down(touch)

