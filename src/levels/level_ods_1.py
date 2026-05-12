"""Fase 1 — Cidade Poluída (ODS 11 — Cidades e Comunidades Sustentáveis).

Bioma: cidade poluída.
ODS: 11 — Cidades e Comunidades Sustentáveis.
Tempo de travessia estimado: 1m30 a 2m30.

Layout (sentido leste, do spawn até a porta):

                                ┌───────┐                ┌───────┐
                                │  alto │                │  alto │       <- mirantes opcionais (H-360)
                                └───────┘                └───────┘
        ┌──────┐                  ┌──────┐                  ┌──────┐
        │ real │   ┌──────┐       │ real │   ┌──────┐       │ real │     <- telhados (H-220)
        └──────┘   │ FAKE │       └──────┘   │ FAKE │       └──────┘
                   └──────┘                  └──────┘
                          ☁ (smog sorteado a cada run)

  D>            [▓▓▓▓]   [▓▓▓▓▓]   [▓▓▓▓]   [▓▓▓▓]   [DOOR]   🚪
  spawn          seg 1     seg 2     seg 3     seg 4*
                          rat ↔                     (* colapsa se nunca pisou em telhado)

Armadilhas que quebram expectativa:
1. Dois telhados FAKE no caminho do alto (x=440 e x=820) — colapsam após
   0,18 s. Quem tenta cortar caminho pelo telhado cai no vão.
2. Caixas de entulho ("debris") caem do céu quando Duck passa por baixo —
   três arranjos sorteados a cada run.
3. Nuvens de fumaça (smog) cobrem a tela inteira por 1,6 s assim que Duck
   entra na zona. **Posição é sorteada por run** entre 4 pontos candidatos
   ao longo do nível.
4. Enquanto qualquer smog está ativo, entulho extra cai do céu em posições
   aleatórias entre Duck e a porta. Quem entra na fumaça e fica parado é
   esmagado.
5. **Armadilha de "chão fácil"**: o segmento do piso embaixo da porta cai
   no instante em que Duck pisa nele — *desde que Duck nunca tenha tocado
   em nenhum telhado durante essa run*. Quem tenta passar a fase só pelo
   chão morre. Pisar num telhado uma vez já desarma a armadilha.

Inimigo específico: Rato (``src.rat.Rat``) patrulha o segundo segmento do
piso. Sprite final ainda não existe — desenhado como caixa escura com olhos
vermelhos por enquanto.

TODOs (não bloqueiam):
- Asset de "concreto rachado" para os debris (hoje usa rock_1a via alias).
- Sprite definitivo do rato.
"""

import random

import pygame

from src.door import Door
from src.platform import Platform
from src.rat import Rat
from src.smog import SmogCloud
from src.traps import FallingBox
from src.utils.textures import TEXTURES

BACKGROUND_PATH = "src/assets/backgrounds/ods-11-background.png"

ODS_NUMBER = 11
ODS_NAME = "Cidades e Comunidades Sustentáveis"

INTRO_PANELS = [
    (
        "O cheiro do ar pesado chega antes da paisagem. Duck avança pelos "
        "telhados de uma cidade que esqueceu de respirar. Concreto rachado, "
        "fumaça baixa, ruído constante."
    ),
    (
        "Há lugares onde o chão parece firme e cede. Há cantos onde a fumaça "
        "esconde o que vem depois. Quem mora aqui aprendeu a desconfiar do "
        "óbvio — e Duck vai precisar fazer o mesmo."
    ),
    (
        "Esta é a primeira parada da viagem: uma cidade poluída. "
        "ODS 11 — Cidades e Comunidades Sustentáveis."
    ),
]

OUTRO_TEXT = (
    "Cidades sustentáveis são lugares em que moradia, transporte, ar e "
    "segurança funcionam para todo mundo, não só para alguns. Reduzir "
    "poluição, melhorar a habitação e proteger os espaços públicos são parte "
    "da ODS 11."
)

# Cadência da chuva de entulho enquanto o smog está ativo.
FOG_DEBRIS_INTERVAL = 0.42  # segundos entre cada caixa extra


