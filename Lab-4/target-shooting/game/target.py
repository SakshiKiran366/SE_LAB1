"""
Target: a circular target the player clicks on. (x, y) is the CENTER
of the circle - this matters for how it's drawn vs. how it's hit-tested.
"""

import pygame


class Target:
    def __init__(self, x, y, radius=28, color=(230, 90, 70)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def get_bounding_rect(self):
        """A square bounding box around the circle - NOT the same
        shape as the actual circle, and easy to build incorrectly."""
        return pygame.Rect(self.x, self.y, self.radius * 2, self.radius * 2)
