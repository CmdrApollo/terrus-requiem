import pygame

pygame.init()

FONT = pygame.font.SysFont("consolas", 20)

WIDTH, HEIGHT = 900, 900

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

planets = {
    "B2-7Z-1": "Mokra",
    "CT-98-4": "Ajaet",
    "MD-48-6": "Zandar",
    "N6-JB-3": "Terrus",
    "XA-B1-12": "XA-B1-12"
}

def main():
    clock = pygame.time.Clock()

    run = True

    view = 0 # far out

    digits = [chr(ord('0') + i) for i in range(10)] + [chr(ord('A') + i) for i in range(26)]

    while run:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                match event.unicode:
                    case '1':
                        view = 0 # far
                    case '2':
                        view = 1 # medium
                    case '3':
                        view = 2 # close
        
        mx, my = pygame.mouse.get_pos()

        x = digits[mx // (WIDTH // 36)]
        y = digits[my // (HEIGHT // 36)]

        t1 = ""
        t2 = ""

        for k, v in planets.items():
            if k[0] == x and k[3] == y:
                t1 = v
                t2 = k

        WIN.fill('#200040')

        for i in range(36):
            pygame.draw.line(WIN, 'midnightblue', (i * (WIDTH // 36), 0), (i * (WIDTH // 36), HEIGHT))
            for j in range(36):
                pygame.draw.line(WIN, 'midnightblue', (0, j * (HEIGHT // 36)), (WIDTH, j * (HEIGHT // 36)))

                for k, v in planets.items():
                    if k[0] == digits[i] and k[3] == digits[j]:
                        pygame.draw.circle(WIN, ['cyan', 'magenta', 'yellow', 'orange', 'green'][((n := sum([ord(e) for e in k])) << 16 | (n - 1)) % 5], (i * (WIDTH // 36) + (WIDTH // 72), j * (HEIGHT // 36) + (HEIGHT // 72)), 10)

        if len(t1):
            WIN.blit(fs := FONT.render(t1, True, 'white', 'black'), (mx, my - fs.get_height() * 2))
            WIN.blit(FONT.render(t2, True, 'gray', 'black'), (mx, my - fs.get_height()))

        pygame.display.flip()
    
    pygame.quit()

main()