import pygame
from settings import *
from player import Player

class UI:
    def __init__(self) -> None:
        # general
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # bar setup
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

    def show_bar(self, current, max, bg_rect, color):
        # bg bar
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # converting width 
        ratio = current / max
        new_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = new_width

        # drawing bar
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_exp(self, exp):
        text_surf = self.font.render(f'Exp.: {int(exp)}', False, TEXT_COLOR)
        text_rect = text_surf.get_rect(bottomright=(WIDTH - 10, HEIGTH-10))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(10, 10))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(10, 10), 3)

    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if has_switched:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    def selection_box_overlay(self, klass, has_switched, left, top, data):
        bg_rect = self.selection_box(left, top, has_switched)
        klass_surf = pygame.image.load(data[klass]['graphic']).convert_alpha()
        klass_rect = klass_surf.get_rect(center=bg_rect.center)
        self.display_surface.blit(klass_surf, klass_rect)

    def display(self, player: Player):
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)
        self.show_exp(player.exp)

        self.selection_box_overlay(player.weapon, not player.weapon_can_switch, 10, 630, weapon_settings)
        self.selection_box_overlay(player.magic, not player.magic_can_switch, 80, 635, magic_settings)
