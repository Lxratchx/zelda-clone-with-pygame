import pygame
from settings import *
from support import *

class Upgrade:
    def __init__(self, player) -> None:
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.attr_number = len(player.stats)
        self.attr_names = list(player.stats.keys())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # selection sys
        self.selection_index = 0
        self.selection_time = 0
        self.selection_can_move = True
        self.selection_cooldown = 300

        # items dimensions
        self.height = self.display_surface.get_size()[1] * .8
        self.width = self.display_surface.get_size()[0] // 6

        self.items_list: list[Item] = self.create_items()

    
    def inputs(self):
        if not self.selection_can_move:
            return
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and self.selection_index < self.attr_number - 1:
            self.selection_index += 1
            self.selection_can_move = False
            self.selection_time = pygame.time.get_ticks()

        elif keys[pygame.K_LEFT] and self.selection_index > 0:
            self.selection_index -= 1
            self.selection_can_move = False
            self.selection_time = pygame.time.get_ticks()

        elif keys[pygame.K_SPACE]:
            self.selection_can_move = False
            self.selection_time = pygame.time.get_ticks()
            self.items_list[self.selection_index].trigger(self.player)

    def selection_move_cooldown(self):
        current_time = pygame.time.get_ticks()
        cooldown_ends = current_time - self.selection_time >= self.selection_cooldown
        if not self.selection_can_move and cooldown_ends:
            self.selection_can_move = True

    def create_items(self):
        items_list = []
        for i in range(self.attr_number):
            top = self.display_surface.get_size()[1] * .1

            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.attr_number
            left = (increment * i) + (increment - self.width) // 2
            item = Item(left, top, self.width, self.height, i, self.font)
            items_list.append(item)
        return items_list

    def display(self):
        self.inputs()
        self.selection_move_cooldown()
        

        for index, item in enumerate(self.items_list):
            name = self.attr_names[index]
            value = self.player.stats[name]
            max = self.player.max_stats[name]
            cost = self.player.upgrade_cost[name]
            item.display(self.display_surface, self.selection_index, name, value, max, cost)


class Item:
    def __init__(self, l, t, w, h, index, font):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font
    
    def display_names(self, surface, name, cost, selected):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        title = self.font.render(name, False, color)
        title_rect = title.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

        cost_surf = self.font.render(str(int(cost)), False, color)
        cost_rect = cost_surf.get_rect(midtop=self.rect.midbottom + pygame.math.Vector2(0, -30))

        surface.blit(title, title_rect)
        surface.blit(cost_surf, cost_rect)
    
    def display_bar(self, surface, value, max_value, selected):
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom + pygame.math.Vector2(0, -60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        full_h = bottom[1] - top[1]
        relative_size = value / max_value * full_h
        value_rect = pygame.Rect(top[0]-15, bottom[1]-relative_size, 30, 10)

        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)
    
    def trigger(self, player):
        up_attr = list(player.stats.keys())[self.index]
        up_cost = player.upgrade_cost[up_attr]
        print(up_attr, up_cost)
        if player.exp >= up_cost and player.stats[up_attr] < player.max_stats[up_attr]:
            player.exp -= up_cost
            player.stats[up_attr] *= 1.2
            player.upgrade_cost[up_attr] *= 1.4
        
        if player.stats[up_attr] > player.max_stats[up_attr]:
            player.stats[up_attr] = player.max_stats[up_attr]

    def display(self, surface, selection_num, name, value, max, cost):
        selected = self.index == selection_num
        if selected:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
            
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, cost, selected)
        self.display_bar(surface, value, max, selected)