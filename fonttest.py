import pygame

FONT = pygame.image.load('px_font.png')

def render_char(win, char, x, y, color = 'red'):
    if 0x20 <= ord(char) < 0x80:
        fx = (ord(char) - 0x20) % 0x10
        fy = (ord(char) - 0x20) // 0x10

        t = FONT.subsurface((fx * 10, fy * 12, 10, 12))
        m = pygame.mask.from_surface(t)

        f = pygame.Surface((10, 12))

        f.fill('black')
        m2 = pygame.mask.from_surface(f)

        o = m.overlap_mask(m2, (0, 0))

        f.blit(o.to_surface(unsetcolor='black', setcolor=color), (0, 0))

        win.blit(f, (x, y))

def render_text(win, text, x, y, color = 'red'):
    cx = x
    for char in text:
        c = color
        if char == '.':
            c = 'gray'
        elif char == '#':
            c = 'lightyellow'
        elif char == '@':
            c = 'pink'
        render_char(win, char, cx, y, c)
        cx += 11

WIDTH, HEIGHT = 320, 240
WIN = pygame.display.set_mode((WIDTH * 4, HEIGHT * 4))
screen = pygame.Surface((WIDTH, HEIGHT))

clock = pygame.time.Clock()
run = True
while run:
    delta = clock.tick(0) / 1000 

    if delta:
        pygame.display.set_caption(f"{(1 / delta):.2f}fps")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    screen.fill('black')

    render_text(screen, "######################", 0, -9 + 13 , '#80ff80')
    render_text(screen, "#?????#..............#", 0, -9 + 13 * 2, '#80ff80')
    render_text(screen, "#######..............#", 0, -9 + 13 * 3, '#80ff80')
    render_text(screen, "#.............>......#", 0, -9 + 13 * 4, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 13 * 5, '#80ff80')
    render_text(screen, "#......D.............#", 0, -9 + 13 * 6, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 13 * 7, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 13 * 8, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 13 * 9, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 13 * 10, '#80ff80')
    render_text(screen, "#####........@.......#", 0, -9 + 13 * 11, '#80ff80')
    render_text(screen, "#.C..................#", 0, -9 + 13 * 12, '#80ff80')
    render_text(screen, "#...#................#", 0, -9 + 13 * 13, '#80ff80')
    render_text(screen, "######################", 0, -9 + 13 * 14, '#80ff80')
    render_text(screen, "commander, do you copy?", 0, -9 + 13 * 15, '#ff8080')
    render_text(screen, "blah blah blah!!!", 0, -9 + 13 * 16, '#8080ff')

    WIN.blit(pygame.transform.scale(screen, (WIDTH * 4, HEIGHT * 4)), (0, 0))

    pygame.display.flip()