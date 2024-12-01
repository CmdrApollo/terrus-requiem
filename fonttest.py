import pygame

FONT = pygame.image.load('bitfont.png')

def render_char(win, char, x, y, color = 'red'):
    if 0x20 <= ord(char) < 0x80:
        fx = (ord(char) - 0x20) % 0x10
        fy = (ord(char) - 0x20) // 0x10

        t = FONT.subsurface((fx * 8, fy * 8, 8, 8))
        m = pygame.mask.from_surface(t)

        f = pygame.Surface((8, 8))

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
        cx += 9

WIDTH, HEIGHT = 9 * 32 - 1, 18 * 9 - 1
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

    render_text(screen, "######################", 0, -9 + 9 , '#80ff80')
    render_text(screen, "#?????#..............#", 0, -9 + 18, '#80ff80')
    render_text(screen, "#######..............#", 0, -9 + 27, '#80ff80')
    render_text(screen, "#.............>......#", 0, -9 + 36, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 45, '#80ff80')
    render_text(screen, "#......D.............#", 0, -9 + 54, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 63, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 72, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 81, '#80ff80')
    render_text(screen, "#....................#", 0, -9 + 90, '#80ff80')
    render_text(screen, "#####........@.......#", 0, -9 + 99, '#80ff80')
    render_text(screen, "#.C..................#", 0, -9 + 108, '#80ff80')
    render_text(screen, "#...#................#", 0, -9 + 117, '#80ff80')
    render_text(screen, "######################", 0, -9 + 126, '#80ff80')
    render_text(screen, "COMMANDER, DO YOU COPY?", 0, -9 + 144, '#ff8080')
    render_text(screen, "BLAH BLAH BLAH!!!", 0, -9 + 153, '#8080ff')

    WIN.blit(pygame.transform.scale(screen, (WIDTH * 4, HEIGHT * 4)), (0, 0))

    pygame.display.flip()