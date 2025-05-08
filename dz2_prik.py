import pygame, math, sys, time, numpy as np

STEP_ANGLE: float = math.pi / 1000
LOWER_LIMIT_ANGLE: float = 0
UPPER_LIMIT_ANGLE: float = math.pi * 7 / 12
VAR_ANGLE: float = 0

FPS = 260
WIDTH, HEIGHT = 800, 750
SIZE_TEXT = 48
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 90, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 90)
DARK_RED = (90, 0, 0)
DARK_YELLOW= (180, 120, 0)
DARK_GREY=(50,50,50)
SaddleBrown = (139, 69, 19)
PURPLE = (90, 0, 90)
VINOUS = (171, 39, 49)
PINK = (255, 0, 153)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

HEIGHT_LINK = 250
WIDTH_LINK = 15
RADIUS_KP = 20
WIDTH_KP = 4

pygame.init()
font = pygame.font.Font(None, SIZE_TEXT)
clock = pygame.time.Clock()

def gen_rotate_func(coords_centre: tuple, *, flag_reverse=False):
    multiplier = -1 if flag_reverse else 1

    def rotate(item: tuple, *, angle=None) -> tuple:  # item = (x,y)
        x_rel = item[0] - coords_centre[0]
        y_rel = item[1] - coords_centre[1]

        cos_t = math.cos((VAR_ANGLE if angle is None else angle) * multiplier)
        sin_t = math.sin((VAR_ANGLE if angle is None else angle) * multiplier)
        x_new = x_rel * cos_t - y_rel * sin_t
        y_new = x_rel * sin_t + y_rel * cos_t

        return (coords_centre[0] + x_new, coords_centre[1] + y_new)

    return rotate


class CinematicPair:
    def __init__(self, x: int, y: int, name: str, *, color=BLACK, radius=RADIUS_KP, width=WIDTH_KP):
        self.x = x
        self.y = y
        self.name = name
        self.radius = radius
        self.width = width
        self.color = color

    def draw_on_screen(self, screen, *, key=None, low_index:str=None, upp_index:str=None, size_name_text=SIZE_TEXT-16, coords_shift_name_text:tuple=(0,0)):
        global font
        temp_x: int = self.x
        temp_y: int = self.y
        if key is not None:
            temp_x, temp_y = key((temp_x, temp_y))
        if low_index is not None or upp_index is not None:
            font = pygame.font.Font(None, size_name_text)
        coords_name_kp: tuple = (temp_x - self.radius * (2 / 3 if low_index is None and upp_index is None else 5/6) + coords_shift_name_text[0], temp_y - self.radius * (2 / 3 if low_index is None and upp_index is None else 1/2) + coords_shift_name_text[1])
        pygame.draw.circle(screen, self.color, (temp_x, temp_y), self.radius + self.width)
        pygame.draw.circle(screen, WHITE, (temp_x, temp_y), self.radius)
        screen.blit(font.render(self.name, True, self.color), coords_name_kp)
        if low_index is not None or upp_index is not None:
            font = pygame.font.Font(None, size_name_text-10)
            if upp_index is not None:
                screen.blit(font.render(upp_index, True, self.color), (coords_name_kp[0]+15+(size_name_text/10)*(size_name_text!=SIZE_TEXT-16), coords_name_kp[1]-3-(size_name_text/10)*(size_name_text!=SIZE_TEXT-16)))
            if low_index is not None:
                screen.blit(font.render(low_index, True, self.color), (coords_name_kp[0] + 15+(size_name_text/10)*(size_name_text!=SIZE_TEXT-16), coords_name_kp[1] + 10+(size_name_text/10)*(size_name_text!=SIZE_TEXT-16)))
            font = pygame.font.Font(None, SIZE_TEXT)

    def get_centre(self):
        return (self.x, self.y)


