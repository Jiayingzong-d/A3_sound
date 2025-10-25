# -*- coding: utf-8 -*-
# Ambient Vortex + Emotional Ripples + Mic Interaction

import os, sys, math, random, wave, datetime
import numpy as np
import pygame
from mic_input import MicInput  

# ========= Basic parameters=========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_PATH = os.path.join(SCRIPT_DIR, "audio", "track.wav")
EXPORT_DIR = os.path.join(SCRIPT_DIR, "exports")
WIN_W, WIN_H = 1280, 720
CENTER = (WIN_W // 2, WIN_H // 2)

# Vortex/Movement
BASE_RADIUS        = 180
RADIUS_VARIATION   = 0.06
ROT_BASE           = 0.00055
ROT_MUSIC_FACTOR   = 0.0085
TYPING_SLOW_FACTOR = 0.22
GLOW_ALPHA         = 90

# color
PALETTES = [(180,40),(195,38),(210,42),(165,45),(155,48),(250,40),(265,42),(325,45),(345,48)]
COLOR_V_MIN, COLOR_V_MAX = 92, 100

# punctuation (the spacebar remains as a function key)
ALLOWED_PUNCT = set(".,!?;:'\"-_/\\()[]{}+=*&%@$#~^|<>")
LINE_SPACING = 44
SEP_DOT_ALPHA = 85
SEP_DOT_RADIUS = 2

# ========= Initialize Pygame =========
SR, BITS, CH = 44100, -16, 1
pygame.mixer.pre_init(SR, BITS, CH, 512)
pygame.init()
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Ambient Vortex + Emotional Ripples + Mic Input")
clock = pygame.time.Clock()
font_char = pygame.font.SysFont("Avenir Next", 30) or pygame.font.SysFont("Arial", 30)

# ========= Initialize microphone monitoring=========
mic = MicInput(device_index=2, sensitivity=0.03, smooth=0.8)
mic.start()

# ========= Read WAV =========
def read_wav_mono_16bit(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"未找到音频文件: {path}")
    wf = wave.open(path, "rb")
    ch, sr, sw, n = wf.getnchannels(), wf.getframerate(), wf.getsampwidth(), wf.getnframes()
    raw = wf.readframes(n); wf.close()
    if sw != 2: raise RuntimeError("请提供 16-bit PCM WAV")
    a = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    if ch == 2: a = a.reshape(-1,2).mean(axis=1)
    return a, sr, n

try:
    audio, sr_wav, nframes = read_wav_mono_16bit(AUDIO_PATH)
    total_len_ms = (len(audio)/sr_wav) * 1000.0
except Exception as e:
    print("音频加载错误：", e); sys.exit(1)

# ========= FFT analysis =========
N_FFT = 2048
HOP   = N_FFT//2
if len(audio) < N_FFT + HOP:
    audio = np.pad(audio, (0, N_FFT + HOP - len(audio)))
pad = (-len(audio)) % HOP
if pad: audio = np.pad(audio, (0, pad))
num_frames = 1 + (len(audio) - N_FFT)//HOP
frames = np.lib.stride_tricks.as_strided(audio, shape=(num_frames, N_FFT),
                                         strides=(audio.strides[0]*HOP, audio.strides[0]), writeable=False)
window = np.hanning(N_FFT).astype(np.float32)
freqs  = np.fft.rfftfreq(N_FFT, 1.0/sr_wav)
low_mask  = freqs < 200
mid_mask  = (freqs >= 200) & (freqs < 2000)
high_mask = freqs >= 2000
# ========= Normalization function =========
def norm01(a):
    a = np.asarray(a, dtype=np.float32)
    if a.size == 0: return a
    p95 = np.percentile(a, 95)
    return np.clip(a/(p95+1e-9), 0, 1)

low_arr, mid_arr, high_arr = [], [], []
for f in frames:
    mag = np.abs(np.fft.rfft(f*window, n=N_FFT))
    low_arr.append(  mag[low_mask].mean()  if low_mask.any()  else 0.0)
    mid_arr.append(  mag[mid_mask].mean()  if mid_mask.any()  else 0.0)
    high_arr.append( mag[high_mask].mean() if high_mask.any() else 0.0)
low_arr, mid_arr, high_arr = map(norm01, [low_arr, mid_arr, high_arr])
FRAME_MS = 1000.0 * HOP / sr_wav

# ========= Music playback control =========
pygame.mixer.music.load(AUDIO_PATH)
pygame.mixer.music.set_volume(0.0)
pygame.mixer.music.play(loops=0)
music_state = "fading_in"   # "fading_in","playing","fading_out","paused","ended"
music_vol = 0.0
FADE_SPEED = 0.006

def update_music_fade():
    global music_vol, music_state
    if music_state == "fading_in":
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(loops=0)
        music_vol = min(1.0, music_vol + FADE_SPEED)
        pygame.mixer.music.set_volume(music_vol)
        if music_vol >= 1.0: music_state = "playing"
    elif music_state == "fading_out":
        music_vol = max(0.0, music_vol - FADE_SPEED)
        pygame.mixer.music.set_volume(music_vol)
        if music_vol <= 0.0:
            pygame.mixer.music.pause(); music_state = "paused"
    elif music_state in ("paused","ended"):
        pygame.mixer.music.set_volume(0.0)

# ========= Ripple emotional ripples =========
VOWELS = set(list("AEIOUaeiou"))
ALLOWED_PUNCT = set(".,!?;:'\"-_/\\()[]{}+=*&%@$#~^|<>")

def char_emotion(ch):
    if ch.isdigit():
        return {"h":200, "s":20, "v":96, "amp":0.9, "thick":3}
    if ch in VOWELS:
        return {"h":330, "s":45, "v":98, "amp":0.6, "thick":4}
    if ch in ALLOWED_PUNCT:
        return {"h":260, "s":50, "v":97, "amp":1.3, "thick":2}
    return {"h":195, "s":40, "v":96, "amp":0.8, "thick":3}

class Ripple:
    def __init__(self, ch, t_ms, cx, cy):
        emo = char_emotion(ch)
        self.h,self.s,self.v = emo["h"], emo["s"], emo["v"]
        self.amp = emo["amp"]
        self.thick = emo["thick"]
        self.birth = t_ms
        self.life = 2500
        self.base_r = 40
        self.noise_seed = random.random()*1000
        self.cx, self.cy = int(cx), int(cy)

    def alive(self, t_ms):
        return (t_ms - self.birth) < self.life

    def draw(self, surf, t_ms, low_energy, high_energy):
        age = max(0.0, t_ms - self.birth)
        k = age / self.life
        r = self.base_r + k*(min(WIN_W,WIN_H)*0.55) * (0.9 + 0.25*low_energy)
        alpha = int(140 * (1.0 - k)**1.2)
        if alpha <= 0: return
        seg = 120
        jitter = (4 + 18*high_energy) * self.amp
        pts = []
        for i in range(seg):
            ang = (i/seg) * math.tau
            jr = math.sin(ang*8 + self.noise_seed) * jitter
            rr = max(1, r + jr)
            x = int(self.cx + math.cos(ang)*rr)
            y = int(self.cy + math.sin(ang)*rr)
            pts.append((x,y))
        col = pygame.Color(0); col.hsva = (self.h, self.s, self.v, 100)
        for t in range(self.thick):
            pygame.draw.polygon(surf, (col.r, col.g, col.b, max(20, alpha- t*15)), pts, width=1)
            # ========= Environmental breathing waves =========
def draw_ambient_breath(surface, t_ms, low_energy, high_energy):
    mist = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    base_r = 120 + 90*low_energy
    for i, (scale, a) in enumerate([(1.0, 26), (1.5, 18), (2.2, 12)]):
        r = int(base_r*scale)
        seg = 64
        pts = []
        jitter = 3 + 10*high_energy
        seed = (t_ms*0.001 + i*3.14)
        for k in range(seg):
            ang = (k/seg)*math.tau
            rr = r + math.sin(ang*6 + seed)*jitter
            x = int(CENTER[0] + math.cos(ang)*rr)
            y = int(CENTER[1] + math.sin(ang)*rr)
            pts.append((x,y))
        col = (210,225,255,a)
        pygame.draw.polygon(mist, col, pts, width=1)
    surface.blit(mist, (0,0), special_flags=pygame.BLEND_PREMULTIPLIED)

# ========= Character logic =========
class Glyph:
    def __init__(self, ch, layer_idx, total_layers):
        self.ch = ch
        self.layer_idx = layer_idx
        self.total_layers = max(1, total_layers)
        hue, sat = random.choice(PALETTES)
        self.hue, self.sat = float(hue), float(sat)
        self.val = random.uniform(COLOR_V_MIN, COLOR_V_MAX)
        self.arm_id    = random.randint(0, 3)
        self.arm_phase = random.random() * math.tau
        self.angle_ofs = random.random() * math.tau
        self.radius_j  = random.uniform(-20, 20)
        self.x, self.y = CENTER
        self.alpha     = GLOW_ALPHA

    def target_vortex(self, global_rot, base_radius, radius_scale):
        layer_ratio = (self.layer_idx + 1) / self.total_layers
        twist = 0.85 + 0.38 * self.arm_id
        ang = self.angle_ofs + global_rot * (twist + 0.25*layer_ratio) + self.arm_phase
        base_r = base_radius * (0.70 + 0.65*layer_ratio)
        r = base_r * (1.0 + radius_scale) + self.radius_j
        return CENTER[0] + math.cos(ang)*r, CENTER[1] + math.sin(ang)*r

    def target_line(self, idx_in_line, total_in_line):
        spacing = LINE_SPACING
        total_w = (total_in_line-1)*spacing if total_in_line>1 else 0
        x0 = CENTER[0] - total_w/2
        return x0 + idx_in_line*spacing, CENTER[1]

    def update(self, mode, global_rot, base_radius, radius_scale, line_idx=0, line_total=1, freeze=False):
        if mode == "line":
            tx, ty = self.target_line(line_idx, line_total); k = 0.12 if not freeze else 0.0
        else:
            tx, ty = self.target_vortex(global_rot, base_radius, radius_scale); k = 0.09 if not freeze else 0.0
        self.x += (tx - self.x) * k; self.y += (ty - self.y) * k

    def draw(self, surface, faded=False):
        v = int(self.val if not faded else max(50, self.val-30))
        col = pygame.Color(0); col.hsva = (self.hue, self.sat, v, 100)
        text = font_char.render(self.ch, True, col)
        glow = pygame.Surface((text.get_width()+10, text.get_height()+10), pygame.SRCALPHA)
        glow.blit(text, (5,5)); glow.set_alpha(self.alpha if not faded else max(20, self.alpha-40))
        surface.blit(glow, (self.x - text.get_width()/2, self.y - text.get_height()/2))
        col2 = pygame.Color(0); col2.hsva = (self.hue, max(0, self.sat-5), min(100, v+2), 100)
        txt2 = font_char.render(self.ch, True, col2)
        surface.blit(txt2, (self.x - txt2.get_width()/2, self.y - txt2.get_height()/2))

# ========= Vortex character set =========
base_chars = list("SLOWHEAT")
live_chars = []
glyphs_vortex, glyphs_line = [], []

def rebuild_vortex():
    global glyphs_vortex
    glyphs_vortex = []
    total = max(1, len(base_chars))
    for i, c in enumerate(base_chars):
        glyphs_vortex.append(Glyph(c, i, total))

def rebuild_line():
    global glyphs_line
    glyphs_line = []
    total = max(1, len(live_chars))
    for i, c in enumerate(live_chars):
        glyphs_line.append(Glyph(c, i, total))

rebuild_vortex(); rebuild_line()
# ========= State variables =========
global_rot = 0.0
lo_s = mi_s = hi_s = 0.0
SMOOTH = 0.86
ROT_SPEED_SCALE = 1.0
last_pos_ms = 0
layout_mode = "vortex"
ripples = []
mouse_ripple_cool = 0

def save_screenshot():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(EXPORT_DIR, f"shot_{ts}.png")
    pygame.image.save(screen, path)
    print("Saved screenshot:", path)

def allowed_char(ch: str) -> bool:
    return (ch.isalnum()) or (ch in ALLOWED_PUNCT)

# ========= Main loop =========
running = True
mic_trigger_timer = 0  # Prevent excessive voice ripple generation

while running:
    dt = clock.tick(60)
    mouse_ripple_cool = max(0, mouse_ripple_cool - dt)
    mic_trigger_timer = max(0, mic_trigger_timer - dt)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            t_ms = pygame.mixer.music.get_pos()
            if t_ms < 0: t_ms = pygame.time.get_ticks()
            mx, my = pygame.mouse.get_pos()
            ripples.append(Ripple('*', t_ms, mx, my))
        elif e.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            if mouse_ripple_cool == 0:
                t_ms = pygame.mixer.music.get_pos()
                if t_ms < 0: t_ms = pygame.time.get_ticks()
                mx, my = pygame.mouse.get_pos()
                ripples.append(Ripple('-', t_ms, mx, my))
                mouse_ripple_cool = 45
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            elif e.key == pygame.K_UP:
                music_state = "fading_out"
            elif e.key == pygame.K_DOWN:
                music_state = "fading_in"
            elif e.key == pygame.K_LEFTBRACKET:
                ROT_SPEED_SCALE = max(0.1, ROT_SPEED_SCALE*0.85)
            elif e.key == pygame.K_RIGHTBRACKET:
                ROT_SPEED_SCALE = min(3.0, ROT_SPEED_SCALE*1.15)
            elif e.key == pygame.K_SPACE:
                if live_chars:
                    base_chars.extend(live_chars)
                    live_chars.clear()
                    rebuild_vortex(); rebuild_line()
                layout_mode = "vortex"
            elif e.key == pygame.K_RETURN:
                save_screenshot()
            elif e.key == pygame.K_BACKSPACE:
                if layout_mode == "line":
                    if live_chars: live_chars.pop(); rebuild_line()
                else:
                    if base_chars: base_chars.pop(); rebuild_vortex()
            else:
                ch = e.unicode
                if ch and allowed_char(ch):
                    live_chars.append(ch)
                    rebuild_line()
                    layout_mode = "line"
                    t_ms = pygame.mixer.music.get_pos()
                    if t_ms < 0: t_ms = pygame.time.get_ticks()
                    ripples.append(Ripple(ch, t_ms, CENTER[0], CENTER[1]))

    # ===== Background =====
    screen.fill((10,12,18))
    update_music_fade()

    pos_ms = pygame.mixer.music.get_pos()
    if pos_ms < 0: pos_ms = last_pos_ms
    else: last_pos_ms = pos_ms
    if pos_ms >= total_len_ms - 5 and music_state != "ended":
        music_state = "ended"

    idx = max(0, min(int(pos_ms / FRAME_MS), len(low_arr)-1))
    lo = float(low_arr[idx]); mi = float(mid_arr[idx]); hi = float(high_arr[idx])
    lo_s = lo_s*SMOOTH + lo*(1-SMOOTH)
    mi_s = mi_s*SMOOTH + mi*(1-SMOOTH)
    hi_s = hi_s*SMOOTH + hi*(1-SMOOTH)

    if music_state in ("playing","fading_in"):
        base_speed = ROT_BASE + mi_s*ROT_MUSIC_FACTOR
        if layout_mode == "line": base_speed *= TYPING_SLOW_FACTOR
        global_rot += base_speed * ROT_SPEED_SCALE * dt
        freeze = False
    else:
        freeze = True

    radius_scale = (lo_s - 0.4) * RADIUS_VARIATION

    # ===== Environmental breathing =====
    t_now = pygame.mixer.music.get_pos()
    if t_now < 0: t_now = pygame.time.get_ticks()
    draw_ambient_breath(screen, t_now, lo_s, hi_s)

    # ===== Microphone input detection =====
    mic_volume = mic.get_volume()
    if mic_volume > 0.03 and mic_trigger_timer == 0:
        ripples.append(Ripple('O', t_now, CENTER[0], CENTER[1]))
        mic_trigger_timer = 400  # Limit to one generated every 0.4s

    # ===== Draw ripples =====
    ripples = [r for r in ripples if r.alive(t_now)]
    if ripples:
        ripple_layer = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        for r in ripples:
            r.draw(ripple_layer, t_now, low_energy=lo_s, high_energy=hi_s)
        screen.blit(ripple_layer, (0,0), special_flags=pygame.BLEND_PREMULTIPLIED)

    # ===== Draw text =====
    if layout_mode == "line":
        total = len(glyphs_line)
        line_positions = []
        for i, g in enumerate(glyphs_line):
            g.update("line", global_rot, BASE_RADIUS, radius_scale, line_idx=i, line_total=total, freeze=freeze)
            line_positions.append((g.x, g.y))
            g.draw(screen, faded=False if music_state in ("playing","fading_in") else True)
        if total >= 2:
            for i in range(total-1):
                x_mid = int((line_positions[i][0] + line_positions[i+1][0]) / 2)
                y_mid = int((line_positions[i][1] + line_positions[i+1][1]) / 2)
                pygame.draw.circle(screen, (210,225,255,SEP_DOT_ALPHA), (x_mid, y_mid), SEP_DOT_RADIUS)
    else:
        if not glyphs_vortex:
            base_chars.append('A'); rebuild_vortex()
        for g in glyphs_vortex:
            g.update("vortex", global_rot, BASE_RADIUS, radius_scale, freeze=freeze)
            g.draw(screen, faded=False if music_state in ("playing","fading_in") else True)

    pygame.display.flip()

# ========= 退出清理 =========
mic.stop()
pygame.quit()