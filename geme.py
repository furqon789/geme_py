import pygame
import sys
import math
import random

pygame.init()
pygame.font.init()

# ==================== KONFIGURASI ====================
W, H = 800, 600
TILE = 40
MAP_W, MAP_H = 5600, 4200
FPS = 60

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Petualangan Hutan & Tambang")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 14)
FONT_BOLD = pygame.font.SysFont("arial", 14, bold=True)
FONT_TITLE = pygame.font.SysFont("arial", 22, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 11)

# ==================== WARNA ====================
C_BG = (26, 26, 46)
C_GRASS = (74, 140, 63)
C_GRASS2 = (90, 156, 79)
C_WATER = (52, 152, 219)
C_WATER2 = (93, 173, 226)
C_TREE_BG = (61, 122, 51)
C_ROCK = (127, 140, 141)
C_ROCK2 = (149, 165, 166)
C_DIRT = (196, 162, 101)
C_DIRT2 = (184, 149, 106)
C_CAVE = (44, 62, 80)
C_CAVE2 = (52, 73, 94)
C_PATH = (196, 162, 101)
C_PATH2 = (212, 178, 117)
C_PLAYER = (68, 136, 204)
C_PLAYER_SKIN = (245, 222, 179)
C_NPC = (196, 162, 101)
C_MERCHANT = (46, 204, 113)
C_SLIME = (45, 140, 63)
C_SLIME2 = (109, 219, 109)
C_DEER = (196, 149, 106)
C_FOX = (232, 112, 32)
C_UI_BG = (20, 20, 40)
C_UI_BORDER = (106, 106, 154)
C_GOLD = (240, 192, 64)
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_RED = (231, 76, 60)
C_GREEN = (46, 204, 113)
C_GRAY = (136, 136, 136)
C_DARK = (42, 42, 74)
C_SHADOW = (15, 15, 25)

# ==================== HELPER ALPHA ====================
def draw_rect_alpha(surface, color, rect, radius=0):
    """Menggambar rect dengan alpha (RGBA) ke surface biasa."""
    if len(color) == 4 and color[3] < 255:
        w, h = int(rect[2]), int(rect[3])
        if w <= 0 or h <= 0:
            return
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, color, s.get_rect(), border_radius=radius)
        surface.blit(s, (int(rect[0]), int(rect[1])))
    else:
        pygame.draw.rect(surface, color[:3], rect, border_radius=radius)

def draw_circle_alpha(surface, color, center, radius):
    """Menggambar circle dengan alpha."""
    if len(color) == 4 and color[3] < 255:
        d = radius * 2
        if d <= 0:
            return
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (radius, radius), radius)
        surface.blit(s, (int(center[0] - radius), int(center[1] - radius)))
    else:
        pygame.draw.circle(surface, color[:3], center, radius)

# ==================== STATE GAME ====================
game_started = False
game_paused = False
dialogue_active = False
shop_open = False
shop_tab = 'buy'
quest_log_open = False
inventory_open = False

player = {
    'x': 400, 'y': 800, 'w': 28, 'h': 32,
    'speed': 3, 'hp': 50, 'max_hp': 50,
    'coins': 20, 'inventory': {},
    'direction': 'down', 'anim_frame': 0, 'anim_timer': 0,
    'is_moving': False, 'attacking': False, 'attack_timer': 0,
    'attack_dir': 'down', 'invincible': 0,
    'spawn_x': 400, 'spawn_y': 800
}

camera = {'x': 0, 'y': 0}
mouse_x, mouse_y = 0, 0
mouse_world_x, mouse_world_y = 0, 0
keys_pressed = {}

map_data = []

