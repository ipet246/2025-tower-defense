import pygame
import sys
import random
import os
import math

# --- INICIALIZACIÓN ---
pygame.init()
pygame.mixer.init() # Para el sonido (aunque no lo usemos, es buena práctica)

# --- CONFIGURACIÓN ---
ANCHO, ALTO = 800, 600
FPS = 60
FUENTE = pygame.font.Font(None, 36)
FUENTE_GRANDE = pygame.font.Font(None, 72)

# --- COLORES ---
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AMARILLO = (255, 255, 0)
AZUL = (0, 100, 255)
MARRON = (139, 69, 19)
VERDE_OSCURO = (0, 100, 0)
GRIS = (128, 128, 128)
CELESTE = (135, 206, 235)

# --- VENTANA ---
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tower Defense Definitivo")
reloj = pygame.time.Clock()

# --- RUTAS (Ajusta estas rutas a tu proyecto) ---
# Como no tengo tus imágenes, las crearé proceduralmente.
# Si tienes las imágenes, descomenta las líneas de carga y comenta las de creación procedural.
RUTA_MAP = "map.png"
RUTA_TORRE = "tower.png"
RUTA_ENEMY = "enemy.png"

# --- FUNCION CARGAR IMÁGENES (O CREAR PROCEDURALMENTE) ---
def cargar_o_crear_imagen(ruta, tamaño, color_relleno):
    if os.path.exists(ruta):
        img = pygame.image.load(ruta).convert_alpha()
        return pygame.transform.scale(img, tamaño)
    else:
        print(f"⚠️ No se encontró {ruta}, creando imagen procedural.")
        superficie = pygame.Surface(tamaño, pygame.SRCALPHA)
        superficie.fill(color_relleno)
        return superficie

# --- CARGAR IMÁGENES ---
imagen_mapa = cargar_o_crear_imagen(RUTA_MAP, (ANCHO, ALTO), (34, 139, 34)) # Fondo verde
imagen_torre = cargar_o_crear_imagen(RUTA_TORRE, (35, 35), GRIS)
imagen_enemigo = cargar_o_crear_imagen(RUTA_ENEMY, (30, 30), ROJO)

# --- RUTA DEL CAMINO ---
ruta_camino = [
    (60, 350), (200, 350), (200, 270),
    (400, 270), (400, 400), (600, 400),
    (600, 250), (800, 250)
]

