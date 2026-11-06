"""Snake state, movement, collision detection, and rendering."""

import math

import pygame

from board import grid_to_pixel
from settings import (
    BOARD_COLUMNS,
    BOARD_ROWS,
    CELL_SIZE,
    DIRECTIONS,
    MAX_QUEUED_TURNS,
    MOVEMENT_SPEED,
    OPPOSITE_DIRECTIONS,
    SNAKE_COLOR,
    TURN_GRACE_DISTANCE,
)


class Snake:
    """A smooth snake with a short, pivot-based late-turn grace window."""

    def __init__(self, sound_effects=None):
        self.sound_effects = sound_effects

        # Logical tile positions, head first. Used for food and collisions.
        self.body = [
            (8, 7),
            (7, 7),
            (6, 7),
            (5, 7),
        ]

        self.direction = "RIGHT"
        self.turn_queue = []
        self.movement_progress = 0.0
        self.started = False

        # A late turn can only be used once at each tile intersection.
        self.late_turn_used = False

        # During a late turn, the head rotates around the last tile center.
        self.turn_arc = None

        # Continuous pixel position of the head.
        self.head_position = tuple(map(float, grid_to_pixel(self.body[0])))

        # Head-to-tail movement history, newest point first. The renderer
        # samples this trail at CELL_SIZE intervals to keep body length steady.
        self.trail = [
            tuple(map(float, grid_to_pixel(position)))
            for position in self.body
        ]
        self.trail.append(tuple(map(float, grid_to_pixel((4, 7)))))

    def _play_turn_sound(self):
        if self.sound_effects is not None:
            self.sound_effects.play_turn()

    def _planned_direction(self):
        """Return the last direction already committed or queued."""
        if self.turn_queue:
            return self.turn_queue[-1]
        if self.turn_arc is not None:
            return self.turn_arc["new_direction"]
        return self.direction

    def request_direction(self, requested_direction):
        """Accept a turn, including a brief grace period just after a tile."""
        reference_direction = self._planned_direction()

        # Never allow a 180-degree turn into the snake's own body.
        if requested_direction == OPPOSITE_DIRECTIONS[reference_direction]:
            return

        if not self.started:
            self.direction = requested_direction
            self.started = True
            return

        if requested_direction == reference_direction:
            return

        # If another turn is already in progress or queued, keep this one
        # behind it rather than trying to pivot twice around the same tile.
        if self.turn_arc is not None or self.turn_queue:
            if len(self.turn_queue) < MAX_QUEUED_TURNS:
                self.turn_queue.append(requested_direction)
            return

        # Coyote-time equivalent: a turn can still belong to the tile center
        # we just passed, but only during a very short grace window.
        if (
                not self.late_turn_used
                and self.movement_progress <= TURN_GRACE_DISTANCE
        ):
            self._start_late_turn(requested_direction)
            return

        # Outside the grace window, schedule the turn for the next tile.
        if len(self.turn_queue) < MAX_QUEUED_TURNS:
            self.turn_queue.append(requested_direction)

    def _start_late_turn(self, new_direction):
        """Rotate the head around the most recently reached tile center.

        The neck/pivot stays at the tile center while the head follows a
        quarter-circle to the new direction. The body follows the recorded
        curve, avoiding a visible position snap.
        """
        radius = self.movement_progress

        if radius <= 0.5:
            # The input arrived essentially at the intersection.
            self.direction = new_direction
            self.late_turn_used = True
            self._play_turn_sound()
            return

        old_dx, old_dy = DIRECTIONS[self.direction]
        new_dx, new_dy = DIRECTIONS[new_direction]

        start_angle = math.atan2(old_dy, old_dx)
        cross = old_dx * new_dy - old_dy * new_dx
        dot = old_dx * new_dx + old_dy * new_dy
        angle_delta = math.atan2(cross, dot)  # +/- 90 degrees

        pivot = tuple(map(float, grid_to_pixel(self.body[0])))
        duration = abs(angle_delta) * radius / MOVEMENT_SPEED

        self.turn_arc = {
            "pivot": pivot,
            "radius": radius,
            "start_angle": start_angle,
            "angle_delta": angle_delta,
            "elapsed": 0.0,
            "duration": duration,
            "new_direction": new_direction,
        }

        self.late_turn_used = True
        self._play_turn_sound()

    def _is_heading_into_wall(self):
        """Check whether the head is at an edge tile and facing outwards."""
        head_x, head_y = self.body[0]
        dx, dy = DIRECTIONS[self.direction]

        return (
                (head_x == 0 and dx == -1)
                or (head_x == BOARD_COLUMNS - 1 and dx == 1)
                or (head_y == 0 and dy == -1)
                or (head_y == BOARD_ROWS - 1 and dy == 1)
        )

    def _record_head_position(self):
        """Add the current head position to the visual movement trail."""
        point = (float(self.head_position[0]), float(self.head_position[1]))

        if self.trail:
            previous = self.trail[0]
            if math.hypot(point[0] - previous[0], point[1] - previous[1]) < 0.01:
                return

        self.trail.insert(0, point)

        # Keep enough history for the whole snake plus a small safety margin.
        max_distance = (len(self.body) + 3) * CELL_SIZE + TURN_GRACE_DISTANCE
        accumulated = 0.0

        for index in range(len(self.trail) - 1):
            first = self.trail[index]
            second = self.trail[index + 1]
            accumulated += math.hypot(
                first[0] - second[0],
                first[1] - second[1],
            )

            if accumulated > max_distance:
                del self.trail[index + 2:]
                break

    def _enter_next_tile(self, food_position):
        """Update the logical snake by one tile. Return (ate_food, error)."""
        head_x, head_y = self.body[0]
        dx, dy = DIRECTIONS[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # Check board boundaries.
        if not (0 <= new_head[0] < BOARD_COLUMNS and 0 <= new_head[1] < BOARD_ROWS):
            return False, "Game Over!"

        ate_food = new_head == food_position

        # The tail vacates its tile during a normal move, so it is safe to
        # enter that tile unless the snake is eating on this move.
        body_to_check = self.body[1:] if ate_food else self.body[1:-1]
        if new_head in body_to_check:
            return False, "Game Over!"

        self.body.insert(0, new_head)
        if not ate_food:
            self.body.pop()

        # A new tile center has been reached; a new late-turn window begins.
        self.late_turn_used = False

        # Apply a previously queued turn at this intersection.
        if self.turn_queue:
            self.direction = self.turn_queue.pop(0)
            self.late_turn_used = True
            self._play_turn_sound()

        return ate_food, None

    def update(self, delta_time, food_position):
        """Advance movement. Return (ate_food, end_message)."""
        if not self.started:
            return False, None

        remaining_time = max(0.0, delta_time)
        ate_food = False
        epsilon = 1e-7

        # Process a late-turn arc first. The neck remains at the pivot while
        # the head rotates around it, then continues straight in the new path.
        while remaining_time > epsilon:
            if self.turn_arc is not None:
                arc = self.turn_arc
                time_left = arc["duration"] - arc["elapsed"]
                time_step = min(remaining_time, time_left)

                arc["elapsed"] += time_step
                remaining_time -= time_step

                progress = min(1.0, arc["elapsed"] / arc["duration"])
                angle = arc["start_angle"] + arc["angle_delta"] * progress

                pivot_x, pivot_y = arc["pivot"]
                radius = arc["radius"]
                self.head_position = (
                    pivot_x + math.cos(angle) * radius,
                    pivot_y + math.sin(angle) * radius,
                )
                self._record_head_position()

                if progress >= 1.0 - epsilon:
                    self.direction = arc["new_direction"]
                    self.turn_arc = None
                else:
                    # The arc is still in progress; wait for the next frame.
                    break

                continue

            # If the head is on an edge tile and facing outwards, end before
            # drawing even a fraction of a tile beyond the wall.
            if self._is_heading_into_wall():
                return False, "Game Over!"

            distance_to_center = CELL_SIZE - self.movement_progress
            distance_this_step = min(
                MOVEMENT_SPEED * remaining_time,
                distance_to_center,
            )

            if distance_this_step <= epsilon:
                break

            dx, dy = DIRECTIONS[self.direction]
            head_x, head_y = self.head_position
            self.head_position = (
                head_x + dx * distance_this_step,
                head_y + dy * distance_this_step,
            )

            self.movement_progress += distance_this_step
            remaining_time -= distance_this_step / MOVEMENT_SPEED
            self._record_head_position()

            # A tile center was reached. Update collisions and food only here.
            if self.movement_progress >= CELL_SIZE - epsilon:
                self.movement_progress = max(
                    0.0,
                    self.movement_progress - CELL_SIZE,
                )

                ate_food, error = self._enter_next_tile(food_position)
                if error is not None:
                    return False, error

                if ate_food:
                    return True, None

        return ate_food, None

    def _position_at_distance(self, distance):
        """Return a point a given pixel distance behind the head on its trail."""
        remaining = max(0.0, distance)

        for index in range(len(self.trail) - 1):
            first = self.trail[index]
            second = self.trail[index + 1]
            segment_length = math.hypot(
                second[0] - first[0],
                second[1] - first[1],
            )

            if segment_length <= 1e-8:
                continue

            if remaining <= segment_length:
                fraction = remaining / segment_length
                return (
                    first[0] + (second[0] - first[0]) * fraction,
                    first[1] + (second[1] - first[1]) * fraction,
                )

            remaining -= segment_length

        return self.trail[-1]

    def draw(self, screen):
        """Draw a smooth body by sampling its recorded path at fixed intervals."""
        tail_distance = (len(self.body) - 1) * CELL_SIZE
        body_points = [self.trail[0]]
        distance_from_head = 0.0

        # Include every recorded bend between the head and tail.
        for index in range(len(self.trail) - 1):
            first = self.trail[index]
            second = self.trail[index + 1]
            segment_length = math.hypot(
                second[0] - first[0],
                second[1] - first[1],
            )

            if distance_from_head + segment_length < tail_distance:
                body_points.append(second)
                distance_from_head += segment_length
            else:
                remaining = tail_distance - distance_from_head
                if segment_length > 1e-8 and remaining > 0:
                    fraction = remaining / segment_length
                    tail_point = (
                        first[0] + (second[0] - first[0]) * fraction,
                        first[1] + (second[1] - first[1]) * fraction,
                    )
                    body_points.append(tail_point)
                break

        # A thick line plus round joins gives the snake a continuous shape.
        if len(body_points) > 1:
            pygame.draw.lines(
                screen,
                SNAKE_COLOR,
                False,
                [(round(x), round(y)) for x, y in body_points],
                CELL_SIZE,
            )

        for x, y in body_points:
            pygame.draw.circle(
                screen,
                SNAKE_COLOR,
                (round(x), round(y)),
                CELL_SIZE // 2,
            )