class Level:
    """Container for everything that lives inside a phase."""

    def __init__(
        self,
        platforms: list[Platform],
        trap_layouts: list[list[FallingBox]],
        door: Door,
        enemies: list[Rat],
        ods_number: int,
        ods_name: str,
        intro_panels: list[str],
        outro_text: str,
        background_path: str,
        rooftop_platforms: list[Platform],
        door_floor_platform: Platform,
        smog_candidates: list[tuple[int, int, int, int]],
        smog_count: int,
    ) -> None:
        self.platforms = platforms
        self.trap_layouts = trap_layouts
        self.door = door
        self.enemies = enemies
        self.ods_number = ods_number
        self.ods_name = ods_name
        self.intro_panels = intro_panels
        self.outro_text = outro_text
        self.background_path = background_path

        self.rooftop_platforms = rooftop_platforms
        self.door_floor_platform = door_floor_platform
        self.smog_candidates = smog_candidates
        self.smog_count = smog_count

        self.traps = random.choice(self.trap_layouts)
        self.smog_clouds = self._roll_smog_clouds()
        self.dynamic_traps: list[FallingBox] = []

        self._rooftop_visited = False
        self._smog_active = False
        self._fog_debris_carry = 0.0

    # ── Helpers ─────────────────────────────────────────────────

    def _roll_smog_clouds(self) -> list[SmogCloud]:
        count = min(self.smog_count, len(self.smog_candidates))
        choices = random.sample(self.smog_candidates, count)
        return [SmogCloud(x=x, y=y, width=w, height=h) for x, y, w, h in choices]

    def _check_rooftop_visited(self, player_rect: pygame.Rect) -> None:
        if self._rooftop_visited:
            return
        for rooftop in self.rooftop_platforms:
            # Standing on a rooftop reads as feet aligned with the top edge.
            # Mid-jump overlap counts too, so the trap disarms even on a brush.
            standing_on = (
                rooftop.rect.left <= player_rect.centerx <= rooftop.rect.right
                and abs(player_rect.bottom - rooftop.rect.top) < 8
            )
            if standing_on or rooftop.rect.colliderect(player_rect):
                self._rooftop_visited = True
                return

    def _check_door_floor_trap(self, player_rect: pygame.Rect) -> None:
        if self._rooftop_visited:
            return
        floor = self.door_floor_platform
        if floor.state != "stable":
            return
        # Player must be standing on top of the floor segment for the trap to fire.
        on_top = (
            floor.rect.left <= player_rect.centerx <= floor.rect.right
            and abs(player_rect.bottom - floor.rect.top) < 6
        )
        if on_top:
            floor.state = "collapsing"
            floor.collapse_timer = 0.0

    def _spawn_fog_debris(self, player_rect: pygame.Rect) -> None:
        """Drop one extra debris box between Duck and the door."""
        spawn_left = max(player_rect.right + 20, 80)
        spawn_right = self.door.rect.left - 40
        if spawn_left >= spawn_right:
            return
        x = random.randint(spawn_left, spawn_right)
        box = FallingBox(x=x, texture_key="debris_1")
        # Start already falling from above the screen so it lands without the
        # usual proximity-arming step.
        box.rect.x = x
        box.rect.y = -box.BOX_SIZE
        box.state = "falling"
        box.velocity_y = 80.0
        self.dynamic_traps.append(box)

    # ── Level lifecycle ─────────────────────────────────────────

    def update(
        self, dt: float, player_rect: pygame.Rect, screen_h: int
    ) -> None:
        for platform in self.platforms:
            platform.update(dt)
        for trap in self.traps:
            trap.update(dt, player_rect, screen_h)
        for enemy in self.enemies:
            enemy.update(dt)
        for cloud in self.smog_clouds:
            cloud.update(dt, player_rect)
        self.door.update(dt, player_rect)

        self._check_rooftop_visited(player_rect)
        self._check_door_floor_trap(player_rect)

        # Fog-time debris — while any smog is in its triggered state, drop
        # extra rocks at a steady cadence.
        self._smog_active = any(c.state == "triggered" for c in self.smog_clouds)
        if self._smog_active:
            self._fog_debris_carry += dt
            while self._fog_debris_carry >= FOG_DEBRIS_INTERVAL:
                self._fog_debris_carry -= FOG_DEBRIS_INTERVAL
                self._spawn_fog_debris(player_rect)
        else:
            self._fog_debris_carry = 0.0

        for trap in self.dynamic_traps:
            trap.update(dt, player_rect, screen_h)
        self.dynamic_traps = [
            t for t in self.dynamic_traps if t.state != "broken"
        ]

    def player_lethal_hit(self, player_rect: pygame.Rect) -> bool:
        if any(trap.is_lethal(player_rect) for trap in self.traps):
            return True
        if any(trap.is_lethal(player_rect) for trap in self.dynamic_traps):
            return True
        if any(enemy.is_lethal(player_rect) for enemy in self.enemies):
            return True
        return False

    def is_complete(self, player_rect: pygame.Rect) -> bool:
        return self.door.player_passed_through(player_rect)

    def reset(self) -> None:
        for platform in self.platforms:
            platform.reset()
        self.traps = random.choice(self.trap_layouts)
        for trap in self.traps:
            trap.reset()
        for enemy in self.enemies:
            enemy.reset()
        self.smog_clouds = self._roll_smog_clouds()
        self.dynamic_traps.clear()
        self.door.reset()
        self._rooftop_visited = False
        self._smog_active = False
        self._fog_debris_carry = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        for cloud in self.smog_clouds:
            cloud.draw_footprint(screen)
        for platform in self.platforms:
            platform.draw(screen)
        for trap in self.traps:
            trap.draw(screen)
        for trap in self.dynamic_traps:
            trap.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        self.door.draw(screen)
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        for cloud in self.smog_clouds:
            cloud.draw_screen_overlay(screen, screen_w, screen_h)