# ==================== MAP ====================
def generate_map():
    global map_data
    map_data = []
    for ty in range(MAP_H // TILE):
        row = []
        for tx in range(MAP_W // TILE):
            x = tx * TILE
            y = ty * TILE
            tile = 'grass'

            edge_dist = 200
            if x < edge_dist or x >= MAP_W - edge_dist or y < edge_dist or y >= MAP_H - edge_dist:
                tile = 'tree'

            if 1200 < x < 3000 and y < 600:
                if random.random() < 0.7: tile = 'tree'
            if x > 4000 and 2000 < y < 3500:
                if random.random() < 0.6: tile = 'tree'
            if y > 3200 and 1000 < x < 3500:
                if random.random() < 0.5: tile = 'tree'

            if ((x - 2400) ** 2 / 500 ** 2 + (y - 1800) ** 2 / 350 ** 2) < 1:
                tile = 'water'
            if ((x - 4200) ** 2 / 180 ** 2 + (y - 800) ** 2 / 140 ** 2) < 1:
                tile = 'water'
            if ((x - 800) ** 2 / 120 ** 2 + (y - 3200) ** 2 / 100 ** 2) < 1:
                tile = 'water'

            if x > 3400 and 1000 < y < 3400:
                tile = 'rock' if random.random() < 0.25 else 'dirt'

            if x > 4200 and 1400 < y < 3000:
                tile = 'cave'

            if 1800 < x < 2200 and 1400 < y < 2200 and tile in ('grass', 'dirt'):
                tile = 'path'
            if 1000 < x < 1400 and 1800 < y < 2600 and tile == 'grass':
                tile = 'path'
            if 2600 < x < 3600 and 1600 < y < 2000 and tile in ('grass', 'dirt'):
                tile = 'path'
            if 2000 < y < 2200 and 1000 < x < 4200 and tile in ('grass', 'dirt'):
                tile = 'path'
            if 2200 < x < 2400 and 1000 < y < 3800 and tile in ('grass', 'dirt'):
                tile = 'path'

            if tile == 'grass' and random.random() < 0.015: tile = 'flower'
            if tile == 'path' and random.random() < 0.005: tile = 'flower'

            row.append(tile)
        map_data.append(row)

def get_tile(wx, wy):
    tx = int(wx // TILE)
    ty = int(wy // TILE)
    if tx < 0 or tx >= len(map_data[0]) or ty < 0 or ty >= len(map_data):
        return 'tree'
    return map_data[ty][tx]

def is_walkable(wx, wy):
    t = get_tile(wx, wy)
    return t not in ('tree', 'water', 'rock')

def is_walkable_at(x, y, w, h):
    return (is_walkable(x, y) and is_walkable(x + w - 1, y) and
            is_walkable(x, y + h - 1) and is_walkable(x + w - 1, y + h - 1))

# ==================== ENTITIES ====================
trees = []
ores = []
stumps = []
mined_nodes = []
animals = []
slimes = []
npcs = []
particles = []
flowers = []
notification = {'text': '', 'timer': 0}
dialogue_npc = None
dialogue_text = ''
dialogue_choices = []
shop_npc = None

def init_entities():
    global trees, ores, animals, slimes, npcs, flowers, stumps, mined_nodes
    trees, ores, animals, slimes, npcs, flowers, stumps, mined_nodes = [], [], [], [], [], [], [], []

    for ty in range(MAP_H // TILE):
        for tx in range(MAP_W // TILE):
            x = tx * TILE + TILE / 2
            y = ty * TILE + TILE / 2
            if get_tile(x, y) == 'tree' and random.random() < 0.5:
                trees.append({
                    'x': x + (random.random() - 0.5) * 10,
                    'y': y + (random.random() - 0.5) * 10,
                    'hp': 3, 'max_hp': 3, 'alive': True,
                    'size': 0.8 + random.random() * 0.5
                })

    for _ in range(120):
        tx = 200 + random.random() * (MAP_W - 400)
        ty = 200 + random.random() * (MAP_H - 400)
        t = get_tile(tx, ty)
        if t in ('grass', 'path'):
            if tx < 1200 and ty > 2400: continue
            if tx > 3400 and 1000 < ty < 3400: continue
            if tx > 4200 and 1400 < ty < 3000: continue
            if t == 'path' and random.random() > 0.15: continue
            trees.append({'x': tx, 'y': ty, 'hp': 3, 'max_hp': 3, 'alive': True,
                          'size': 0.7 + random.random() * 0.6})

    for _ in range(80):
        fx = 200 + random.random() * (MAP_W - 400)
        fy = 200 + random.random() * (MAP_H - 400)
        if get_tile(fx, fy) == 'grass':
            flowers.append({
                'x': fx, 'y': fy,
                'color': random.choice([(255, 107, 138), (255, 217, 61), (107, 203, 255), (255, 153, 51), (204, 102, 255)]),
                'size': 3 + random.random() * 3
            })

    for _ in range(50):
        ox = 4250 + random.random() * 1200
        oy = 1450 + random.random() * 1400
        if get_tile(ox, oy) in ('cave', 'dirt'):
            ores.append({'x': ox, 'y': oy, 'hp': 4, 'max_hp': 4, 'alive': True,
                         'type': 'iron' if random.random() < 0.65 else 'copper'})

    for _ in range(20):
        ox = 3450 + random.random() * 700
        oy = 1050 + random.random() * 2200
        if get_tile(ox, oy) in ('rock', 'dirt'):
            ores.append({'x': ox, 'y': oy, 'hp': 4, 'max_hp': 4, 'alive': True,
                         'type': 'iron' if random.random() < 0.65 else 'copper'})

    for _ in range(15):
        ax = 300 + random.random() * 3000
        ay = 300 + random.random() * 2500
        if get_tile(ax, ay) in ('grass', 'path'):
            animals.append({
                'type': 'deer', 'x': ax, 'y': ay,
                'speed': 1.4, 'dir': random.random() * math.pi * 2,
                'move_timer': 0, 'move_interval': 100 + random.random() * 200,
                'hp': 10, 'fleeing': False, 'flee_timer': 0
            })

    for _ in range(10):
        ax = 400 + random.random() * 2800
        ay = 400 + random.random() * 2200
        if get_tile(ax, ay) in ('grass', 'path'):
            animals.append({
                'type': 'fox', 'x': ax, 'y': ay,
                'speed': 2.0, 'dir': random.random() * math.pi * 2,
                'move_timer': 0, 'move_interval': 80 + random.random() * 150,
                'hp': 8, 'fleeing': False, 'flee_timer': 0
            })

    for _ in range(15):
        sx = 4300 + random.random() * 1000
        sy = 1500 + random.random() * 1300
        slimes.append({
            'x': sx, 'y': sy, 'hp': 15, 'max_hp': 15,
            'speed': 0.9, 'dir': random.random() * math.pi * 2,
            'move_timer': 0, 'move_interval': 60 + random.random() * 100,
            'attack_timer': 0, 'attack_cooldown': 120, 'damage': 5,
            'alive': True, 'anim_timer': 0, 'bounce_y': 0
        })

    npcs.extend([
        {
            'id': 'elder', 'name': 'Kakek Desa', 'x': 600, 'y': 2700, 'type': 'npc', 'sprite': 0,
            'dialogues': ['Halo, anak muda. Aku butuh bantuanmu.',
                          'Ada slime yang mengacau di gua tambang. Bisakah kau membunuh 3 slime untukku?',
                          'Terima kasih! Kau sangat berani.'],
            'quest': {'title': 'Basmi Slime', 'desc': 'Bunuh 3 slime di gua tambang',
                      'type': 'kill_slimes', 'target': 3, 'progress': 0,
                      'reward': {'coins': 30}, 'completed': False, 'given': False},
            'interacted': False
        },
        {
            'id': 'villager1', 'name': 'Petani Joko', 'x': 760, 'y': 2800, 'type': 'npc', 'sprite': 1,
            'dialogues': ['Halo! Aku butuh kayu untuk memperbaiki pagar.',
                          'Bisa tolong tebang 5 pohon untukku?',
                          'Kau sangat membantu! Terima kasih banyak!'],
            'quest': {'title': 'Tebang Pohon', 'desc': 'Tebang 5 pohon',
                      'type': 'chop_trees', 'target': 5, 'progress': 0,
                      'reward': {'coins': 20}, 'completed': False, 'given': False},
            'interacted': False
        },
        {
            'id': 'villager2', 'name': 'Penambang Budi', 'x': 500, 'y': 2600, 'type': 'npc', 'sprite': 1,
            'dialogues': ['Hai! Gua tambang penuh bijih tapi butuh alat.',
                          'Bisa tambang 5 bijih besi untukku?',
                          'Luar biasa! Kau penambang sejati!'],
            'quest': {'title': 'Tambang Bijih', 'desc': 'Tambang 5 bijih besi',
                      'type': 'mine_ores', 'target': 5, 'progress': 0,
                      'reward': {'coins': 40}, 'completed': False, 'given': False},
            'interacted': False
        },
        {
            'id': 'explorer', 'name': 'Penjelajah Sari', 'x': 800, 'y': 600, 'type': 'npc', 'sprite': 0,
            'dialogues': ['Ah! Seorang petualang! Aku baru menemukan area baru di utara.',
                          'Ada banyak pohon dan hewan di sana. Hati-hati ya!',
                          'Semoga petualanganmu menyenangkan!'],
            'quest': {'title': 'Jelajahi Utara', 'desc': 'Kunjungi area hutan utara',
                      'type': 'explore_north', 'target': 1, 'progress': 0,
                      'reward': {'coins': 25}, 'completed': False, 'given': False},
            'interacted': False
        },
        {
            'id': 'merchant', 'name': 'Pedagang Ali', 'x': 300, 'y': 500, 'type': 'merchant', 'sprite': 2,
            'dialogues': ['Selamat datang! Mau beli apa?'],
            'interacted': False,
            'shop': {'buy': [
                {'id': 'sword', 'name': 'Pedang', 'desc': 'Untuk melawan slime', 'price': 20},
                {'id': 'axe', 'name': 'Kapak', 'desc': 'Untuk menebang pohon', 'price': 15},
                {'id': 'pickaxe', 'name': 'Beliung', 'desc': 'Untuk menambang bijih', 'price': 20},
                {'id': 'potion', 'name': 'Ramuan Kesehatan', 'desc': 'Memulihkan 20 HP', 'price': 10}
            ]}
        },
        {
            'id': 'mining_camp', 'name': 'Penjaga Camp', 'x': 3100, 'y': 1600, 'type': 'sell_ore', 'sprite': 3,
            'dialogues': ['Hai! Aku bisa beli bijih darimu. Besi: 5 koin, Tembaga: 3 koin.'],
            'interacted': False
        },
        {
            'id': 'cave_guard', 'name': 'Penjaga Gua', 'x': 4200, 'y': 1400, 'type': 'npc', 'sprite': 3,
            'dialogues': ['Hati-hati masuk ke dalam gua! Banyak slime di sana.',
                          'Pastikan kau sudah punya pedang sebelum masuk.',
                          'Semoga beruntung, pejuang!'],
            'quest': {'title': 'Basmi Semua Slime', 'desc': 'Bunuh 5 slime di dalam gua',
                      'type': 'kill_slimes_all', 'target': 5, 'progress': 0,
                      'reward': {'coins': 50}, 'completed': False, 'given': False},
            'interacted': False
        }
    ])

# ==================== NOTIFIKASI ====================
def show_notification(text):
    global notification
    notification['text'] = text
    notification['timer'] = 90

# ==================== SHOP ====================
def open_shop(npc):
    global shop_open, shop_npc, shop_tab
    shop_npc = npc
    shop_open = True
    shop_tab = 'buy'

def close_shop():
    global shop_open, shop_npc
    shop_open = False
    shop_npc = None

def buy_item(item_id, price):
    if player['coins'] < price:
        show_notification('Koin tidak cukup!')
        return
    player['coins'] -= price
    player['inventory'][item_id] = player['inventory'].get(item_id, 0) + 1
    names = {'potion': 'Ramuan Kesehatan', 'sword': 'Pedang', 'axe': 'Kapak', 'pickaxe': 'Beliung'}
    show_notification('+1 ' + names.get(item_id, item_id))

def sell_ore(ore_id, price, all_sell=False):
    count = player['inventory'].get(ore_id, 0)
    if count <= 0: return
    amount = count if all_sell else 1
    player['inventory'][ore_id] -= amount
    if player['inventory'][ore_id] <= 0:
        del player['inventory'][ore_id]
    player['coins'] += price * amount
    show_notification('+' + str(price * amount) + ' koin')

# ==================== QUEST ====================
def check_quest_progress(qtype):
    for npc in npcs:
        q = npc.get('quest')
        if q and q['given'] and not q['completed'] and q['type'] == qtype:
            q['progress'] += 1
            if q['progress'] >= q['target']:
                q['completed'] = True
                player['coins'] += q['reward']['coins']
                show_notification('Quest selesai! +' + str(q['reward']['coins']) + ' koin')

# ==================== DIALOGUE ====================
def show_dialogue(npc):
    global dialogue_active, dialogue_npc, dialogue_text, dialogue_choices
    dialogue_active = True
    dialogue_npc = npc
    dialogue_choices = []

    q = npc.get('quest')
    if q and not q['given']:
        q['given'] = True
        dialogue_text = npc['dialogues'][0]
        dialogue_choices = [{'text': 'Apa yang bisa kubantu?', 'action': 'next1'}]
    elif q and not q['completed']:
        dialogue_text = 'Progress: ' + str(q['progress']) + '/' + str(q['target'])
        dialogue_choices = [{'text': 'Lanjut', 'action': 'close'}]
    elif q and q['completed']:
        dialogue_text = 'Terima kasih atas bantuanmu!'
        dialogue_choices = [{'text': 'Sama-sama', 'action': 'close'}]
    else:
        dialogue_text = npc['dialogues'][0]
        dialogue_choices = [{'text': 'Lanjut', 'action': 'close'}]

def close_dialogue():
    global dialogue_active, dialogue_npc, dialogue_text, dialogue_choices
    dialogue_active = False
    dialogue_npc = None
    dialogue_text = ''
    dialogue_choices = []

def handle_dialogue_choice(idx):
    global dialogue_text, dialogue_choices
    if idx >= len(dialogue_choices): return
    action = dialogue_choices[idx]['action']
    if action == 'close':
        close_dialogue()
    elif action == 'next1':
        dialogue_text = dialogue_npc['dialogues'][1]
        dialogue_choices = [{'text': 'Tentu, aku akan membantumu!', 'action': 'next2'}]
    elif action == 'next2':
        dialogue_text = dialogue_npc['dialogues'][2] if len(dialogue_npc['dialogues']) > 2 else 'Terima kasih!'
        dialogue_choices = [{'text': 'Sama-sama', 'action': 'close'}]

# ==================== INTERACTION ====================
def handle_interaction():
    if dialogue_active or shop_open: return
    for npc in npcs:
        dx = npc['x'] - player['x']
        dy = npc['y'] - player['y']
        if math.sqrt(dx*dx + dy*dy) < 60:
            if npc['type'] in ('merchant', 'sell_ore'):
                open_shop(npc)
            else:
                show_dialogue(npc)
            return

def handle_attack():
    if dialogue_active or shop_open or not game_started: return
    player['attacking'] = True
    player['attack_timer'] = 15

    dx = mouse_world_x - (player['x'] + player['w']/2)
    dy = mouse_world_y - (player['y'] + player['h']/2)
    if abs(dx) > abs(dy):
        player['attack_dir'] = 'right' if dx > 0 else 'left'
    else:   
        player['attack_dir'] = 'down' if dy > 0 else 'up'

    attack_range = 45
    cx = player['x'] + player['w']/2
    cy = player['y'] + player['h']/2

    if player['inventory'].get('axe', 0) > 0:
        for tree in trees:
            if not tree['alive']: continue
            tx, ty = tree['x'] - cx, tree['y'] - cy
            if math.sqrt(tx*tx + ty*ty) < attack_range:
                tree['hp'] -= 1
                spawn_particles(tree['x'], tree['y'], (139, 69, 19), 5)
                if tree['hp'] <= 0:
                    tree['alive'] = False
                    stumps.append({'x': tree['x'], 'y': tree['y']})
                    player['inventory']['wood'] = player['inventory'].get('wood', 0) + 1
                    check_quest_progress('chop_trees')
                    show_notification('+1 Kayu')
                return

    if player['inventory'].get('pickaxe', 0) > 0:
        for ore in ores:
            if not ore['alive']: continue
            ox, oy = ore['x'] - cx, ore['y'] - cy
            if math.sqrt(ox*ox + oy*oy) < attack_range:
                ore['hp'] -= 1
                color = (170, 170, 170) if ore['type'] == 'iron' else (200, 117, 51)
                spawn_particles(ore['x'], ore['y'], color, 5)
                if ore['hp'] <= 0:
                    ore['alive'] = False
                    mined_nodes.append({'x': ore['x'], 'y': ore['y'], 'type': ore['type']})
                    ore_key = ore['type'] + '_ore'
                    player['inventory'][ore_key] = player['inventory'].get(ore_key, 0) + 1
                    if ore['type'] == 'iron':
                        check_quest_progress('mine_ores')
                    show_notification('+1 Bijih ' + ('Besi' if ore['type'] == 'iron' else 'Tembaga'))
                return

    if player['inventory'].get('sword', 0) > 0:
        for slime in slimes:
            if not slime['alive']: continue
            sx, sy = slime['x'] - cx, slime['y'] - cy
            if math.sqrt(sx*sx + sy*sy) < attack_range + 10:
                dmg = 8
                slime['hp'] -= dmg
                spawn_particles(slime['x'], slime['y'], (76, 175, 80), 8)
                show_notification('Slime -' + str(dmg) + ' HP')
                if slime['hp'] <= 0:
                    slime['alive'] = False
                    check_quest_progress('kill_slimes')
                    check_quest_progress('kill_slimes_all')
                    show_notification('Slime dikalahkan! +5 koin')
                    player['coins'] += 5
                return

    for slime in slimes:
        if not slime['alive']: continue
        sx, sy = slime['x'] - cx, slime['y'] - cy
        if math.sqrt(sx*sx + sy*sy) < attack_range + 10:
            show_notification('Butuh pedang untuk menyerang slime!')
            return
    for tree in trees:
        if not tree['alive']: continue
        tx, ty = tree['x'] - cx, tree['y'] - cy
        if math.sqrt(tx*tx + ty*ty) < attack_range:
            show_notification('Butuh kapak untuk menebang pohon!')
            return
    for ore in ores:
        if not ore['alive']: continue
        ox, oy = ore['x'] - cx, ore['y'] - cy
        if math.sqrt(ox*ox + oy*oy) < attack_range:
            show_notification('Butuh beliung untuk menambang!')
            return

def spawn_particles(x, y, color, count):
    for _ in range(count):
        particles.append({
            'x': x, 'y': y,
            'vx': (random.random() - 0.5) * 4,
            'vy': (random.random() - 0.5) * 4 - 2,
            'life': 30 + random.random() * 20,
            'color': color, 'size': 2 + random.random() * 3
        })

# ==================== UPDATE ====================
slime_spawn_timer = 0

def update(dt):
    global game_paused, slime_spawn_timer

    if not game_started or game_paused or dialogue_active or shop_open:
        return

    dx, dy = 0, 0
    if keys_pressed.get(pygame.K_w) or keys_pressed.get(pygame.K_UP):
        dy = -1; player['direction'] = 'up'
    if keys_pressed.get(pygame.K_s) or keys_pressed.get(pygame.K_DOWN):
        dy = 1; player['direction'] = 'down'
    if keys_pressed.get(pygame.K_a) or keys_pressed.get(pygame.K_LEFT):
        dx = -1; player['direction'] = 'left'
    if keys_pressed.get(pygame.K_d) or keys_pressed.get(pygame.K_RIGHT):
        dx = 1; player['direction'] = 'right'

    if dx != 0 and dy != 0:
        dx *= 0.707; dy *= 0.707

    player['is_moving'] = dx != 0 or dy != 0

    if player['is_moving']:
        new_x = player['x'] + dx * player['speed']
        new_y = player['y'] + dy * player['speed']
        if is_walkable_at(new_x, player['y'], player['w'], player['h']):
            player['x'] = new_x
        if is_walkable_at(player['x'], new_y, player['w'], player['h']):
            player['y'] = new_y

        # Push-back jika terjebak
        if not is_walkable_at(player['x'], player['y'], player['w'], player['h']):
            player['x'] = player['spawn_x']
            player['y'] = player['spawn_y']

        player['x'] = max(0, min(player['x'], MAP_W - player['w']))
        player['y'] = max(0, min(player['y'], MAP_H - player['h']))

    player['anim_timer'] += dt
    if player['is_moving'] and player['anim_timer'] > 150:
        player['anim_timer'] = 0
        player['anim_frame'] = (player['anim_frame'] + 1) % 4

    if player['attack_timer'] > 0:
        player['attack_timer'] -= 1
    if player['attack_timer'] <= 0:
        player['attacking'] = False
    if player['invincible'] > 0:
        player['invincible'] -= 1

    if player['y'] < 1000:
        check_quest_progress('explore_north')

    for slime in slimes:
        if not slime['alive']: continue
        slime['anim_timer'] += dt
        slime['bounce_y'] = math.sin(slime['anim_timer'] / 200) * 3

        dist = math.sqrt((slime['x'] - player['x'])**2 + (slime['y'] - player['y'])**2)
        if dist < 280:
            angle = math.atan2(player['y'] - slime['y'], player['x'] - slime['x'])
            slime['x'] += math.cos(angle) * slime['speed']
            slime['y'] += math.sin(angle) * slime['speed']
        else:
            slime['move_timer'] += 1
            if slime['move_timer'] > slime['move_interval']:
                slime['move_timer'] = 0
                slime['dir'] += (random.random() - 0.5) * math.pi
            slime['x'] += math.cos(slime['dir']) * slime['speed'] * 0.5
            slime['y'] += math.sin(slime['dir']) * slime['speed'] * 0.5

        if dist < 25 and player['invincible'] <= 0:
            slime['attack_timer'] += 1
            if slime['attack_timer'] >= slime['attack_cooldown']:
                slime['attack_timer'] = 0
                player['hp'] -= slime['damage']
                player['invincible'] = 30
                show_notification('-' + str(slime['damage']) + ' HP!')
                if player['hp'] <= 0:
                    player['hp'] = 0
                    game_paused = True

        slime['x'] = max(3400, min(slime['x'], MAP_W - 20))
        slime['y'] = max(1000, min(slime['y'], MAP_H - 20))

    slime_spawn_timer += dt
    if slime_spawn_timer > 15000:
        slime_spawn_timer = 0
        alive_count = sum(1 for s in slimes if s['alive'])
        if alive_count < 12:
            slimes.append({
                'x': 4300 + random.random() * 1000,
                'y': 1500 + random.random() * 1300,
                'hp': 15, 'max_hp': 15, 'speed': 0.9,
                'dir': random.random() * math.pi * 2,
                'move_timer': 0, 'move_interval': 60 + random.random() * 100,
                'attack_timer': 0, 'attack_cooldown': 120, 'damage': 5,
                'alive': True, 'anim_timer': 0, 'bounce_y': 0
            })

    for animal in animals:
        dist = math.sqrt((animal['x'] - player['x'])**2 + (animal['y'] - player['y'])**2)
        if dist < 140 and not animal['fleeing']:
            animal['fleeing'] = True
            animal['flee_timer'] = 180
            animal['dir'] = math.atan2(animal['y'] - player['y'], animal['x'] - player['x'])

        if animal['fleeing']:
            animal['flee_timer'] -= 1
            if animal['flee_timer'] <= 0: animal['fleeing'] = False
            animal['x'] += math.cos(animal['dir']) * animal['speed'] * 2
            animal['y'] += math.sin(animal['dir']) * animal['speed'] * 2
        else:
            animal['move_timer'] += 1
            if animal['move_timer'] > animal['move_interval']:
                animal['move_timer'] = 0
                animal['dir'] += (random.random() - 0.5) * math.pi * 0.8
            animal['x'] += math.cos(animal['dir']) * animal['speed'] * 0.5
            animal['y'] += math.sin(animal['dir']) * animal['speed'] * 0.5

        animal['x'] = max(50, min(animal['x'], MAP_W - 50))
        animal['y'] = max(50, min(animal['y'], MAP_H - 50))

        if get_tile(animal['x'], animal['y']) == 'water':
            animal['dir'] += math.pi
            animal['x'] += math.cos(animal['dir']) * 5
            animal['y'] += math.sin(animal['dir']) * 5

    for i in range(len(particles) - 1, -1, -1):
        p = particles[i]
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vy'] += 0.1
        p['life'] -= 1
        if p['life'] <= 0:
            particles.pop(i)

    if notification['timer'] > 0:
        notification['timer'] -= 1

    camera['x'] = player['x'] + player['w']/2 - W/2
    camera['y'] = player['y'] + player['h']/2 - H/2
    camera['x'] = max(0, min(camera['x'], MAP_W - W))
    camera['y'] = max(0, min(camera['y'], MAP_H - H))

# ==================== RENDER ====================
def draw_tree(x, y, size=1):
    s = size
    pygame.draw.rect(screen, (139, 105, 20), (x - 4*s, y - 5*s, 8*s, 18*s))
    pygame.draw.circle(screen, (45, 140, 63), (int(x), int(y - 12*s)), int(16*s))
    pygame.draw.circle(screen, (61, 160, 79), (int(x - 4*s), int(y - 16*s)), int(10*s))
    pygame.draw.circle(screen, (61, 160, 79), (int(x + 5*s), int(y - 10*s)), int(11*s))
    pygame.draw.circle(screen, (77, 176, 95), (int(x), int(y - 20*s)), int(8*s))

def draw_deer(x, y):
    pygame.draw.ellipse(screen, C_DEER, (x-12, y-8, 24, 16))
    pygame.draw.circle(screen, (212, 165, 122), (int(x+10), int(y-6)), 6)
    pygame.draw.line(screen, (139, 105, 20), (x+10, y-12), (x+8, y-20), 2)
    pygame.draw.line(screen, (139, 105, 20), (x+12, y-12), (x+15, y-19), 2)
    pygame.draw.rect(screen, (160, 120, 80), (x-6, y+6, 3, 8))
    pygame.draw.rect(screen, (160, 120, 80), (x+4, y+6, 3, 8))
    pygame.draw.circle(screen, C_BLACK, (int(x+12), int(y-7)), 2)

def draw_fox(x, y):
    pygame.draw.ellipse(screen, C_FOX, (x-10, y-7, 20, 14))
    pygame.draw.circle(screen, (240, 128, 48), (int(x+8), int(y-4)), 5)
    pygame.draw.polygon(screen, (208, 96, 16), [(x+5, y-8), (x+3, y-14), (x+8, y-9)])
    pygame.draw.polygon(screen, (208, 96, 16), [(x+10, y-8), (x+12, y-14), (x+13, y-8)])
    pygame.draw.polygon(screen, C_FOX, [(x-10, y), (x-18, y-8), (x-15, y-15), (x-8, y-2)])
    pygame.draw.circle(screen, C_WHITE, (int(x-15), int(y-14)), 4)
    pygame.draw.circle(screen, C_BLACK, (int(x+10), int(y-5)), 2)

def draw_slime(slime):
    x, y = slime['x'], slime['y'] + slime['bounce_y']
    # Shadow (solid dark)
    pygame.draw.ellipse(screen, C_SHADOW, (x-14, y+10, 28, 6))
    # Body
    pygame.draw.ellipse(screen, C_SLIME, (x-14, y-10, 28, 24))
    pygame.draw.ellipse(screen, C_SLIME2, (x-8, y-8, 10, 8))
    # Eyes
    pygame.draw.circle(screen, C_WHITE, (int(x-4), int(y-2)), 3)
    pygame.draw.circle(screen, C_WHITE, (int(x+4), int(y-2)), 3)
    pygame.draw.circle(screen, C_BLACK, (int(x-4), int(y-2)), 2)
    pygame.draw.circle(screen, C_BLACK, (int(x+4), int(y-2)), 2)
    # Mouth (fixed arc: start < stop)
    pygame.draw.arc(screen, (26, 108, 42), (x-4, y+1, 8, 6), 0.2, math.pi - 0.2, 2)
    # HP bar
    if slime['hp'] < slime['max_hp']:
        pygame.draw.rect(screen, (50, 50, 50), (x-12, y-18, 24, 3))
        pygame.draw.rect(screen, C_RED, (x-12, y-18, int(24 * slime['hp'] / slime['max_hp']), 3))

def draw_npc(npc):
    x, y = npc['x'], npc['y']
    # Shadow
    pygame.draw.ellipse(screen, C_SHADOW, (x-10, y+12, 20, 6))

    if npc['type'] == 'merchant':
        pygame.draw.rect(screen, (139, 105, 20), (x-4, y-2, 8, 14))
        pygame.draw.rect(screen, C_MERCHANT, (x-6, y-10, 12, 12))
        pygame.draw.rect(screen, (245, 222, 179), (x-3, y-14, 6, 6))
        pygame.draw.rect(screen, C_BLACK, (x-8, y-20, 16, 3))
        pygame.draw.rect(screen, C_BLACK, (x-5, y-26, 10, 8))
    elif npc['type'] == 'sell_ore':
        pygame.draw.rect(screen, (85, 102, 119), (x-4, y-2, 8, 14))
        pygame.draw.rect(screen, (102, 119, 136), (x-6, y-10, 12, 12))
        pygame.draw.rect(screen, (245, 222, 179), (x-3, y-14, 6, 6))
        # Helm (fixed: pakai arc dengan start < stop)
        pygame.draw.arc(screen, (136, 136, 136), (x-7, y-23, 14, 14), math.pi, 2*math.pi, 3)
        pygame.draw.circle(screen, C_GOLD, (int(x), int(y-18)), 3)
    else:
        pygame.draw.rect(screen, (139, 105, 20), (x-4, y-2, 8, 14))
        pygame.draw.rect(screen, C_NPC, (x-6, y-10, 12, 12))
        pygame.draw.rect(screen, (245, 222, 179), (x-3, y-14, 6, 6))
        pygame.draw.rect(screen, (212, 178, 117), (x-10, y-18, 20, 3))
        pygame.draw.rect(screen, (212, 178, 117), (x-5, y-24, 10, 8))

    # Mata
    pygame.draw.rect(screen, C_BLACK, (x-2, y-12, 2, 2))
    pygame.draw.rect(screen, C_BLACK, (x+1, y-12, 2, 2))

    q = npc.get('quest')
    if q:
        if not q['given']:
            txt = FONT_BOLD.render('!', True, C_GOLD)
        elif not q['completed']:
            txt = FONT_BOLD.render('?', True, C_GREEN)
        else:
            txt = FONT_BOLD.render('✓', True, C_GOLD)
        screen.blit(txt, (x - txt.get_width()//2, y - 35))

    # Name label (solid dark bg)
    pygame.draw.rect(screen, C_SHADOW, (x-25, y+18, 50, 14))
    name_txt = FONT_SMALL.render(npc['name'], True, C_WHITE)
    screen.blit(name_txt, (x - name_txt.get_width()//2, y + 20))

def draw_player():
    x = player['x'] + player['w']/2 - camera['x']
    y = player['y'] + player['h']/2 - camera['y']

    if player['invincible'] > 0 and (player['invincible'] // 4) % 2 == 0:
        return

    pygame.draw.ellipse(screen, C_SHADOW, (x-12, y+13, 24, 6))
    pygame.draw.rect(screen, C_PLAYER, (x-8, y-2, 16, 16))
    pygame.draw.circle(screen, C_PLAYER_SKIN, (int(x), int(y-8)), 8)

    # dst...

    if player['invincible'] > 0 and (player['invincible'] // 4) % 2 == 0:
        return

    # Shadow
    pygame.draw.ellipse(screen, C_SHADOW, (x-12, y+13, 24, 6))
    # Body
    pygame.draw.rect(screen, C_PLAYER, (x-8, y-2, 16, 16))
    # Head
    pygame.draw.circle(screen, C_PLAYER_SKIN, (int(x), int(y-8)), 8)
    # Rambut (fixed arc: start < stop)
    pygame.draw.arc(screen, (102, 153, 204), (x-9, y-19, 18, 16), math.pi, 2*math.pi, 3)
    pygame.draw.rect(screen, (85, 136, 187), (x-9, y-12, 18, 4))
    # Mata
    pygame.draw.circle(screen, C_BLACK, (int(x-3), int(y-10)), 1)
    pygame.draw.circle(screen, C_BLACK, (int(x+3), int(y-10)), 1)
    # Kaki
    leg_off = math.sin(player['anim_timer'] / 100) * 3 if player['is_moving'] else 0
    pygame.draw.rect(screen, (51, 102, 153), (x-6, y+12, 4, int(6 + leg_off)))
    pygame.draw.rect(screen, (51, 102, 153), (x+3, y+12, 4, int(6 - leg_off)))
    # Senjata
    if player['attacking']:
        angle = {'right': 0, 'left': math.pi, 'up': -math.pi/2, 'down': math.pi/2}[player['attack_dir']]
        pygame.draw.line(screen, (220, 220, 220), (x, y),
                         (x + math.cos(angle)*25, y + math.sin(angle)*25), 3)
    else:
        if player['inventory'].get('sword', 0) > 0:
            pygame.draw.rect(screen, (170, 170, 170), (x+12, y-8, 3, 16))
            pygame.draw.rect(screen, (136, 136, 136), (x+10, y-4, 7, 3))
        elif player['inventory'].get('pickaxe', 0) > 0:
            pygame.draw.rect(screen, (139, 105, 20), (x+12, y-12, 3, 20))
            pygame.draw.rect(screen, (170, 170, 170), (x+8, y-14, 12, 4))
        elif player['inventory'].get('axe', 0) > 0:
            pygame.draw.rect(screen, (139, 105, 20), (x+12, y-12, 3, 18))
            pygame.draw.rect(screen, (170, 170, 170), (x+10, y-16, 8, 6))

def draw_building(x, y, w, h, wall_color, roof_color):
    pygame.draw.rect(screen, wall_color, (x, y, w, h))
    pygame.draw.polygon(screen, roof_color, [(x-5, y), (x+w//2, y-15), (x+w+5, y)])
    pygame.draw.rect(screen, (90, 58, 26), (x+w//2-5, y+h-18, 10, 18))
    pygame.draw.rect(screen, (135, 206, 235), (x+8, y+10, 10, 10))
    pygame.draw.rect(screen, (135, 206, 235), (x+w-18, y+10, 10, 10))
    pygame.draw.rect(screen, (85, 85, 85), (x, y, w, h), 1)

def draw_tent(x, y, label):
    pygame.draw.polygon(screen, (232, 216, 200), [(x, y+30), (x+20, y), (x+40, y+30)])
    pygame.draw.polygon(screen, (212, 196, 180), [(x+5, y+25), (x+20, y+5), (x+35, y+25)])
    pygame.draw.polygon(screen, (90, 58, 26), [(x+15, y+30), (x+20, y+15), (x+25, y+30)])
    lbl = FONT_SMALL.render(label, True, C_WHITE)
    screen.blit(lbl, (x+20 - lbl.get_width()//2, y+42))

def draw_buildings():
    draw_building(
        560 - camera['x'],
        2620 - camera['y'],
        60, 50,
        (196, 162, 101),
        (139, 105, 20)
    )

    draw_tent(
    260 - camera['x'],
    440 - camera['y'],
    'Toko')

    draw_building(760, 520, 55, 45, (196, 162, 101), (139, 105, 20))
    draw_building(830, 560, 50, 40, (196, 162, 101), (139, 105, 20))

    draw_building(3040, 1550, 70, 50, (139, 105, 20), (85, 85, 85))
    draw_building(3120, 1600, 60, 45, (139, 105, 20), (85, 85, 85))
    draw_building(3000, 1650, 55, 40, (139, 105, 20), (85, 85, 85))

    # Gua (fixed arc)
    pygame.draw.rect(screen, (26, 26, 46), (4165, 1755, 70, 105))
    pygame.draw.arc(screen, (44, 62, 80), (4155, 1755, 90, 90), math.pi, 2*math.pi, 8)

    txt1 = FONT.render('Gua Tambang', True, C_WHITE)
    txt2 = FONT_SMALL.render('Masuk untuk menambang bijih', True, C_GOLD)
    screen.blit(txt1, (4200 - txt1.get_width()//2, 1740))
    screen.blit(txt2, (4200 - txt2.get_width()//2, 1720))

def render():
    screen.fill(C_BG)

    start_tx = max(0, int(camera['x'] // TILE) - 1)
    start_ty = max(0, int(camera['y'] // TILE) - 1)
    end_tx = min(int((camera['x'] + W) // TILE) + 2, len(map_data[0]))
    end_ty = min(int((camera['y'] + H) // TILE) + 2, len(map_data))

    for ty in range(start_ty, end_ty):
        for tx in range(start_tx, end_tx):
            tile = map_data[ty][tx]
            x = tx * TILE - camera['x']
            y = ty * TILE - camera['y']

            if tile == 'grass':
                pygame.draw.rect(screen, C_GRASS, (x, y, TILE, TILE))
                pygame.draw.rect(screen, C_GRASS2, (x+5, y+10, 2, 6))
                pygame.draw.rect(screen, C_GRASS2, (x+25, y+20, 2, 5))
            elif tile == 'water':
                pygame.draw.rect(screen, C_WATER, (x, y, TILE, TILE))
                pygame.draw.rect(screen, C_WATER2, (x+8, y+12, 12, 3))
                pygame.draw.rect(screen, C_WATER2, (x+20, y+28, 8, 2))
            elif tile == 'tree':
                pygame.draw.rect(screen, C_TREE_BG, (x, y, TILE, TILE))
            elif tile == 'rock':
                pygame.draw.rect(screen, C_ROCK, (x, y, TILE, TILE))
                pygame.draw.circle(screen, C_ROCK2, (int(x+TILE/2), int(y+TILE/2)), 12)
            elif tile == 'dirt':
                pygame.draw.rect(screen, C_DIRT, (x, y, TILE, TILE))
                pygame.draw.rect(screen, C_DIRT2, (x+10, y+15, 8, 3))
            elif tile == 'cave':
                pygame.draw.rect(screen, C_CAVE, (x, y, TILE, TILE))
                pygame.draw.rect(screen, C_CAVE2, (x+5, y+5, TILE-10, TILE-10))
                pygame.draw.circle(screen, (52, 152, 219), (int(x+10), int(y+15)), 4)
                pygame.draw.circle(screen, (52, 152, 219), (int(x+30), int(y+25)), 3)
            elif tile == 'path':
                pygame.draw.rect(screen, C_PATH, (x, y, TILE, TILE))
                pygame.draw.rect(screen, C_PATH2, (x+5, y+5, TILE-10, TILE-10))
            elif tile == 'flower':
                pygame.draw.rect(screen, C_GRASS, (x, y, TILE, TILE))

    for flower in flowers:
        fx, fy = flower['x'] - camera['x'], flower['y'] - camera['y']
        if -20 < fx < W+20 and -20 < fy < H+20:
            pygame.draw.circle(screen, flower['color'], (int(fx), int(fy)), int(flower['size']))
            pygame.draw.circle(screen, C_WHITE, (int(fx), int(fy)), int(flower['size'] * 0.4))

    for stump in stumps:
        sx, sy = stump['x'] - camera['x'], stump['y'] - camera['y']
        if -20 < sx < W+20 and -20 < sy < H+20:
            pygame.draw.circle(screen, (139, 105, 20), (int(sx), int(sy)), 10)
            pygame.draw.circle(screen, (160, 120, 40), (int(sx), int(sy)), 7)

    for node in mined_nodes:
        nx, ny = node['x'] - camera['x'], node['y'] - camera['y']
        if -20 < nx < W+20 and -20 < ny < H+20:
            pygame.draw.circle(screen, (85, 85, 85), (int(nx), int(ny)), 8)

    for ore in ores:
        if not ore['alive']: continue
        ox, oy = ore['x'] - camera['x'], ore['y'] - camera['y']
        if -20 < ox < W+20 and -20 < oy < H+20:
            color = (170, 170, 170) if ore['type'] == 'iron' else (200, 117, 51)
            pygame.draw.circle(screen, color, (int(ox), int(oy)), 10)
            pygame.draw.circle(screen, (204, 204, 204) if ore['type'] == 'iron' else (218, 160, 109), (int(ox-2), int(oy-2)), 4)
            if ore['hp'] < ore['max_hp']:
                pygame.draw.rect(screen, (50, 50, 50), (ox-10, oy-16, 20, 3))
                pygame.draw.rect(screen, C_GREEN, (ox-10, oy-16, int(20 * ore['hp'] / ore['max_hp']), 3))

    for tree in trees:
        if not tree['alive']: continue
        tx, ty = tree['x'] - camera['x'], tree['y'] - camera['y']
        if -50 < tx < W+50 and -50 < ty < H+50:
            draw_tree(tx, ty, tree['size'])
            if tree['hp'] < tree['max_hp']:
                pygame.draw.rect(screen, (50, 50, 50), (tx-10, ty-25, 20, 3))
                pygame.draw.rect(screen, C_GREEN, (tx-10, ty-25, int(20 * tree['hp'] / tree['max_hp']), 3))

    draw_buildings()

    for animal in animals:
        ax, ay = animal['x'] - camera['x'], animal['y'] - camera['y']
        if -30 < ax < W+30 and -30 < ay < H+30:
            if animal['type'] == 'deer': draw_deer(ax, ay)
            else: draw_fox(ax, ay)

    for slime in slimes:
        if not slime['alive']: continue
        sx, sy = slime['x'] - camera['x'], slime['y'] - camera['y']
        if -30 < sx < W+30 and -30 < sy < H+30:
            draw_slime({'x': sx, 'y': sy, 'bounce_y': slime['bounce_y'], 'hp': slime['hp'], 'max_hp': slime['max_hp']})

    for npc in npcs:
        nx, ny = npc['x'] - camera['x'], npc['y'] - camera['y']
        if -50 < nx < W+50 and -50 < ny < H+50:
            draw_npc({'x': nx, 'y': ny, 'name': npc['name'], 'type': npc['type'], 'quest': npc.get('quest')})

    draw_player()

    for p in particles:
        px, py = p['x'] - camera['x'], p['y'] - camera['y']
        alpha = max(0, min(1, p['life'] / 50))
        color = tuple(int(c * alpha) for c in p['color'])
        pygame.draw.circle(screen, color, (int(px), int(py)), int(p['size']))

    if player['attacking']:
        cx = player['x'] + player['w']/2 - camera['x']
        cy = player['y'] + player['h']/2 - camera['y']
        angle = {'right': 0, 'left': math.pi, 'up': -math.pi/2, 'down': math.pi/2}[player['attack_dir']]
        pygame.draw.arc(screen, (220, 220, 220), (cx-30, cy-30, 60, 60), angle - 0.6, angle + 0.6, 3)

    # Hint interaksi
    if not dialogue_active and not shop_open:
        for npc in npcs:
            dx = npc['x'] - player['x']
            dy = npc['y'] - player['y']
            if math.sqrt(dx*dx + dy*dy) < 60:
                px = player['x'] + player['w']/2 - camera['x']
                py = player['y'] - camera['y'] - 30
                pygame.draw.rect(screen, C_SHADOW, (px-40, py, 80, 20))
                txt = FONT_SMALL.render('E - Interaksi', True, C_GOLD)
                screen.blit(txt, (px - txt.get_width()//2, py + 4))
                break

    # Notifikasi
    if notification['timer'] > 0:
        alpha = min(1.0, notification['timer'] / 30)
        txt = FONT_BOLD.render(notification['text'], True, C_WHITE)
        tw, th = txt.get_size()
        draw_rect_alpha(screen, (0, 0, 0, int(200 * alpha)),
                        (W//2 - tw//2 - 20, H//2 - 20, tw + 40, 40), radius=10)
        screen.blit(txt, (W//2 - tw//2, H//2 - 8))

    draw_hud()
    if dialogue_active: draw_dialogue()
    if shop_open: draw_shop()
    if quest_log_open: draw_quest_log()
    if inventory_open: draw_inventory()

def draw_hud():
    draw_rect_alpha(screen, (0, 0, 0, 180), (0, 0, W, 40))

    pygame.draw.rect(screen, (50, 50, 50), (10, 15, 80, 10), border_radius=5)
    hp_w = int(80 * player['hp'] / player['max_hp'])
    pygame.draw.rect(screen, C_RED if player['hp'] < 20 else C_GREEN, (10, 15, hp_w, 10), border_radius=5)
    txt = FONT_SMALL.render(f"HP {player['hp']}/{player['max_hp']}", True, C_WHITE)
    screen.blit(txt, (95, 15))

    txt = FONT.render(f"Koin: {player['coins']}", True, C_GOLD)
    screen.blit(txt, (200, 12))

    total = sum(player['inventory'].values())
    txt = FONT.render(f"Inventaris: {total}", True, C_WHITE)
    screen.blit(txt, (320, 12))

    txt = FONT_SMALL.render("WASD:Gerak | E:Interaksi | Klik:Serang | I:Inventaris | Q:Quest", True, (150, 150, 150))
    screen.blit(txt, (W - txt.get_width() - 10, 15))

def draw_dialogue():
    draw_rect_alpha(screen, (20, 20, 40, 240), (W//2 - 300, H - 120, 600, 100), radius=12)
    pygame.draw.rect(screen, C_UI_BORDER, (W//2 - 300, H - 120, 600, 100), 2, border_radius=12)

    if dialogue_npc:
        name_txt = FONT_BOLD.render(dialogue_npc['name'], True, C_GOLD)
        screen.blit(name_txt, (W//2 - 280, H - 110))

        text_txt = FONT.render(dialogue_text, True, (224, 224, 224))
        screen.blit(text_txt, (W//2 - 280, H - 85))

        for i, choice in enumerate(dialogue_choices):
            btn_rect = pygame.Rect(W//2 - 280 + i * 150, H - 50, 140, 28)
            pygame.draw.rect(screen, C_DARK, btn_rect, border_radius=6)
            pygame.draw.rect(screen, C_UI_BORDER, btn_rect, 1, border_radius=6)
            txt = FONT.render(choice['text'], True, C_WHITE)
            screen.blit(txt, (btn_rect.centerx - txt.get_width()//2, btn_rect.centery - txt.get_height()//2))

def draw_shop():
    draw_rect_alpha(screen, (20, 20, 40, 245), (W//2 - 250, H//2 - 200, 500, 400), radius=16)
    pygame.draw.rect(screen, C_GOLD, (W//2 - 250, H//2 - 200, 500, 400), 2, border_radius=16)

    title = FONT_TITLE.render(shop_npc['name'], True, C_GOLD)
    screen.blit(title, (W//2 - title.get_width()//2, H//2 - 190))

    sub = 'Toko Peralatan & Ramuan' if shop_npc['type'] == 'merchant' else 'Jual Bijih Tambang'
    sub_txt = FONT_SMALL.render(sub, True, C_GRAY)
    screen.blit(sub_txt, (W//2 - sub_txt.get_width()//2, H//2 - 165))

    buy_rect = pygame.Rect(W//2 - 220, H//2 - 140, 210, 30)
    sell_rect = pygame.Rect(W//2 + 10, H//2 - 140, 210, 30)
    pygame.draw.rect(screen, C_GOLD if shop_tab == 'buy' else C_DARK, buy_rect, border_radius=8)
    pygame.draw.rect(screen, C_GOLD if shop_tab == 'sell' else C_DARK, sell_rect, border_radius=8)
    buy_txt = FONT.render('Beli', True, C_BLACK if shop_tab == 'buy' else C_WHITE)
    sell_txt = FONT.render('Jual', True, C_BLACK if shop_tab == 'sell' else C_WHITE)
    screen.blit(buy_txt, (buy_rect.centerx - buy_txt.get_width()//2, buy_rect.centery - buy_txt.get_height()//2))
    screen.blit(sell_txt, (sell_rect.centerx - sell_txt.get_width()//2, sell_rect.centery - sell_txt.get_height()//2))

    y_pos = H//2 - 95
    if shop_tab == 'buy':
        for item in shop_npc['shop']['buy']:
            count = player['inventory'].get(item['id'], 0)
            can_buy = player['coins'] >= item['price']
            item_rect = pygame.Rect(W//2 - 220, y_pos, 440, 40)
            pygame.draw.rect(screen, C_DARK, item_rect, border_radius=8)
            name_txt = FONT_BOLD.render(item['name'], True, C_WHITE)
            screen.blit(name_txt, (W//2 - 200, y_pos + 5))
            desc_txt = FONT_SMALL.render(item['desc'], True, C_GRAY)
            screen.blit(desc_txt, (W//2 - 200, y_pos + 22))
            count_txt = FONT_SMALL.render(f"Dimiliki: {count}", True, (170, 170, 170))
            screen.blit(count_txt, (W//2 - 50, y_pos + 22))
            price_txt = FONT.render(f"Koin {item['price']}", True, C_GOLD)
            screen.blit(price_txt, (W//2 + 100, y_pos + 12))
            btn_rect = pygame.Rect(W//2 + 180, y_pos + 8, 50, 24)
            pygame.draw.rect(screen, C_GREEN if can_buy else (100, 100, 100), btn_rect, border_radius=6)
            btn_txt = FONT.render('Beli', True, C_WHITE)
            screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))
            y_pos += 50
    else:
        iron = player['inventory'].get('iron_ore', 0)
        copper = player['inventory'].get('copper_ore', 0)
        if iron > 0:
            item_rect = pygame.Rect(W//2 - 220, y_pos, 440, 40)
            pygame.draw.rect(screen, C_DARK, item_rect, border_radius=8)
            name_txt = FONT_BOLD.render('Bijih Besi', True, C_WHITE)
            screen.blit(name_txt, (W//2 - 200, y_pos + 5))
            count_txt = FONT_SMALL.render(f"Jumlah: {iron}", True, (170, 170, 170))
            screen.blit(count_txt, (W//2 - 200, y_pos + 22))
            price_txt = FONT.render('Koin 5', True, C_GOLD)
            screen.blit(price_txt, (W//2 + 100, y_pos + 12))
            btn_rect = pygame.Rect(W//2 + 180, y_pos + 8, 50, 24)
            pygame.draw.rect(screen, C_RED, btn_rect, border_radius=6)
            btn_txt = FONT.render('Jual', True, C_WHITE)
            screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))
            y_pos += 50
        if copper > 0:
            item_rect = pygame.Rect(W//2 - 220, y_pos, 440, 40)
            pygame.draw.rect(screen, C_DARK, item_rect, border_radius=8)
            name_txt = FONT_BOLD.render('Bijih Tembaga', True, C_WHITE)
            screen.blit(name_txt, (W//2 - 200, y_pos + 5))
            count_txt = FONT_SMALL.render(f"Jumlah: {copper}", True, (170, 170, 170))
            screen.blit(count_txt, (W//2 - 200, y_pos + 22))
            price_txt = FONT.render('Koin 3', True, C_GOLD)
            screen.blit(price_txt, (W//2 + 100, y_pos + 12))
            btn_rect = pygame.Rect(W//2 + 180, y_pos + 8, 50, 24)
            pygame.draw.rect(screen, C_RED, btn_rect, border_radius=6)
            btn_txt = FONT.render('Jual', True, C_WHITE)
            screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))
            y_pos += 50
        if iron == 0 and copper == 0:
            txt = FONT.render('Tidak ada bijih untuk dijual', True, C_GRAY)
            screen.blit(txt, (W//2 - txt.get_width()//2, y_pos + 20))

    close_rect = pygame.Rect(W//2 - 220, H//2 + 160, 440, 30)
    pygame.draw.rect(screen, (74, 74, 106), close_rect, border_radius=8)
    close_txt = FONT.render('Tutup (ESC)', True, C_WHITE)
    screen.blit(close_txt, (close_rect.centerx - close_txt.get_width()//2, close_rect.centery - close_txt.get_height()//2))

def draw_quest_log():
    draw_rect_alpha(screen, (20, 20, 40, 230), (W - 220, 50, 210, 300), radius=10)
    pygame.draw.rect(screen, C_UI_BORDER, (W - 220, 50, 210, 300), 1, border_radius=10)

    title = FONT_BOLD.render('Quest', True, C_GOLD)
    screen.blit(title, (W - 220 + 105 - title.get_width()//2, 60))

    y = 90
    has_quest = False
    for npc in npcs:
        q = npc.get('quest')
        if q and q['given']:
            has_quest = True
            pygame.draw.rect(screen, C_DARK, (W - 210, y, 190, 50), border_radius=6)
            if q['completed']:
                pygame.draw.rect(screen, C_GREEN, (W - 210, y, 3, 50))
            title_txt = FONT_BOLD.render(q['title'], True, C_GOLD)
            screen.blit(title_txt, (W - 200, y + 5))
            desc_txt = FONT_SMALL.render(q['desc'], True, (170, 170, 170))
            screen.blit(desc_txt, (W - 200, y + 22))
            prog_txt = FONT_SMALL.render(f"{min(q['progress'], q['target'])}/{q['target']}", True, C_GREEN)
            screen.blit(prog_txt, (W - 200, y + 36))
            y += 60

    if not has_quest:
        txt = FONT_SMALL.render('Belum ada quest', True, C_GRAY)
        screen.blit(txt, (W - 220 + 105 - txt.get_width()//2, 150))

def draw_inventory():
    draw_rect_alpha(screen, (20, 20, 40, 230), (10, 50, 180, 300), radius=10)
    pygame.draw.rect(screen, C_UI_BORDER, (10, 50, 180, 300), 1, border_radius=10)

    title = FONT_BOLD.render('Inventaris', True, C_GOLD)
    screen.blit(title, (10 + 90 - title.get_width()//2, 60))

    item_info = {
        'sword': ('Pedang', (170, 170, 170)),
        'axe': ('Kapak', (139, 105, 20)),
        'pickaxe': ('Beliung', (139, 105, 20)),
        'potion': ('Ramuan Kesehatan', (231, 76, 60)),
        'iron_ore': ('Bijih Besi', (170, 170, 170)),
        'copper_ore': ('Bijih Tembaga', (200, 117, 51)),
        'wood': ('Kayu', (139, 105, 20))
    }

    y = 90
    has_items = False
    for item_id, count in player['inventory'].items():
        if count <= 0: continue
        has_items = True
        name, color = item_info.get(item_id, (item_id, C_WHITE))
        pygame.draw.rect(screen, C_DARK, (20, y, 160, 26), border_radius=6)
        pygame.draw.circle(screen, color, (32, y + 13), 6)
        txt = FONT.render(f"{name} x{count}", True, C_WHITE)
        screen.blit(txt, (45, y + 6))
        y += 32

    if not has_items:
        txt = FONT_SMALL.render('Inventaris kosong', True, C_GRAY)
        screen.blit(txt, (10 + 90 - txt.get_width()//2, 150))

def draw_minimap():
    mm_w, mm_h = 160, 120
    mm_x, mm_y = W - mm_w - 8, H - mm_h - 8
    draw_rect_alpha(screen, (0, 0, 0, 180), (mm_x, mm_y, mm_w, mm_h))
    pygame.draw.rect(screen, C_UI_BORDER, (mm_x, mm_y, mm_w, mm_h), 2)

    scale_x = mm_w / MAP_W
    scale_y = mm_h / MAP_H

    step = 4
    color_map = {
        'grass': C_GRASS, 'water': C_WATER, 'tree': (45, 90, 30),
        'rock': C_ROCK, 'dirt': C_DIRT, 'cave': C_CAVE,
        'path': C_PATH2, 'flower': C_GRASS
    }
    for ty in range(0, len(map_data), step):
        for tx in range(0, len(map_data[0]), step):
            tile = map_data[ty][tx]
            color = color_map.get(tile, C_GRASS)
            pygame.draw.rect(screen, color, (mm_x + tx * TILE * scale_x, mm_y + ty * TILE * scale_y,
                                             TILE * step * scale_x + 1, TILE * step * scale_y + 1))

    for npc in npcs:
        color = C_GOLD if npc['type'] == 'merchant' else C_WHITE
        pygame.draw.rect(screen, color, (mm_x + npc['x'] * scale_x - 2, mm_y + npc['y'] * scale_y - 2, 4, 4))

    pygame.draw.rect(screen, C_RED, (mm_x + player['x'] * scale_x - 3, mm_y + player['y'] * scale_y - 3, 6, 6))
    pygame.draw.rect(screen, C_WHITE, (mm_x + camera['x'] * scale_x, mm_y + camera['y'] * scale_y,
                                       W * scale_x, H * scale_y), 1)

# ==================== MAIN ====================
def start_screen():
    screen.fill((26, 26, 46))
    title = FONT_TITLE.render('Petualangan Hutan & Tambang', True, C_GOLD)
    screen.blit(title, (W//2 - title.get_width()//2, H//2 - 80))

    sub = FONT.render('Jelajahi hutan luas, tambang bijih, dan kalahkan slime!', True, (170, 170, 170))
    screen.blit(sub, (W//2 - sub.get_width()//2, H//2 - 40))

    btn_rect = pygame.Rect(W//2 - 100, H//2 + 20, 200, 50)
    pygame.draw.rect(screen, C_GOLD, btn_rect, border_radius=12)
    btn_txt = FONT_TITLE.render('Mulai', True, (26, 26, 46))
    screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))

    controls = [
        'WASD / Arrow Keys — Gerak',
        'E — Interaksi dengan NPC',
        'Klik Kiri — Serang / Tebang / Tambang',
        'I — Inventaris | Q — Quest | ESC — Tutup'
    ]
    for i, line in enumerate(controls):
        txt = FONT_SMALL.render(line, True, (100, 100, 100))
        screen.blit(txt, (W//2 - txt.get_width()//2, H//2 + 100 + i * 20))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    waiting = False

def death_screen():
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    title = FONT_TITLE.render('Kamu Mati!', True, C_RED)
    screen.blit(title, (W//2 - title.get_width()//2, H//2 - 40))

    sub = FONT.render('Slime mengalahkannu...', True, (170, 170, 170))
    screen.blit(sub, (W//2 - sub.get_width()//2, H//2))

    btn_rect = pygame.Rect(W//2 - 80, H//2 + 40, 160, 40)
    pygame.draw.rect(screen, C_RED, btn_rect, border_radius=10)
    btn_txt = FONT.render('Bangkit Kembali', True, C_WHITE)
    screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidespoint(event.pos):
                    player['hp'] = player['max_hp']
                    player['x'] = player['spawn_x']
                    player['y'] = player['spawn_y']
                    player['invincible'] = 60
                    global game_paused
                    game_paused = False
                    waiting = False

def main():
    global game_started, game_paused
    global dialogue_active, shop_open
    global quest_log_open, inventory_open
    global mouse_world_x, mouse_world_y
    global shop_tab

    start_screen()
    game_started = True

    generate_map()
    init_entities()

    running = True
    last_time = pygame.time.get_ticks()

    while running:
        now = pygame.time.get_ticks()
        dt = now - last_time
        last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys_pressed[event.key] = True
                if event.key == pygame.K_e:
                    handle_interaction()
                elif event.key == pygame.K_i and not shop_open and not dialogue_active:
                    inventory_open = not inventory_open
                    quest_log_open = False
                elif event.key == pygame.K_q and not shop_open and not dialogue_active:
                    quest_log_open = not quest_log_open
                    inventory_open = False
                elif event.key == pygame.K_ESCAPE:
                    if shop_open: close_shop()
                    elif dialogue_active: close_dialogue()
                    else:
                        inventory_open = False
                        quest_log_open = False
                elif event.key == pygame.K_h:
                    if player['inventory'].get('potion', 0) > 0 and player['hp'] < player['max_hp']:
                        player['inventory']['potion'] -= 1
                        if player['inventory']['potion'] <= 0:
                            del player['inventory']['potion']
                        player['hp'] = min(player['max_hp'], player['hp'] + 20)
                        show_notification('HP +20')
            elif event.type == pygame.KEYUP:
                keys_pressed[event.key] = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                mouse_world_x = mouse_x + camera['x']
                mouse_world_y = mouse_y + camera['y']
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if dialogue_active:
                    for i, choice in enumerate(dialogue_choices):
                        btn_rect = pygame.Rect(W//2 - 280 + i * 150, H - 50, 140, 28)
                        if btn_rect.collidepoint(mx, my):
                            handle_dialogue_choice(i)
                            break
                elif shop_open:
                    buy_rect = pygame.Rect(W//2 - 220, H//2 - 140, 210, 30)
                    sell_rect = pygame.Rect(W//2 + 10, H//2 - 140, 210, 30)
                    if buy_rect.collidepoint(mx, my):
                        shop_tab = 'buy'
                    elif sell_rect.collidepoint(mx, my):
                        shop_tab = 'sell'
                    else:
                        close_rect = pygame.Rect(W//2 - 220, H//2 + 160, 440, 30)
                        if close_rect.collidepoint(mx, my):
                            close_shop()
                        else:
                            y_pos = H//2 - 95
                            if shop_tab == 'buy':
                                for item in shop_npc['shop']['buy']:
                                    btn_rect = pygame.Rect(W//2 + 180, y_pos + 8, 50, 24)
                                    if btn_rect.collidepoint(mx, my):
                                        buy_item(item['id'], item['price'])
                                        break
                                    y_pos += 50
                            else:
                                iron = player['inventory'].get('iron_ore', 0)
                                copper = player['inventory'].get('copper_ore', 0)
                                clicked = False
                                if iron > 0:
                                    btn_rect = pygame.Rect(W//2 + 180, y_pos + 8, 50, 24)
                                    if btn_rect.collidepoint(mx, my):
                                        sell_ore('iron_ore', 5)
                                        clicked = True
                                    y_pos += 50
                                if not clicked and copper > 0:
                                    btn_rect = pygame.Rect(W//2 + 180, y_pos + 8, 50, 24)
                                    if btn_rect.collidepoint(mx, my):
                                        sell_ore('copper_ore', 3)
                elif inventory_open:
                    y = 90
                    for item_id, count in player['inventory'].items():
                        if count <= 0: continue
                        item_rect = pygame.Rect(20, y, 160, 26)
                        if item_rect.collidepoint(mx, my):
                            if item_id == 'potion' and player['hp'] < player['max_hp']:
                                player['inventory']['potion'] -= 1
                                if player['inventory']['potion'] <= 0:
                                    del player['inventory']['potion']
                                player['hp'] = min(player['max_hp'], player['hp'] + 20)
                                show_notification('HP +20')
                            break
                        y += 32
                else:
                    handle_attack()

        update(dt)
        render()
        draw_minimap()
        pygame.display.flip()

        if game_paused and player['hp'] <= 0:
            death_screen()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()