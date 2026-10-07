"""
GameEngine: owns the targets and handles player clicks.

Targets move continuously with different velocities and bounce
off the play-area boundaries.

The game also has a 30-second timed round with score and combo.
"""

import random
import time

from game.target import Target
from game.hit_detection import check_hit
from game.renderer import WIDTH, HEIGHT

NUM_TARGETS = 3
TARGET_RADIUS = 28
ROUND_DURATION = 30


class GameEngine:
    def __init__(self):
        self._start_round()

    def _start_round(self):
        """Start or restart a 30-second round."""

        self.targets = [self._random_target() for _ in range(NUM_TARGETS)]

        # Slow movement speeds for the starting targets
        self.velocities = [
            [1, 0.5],
            [-0.5, 1],
            [1.5, -1],
        ]

        self.hits = 0
        self.misses = 0

        # Score and combo
        self.score = 0
        self.combo = 1

        # Timer
        self.start_time = time.time()
        self.time_remaining = ROUND_DURATION
        self.game_over = False

    def _random_target(self):
        x = random.randint(TARGET_RADIUS + 10, WIDTH - TARGET_RADIUS - 10)
        y = random.randint(TARGET_RADIUS + 10, HEIGHT - TARGET_RADIUS - 10)
        return Target(x, y, radius=TARGET_RADIUS)

    def handle_click(self, pos):
        """Handle a mouse click during an active round."""

        # Ignore clicks after the round has ended
        if self.game_over:
            return

        target = check_hit(self.targets, pos)

        if target is not None:
            self.hits += 1

            # Award points based on the current combo
            self.score += 10 * self.combo

            # Increase combo after a successful hit
            self.combo += 1

            # Find the target's velocity before removing it
            index = self.targets.index(target)

            self.targets.remove(target)
            self.velocities.pop(index)

            # Add a new target
            self.targets.append(self._random_target())

            # Give the new target a slow random velocity
            new_velocity = [
                random.choice([-1.5, -1, 1, 1.5]),
                random.choice([-1.5, -1, 1, 1.5]),
            ]

            self.velocities.append(new_velocity)

        else:
            self.misses += 1

            # Reset combo after a miss
            self.combo = 1

    def update(self):
        """Update the timer and move the targets."""

        # Calculate remaining time
        elapsed = time.time() - self.start_time
        self.time_remaining = max(0, ROUND_DURATION - elapsed)

        # Stop the round when time reaches zero
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_over = True
            return

        # Move targets while the round is active
        for target, velocity in zip(self.targets, self.velocities):
            vx, vy = velocity

            # Move the target
            target.x += vx
            target.y += vy

            # Bounce off left/right boundaries
            if target.x - target.radius <= 0:
                target.x = target.radius
                velocity[0] *= -1

            elif target.x + target.radius >= WIDTH:
                target.x = WIDTH - target.radius
                velocity[0] *= -1

            # Bounce off top/bottom boundaries
            if target.y - target.radius <= 0:
                target.y = target.radius
                velocity[1] *= -1

            elif target.y + target.radius >= HEIGHT:
                target.y = HEIGHT - target.radius
                velocity[1] *= -1

    def restart(self):
        """Start a fresh round."""

        self._start_round()

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_scene(surface, self.targets)

        if self.game_over:
            renderer.draw_text(
                surface,
                font,
                f"GAME OVER!  Final Score: {self.score}",
                (10, 10),
            )
            renderer.draw_text(
                surface,
                font,
                "Press R to restart",
                (10, 40),
            )
        else:
            renderer.draw_text(
                surface,
                font,
                f"Score: {self.score}  Combo: x{self.combo}",
                (10, 10),
            )

            renderer.draw_text(
                surface,
                font,
                f"Time: {int(self.time_remaining)}",
                (10, 40),
            )