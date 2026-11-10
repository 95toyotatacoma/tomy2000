"""TOMY V1.6c — geometry-based dazzled trance for the dual RGB eyes."""

from bisect import bisect_right
from dataclasses import dataclass
import math
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter


SVG_PATH = Path(__file__).with_name("trance_strands.svg")
SIZE = 128
SUPERSAMPLE = 2
FPS = 30
MOTION_SPEED = 0.55
HOLD_END = 0.10
CONTRACT_END = 0.55
SMALL_PUPIL_HOLD = 1.0
EXPANSION_DURATION = 2.0
TRACE_LEAD = 1.30
STRAND_INTERVAL = 0.59
POINT_HOLD = 0.08
TRACE_DURATION = 0.47
MOTION_RAMP = 0.18
ROTATION_SPEEDS = (0.50, -0.78, 0.62, -0.45, 0.93, -0.70, 0.75)
DIVE_SPEEDS = (3.2, 4.1, -3.6, 4.7, -4.3, 3.8, -3.1)
TOKEN = re.compile(r"[MCZ]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


@dataclass(frozen=True)
class Strand:
    # Each point stores its polar coordinates and phase along the closed loop.
    points: tuple
    arc_phases: tuple
    stroke: str
    width: int


def sample_cubics(path_data):
    """Sample the original asset's absolute M/C/Z path syntax."""
    tokens = TOKEN.findall(path_data)
    if "".join(tokens) != re.sub(r"[\s,]+", "", path_data):
        raise ValueError("Unsupported command in trance SVG path")
    if tokens[0] != "M" or tokens[-1] != "Z":
        raise ValueError("Expected a closed cubic path in trance SVG")

    start = complex(*map(float, tokens[1:3]))
    points = [start]
    cursor = 3
    while cursor < len(tokens) - 1:
        if tokens[cursor] == "C":
            cursor += 1
        x1, y1, x2, y2, x3, y3 = map(float, tokens[cursor:cursor + 6])
        p0, p1, p2, p3 = points[-1], complex(x1, y1), complex(x2, y2), complex(x3, y3)
        length = abs(p1 - p0) + abs(p2 - p1) + abs(p3 - p2)
        steps = max(8, math.ceil(length / 2.5))
        for step in range(1, steps + 1):
            t = step / steps
            u = 1 - t
            points.append(u**3 * p0 + 3 * u**2 * t * p1 + 3 * u * t**2 * p2 + t**3 * p3)
        cursor += 6
    if points[-1] != start:
        points.append(start)
    return points


def prepare_strands(svg_path=SVG_PATH):
    root = ET.parse(svg_path).getroot()
    paths = root.findall("{http://www.w3.org/2000/svg}path")
    if len(paths) != len(ROTATION_SPEEDS):
        raise ValueError(f"Expected seven original SVG paths, found {len(paths)}")

    x, y, width, height = map(float, root.attrib["viewBox"].replace(",", " ").split())
    center = complex(x + width / 2, y + height / 2)
    scale = 111 / max(width, height)
    strands = []
    for path in paths:
        points = sample_cubics(path.attrib["d"])
        distances = [0.0]
        for previous, current in zip(points, points[1:]):
            distances.append(distances[-1] + abs(current - previous))
        samples = tuple(
            (abs(point - center) * scale,
             math.atan2(point.imag - center.imag, point.real - center.real),
             math.tau * distance / distances[-1])
            for point, distance in zip(points[:-1], distances)
        )
        stroke_width = float(path.get("stroke-width", "1"))
        strands.append(Strand(samples, tuple(sample[2] for sample in samples) + (math.tau,),
                              path.attrib["stroke"],
                              max(2, round(stroke_width * scale * SUPERSAMPLE))))
    return strands


def deform_strand(strand, index, elapsed, eye_phase):
    phase = index * 2.39996 + eye_phase * (1 + index * 0.13)
    rotation = (ROTATION_SPEEDS[index] * elapsed + phase
                + 0.24 * math.sin(2.6 * elapsed + phase))
    travel = DIVE_SPEEDS[index] * elapsed + phase
    strength = 0.68 + 0.38 * math.sin(2.1 * elapsed + phase)
    drift_x = 6 * math.sin(2.0 * elapsed + phase)
    drift_y = 6 * math.cos(2.3 * elapsed - phase)
    points = []
    for radius, angle, along in strand.points:
        wave = along - travel
        # A narrow packet travels around the loop. It can pull a section
        # past the center while the rest of the strand keeps rotating.
        dive = (0.5 + 0.5 * math.cos(wave)) ** 5
        bent_radius = radius * (0.95 + 0.09 * math.sin(2 * along + travel))
        bent_radius -= dive * strength * (0.88 * radius + 13)
        bent_angle = angle + rotation + 0.26 * math.sin(2 * along - travel)
        bent_angle += 1.25 * dive * math.sin(wave + 0.7)
        points.append((
            (SIZE / 2 + drift_x + bent_radius * math.cos(bent_angle)) * SUPERSAMPLE,
            (SIZE / 2 + drift_y + bent_radius * math.sin(bent_angle)) * SUPERSAMPLE,
        ))
    return points


def smoothstep(progress):
    progress = max(0.0, min(1.0, progress))
    return progress * progress * (3 - 2 * progress)


def trace_strand(draw, strand, points, progress):
    distance = progress * math.tau
    index = bisect_right(strand.arc_phases, distance) - 1
    start, end = strand.arc_phases[index:index + 2]
    fraction = (distance - start) / (end - start)
    x, y = points[index]
    next_x, next_y = points[index + 1]
    tip = (x + fraction * (next_x - x), y + fraction * (next_y - y))
    draw.line(points[:index + 1] + [tip], fill=strand.stroke, width=strand.width)

    # The luminous point shrinks into the stroke as the loop closes.
    radius = strand.width / 2 + SUPERSAMPLE * (1 - progress)
    head_color = tuple(round(channel + (255 - channel) * 0.6 * (1 - progress))
                       for channel in ImageColor.getrgb(strand.stroke))
    x, y = tip
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=head_color)