# --- CLASES ---
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, color_texto=BLANCO):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_texto = color_texto
        self.font = FUENTE

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)
        pygame.draw.rect(pantalla, BLANCO, self.rect, 2)
        texto_surf = self.font.render(self.texto, True, self.color_texto)
        texto_rect = texto_surf.get_rect(center=self.rect.center)
        pantalla.blit(texto_surf, texto_rect)

    def fue_clickeado(self, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(evento.pos)

class Nube:
    def __init__(self):
        self.x = random.randint(-100, ANCHO)
        self.y = random.randint(20, 150)
        self.velocidad = random.uniform(0.1, 0.3)
        self.tamano = random.randint(40, 70)

    def mover(self):
        self.x += self.velocidad
        if self.x > ANCHO + 100:
            self.x = random.randint(-200, -100)
            self.y = random.randint(20, 150)

    def dibujar(self, pantalla):
        # Dibuja una nube simple con círculos
        pygame.draw.circle(pantalla, BLANCO, (int(self.x), int(self.y)), self.tamano)
        pygame.draw.circle(pantalla, BLANCO, (int(self.x - self.tamano * 0.5), int(self.y)), int(self.tamano * 0.8))
        pygame.draw.circle(pantalla, BLANCO, (int(self.x + self.tamano * 0.5), int(self.y)), int(self.tamano * 0.8))

class Arbol:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tronco_ancho = 15
        self.tronco_alto = 30
        self.hoja_radio = random.randint(25, 40)

    def dibujar(self, pantalla):
        # Tronco
        pygame.draw.rect(pantalla, MARRON, (self.x - self.tronco_ancho // 2, self.y, self.tronco_ancho, self.tronco_alto))
        # Hojas
        pygame.draw.circle(pantalla, VERDE_OSCURO, (self.x, self.y - 5), self.hoja_radio)

class Enemigo:
    def __init__(self, vida_maxima=100):
        self.pos_punto = 0
        self.x, self.y = ruta_camino[0]
        self.velocidad = random.uniform(1.0, 2.0)
        self.vida_maxima = vida_maxima
        self.vida = vida_maxima
        self.vivo = True
        self.recompensa = 50

    def mover(self):
        if self.pos_punto < len(ruta_camino) - 1:
            objetivo = ruta_camino[self.pos_punto + 1]
            dx, dy = objetivo[0] - self.x, objetivo[1] - self.y
            distancia = math.hypot(dx, dy)
            if distancia > 0:
                paso_x = self.velocidad * dx / distancia
                paso_y = self.velocidad * dy / distancia
                self.x += paso_x
                self.y += paso_y

            if abs(self.x - objetivo[0]) < 2 and abs(self.y - objetivo[1]) < 2:
                self.x, self.y = objetivo
                self.pos_punto += 1
        else:
            self.vivo = False
            return "llegó"

    def dibujar(self, pantalla):
        pantalla.blit(imagen_enemigo, (self.x - 15, self.y - 15))
        # Barra de vida
        ancho_barra = 30
        alto_barra = 4
        pygame.draw.rect(pantalla, ROJO, (self.x - ancho_barra // 2, self.y - 25, ancho_barra, alto_barra))
        pygame.draw.rect(pantalla, VERDE, (self.x - ancho_barra // 2, self.y - 25, ancho_barra * (self.vida / self.vida_maxima), alto_barra))

class Torre:
    COSTO_BASE = 100
    COSTO_MEJORA = 75
    VENTA_REEMBOLSO = 0.5 # 50% del costo total

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.nivel = 1
        self.rango = 120
        self.daño = 25
        self.tiempo_disparo = 0
        self.cadencia = 600  # ms
        self.seleccionada = False

    def mejorar(self):
        self.nivel += 1
        self.daño += 15
        self.rango += 10
        self.cadencia = max(200, self.cadencia - 50) # Dispara más rápido

    def get_costo_mejora(self):
        return self.COSTO_MEJORA * self.nivel

    def get_valor_venta(self):
        costo_total = self.COSTO_BASE + sum([self.COSTO_MEJORA * i for i in range(1, self.nivel)])
        return int(costo_total * self.VENTA_REEMBOLSO)

    def dibujar(self, pantalla):
        color_rango = VERDE if not self.seleccionada else AMARILLO
        pygame.draw.circle(pantalla, color_rango, (self.x, self.y), self.rango, 1)
        pantalla.blit(imagen_torre, (self.x - 17, self.y - 17))
        
        # Indicador de nivel
        nivel_texto = FUENTE.render(str(self.nivel), True, BLANCO)
        pantalla.blit(nivel_texto, (self.x - 5, self.y - 5))

    def disparar(self, enemigos):
        if pygame.time.get_ticks() - self.tiempo_disparo > self.cadencia:
            for enemigo in enemigos:
                distancia = math.hypot(enemigo.x - self.x, enemigo.y - self.y)
                if distancia < self.rango:
                    enemigo.vida -= self.daño
                    self.tiempo_disparo = pygame.time.get_ticks()
                    break

# --- FUNCIONES DE DIBUJO ---
def dibujar_camino(pantalla, puntos, ancho=40):
    for i in range(len(puntos) - 1):
        pygame.draw.line(pantalla, (100, 50, 10), puntos[i], puntos[i+1], ancho + 4)
    for i in range(len(puntos) - 1):
        pygame.draw.line(pantalla, MARRON, puntos[i], puntos[i+1], ancho)
    for punto in puntos:
        pygame.draw.circle(pantalla, (100, 50, 10), punto, ancho // 2 + 2)
        pygame.draw.circle(pantalla, MARRON, punto, ancho // 2)

def dibujar_ui_juego(pantalla, dinero, vidas, puntaje, mensaje):
    texto = FUENTE.render(f"Puntaje: {puntaje}   💰 {dinero}   ❤️ {vidas}", True, BLANCO)
    ventana.blit(texto, (10, 10))
    if mensaje:
        aviso = FUENTE.render(mensaje, True, AMARILLO)
        ventana.blit(aviso, (180, 560))

# --- FUNCIONES DE MANEJO DE DATOS ---
def guardar_puntaje(nombre, puntaje):
    with open("ranking100.txt", "a") as f:
        f.write(f"{nombre},{puntaje}\n")

def leer_puntajes(top=100):
    if not os.path.exists("ranking100.txt"):
        return []
    with open("ranking100.txt", "r") as f:
        lineas = f.readlines()
    puntajes = []
    for linea in lineas:
        try:
            nombre, p = linea.strip().split(",")
            puntajes.append((nombre, int(p)))
        except ValueError:
            continue
    return sorted(puntajes, key=lambda x: x[1], reverse=True)[:top]

def cargar_estadisticas(nombre):
    if not os.path.exists("estadisticas.txt"):
        return {"jugadas": 0, "enemigos_eliminados": 0, "dinero_gastado": 0}
    with open("estadisticas.txt", "r") as f:
        for linea in f:
            n, jugadas, eliminados, gastado = linea.strip().split(",")
            if n == nombre:
                return {"jugadas": int(jugadas), "enemigos_eliminados": int(eliminados), "dinero_gastado": int(gastado)}
    return {"jugadas": 0, "enemigos_eliminados": 0, "dinero_gastado": 0}

def guardar_estadisticas(nombre, stats):
    lineas = []
    jugador_encontrado = False
    if os.path.exists("estadisticas.txt"):
        with open("estadisticas.txt", "r") as f:
            lineas = f.readlines()
    
    with open("estadisticas.txt", "w") as f:
        for linea in lineas:
            n, jugadas, eliminados, gastado = linea.strip().split(",")
            if n == nombre:
                f.write(f"{nombre},{stats['jugadas']},{stats['enemigos_eliminados']},{stats['dinero_gastado']}\n")
                jugador_encontrado = True
            else:
                f.write(linea)
        if not jugador_encontrado:
            f.write(f"{nombre},{stats['jugadas']},{stats['enemigos_eliminados']},{stats['dinero_gastado']}\n")


# --- PANTALLAS DEL JUEGO ---
def pantalla_menu_principal():
    titulo = FUENTE_GRANDE.render("Tower Defense", True, BLANCO)
    boton_jugar = Boton(300, 200, 200, 50, "Jugar", VERDE)
    boton_opciones = Boton(300, 270, 200, 50, "Opciones", AZUL)
    boton_tutorial = Boton(300, 340, 200, 50, "Tutorial", AMARILLO)
    boton_ranking = Boton(300, 410, 200, 50, "Ranking", ROJO)
    boton_salir = Boton(300, 480, 200, 50, "Salir", GRIS)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if boton_jugar.fue_clickeado(evento):
                return "JUGAR"
            if boton_opciones.fue_clickeado(evento):
                return "OPCIONES"
            if boton_tutorial.fue_clickeado(evento):
                return "TUTORIAL"
            if boton_ranking.fue_clickeado(evento):
                return "RANKING"
            if boton_salir.fue_clickeado(evento):
                pygame.quit()
                sys.exit()

        ventana.fill(NEGRO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))
        boton_jugar.dibujar(ventana)
        boton_opciones.dibujar(ventana)
        boton_tutorial.dibujar(ventana)
        boton_ranking.dibujar(ventana)
        boton_salir.dibujar(ventana)
        pygame.display.flip()
        reloj.tick(FPS)

def pantalla_opciones(nombre_jugador):
    # Simulación de estado de música
    musica_activada = True
    boton_volver = Boton(300, 500, 200, 50, "Volver", GRIS)
    boton_musica = Boton(300, 200, 200, 50, "Musica: ON" if musica_activada else "Musica: OFF", AZUL)
    
    stats = cargar_estadisticas(nombre_jugador)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if boton_volver.fue_clickeado(evento):
                return "MENU"
            if boton_musica.fue_clickeado(evento):
                musica_activada = not musica_activada
                boton_musica.texto = "Musica: ON" if musica_activada else "Musica: OFF"
                print(f"Música {'activada' if musica_activada else 'desactivada'}")

        ventana.fill(NEGRO)
        titulo = FUENTE_GRANDE.render("Opciones", True, BLANCO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))
        
        boton_musica.dibujar(ventana)
        
        # Mostrar estadísticas
        stats_titulo = FUENTE.render(f"Estadísticas de {nombre_jugador}", True, AMARILLO)
        ventana.blit(stats_titulo, (ANCHO // 2 - stats_titulo.get_width() // 2, 280))
        
        stats_texto = [
            f"Partidas Jugadas: {stats['jugadas']}",
            f"Enemigos Eliminados: {stats['enemigos_eliminados']}",
            f"Dinero Total Gastado: {stats['dinero_gastado']}"
        ]
        for i, texto in enumerate(stats_texto):
            surf = FUENTE.render(texto, True, BLANCO)
            ventana.blit(surf, (ANCHO // 2 - surf.get_width() // 2, 330 + i * 40))

        boton_volver.dibujar(ventana)
        pygame.display.flip()
        reloj.tick(FPS)

def pantalla_tutorial():
    boton_volver = Boton(300, 500, 200, 50, "Volver", GRIS)
    
    reglas = [
        "1. El objetivo es evitar que los enemigos lleguen al final.",
        "2. Coloca torres cerca del camino para que ataquen.",
        "3. Las torres cuestan 100 de oro.",
        "4. Al eliminar enemigos, obtienes oro y puntos.",
        "5. Haz clic en una torre para mejorarla o venderla.",
        "6. Mejorar aumenta el daño y el rango.",
        "7. Vender una torre te devuelve el 50% de su inversión.",
        "8. Si pierdes todas tus vidas (10), el juego termina."
    ]

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if boton_volver.fue_clickeado(evento):
                return "MENU"

        ventana.fill(NEGRO)
        titulo = FUENTE_GRANDE.render("Tutorial", True, BLANCO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))
        
        for i, regla in enumerate(reglas):
            texto_surf = FUENTE.render(regla, True, BLANCO)
            ventana.blit(texto_surf, (50, 120 + i * 40))
            
        boton_volver.dibujar(ventana)
        pygame.display.flip()
        reloj.tick(FPS)

def pantalla_ranking():
    boton_volver = Boton(300, 520, 200, 50, "Volver", GRIS)
    top = leer_puntajes(100)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if boton_volver.fue_clickeado(evento):
                return "MENU"
        
        ventana.fill(NEGRO)
        titulo = FUENTE_GRANDE.render("Ranking Top 100", True, AMARILLO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 20))

        if not top:
            texto = FUENTE.render("Aún no hay puntajes guardados", True, BLANCO)
            ventana.blit(texto, (220, 250))
        else:
            # Crear una superficie para el ranking con scroll
            y_offset = 80
            for i, (nombre, puntaje) in enumerate(top[:20]): # Mostrar solo los primeros 20 por espacio
                t = FUENTE.render(f"{i+1:2d}. {nombre:<15} - {puntaje}", True, BLANCO)
                ventana.blit(t, (150, y_offset + i * 25))
        
        boton_volver.dibujar(ventana)
        pygame.display.flip()
        reloj.tick(FPS)

def pantalla_juego(nombre_jugador):
    # Inicialización del juego
    arboles = [Arbol(random.randint(50, ANCHO-50), random.randint(50, ALTO-50)) for _ in range(15)]
    nubes = [Nube() for _ in range(5)]
    
    enemigos = []
    torres = []
    puntaje = 0
    dinero = 500
    vidas = 10
    mensaje = ""
    tiempo_mensaje = 0
    spawn_timer = 0
    torre_seleccionada = None

    # Estadísticas de la partida actual
    stats_partida = {"enemigos_eliminados": 0, "dinero_gastado": 0}

    corriendo = True
    while corriendo:
        dt = reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "SALIR"
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = evento.pos
                
                # Deseleccionar torre si se hace clic en el vacío
                torre_seleccionada = None
                for t in torres:
                    t.seleccionada = False

                # Comprobar si se hizo clic en una torre
                for torre in torres:
                    if math.hypot(torre.x - x, torre.y - y) < 20:
                        torre_seleccionada = torre
                        torre.seleccionada = True
                        break
                
                # Si no se seleccionó una torre, intentar colocar una nueva
                if not torre_seleccionada:
                    distancia_camino = min([math.hypot(px - x, py - y) for px, py in ruta_camino])
                    if dinero >= Torre.COSTO_BASE and 30 < distancia_camino < 100:
                        if not any(math.hypot(t.x - x, t.y - y) < 40 for t in torres):
                            torres.append(Torre(x, y))
                            dinero -= Torre.COSTO_BASE
                            stats_partida['dinero_gastado'] += Torre.COSTO_BASE
                        else:
                            mensaje = "¡Demasiado cerca de otra torre!"
                            tiempo_mensaje = pygame.time.get_ticks()
                    else:
                        mensaje = "¡Coloca torres cerca del camino!"
                        tiempo_mensaje = pygame.time.get_ticks()

            elif evento.type == pygame.KEYDOWN:
                if torre_seleccionada:
                    if evento.key == pygame.K_u: # Mejorar
                        costo = torre_seleccionada.get_costo_mejora()
                        if dinero >= costo:
                            dinero -= costo
                            stats_partida['dinero_gastado'] += costo
                            torre_seleccionada.mejorar()
                            mensaje = f"¡Torre mejorada a Nivel {torre_seleccionada.nivel}!"
                            tiempo_mensaje = pygame.time.get_ticks()
                        else:
                            mensaje = "¡No tienes suficiente oro!"
                            tiempo_mensaje = pygame.time.get_ticks()
                    elif evento.key == pygame.K_s: # Vender
                        dinero += torre_seleccionada.get_valor_venta()
                        torres.remove(torre_seleccionada)
                        torre_seleccionada = None
                        mensaje = "Torre vendida."
                        tiempo_mensaje = pygame.time.get_ticks()

        # Lógica del juego
        spawn_timer += dt
        if spawn_timer > 2000: # Spawn cada 2 segundos
            enemigos.append(Enemigo(vida_maxima=100 + puntaje // 10)) # Los enemigos se vuelven más resistentes
            spawn_timer = 0

        for enemigo in enemigos[:]:
            if enemigo.mover() == "llegó":
                vidas -= 1
                enemigos.remove(enemigo)

        for torre in torres:
            torre.disparar(enemigos)

        for enemigo in enemigos[:]:
            if enemigo.vida <= 0:
                enemigos.remove(enemigo)
                dinero += enemigo.recompensa
                puntaje += 10
                stats_partida['enemigos_eliminados'] += 1

        if vidas <= 0:
            # Guardar estadísticas y puntaje al finalizar
            stats = cargar_estadisticas(nombre_jugador)
            stats['jugadas'] += 1
            stats['enemigos_eliminados'] += stats_partida['enemigos_eliminados']
            stats['dinero_gastado'] += stats_partida['dinero_gastado']
            guardar_estadisticas(nombre_jugador, stats)
            guardar_puntaje(nombre_jugador, puntaje)
            return "GAME_OVER"

        # Dibujar
        ventana.blit(imagen_mapa, (0, 0))
        for nube in nubes:
            nube.mover()
            nube.dibujar(ventana)
        for arbol in arboles:
            arbol.dibujar(ventana)
        
        dibujar_camino(ventana, ruta_camino)
        
        for torre in torres:
            torre.dibujar(ventana)
        for enemigo in enemigos:
            enemigo.dibujar(ventana)

        # UI de torre seleccionada
        if torre_seleccionada:
            ui_y = torre_seleccionada.y - 60
            mejora_texto = FUENTE.render(f"[U] Mejorar ({torre_seleccionada.get_costo_mejora()}G)", True, AMARILLO)
            venta_texto = FUENTE.render(f"[S] Vender ({torre_seleccionada.get_valor_venta()}G)", True, ROJO)
            ventana.blit(mejora_texto, (torre_seleccionada.x - mejora_texto.get_width()//2, ui_y))
            ventana.blit(venta_texto, (torre_seleccionada.x - venta_texto.get_width()//2, ui_y + 25))

        dibujar_ui_juego(ventana, dinero, vidas, puntaje, mensaje)
        
        if mensaje and pygame.time.get_ticks() - tiempo_mensaje > 2000:
            mensaje = ""

        pygame.display.flip()

def pantalla_game_over(nombre_jugador, puntaje):
    mostrar_ranking(ventana) # Reutilizamos la pantalla de ranking
    # Pequeña pausa antes de volver al menú
    pygame.time.wait(1000) 
    return "MENU"

# --- BUCLE PRINCIPAL ---
def main():
    estado = "MENU"
    nombre_jugador = input("Ingresa tu nombre: ") or "Jugador"

    while True:
        if estado == "MENU":
            estado = pantalla_menu_principal()
        elif estado == "JUGAR":
            resultado = pantalla_juego(nombre_jugador)
            if resultado == "GAME_OVER":
                estado = pantalla_game_over(nombre_jugador, 0) # Puntaje se guarda internamente
            else: # SALIR
                pygame.quit()
                sys.exit()
        elif estado == "OPCIONES":
            estado = pantalla_opciones(nombre_jugador)
        elif estado == "TUTORIAL":
            estado = pantalla_tutorial()
        elif estado == "RANKING":
            estado = pantalla_ranking()
        elif estado == "SALIR":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()