def create_level_1(
    screen_height: int,
) -> tuple[Level, tuple[int, int]]:
    """Fase 1 — Cidade Poluída."""
    H = screen_height

    rock_a = TEXTURES["rock_1a"]
    rock_b = TEXTURES["rock_1b"]
    rock_c = TEXTURES["rock_1c"]
    rock_d = TEXTURES["rock_1d"]

    # ─── Piso — quatro segmentos separados por vãos letais ──────
    floor_segments = [
        Platform(0,    H - 80,  300, 20, rock_b),
        Platform(380,  H - 80,  240, 20, rock_b),
        Platform(700,  H - 80,  220, 20, rock_b),
        Platform(1000, H - 80,  280, 20, rock_b),
    ]
    door_floor_platform = floor_segments[3]

    # ─── Telhados (H-220) — rota alternativa com dois fakes ─────
    rooftop_platforms = [
        Platform(180,  H - 220, 128, 20, rock_c),
        Platform(440,  H - 220, 128, 20, rock_a, is_fake=True),
        Platform(620,  H - 220, 144, 20, rock_c),
        Platform(820,  H - 220, 128, 20, rock_a, is_fake=True),
        Platform(1040, H - 220, 144, 20, rock_c),
    ]

    # ─── Mirantes altos (H-360) — opcionais ─────────────────────
    lookouts = [
        Platform(320,  H - 360, 128, 20, rock_d),
        Platform(760,  H - 360, 128, 20, rock_d),
    ]

    platforms = floor_segments + rooftop_platforms + lookouts

    # Três arranjos de entulho — um é sorteado a cada run.
    trap_layouts_x = [
        [340, 520, 660, 860, 950, 1140],
        [250, 460, 740, 870, 1080, 1200],
        [380, 580, 690, 820, 970, 1100],
    ]
    trap_layouts = [
        [FallingBox(x=x, texture_key="debris_1") for x in layout]
        for layout in trap_layouts_x
    ]

    # Candidatos de smog — em cada run sorteia 2 desses 5 pontos.
    smog_candidates = [
        (340, H - 200, 180, 140),  # sobre o vão entre seg 1 e seg 2
        (610, H - 200, 180, 140),  # sobre o vão entre seg 2 e seg 3
        (820, H - 200, 180, 140),  # em cima do telhado fake 2
        (940, H - 200, 180, 140),  # sobre o vão final antes da porta
        (480, H - 320, 160, 130),  # mais alto, junto ao telhado fake 1
    ]

    enemies = [
        Rat(patrol_min_x=390, patrol_max_x=615, ground_y=H - 80),
    ]

    door = Door(x=1220, ground_y=H - 80)

    spawn = (60, 200)

    level = Level(
        platforms=platforms,
        trap_layouts=trap_layouts,
        door=door,
        enemies=enemies,
        ods_number=ODS_NUMBER,
        ods_name=ODS_NAME,
        intro_panels=INTRO_PANELS,
        outro_text=OUTRO_TEXT,
        background_path=BACKGROUND_PATH,
        rooftop_platforms=rooftop_platforms,
        door_floor_platform=door_floor_platform,
        smog_candidates=smog_candidates,
        smog_count=2,
    )
    return level, spawn
