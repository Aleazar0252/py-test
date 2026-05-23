import cv2
import mediapipe as mp
import numpy as np
import math
import random
import time


# ---------- 3D Orbital Chakra Stream ----------
# Simulates wind streams tumbling in 3D space
class OrbitalStream:
    def __init__(self):
        self.angle = random.uniform(0, 360)  # Rotation on screen
        self.phase = random.uniform(0, 2 * math.pi)  # 3D tilt phase
        self.speed_angle = random.uniform(5, 15) * random.choice([-1, 1])
        self.speed_phase = random.uniform(0.05, 0.15)
        self.arc_length = random.uniform(40, 180)
        self.thickness = random.randint(1, 3)
        self.depth_ratio = random.uniform(0.3, 1.0)  # How close to the core vs edge
        self.color = (
            255,
            random.randint(200, 255),
            random.randint(150, 255)
        )

    def draw(self, canvas, center, max_radius):
        self.angle = (self.angle + self.speed_angle) % 360
        self.phase += self.speed_phase

        # Calculate 3D illusion axes
        r = max(2, int(max_radius * self.depth_ratio))
        major_axis = r
        # Sine wave controls the minor axis, making the ring look like it's flipping in 3D
        minor_axis = max(1, int(r * abs(math.sin(self.phase))))

        cv2.ellipse(
            canvas,
            center,
            (major_axis, minor_axis),
            self.angle,
            0,
            self.arc_length,
            self.color,
            self.thickness
        )


# ---------- Volatile Chakra Sparks ----------
# Energy tearing off the Rasengan and fading out
class ChakraSpark:
    def __init__(self, center, radius):
        self.reset(center, radius)

    def reset(self, center, radius):
        angle = random.uniform(0, 2 * math.pi)
        self.x = center[0] + math.cos(angle) * (radius * 0.9)
        self.y = center[1] + math.sin(angle) * (radius * 0.9)
        # Explode outwards radially + tangentially
        self.vx = math.cos(angle) * random.uniform(2, 6) - math.sin(angle) * random.uniform(2, 5)
        self.vy = math.sin(angle) * random.uniform(2, 6) + math.cos(angle) * random.uniform(2, 5)
        self.life = 255
        self.decay = random.uniform(15, 30)
        self.size = random.randint(1, 3)

    def update_and_draw(self, canvas, center, radius):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay

        if self.life > 0:
            color = (255, 220, int(self.life))  # Fades from white -> cyan -> dark blue
            cv2.circle(canvas, (int(self.x), int(self.y)), self.size, color, -1)
        else:
            self.reset(center, radius)


# ---------- Initialize Engine ----------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

streams = [OrbitalStream() for _ in range(70)]
sparks = []
global_time = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Black canvas for additive blending
    energy_canvas = np.zeros_like(frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm = hand_landmarks.landmark
            wrist = (int(lm[0].x * w), int(lm[0].y * h))
            middle_mcp = (int(lm[9].x * w), int(lm[9].y * h))

            palm_center = (
                (wrist[0] + middle_mcp[0]) // 2,
                (wrist[1] + middle_mcp[1]) // 2 - 40
            )

            palm_dist = int(math.hypot(middle_mcp[0] - wrist[0], middle_mcp[1] - wrist[1]))
            # Unstable pulsating radius
            noise = math.sin(global_time * 0.5) * 4 + math.cos(global_time * 0.8) * 3
            radius = int(max(palm_dist * 1.2, 60) + noise)

            # 1. Ambient Room Illumination (Massive faint glow on surroundings)
            # Drawing directly on the energy canvas before the blur to spread the light
            cv2.circle(energy_canvas, palm_center, radius * 4, (40, 20, 0), -1)  # Faint blue outer
            cv2.circle(energy_canvas, palm_center, radius * 2, (80, 40, 10), -1)  # Stronger mid glow

            # 2. Outer Shell Boundary
            cv2.circle(energy_canvas, palm_center, radius, (255, 180, 50), 2)

            # 3. Draw 3D Orbital Streams
            for stream in streams:
                stream.draw(energy_canvas, palm_center, radius)

            # 4. Draw and Update Volatile Sparks
            if len(sparks) < 30:  # Maintain a pool of sparks
                sparks.append(ChakraSpark(palm_center, radius))
            for spark in sparks:
                spark.update_and_draw(energy_canvas, palm_center, radius)

            # 5. Intense Gaussian Bloom
            # Blur the canvas heavily to create the optical illusion of bright, glowing plasma
            energy_canvas = cv2.GaussianBlur(energy_canvas, (31, 31), 0)

            # 6. The Chaotic Core (Drawn after blur for pure white intensity)
            core_r = max(int(radius * 0.25), 5)
            # Violent jitter for the core
            jitter_x = random.randint(-2, 2)
            jitter_y = random.randint(-2, 2)
            jittered_center = (palm_center[0] + jitter_x, palm_center[1] + jitter_y)

            # Outer core halo
            cv2.circle(energy_canvas, jittered_center, core_r + 5, (255, 230, 150), -1)
            # Inner pure white core
            cv2.circle(energy_canvas, jittered_center, core_r, (255, 255, 255), -1)

            # Inner turbulent star (Darker blue chaotic lines inside the core)
            for _ in range(3):
                pt1 = (jittered_center[0] + random.randint(-core_r, core_r),
                       jittered_center[1] + random.randint(-core_r, core_r))
                pt2 = (jittered_center[0] + random.randint(-core_r, core_r),
                       jittered_center[1] + random.randint(-core_r, core_r))
                cv2.line(energy_canvas, pt1, pt2, (255, 150, 100), 2)

    # ----- Apply the "Light" to the Camera Feed -----
    frame = cv2.add(frame, energy_canvas)

    global_time += 1

    cv2.imshow("Ultra Anime Rasengan", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()