def strand_motion_time(time_since_closing):
    motion = max(0.0, time_since_closing)
    # Integrate a short linear speed ramp, then keep the tuned trance pace.
    if motion < MOTION_RAMP:
        return motion**2 / (2 * MOTION_RAMP)
    return motion - MOTION_RAMP / 2


def render_trance(strands, elapsed, eye_index, reveal_elapsed=math.inf):
    eye_phase = eye_index * 1.73
    eye_speed = MOTION_SPEED * (1 + eye_index * 0.037)
    revealing = math.isfinite(reveal_elapsed)
    layer = Image.new("RGB", (SIZE * SUPERSAMPLE, SIZE * SUPERSAMPLE))
    draw = ImageDraw.Draw(layer)
    for index, strand in enumerate(strands):
        strand_time = reveal_elapsed - index * STRAND_INTERVAL
        if strand_time < 0:
            continue
        motion = strand_motion_time(strand_time - POINT_HOLD - TRACE_DURATION) if revealing else elapsed
        points = deform_strand(strand, index, motion * eye_speed, eye_phase)
        points.append(points[0])
        progress = max(0.0, (strand_time - POINT_HOLD) / TRACE_DURATION)
        if progress < 1:
            trace_strand(draw, strand, points, progress)
        else:
            draw.line(points, fill=strand.stroke, width=strand.width)

    core = layer.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    glow = core.filter(ImageFilter.GaussianBlur(1.6))
    return ImageChops.add(core, glow, scale=1.0)


class TranceTransition:
    """Produce unrotated eye frames while the behavior system requests trance.

    The caller owns the display loop and orientation. On entry, it supplies a
    renderer bound to a snapshot of the current normal eyes. That renderer
    accepts (eye_index, pupil_scale) and returns a 128x128 RGB image.
    """

    def __init__(self, strands):
        self.strands = strands
        self.started_at = None
        self.frozen_eyes = None

    def enter(self, now, frozen_eyes):
        if self.started_at is None:
            self.started_at = now
            self.frozen_eyes = frozen_eyes

    def leave(self):
        self.started_at = None
        self.frozen_eyes = None

    def render(self, now, eye_index):
        """Return None when normal expressions should own the display."""
        if self.started_at is None:
            return None

        elapsed = now - self.started_at
        if elapsed < CONTRACT_END:
            contraction = smoothstep((elapsed - HOLD_END) / (CONTRACT_END - HOLD_END))
            return self.frozen_eyes(eye_index, 1 - 0.82 * contraction)

        expansion = elapsed - CONTRACT_END - SMALL_PUPIL_HOLD
        reveal_elapsed = expansion - (EXPANSION_DURATION - TRACE_LEAD)
        if expansion < EXPANSION_DURATION:
            growth = smoothstep(expansion / EXPANSION_DURATION)
            # A 120px radius covers even the far corner of an off-center eye.
            normal = self.frozen_eyes(eye_index, 0.18 + (2.7 - 0.18) * growth)
            if reveal_elapsed < 0:
                return normal
            strands = render_trance(self.strands, 0.0, eye_index, reveal_elapsed)
            darkness = normal.convert("L").point([255] + [0] * 255)
            return Image.composite(strands, normal, darkness)

        return render_trance(self.strands, 0.0, eye_index, reveal_elapsed)


def main():
    strands = prepare_strands()
    # Import the hardware driver only when running on the Pi.
    import rgb_dual_eyes as rgb

    eyes = []
    try:
        for config in rgb.EYES:
            eyes.append(rgb.EyeDisplay(config))

        print("TOMY V1.6c dazzled trance. Press Ctrl+C to stop.")
        start = time.monotonic()
        while True:
            frame_start = time.monotonic()
            elapsed = frame_start - start
            for index, eye in enumerate(eyes):
                frame = render_trance(strands, elapsed, index)
                if index == 1:
                    frame = frame.transpose(Image.Transpose.ROTATE_180)
                eye.show(frame)

            remaining = 1 / FPS - (time.monotonic() - frame_start)
            if remaining > 0:
                time.sleep(remaining)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            for eye in eyes:
                eye.close()
        finally:
            rgb.lgpio.gpiochip_close(rgb.gpio)


if __name__ == "__main__":
    main()