class Flap:
    def __init__(self, x: int, y: int, name: str, *, color = BLACK, width=WIDTH_LINK, height=HEIGHT_LINK):
        self.x = x
        self.y = y
        self.name = name
        self.width = width
        self.height = height
        self.color = color

    def draw_on_screen(self, screen, *, list_texture=None, key=None, shift_name_x=0, shift_name_y=0):
        points = [
            (self.x - self.width / 2, self.y - self.height / 2),
            (self.x + self.width / 2, self.y - self.height / 2),
            (self.x + self.width / 2, self.y + self.height / 2),
            (self.x - self.width / 2, self.y + self.height / 2)
        ]
        if key is not None:
            for i in range(len(points)):
                points[i] = key(points[i])
            if list_texture is not None:
                for texture in list_texture:
                    for i in range(len(texture)):
                        texture[i]=key(texture[i])

        pygame.draw.polygon(screen, self.color, points)

        if list_texture is not None:
            for texture in list_texture:
                pygame.draw.polygon(screen, self.color, texture)

        coords_name=(sum(item[0] for item in points)/len(points)-shift_name_x, sum(item[1] for item in points)/len(points)-shift_name_y)
        screen.blit(font.render(self.name, True, self.color), coords_name)


class ComplexLink:
    def __init__(self, points: list, name: str, *, color = BLACK):
        self.points = points
        self.name = name
        self.color = color

    def draw_on_screen(self, screen, *, key=None):
        temp_points: list = self.points.copy()

        if key is not None:
            for i in range(len(temp_points)):
                temp_points[i] = key(temp_points[i])

        pygame.draw.polygon(screen, self.color, temp_points)

    def dynamic_draw_on_screen(self, screen, cp1, cp2, *, shift_name_x=0, shift_name_y=0):
        vector_cp1_cp2 = (cp2[0]-cp1[0], cp2[1] - cp1[1])
        vertical_vector_cp1_cp2 = (vector_cp1_cp2[1], -vector_cp1_cp2[0])
        coef = math.sqrt(vertical_vector_cp1_cp2[0]**2+vertical_vector_cp1_cp2[1]**2)
        norm_vertical_vector_cp1_cp2 = (vertical_vector_cp1_cp2[0]/coef, vertical_vector_cp1_cp2[1]/coef)
        ness_vertical_vector_cp1_cp2 = (norm_vertical_vector_cp1_cp2[0]*WIDTH_LINK/2, norm_vertical_vector_cp1_cp2[1]*WIDTH_LINK/2)
        points=[
            (cp1[0] - ness_vertical_vector_cp1_cp2[0], cp1[1] - ness_vertical_vector_cp1_cp2[1]),
            (cp1[0] + ness_vertical_vector_cp1_cp2[0], cp1[1] + ness_vertical_vector_cp1_cp2[1]),
            (cp2[0] + ness_vertical_vector_cp1_cp2[0], cp2[1] + ness_vertical_vector_cp1_cp2[1]),
            (cp2[0] - ness_vertical_vector_cp1_cp2[0], cp2[1] - ness_vertical_vector_cp1_cp2[1])
        ]
        pygame.draw.polygon(screen, self.color, points)
        coords_name = (sum(item[0] for item in points) / len(points) - shift_name_x,
                       sum(item[1] for item in points) / len(points) - shift_name_y)
        screen.blit(font.render(self.name, True, self.color), coords_name)

class Emphasis:
    def __init__(self, *, color = BLACK):
        self.color = color

    def draw_on_screen(self, screen, cx, cy, func_rotate):
        rect1: list = list()
        rect2: list = list()
        for item in [
            (cx, cy+WIDTH_LINK/6),
            (cx, cy-WIDTH_LINK/6),
            (cx + HEIGHT_LINK/6, cy-WIDTH_LINK/6),
            (cx + HEIGHT_LINK/6, cy+WIDTH_LINK/6)
        ]:
            rect1.append(func_rotate(item, angle=100))
            rect2.append(func_rotate(item, angle=-100))

        pygame.draw.polygon(screen, self.color, rect1)
        pygame.draw.polygon(screen, self.color, rect2)
        pygame.draw.rect(screen, self.color, (cx + 35, cy-30, 7, 60) )

        for shit_y in [25, 8, -8, -25]:
            pygame.draw.polygon(screen, self.color, [(rect2[i][0] + 40 - 15*(i>=len(rect2)/2), rect2[i][1]+shit_y) for i in range(len(rect2))])

        screen.blit(font.render("0", True, self.color), (cx+65,cy-25))

