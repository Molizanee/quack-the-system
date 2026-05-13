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
from src.water_mine import MineField

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

    # Inimigos radioativos: 16 tubarões e 16 caranguejos. Todos
    # compartilham a tela inteira (sem caixa de patrulha individual),
    # então o enxame fecha em cima do Duck venha ele de onde vier. As
    # posições de spawn formam grades só para o frame inicial parecer
    # arrumado; a partir do primeiro update cada inimigo pode chegar
    # a qualquer canto da tela.
    SCREEN_X_MIN = 20
    SCREEN_X_MAX = 1260
    SHARK_Y_MIN = 20
    SHARK_Y_MAX = H - 100
    CRAB_Y_MIN = 20
    CRAB_Y_MAX = H - 80

    shark_spawn_xs = [180, 520, 860, 1180]
    shark_spawn_ys = [H - 540, H - 420, H - 300, H - 180]
    enemies = []
    for spawn_x in shark_spawn_xs:
        for spawn_y in shark_spawn_ys:
            enemies.append(
                Shark(
                    x_min=SCREEN_X_MIN,
                    x_max=SCREEN_X_MAX,
                    y_min=SHARK_Y_MIN,
                    y_max=SHARK_Y_MAX,
                    start_x=spawn_x,
                    start_y=spawn_y,
                )
            )

    crab_spawn_xs = [100, 260, 420, 580, 740, 900, 1060, 1200]
    crab_spawn_ys = [H - 220, H - 120]  # acima do leito + rente ao leito
    for spawn_x in crab_spawn_xs:
        for spawn_y in crab_spawn_ys:
            enemies.append(
                Crab(
                    x_min=SCREEN_X_MIN,
                    x_max=SCREEN_X_MAX,
                    y_min=CRAB_Y_MIN,
                    y_max=CRAB_Y_MAX,
                    start_x=spawn_x,
                    start_y=spawn_y,
                )
            )

    door = Door(x=1220, ground_y=H - 80)

    spawn = (60, 200)

    atmosphere = WaterAtmosphere(screen_width, screen_height)

    # Minas radioativas aparecem em pontos aleatórios cobrindo a tela
    # inteira — da quase superfície até logo acima do leito, e da borda
    # esquerda à direita. ``min_mine_distance`` força que duas minas não
    # fiquem coladas, espalhando o campo pela tela inteira.
    mine_field = MineField(
        x_min=SCREEN_X_MIN,
        x_max=SCREEN_X_MAX,
        y_min=20,
        y_max=H - 90,
        max_active=20,
        min_mine_distance=160,
    )

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
        mine_field=mine_field,
    )
    return level, spawn
