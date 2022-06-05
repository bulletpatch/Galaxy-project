
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

    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - linear_y
    factor_y = diff_y / self.perspective_point_y
    factor_y = pow(factor_y, 3)      # This creates weird behaviour when used inline in "transformed_y"

    transformed_x = self.perspective_point_x + diff_x * factor_y
    transformed_y = self.perspective_point_y - (factor_y * self.perspective_point_y)

    # take care to use int's for coordinates - floats create weird behaviour
    return int(transformed_x), int(transformed_y)