class Arrow:
    def __init__(self, cx, cy, radius, angle_arc, width_arc, *, color=BLACK, len_arrow=25):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.angle_arc =angle_arc
        self.width_arc = width_arc
        self.len_arrow=len_arrow
        self.color=color

    def draw_on_screen(self, screen, *, func_rotate=None, angle_rotate=0):
        crotate = gen_rotate_func((self.cx, self.cy), flag_reverse=True)
        part1_line = [
            crotate((self.cx - self.radius, self.cy), angle=-angle) for angle in
            np.arange(0, self.angle_arc + math.pi / 100, math.pi / 100)
        ]
        part2_line = [
            crotate((self.cx - self.radius - self.width_arc, self.cy), angle=-angle) for angle in
            np.arange(0, self.angle_arc + math.pi / 100, math.pi / 100)
        ]

        part1_arrow = [
            ((part1_line[0][0] + part2_line[0][0]) / 2, part1_line[0][1] + self.len_arrow),
            ((part1_line[0][0] + part2_line[0][0]) / 2 - self.width_arc*2, part1_line[0][1]),
            ((part1_line[0][0] + part2_line[0][0]) / 2 + self.width_arc*2, part1_line[0][1])
        ]

        tt_rotate = gen_rotate_func(((part1_line[0][0] + part2_line[0][0]) / 2, part1_line[0][1]), flag_reverse=True)

        part2_arrow = [tt_rotate(item, angle=math.pi - self.angle_arc) for item in part1_arrow]
        part2_arrow = [(part2_arrow[i][0] + (
                    (part1_line[-1][0] + part2_line[-1][0]) - (part1_line[0][0] + part2_line[0][0])) / 2,
                        part2_arrow[i][1] + ((part1_line[-1][1] + part2_line[-1][1]) - (
                                    part1_line[0][1] + part2_line[0][1])) / 2) for i in range(len(part2_arrow))]

        if func_rotate is not None:
            part1_line=[func_rotate(item, angle=angle_rotate) for item in part1_line]
            part2_line=[func_rotate(item, angle=angle_rotate) for item in part2_line]
            part1_arrow=[func_rotate(item, angle=angle_rotate) for item in part1_arrow]
            part2_arrow=[func_rotate(item, angle=angle_rotate) for item in part2_arrow]

        pygame.draw.polygon(screen, self.color, part1_line + part2_line[::-1])
        pygame.draw.polygon(screen, self.color, part1_arrow)
        pygame.draw.polygon(screen, self.color, part2_arrow)


kinematic_pairs: dict = {
    "A": CinematicPair(WIDTH / 2, HEIGHT / 2 - HEIGHT_LINK, "A", color=DARK_GREEN),
    "B": CinematicPair(WIDTH / 2, HEIGHT / 2 - HEIGHT_LINK / 2, "B", color=DARK_GREEN),
    "C": CinematicPair(WIDTH / 2 + HEIGHT_LINK / 2, HEIGHT / 2 + HEIGHT_LINK, "C", color=DARK_GREEN),
    "D": CinematicPair(WIDTH / 2, HEIGHT / 2 + HEIGHT_LINK, "D", color=DARK_GREEN),
    "E": CinematicPair(WIDTH / 2, HEIGHT / 2, "E", color=DARK_GREEN),
    "F": CinematicPair(WIDTH / 2, HEIGHT / 2, "F", color=DARK_GREEN)
}
rotate={
    "A": gen_rotate_func(kinematic_pairs["A"].get_centre()),
    "A_r": gen_rotate_func(kinematic_pairs["A"].get_centre(), flag_reverse=True),
    "B": gen_rotate_func(kinematic_pairs["B"].get_centre()),
    "D_r": gen_rotate_func(kinematic_pairs["D"].get_centre(), flag_reverse=True),
    "C_r": gen_rotate_func(kinematic_pairs["C"].get_centre(), flag_reverse=True)
}
links: dict = {
    "1": Flap(WIDTH / 2, HEIGHT / 2 - HEIGHT_LINK / 2, "1", color=DARK_BLUE),
    "3_1": Flap(WIDTH / 2, HEIGHT / 2 + HEIGHT_LINK / 2, "3", color=PURPLE),
    "3_2": ComplexLink(
        [rotate["D_r"]((WIDTH / 2, HEIGHT / 2 + HEIGHT_LINK / 2 - WIDTH_LINK / 2), angle=-angle) for angle in
         np.arange(0, math.pi / 2 + math.pi / 99, math.pi / 100, dtype=float)] +
        [rotate["D_r"]((WIDTH / 2 + HEIGHT_LINK / 2 - WIDTH_LINK / 2, HEIGHT / 2 + HEIGHT_LINK), angle=angle) for
         angle in np.arange(0, math.pi / 2 + math.pi / 99, math.pi / 100, dtype=float)],
        "3", color=PURPLE),
    "2": ComplexLink([],"2", color=DARK_YELLOW)
}

