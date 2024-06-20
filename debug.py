import pygame

pygame.init()
font = pygame.font.Font(size=30)

def debug(info, y=10, x=10):
    display_surface = pygame.display.get_surface()
    dbg_surf = font.render(str(info), True, 'White')
    dbg_rect = dbg_surf.get_rect(topleft=(x, y))
    display_surface.blit(dbg_surf, dbg_rect)
    