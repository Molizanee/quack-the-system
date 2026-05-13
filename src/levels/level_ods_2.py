"""Fase 2 — Oceano Contaminado (ODS 14 — Vida na Água).

Bioma: enseada radioativa — única plataforma é o leito marinho. Duck
nada livremente entre tubarões e caranguejos contaminados até alcançar
a porta.

ODS: 14 — Vida na Água.
Tempo de travessia estimado: 1m a 2m.

Layout (sentido leste, do spawn até a porta):

  D> (spawn no alto)
            ~~~~~~~ bolhas e tinta azul cobrem a tela inteira ~~~~~~~

                 🦈  tubarão A patrulha aqui (H-460)
        🦈                 tubarão B patrulha aqui (H-300)
  ___________________________________________________ <- leito (H-80)
        🦀         🦀                                       🚪
       caranguejo A  caranguejo B                          porta

Mecânicas (todas pré-existentes):
* Modo aquático do Player (``swim_mode=True``) reduz gravidade e converte
  cada pulo em um "swim stroke" para cima.
* Sem plataformas no ar, sem entulho caindo, sem nuvens de fumaça —
  apenas inimigos radioativos e o leito marinho.
* Atmosfera (``src.water.WaterAtmosphere``) pinta uma tinta azul sobre
  toda a tela e emite bolhas ambientes; bolhas extras saem do Duck cada
  vez que ele nada para cima.
* Inimigos: ``Shark`` (mid-water) e ``Crab`` (leito). Ambos seguem a
  mesma interface do ``Rat``, então cabem na lista ``Level.enemies``
  sem mudanças no engine.

TODOs (não bloqueiam):
- Sprites definitivos para tubarão e caranguejo.
- Asset de tile para o leito (hoje reusa rock_1b).
- Som de bolha / nado.
"""

from src.crab import Crab
from src.door import Door
from src.levels.level import Level
from src.platform import Platform
from src.shark import Shark
from src.utils.textures import TEXTURES
from src.water import WaterAtmosphere

BACKGROUND_PATH = "src/assets/backgrounds/ods-14-background.png"
MUSIC_PATH = "src/assets/sounds/ods-14.mp3"

ODS_NUMBER = 14
ODS_NAME = "Vida na Água"

INTRO_PANELS = [
    (
        "O mergulho começa com um silêncio estranho. A água tem cor de "
        "ferrugem e algo brilha verde no fundo. Duck percebe rápido: este "
        "oceano foi contaminado por décadas de descarte sem controle."
    ),
    (
        "Tubarões e caranguejos que viviam aqui mudaram. Brilham, atacam "
        "qualquer coisa que se mova, e não dá para passar entre eles à "
        "força — só nadando com paciência, subindo e descendo na hora "
        "certa."
    ),
    (
        "Esta é a segunda parada da viagem: um oceano radioativo. "
        "ODS 14 — Vida na Água."
    ),
]

OUTRO_TEXT = (
    "Os oceanos cobrem mais de 70% do planeta e regulam o clima de todo "
    "mundo. Descarte irregular de resíduos químicos, plástico e esgoto "
    "contamina ecossistemas inteiros e volta para a cadeia alimentar. "
    "Proteger a vida marinha é parte da ODS 14."
)


def create_level_2(
    screen_width: int,
    screen_height: int,
) -> tuple[Level, tuple[int, int]]:
    """Fase 2 — Oceano Contaminado (open water)."""
    H = screen_height

    rock_b = TEXTURES["rock_1b"]

    # Único elemento sólido: leito marinho contínuo.
    seabed = Platform(0, H - 80, 1280, 20, rock_b)
    platforms = [seabed]

    # Sem armadilhas, sem fumaça, sem plataformas flutuantes.
    trap_layouts = [[]]  # uma "lista de armadilhas" vazia satisfaz o engine
    rooftop_platforms: list[Platform] = []
    smog_candidates: list[tuple[int, int, int, int]] = []

    # Inimigos radioativos: cada um patrulha uma "sala" da enseada, mas
    # dentro da própria zona persegue o Duck em x e y com forte jitter
    # aleatório (definido em Shark/Crab) — o jogador tem que cronometrar
    # a entrada em cada sala.
    enemies = [
        # Tubarões — coluna d'água quase inteira por zona horizontal.
        Shark(x_min=100,  x_max=460,  y_min=H - 520, y_max=H - 180),
        Shark(x_min=360,  x_max=720,  y_min=H - 520, y_max=H - 180),
        Shark(x_min=620,  x_max=980,  y_min=H - 520, y_max=H - 180),
        Shark(x_min=860,  x_max=1180, y_min=H - 520, y_max=H - 180),
        # Caranguejos — leito + faixa baixa.
        Crab(x_min=100,  x_max=420,  y_min=H - 200, y_max=H - 80),
        Crab(x_min=360,  x_max=680,  y_min=H - 200, y_max=H - 80),
        Crab(x_min=620,  x_max=940,  y_min=H - 200, y_max=H - 80),
        Crab(x_min=880,  x_max=1180, y_min=H - 200, y_max=H - 80),
    ]

    door = Door(x=1220, ground_y=H - 80)

    spawn = (60, 200)

    atmosphere = WaterAtmosphere(screen_width, screen_height)

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
        door_floor_platform=seabed,
        smog_candidates=smog_candidates,
        smog_count=0,
        swim_mode=True,
        atmosphere=atmosphere,
        music_path=MUSIC_PATH,
    )
    return level, spawn