if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DZ2")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(WHITE)

        links["1"].draw_on_screen(screen, key=rotate["A"],list_texture = [[rotate["B"]((kinematic_pairs["B"].x, kinematic_pairs["B"].y+RADIUS_KP+WIDTH_LINK),angle=angle) for angle in np.arange(0, math.pi+math.pi/100, math.pi/100, dtype=float)]
                      +[rotate["B"]((kinematic_pairs["B"].x, kinematic_pairs["B"].y + RADIUS_KP), angle=angle) for angle in np.arange(math.pi, -math.pi / 100, -math.pi / 100, dtype=float)]],
                                  shift_name_x=50, shift_name_y=50)
        links["3_1"].draw_on_screen(screen, key=rotate["D_r"], shift_name_x=25, shift_name_y=-12)
        links["3_2"].draw_on_screen(screen, key=rotate["D_r"])
        links["2"].dynamic_draw_on_screen(screen, rotate["A"](kinematic_pairs["B"].get_centre()), rotate["D_r"](kinematic_pairs["C"].get_centre()), shift_name_x=30)

        Emphasis(color=DARK_RED).draw_on_screen(screen, *kinematic_pairs["D"].get_centre(), rotate["D_r"])
        Emphasis(color=DARK_RED).draw_on_screen(screen, *kinematic_pairs["A"].get_centre(), rotate["A_r"])

        Arrow(*kinematic_pairs["A"].get_centre(), HEIGHT_LINK / 4, math.pi * 5 / 12, WIDTH_LINK / 4, color =DARK_GREY).draw_on_screen(
            screen, func_rotate=rotate["A"], angle_rotate=-math.pi * 2 / 5)
        Arrow(*kinematic_pairs["D"].get_centre(), HEIGHT_LINK / 4, math.pi * 5 / 12, WIDTH_LINK / 4, color=DARK_GREY).draw_on_screen(
            screen)

        kinematic_pairs["A"].draw_on_screen(screen, upp_index="01", low_index="1В", size_name_text=42,coords_shift_name_text=(0, -45))
        kinematic_pairs["B"].draw_on_screen(screen, key=rotate["A"], upp_index="12", low_index="1В", size_name_text=42,coords_shift_name_text=(40, 0))
        kinematic_pairs["C"].draw_on_screen(screen, key=rotate["D_r"], upp_index="23", low_index="1В", size_name_text=42,coords_shift_name_text=(40, 0))
        kinematic_pairs["D"].draw_on_screen(screen, upp_index="30", low_index="1В", size_name_text=42,coords_shift_name_text=(0, 45))
        kinematic_pairs["E"].draw_on_screen(screen, key=rotate["A"], size_name_text=42, coords_shift_name_text=(-33, -15))
        kinematic_pairs["F"].draw_on_screen(screen, key=rotate["D_r"], size_name_text=42, coords_shift_name_text=(-33, 15))

        pygame.display.flip()
        VAR_ANGLE+=STEP_ANGLE
        if VAR_ANGLE > UPPER_LIMIT_ANGLE or VAR_ANGLE < LOWER_LIMIT_ANGLE:
            STEP_ANGLE=-STEP_ANGLE

        clock.tick(FPS)

pygame.quit()
