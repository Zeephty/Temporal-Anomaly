import pygame
from scenes import StageCenter


if __name__ == '__main__':
    # Инициализация
    pygame.init()
    clock = pygame.time.Clock()   

    run = True

    # Размер окна
    size = pygame.display.Info().current_w, pygame.display.Info().current_h

    # Создание окна
    win = pygame.display.set_mode(size)
    pygame.display.set_caption("Mission Impossible")

    # FPS
    fps = 60

    # Основная система сцен
    core = StageCenter(win)

    # Основной цикл
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # События мыши
            if event.type == pygame.MOUSEMOTION:
                core.mouse_motion(*event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                core.mouse_down(*event.pos)

            if event.type == pygame.MOUSEBUTTONUP:
                core.mouse_up(*event.pos)
            
            # Дополнительные события
            core.event_additional(event)
        
        # Обновление
        core.update()

        # Отрисовка
        core.draw(win)        

        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()