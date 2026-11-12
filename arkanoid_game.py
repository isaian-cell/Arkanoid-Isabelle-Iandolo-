"""Plantilla del juego Arkanoid para el hito M2.

Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""
from pathlib import Path

from arkanoid_core import *
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

@arkanoid_method
def cargar_nivel(self) -> list[str]:
    if not Path(self.level_path).is_file():
        raise FileNotFoundError(f"El fichero {self.level_path} no existe.")
    contenido = Path(self.level_path).read_text(encoding='utf-8')
    filas = []
    for linea in contenido.splitlines():
        linea_limpia = linea.strip()
        if linea_limpia:
            filas.append(linea_limpia)
    ancho = len(filas[0])
    for f in filas:
        if len(f)!= ancho:
            raise ValueError("No todas las filas tienen el mismo ancho")
    self.layout = filas
    return self.layout 

@arkanoid_method
def preparar_entidades(self) -> None:
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""
    self.paddle = self.crear_rect(0,0, 120,18)
    self.paddle.midbottom = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 25)
    self.score = 0
    self.lives = 3
    self.end_message = ""
    self.reiniciar_bola((1, -1))
    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.
    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.

@arkanoid_method
@arkanoid_method
def crear_bloques(self) -> None:
    """Genera los rectángulos de los bloques en base a la cuadrícula."""
    self.blocks = []
    self.block_colors = []
    self.block_symbols = []

    for f in range(len(self.layout)):
        fila = self.layout[f]
        for col in range(len(fila)):
            simbolo = fila[col]
            if simbolo == '.' or simbolo not in self.BLOCK_COLORS:
                continue

            # calcular_posicion_bloque calcula x e y, y devuelve directamente el Rect
            rect = self.calcular_posicion_bloque(f, col)

            self.blocks.append(rect)
            self.block_colors.append(self.BLOCK_COLORS[simbolo])
            self.block_symbols.append(simbolo)
    
@arkanoid_method
def procesar_input(self) -> None:
    teclas = self.obtener_estado_teclas()
    izquierda = teclas[self.KEY_LEFT] or teclas[self.KEY_A]
    derecha = teclas[self.KEY_RIGHT] or teclas[self.KEY_D]
    desplazamiento = (int(bool(derecha)) - int(bool(izquierda))) * self.PADDLE_SPEED
    self.paddle.x += desplazamiento
    self.paddle.left = max(0, self.paddle.left)
    self.paddle.right = min(self.SCREEN_WIDTH, self.paddle.right)
    """Gestiona la entrada de teclado para mover la paleta."""
    # - Obtén el estado de teclas con `self.obtener_estado_teclas()`.
    # - Desplaza la paleta con `self.PADDLE_SPEED` si se pulsan las teclas izquierda/derecha.
    # - Limita la posición para que no salga de la pantalla.

@arkanoid_method
def actualizar_bola(self) -> None:
# Movimiento de la bola
    self.ball_pos += self.ball_velocity
    ball_rect = self.obtener_rect_bola()
#Rebotes con paredes y techo
    if ball_rect.left <= 0 and self.ball_velocity.x < 0:
        self.ball_velocity.x *= -1
    elif ball_rect.right >= self.SCREEN_WIDTH and self.ball_velocity.x > 0:
        self.ball_velocity.x *= -1

#Rebote con el techo
    if ball_rect.top <= 0 and self.ball_velocity.y < 0:
        self.ball_velocity.y *= -1
#Rebote con la paleta
    # 4. Rebote con la paleta (permite dirigir la bola hacia izquierda o derecha)
    if ball_rect.colliderect(self.paddle) and self.ball_velocity.y > 0:
        desplazamiento = (self.ball_pos.x - self.paddle.centerx) / (self.paddle.width / 2)
        desplazamiento = max(-1.0, min(1.0, desplazamiento))

        self.ball_velocity = Vector2(desplazamiento, -1).normalize() * self.BALL_SPEED
        self.ball_pos.y = self.paddle.top - self.BALL_RADIUS

#Colisión con bloques
    for n in range(len(self.blocks)):
        if ball_rect.colliderect(self.blocks[n]):
            self.blocks.pop(n)
            self.block_colors.pop(n)
            simbolo = self.block_symbols.pop(n)

            puntos = self.BLOCK_POINTS.get(simbolo, 50)
            self.score += puntos

            self.ball_velocity.y *= -1
            if len(self.blocks) == 1:
                self.BALL_SPEED *= 2
                self.ball_velocity *= 2

            break

#Sumar puntos según el tipo de bloque
            puntos = self.BLOCK_POINTS.get(simbolo, 50)
            self.score += puntos
            self.ball_velocity.y *= -1
            break

#Caída por el borde inferior (pérdida de vida)
    if ball_rect.top >= self.SCREEN_HEIGHT:
        self.lives -= 1
        if self.lives <= 0:
            self.end_message = "Game Over"
            self.ball_velocity = Vector2(0, 0)
        else:
            self.reiniciar_bola()

    if not self.blocks and not self.end_message:
        self.end_message = "¡Victoria!"
        self.score += 100

@arkanoid_method
def dibujar_escena(self) -> None:
# - Rellena el fondo y dibuja cada bloque con `self.dibujar_rectangulo`.
    self.screen.fill(self.BACKGROUND_COLOR)
    for i in range(len(self.blocks)):
        self.dibujar_rectangulo(self.blocks[i], self.block_colors[i])

# - Pinta la paleta y la bola con las utilidades proporcionadas.
    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)
    centro_bola = (int(self.ball_pos.x), int(self.ball_pos.y))
    self.dibujar_circulo(centro_bola, self.BALL_RADIUS, self.BALL_COLOR)

# - Muestra puntuación, vidas y mensajes usando `self.dibujar_texto`.
    self.dibujar_texto(f"Puntos: {self.score}", (20, 10))
    self.dibujar_texto(f"Vidas: {self.lives}", (self.SCREEN_WIDTH - 120, 10))
    if self.end_message:
        self.dibujar_texto(
            self.end_message,
            (self.SCREEN_WIDTH // 2 - 120, self.SCREEN_HEIGHT // 2),
                grande=True)

    
@arkanoid_method
def run(self) -> None:
    """Implementa el bucle de juego principal."""
#el código a continuación me lo ha dado gemini porque no el run no me funcionaba
    import os
    if os.name == "nt" and "SDL_VIDEODRIVER" not in os.environ:
        os.environ["SDL_VIDEODRIVER"] = "windows"

    self.inicializar_pygame()
    # ... rest of your run() code ...
    # 1. Inicializar la ventana y el reloj antes de cargar datos
    self.inicializar_pygame()

    # 2. Cargar el mapa y preparar los elementos
    self.cargar_nivel()
    self.preparar_entidades()
    self.crear_bloques()

    jugando = True
    while jugando:
        for evento in self.iterar_eventos():
            if evento.type == self.EVENT_QUIT:
                jugando = False
            elif evento.type == self.EVENT_KEYDOWN:
                if evento.key == self.KEY_ESCAPE:
                    jugando = False

        if not self.end_message:
            self.procesar_input()
            self.actualizar_bola()

        self.dibujar_escena()
        self.actualizar_pantalla()
        self.clock.tick(self.FPS)

    self.finalizar_pygame()



def main() -> None:
    """Permite ejecutar el juego desde la línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Plantilla del hito M2: Arkanoid con pygame.",
    )
    parser.add_argument(
        "level",
        type=str,
        help="Ruta al fichero de nivel (texto con # para bloques y . para huecos).",
    )
    args = parser.parse_args()

    game = ArkanoidGame(args.level)
    game.run()


if __name__ == "__main__":
    main()

# python arkanoid_game.py niveles/demo.txt se añade a la terminal

