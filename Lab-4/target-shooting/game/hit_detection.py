"""
hit_detection: figures out whether a click landed on a target.
"""


def check_hit(targets, click_pos):
    """
    Returns the target that was clicked, or None if the click missed
    every target.
    """
    for target in targets:
        dx = click_pos[0] - target.x
        dy = click_pos[1] - target.y

        if dx * dx + dy * dy <= target.radius * target.radius:
            return target

    return None