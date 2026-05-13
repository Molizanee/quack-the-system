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

from src.door import Door
from src.levels.level import Level
from src.platform import Platform
from src.rat import Rat
from src.traps import FallingBox
from src.utils.textures import TEXTURES

BACKGROUND_PATH = "src/assets/backgrounds/ods-11-background.png"
MUSIC_PATH = "src/assets/sounds/ods-11.mp3"

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
        music_path=MUSIC_PATH,
    )
    return level, spawn
