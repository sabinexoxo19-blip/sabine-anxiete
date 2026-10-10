"""Version B (essai) : voix dès la 1re image, hook mot à mot, zoom d'entrée.
Fábrica de Reels para el libro 2 de Sabine Mercier (ansiedad) — « Hook + texto », papel crema,
lago al amanecer (decorado sacado de la portada: montañas azules, sol, reflejo, cipreses, olivo).

1. Primer fotograma: el HOOK, grande, visible desde el primer instante (y portada del Reel).
2. El hook se desvanece; el TEXTO aparece párrafo a párrafo, sincronizado con la voz
   (papel crema, sol que sube detrás de las montañas y se refleja en el lago, grano, cámara que se acerca).
3. Última frase con una palabra en caligrafía coral que se escribe; firma « Sabine ».

Marcado: *palabra* = caligrafía coral.  Párrafos del texto = lista de cadenas.
Fuentes libres: DM Serif Display (hook), EB Garamond (texto, la del interior del libro),
Caveat (escritura a mano), Jost (etiquetas).
"""
import os
import re
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
F_HOOK = os.path.join(AQUI, "DMSerifDisplay-Regular.ttf")
F_TEXTO = os.path.join(AQUI, "EBGaramond.ttf")
F_SCRIPT = os.path.join(AQUI, "Caveat.ttf")
F_SANS = os.path.join(AQUI, "Jost.ttf")

W, H = 1080, 1920
FPS = 30
SS = 2
X_MIN, X_MAX = 160, 920            # columna de texto: lejos de los botones de la derecha (x > 950)
Y_ETIQUETA = 400
ZONA_TEXTO = (500, 1290)           # el texto del cuerpo cabe aquí
CENTRO_HOOK = 880
Y_FIRMA = 1380                     # por encima de la leyenda de Instagram (y > 1560)
T_HOOK = 2.6                       # segundos de hook a pantalla completa
ZOOM = 0.035
T_LIBRO = 3.2                      # segundos de foto del libro al final (si se pide)
FUNDIDO_LIBRO = 0.6
PAUSE_PARA = 0.15                  # silence entre deux paragraphes (page 2)
ATTENTE_LIVRE = 1.0               # la page reste 1 s avant la photo du livre
HOOK_PALE = 0.5                    # opacité du hook pas encore lu (lisible dès la 1re image)

PAPEL = np.array([243, 233, 218], dtype=np.float32)
# Colores sacados de la portada del libro 2 (azul « 101 / anxiété », coral de los puntos y del subrayado).
ROJO = (184, 86, 54)               # caligrafía (palabra marcada, firma): coral oscuro, contraste 4:1 sobre el papel
VERDE = (30, 75, 132)              # hook: azul marino de la portada (#1E4B84)
TINTA = (47, 58, 66)               # texto del cuerpo: pizarra oscura, muy legible
TERRA = (196, 110, 76)             # etiqueta « VÉRITÉ N° » y @cuenta: coral de la portada
FIRMA = "@sabine_anxiete"          # compte Instagram du livre 2 (validé le 10 octobre 2026)
FIRMA_VALIDEE = True
NOMBRE = "Sabine"


def fuente(ruta, tam, ejes=None):
    f = ImageFont.truetype(ruta, int(round(tam)))
    if ejes:
        f.set_variation_by_axes(ejes)
    return f


def f_script(tam):
    return fuente(F_SCRIPT, tam, [600])


def f_texto(tam):
    return fuente(F_TEXTO, tam, [470])


def tipografia(texto):
    texto = texto.replace("'", "’").replace("...", "…")
    texto = re.sub(r" ([:;!?»])", " \\1", texto)
    return re.sub(r"« ", "« ", texto)


# ---------------------------------------------------------------- papel y luz
def _suave(rng, escala, w, h):
    pw, ph = max(2, w // escala), max(2, h // escala)
    r = (rng.random((ph, pw)) * 255).astype(np.uint8)
    return np.asarray(Image.fromarray(r).resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0


def papel(seed):
    rng = np.random.default_rng(seed)
    fino = (rng.random((H, W)) * 255).astype(np.uint8)
    fino = np.asarray(Image.fromarray(fino).filter(ImageFilter.GaussianBlur(1.1)), dtype=np.float32) / 255.0
    fibras = _suave(rng, 3, W, H)
    nubes = 0.6 * _suave(rng, 220, W, H) + 0.4 * _suave(rng, 70, W, H)
    nubes -= nubes.mean()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d_l = np.sqrt(((xx - W * 0.30) / W) ** 2 + ((yy - H * 0.30) / H * 0.75) ** 2)
    halo = np.clip(1.0 - d_l / 0.85, 0, 1) ** 1.6
    d_c = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.47) / H) ** 2)
    vin = 1.0 - 0.07 * np.clip((d_c - 0.30) / 0.55, 0, 1) ** 1.5
    base = PAPEL * vin[..., None] * (1 + 0.035 * nubes[..., None])
    base += halo[..., None] * np.array([8, 5, 0], dtype=np.float32)
    base += (fino[..., None] - 0.5) * 7.0 + (fibras[..., None] - 0.5) * 4.0
    return np.clip(base, 0, 255)


def granos(seed, n=8):
    rng = np.random.default_rng(seed + 7)
    return [rng.normal(0, 2.2, (H, W, 1)).astype(np.float32) for _ in range(n)]




# ---------------------------------------------------------------- decorado de la portada
HORIZONTE = 1748                    # línea del lago
SOL_R = 112
SOL_X = 742
SOL_Y0, SOL_Y1 = 1800, 1690          # el sol sube detrás de las montañas
SOL_C = np.array([244, 214, 186], dtype=np.float32)
SOL_B = np.array([248, 230, 205], dtype=np.float32)
RESPLANDOR = np.array([245, 191, 160], dtype=np.float32)   # cielo melocotón cerca del horizonte
NUBE = [(241, 193, 167), (244, 178, 140)]
MONTE_FONDO = (163, 182, 207)
MONTE_IZQ = (123, 150, 193)
MONTE_DER = (142, 146, 169)
LAGO_A = np.array([180, 201, 215], dtype=np.float32)
LAGO_B = np.array([138, 166, 200], dtype=np.float32)
REFLEJO = np.array([245, 215, 177], dtype=np.float32)
CIPRES = [(69, 80, 85), (62, 67, 68)]
OLIVO_V = (110, 124, 114)
OLIVO_O = (79, 86, 72)


def sol():
    """Capa del sol: (alfa, color) a tamaño completo, centrado en (SOL_X, H/2) para desplazarlo.
    Dos finas franjas de papel lo cruzan, como en la portada."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt((xx - SOL_X) ** 2 + (yy - H / 2) ** 2)
    alfa = np.clip((SOL_R - r) / 2.5 + 0.5, 0, 1)
    for dy, gr in ((0.38, 7), (0.62, 5)):
        yb = H / 2 - SOL_R + 2 * SOL_R * dy
        alfa *= 1 - 0.85 * np.clip(1 - np.abs(yy - yb) / gr, 0, 1)
    t = np.clip((yy - (H / 2 - SOL_R)) / (2 * SOL_R), 0, 1)[..., None]
    color = SOL_B * (1 - t) + SOL_C * t
    return alfa, color


def hoja(d, x, y, ang, largo, ancho, color, nervio):
    """Hoja lanceolada dibujada desde su base (x, y) con ángulo en grados (0 = hacia arriba)."""
    a = np.radians(ang)
    ux, uy = np.sin(a), -np.cos(a)            # eje de la hoja
    vx, vy = -uy, ux                          # perpendicular
    izq, der = [], []
    for k in range(41):
        u = k / 40
        w = ancho * np.sin(np.pi * u) ** 0.85 * (1 - 0.25 * u)
        cx, cy = x + ux * largo * u, y + uy * largo * u
        izq.append((cx + vx * w, cy + vy * w))
        der.append((cx - vx * w, cy - vy * w))
    d.polygon(izq + der[::-1], fill=color)
    if nervio:
        d.line([(x, y), (x + ux * largo * 0.92, y + uy * largo * 0.92)], fill=nervio,
               width=max(2, int(ancho * 0.07)))


def _cresta(d, s, x0, x1, base, picos, color):
    """Cordillera: polígono suave que pasa por los picos [(x, y)], cerrado sobre la línea base."""
    xs = np.linspace(x0, x1, 160)
    px = np.array([p[0] for p in picos], dtype=np.float32)
    py = np.array([p[1] for p in picos], dtype=np.float32)
    ys = np.interp(xs, px, py)
    ys += 6 * np.sin(xs / 37.0) + 3 * np.sin(xs / 11.0)
    pts = [(x0 * s, base * s)] + [(x * s, y * s) for x, y in zip(xs, ys)] + [(x1 * s, base * s)]
    d.polygon(pts, fill=color + (255,))


def resplandor():
    """Cielo melocotón muy suave encima del horizonte y nubes alargadas. Devuelve (alfa, color)."""
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    alfa = 0.42 * np.clip((yy - 1470) / (HORIZONTE - 1470), 0, 1) ** 1.6
    alfa[yy >= HORIZONTE] = 0
    color = np.broadcast_to(RESPLANDOR, (H, W, 3)).copy()
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = SS
    for (x0, x1, y, g, c) in [(560, 1080, 1528, 15, NUBE[0]), (690, 1010, 1566, 9, NUBE[1]),
                              (0, 360, 1552, 12, NUBE[0]), (90, 300, 1590, 7, NUBE[1]),
                              (430, 700, 1618, 6, NUBE[0])]:
        d.rounded_rectangle([x0 * s, (y - g) * s, x1 * s, (y + g) * s], radius=g * s, fill=c + (235,))
    arr = np.asarray(img.resize((W, H), Image.LANCZOS), dtype=np.float32)
    an = arr[..., 3] / 255.0
    color = color * (1 - an[..., None]) + arr[..., :3] * an[..., None]
    alfa = np.maximum(alfa, an)
    return alfa, color


def montes():
    """Montañas azules (delante del sol). Devuelve (alfa, color)."""
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = SS
    _cresta(d, s, 0, 1080, HORIZONTE + 2, [(0, 1676), (180, 1640), (330, 1668), (520, 1712),
                                            (680, 1738), (860, 1728), (1000, 1700), (1080, 1690)],
            MONTE_FONDO)
    _cresta(d, s, 0, 760, HORIZONTE + 2, [(0, 1690), (120, 1662), (260, 1650), (400, 1690),
                                           (560, 1730), (760, 1748)], MONTE_IZQ)
    _cresta(d, s, 850, 1080, HORIZONTE + 2, [(850, 1748), (940, 1724), (1020, 1712), (1080, 1716)],
            MONTE_DER)
    arr = np.asarray(img.resize((W, H), Image.LANCZOS), dtype=np.float32)
    return arr[..., 3] / 255.0, arr[..., :3]


def lago():
    """Lago (bajo el horizonte), con degradado. Devuelve (alfa, color)."""
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    alfa = np.clip((yy - HORIZONTE) + 0.5, 0, 1)
    t = np.clip((yy - HORIZONTE) / (H - HORIZONTE), 0, 1)[..., None]
    color = LAGO_A * (1 - t) + LAGO_B * t
    return alfa, color


def reflejo(fase, fuerza):
    """Reflejo del sol en el agua: trazos horizontales que tiemblan. Devuelve alfa (H, W)."""
    a = np.zeros((H, W), dtype=np.float32)
    if fuerza <= 0:
        return a
    rng = np.random.default_rng(5)
    for k in range(16):
        y = HORIZONTE + 8 + k * 11
        if y >= H - 4:
            break
        semi = (SOL_R * 0.95) * (1 - k / 22) * (0.75 + 0.25 * rng.random())
        dx = 9 * np.sin(fase * 1.7 + k * 0.9)
        x0, x1 = int(SOL_X - semi + dx), int(SOL_X + semi + dx)
        g = 2 + (k % 3 == 0)
        a[y - g:y + g, max(0, x0):min(W, x1)] = 0.85 * (1 - k / 20)
    return a * fuerza


def frente():
    """Cipreses (derecha) y rama de olivo (izquierda), delante del lago. Devuelve (alfa, color)."""
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = SS
    for (x, alto, ancho, c) in [(968, 300, 30, CIPRES[0]), (1018, 360, 34, CIPRES[1]),
                                (1062, 250, 28, CIPRES[0]), (918, 190, 22, CIPRES[1])]:
        pts = []
        for k in range(41):
            u = k / 40                                   # 0 = pie, 1 = punta
            w = ancho * (np.sin(np.pi * min(1.0, 0.18 + u * 0.95)) ** 0.7) * (1 - u) ** 0.35
            pts.append((x + w, 1920 - alto * u))
        izq = [(2 * x - px, py) for px, py in pts]
        d.polygon([(px * s, py * s) for px, py in pts + izq[::-1]], fill=c + (255,))
    tallo = [(20 * s, 1960 * s), (88 * s, 1760 * s), (140 * s, 1600 * s)]
    d.line(tallo, fill=OLIVO_O + (255,), width=4 * s, joint="curve")
    for (x, y, ang, l, w, c) in [
        (44, 1880, -62, 175, 22, OLIVO_O), (60, 1830, 50, 185, 23, OLIVO_V),
        (76, 1770, -55, 180, 22, OLIVO_V), (92, 1716, 44, 170, 21, OLIVO_O),
        (108, 1664, -40, 155, 19, OLIVO_V), (122, 1626, 30, 140, 18, OLIVO_O),
        (138, 1600, 4, 120, 16, OLIVO_V),
    ]:
        hoja(d, x * s, y * s, ang, l * s, w * s, c + (255,), None)
    arr = np.asarray(img.resize((W, H), Image.LANCZOS), dtype=np.float32)
    return arr[..., 3] / 255.0, arr[..., :3]


def foto_vertical(ruta):
    """Foto del libro en 9:16: la foto entera en el centro, fondo = la misma foto ampliada y difuminada."""
    im = Image.open(ruta).convert("RGB")
    if abs(im.width / im.height - W / H) < 0.01:
        return im.resize((W, H), Image.LANCZOS)
    k = max(W / im.width, H / im.height)
    fondo_f = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
    x0, y0 = (fondo_f.width - W) // 2, (fondo_f.height - H) // 2
    fondo_f = fondo_f.crop((x0, y0, x0 + W, y0 + H)).filter(ImageFilter.GaussianBlur(38))
    fondo_f = Image.blend(fondo_f, Image.new("RGB", (W, H), (40, 30, 24)), 0.18)
    k2 = 1300 / im.height                      # la foto un peu rognée sur les côtés : le livre reste entier
    nueva = im.resize((int(im.width * k2), int(im.height * k2)), Image.LANCZOS)
    if nueva.width > W:
        x = (nueva.width - W) // 2
        nueva = nueva.crop((x, 0, x + W, nueva.height))
    fondo_f.paste(nueva, ((W - nueva.width) // 2, int(H * 0.44 - nueva.height / 2)))
    return fondo_f


# ---------------------------------------------------------------- maquetación
def capa():
    return Image.new("L", (W * SS, H * SS), 0)


def mascara(img):
    return np.asarray(img.resize((W, H), Image.LANCZOS), dtype=np.float32) / 255.0


def tokens(texto):
    """Palabras = listas de segmentos [(trozo, es_script)]; "\n" fuerza un salto de línea."""
    out, script = [], False
    for linea_i, linea in enumerate(texto.split("\n")):
        if linea_i:
            out.append(None)
        for palabra in linea.split(" "):
            if not palabra:
                continue
            segs, buf = [], ""
            for ch in palabra:
                if ch == "*":
                    if buf:
                        segs.append((buf, script))
                    buf, script = "", not script
                else:
                    buf += ch
            if buf:
                segs.append((buf, script))
            out.append(segs)
    return out


PAD_S = 0.06            # aire alrededor de la escritura a mano (fracción de su tamaño)


def ancho_palabra(segs, fn, fk, d):
    return sum(d.textlength(t, font=fk if es else fn) + (2 * fk.size * PAD_S if es else 0) for t, es in segs)


def partir(toks, fn, fk, ancho_max, d):
    """Reparte las palabras en líneas que caben en ancho_max (respeta los saltos forzados)."""
    esp = d.textlength(" ", font=fn)
    lineas, actual, ancho = [], [], 0.0
    for segs in toks:
        if segs is None:
            if actual:
                lineas.append(actual)
            actual, ancho = [], 0.0
            continue
        w = ancho_palabra(segs, fn, fk, d)
        extra = w + (esp if actual else 0)
        if actual and ancho + extra > ancho_max:
            lineas.append(actual)
            actual, ancho, extra = [], 0.0, w
        actual.append((segs, w))
        ancho += extra
    if actual:
        lineas.append(actual)
    return lineas, esp


def dibujar(lineas, esp, fn, fk, y0, interl, centrar=True):
    """Dibuja líneas en dos capas (texto / caligrafía). Devuelve capas y cajas de caligrafía."""
    ct, ck = capa(), capa()
    dt, dk = ImageDraw.Draw(ct), ImageDraw.Draw(ck)
    d = dt
    cajas = []
    for i, linea in enumerate(lineas):
        total = sum(w for _, w in linea) + esp * (len(linea) - 1)
        x = ((W * SS - total) / 2) if centrar else X_MIN * SS
        yb = y0 + i * interl
        for segs, w in linea:
            for t, es in segs:
                f = fk if es else fn
                wt = d.textlength(t, font=f)
                if es:
                    x += fk.size * PAD_S
                    dk.text((x, yb + interl * 0.04), t, font=fk, fill=255, anchor="ls")
                    cajas.append((x, x + wt, yb))
                    x += fk.size * PAD_S
                else:
                    dt.text((x, yb), t, font=fn, fill=255, anchor="ls")
                x += wt
            x += esp
    return ct, ck, cajas


def sin_viuda(toks, fn, fk, d):
    """Evita una palabra sola en la última línea estrechando un poco la columna."""
    ancho = (X_MAX - X_MIN) * SS
    mejor = partir(toks, fn, fk, ancho, d)
    for k in range(1, 7):
        lineas, esp = partir(toks, fn, fk, ancho * (1 - 0.04 * k), d)
        if len(mejor[0]) < 2 or len(mejor[0][-1]) > 1:
            break
        if len(lineas) == len(mejor[0]) and len(lineas[-1]) > 1:
            return lineas, esp
    return mejor


def hook(texto, d, tam_max=132):
    toks = tokens(tipografia(texto))
    forzadas = texto.count("\n") + 1
    for tam in range(tam_max, 40, -2):
        fn, fk = fuente(F_HOOK, tam * SS), f_script(tam * 1.32 * SS)
        lineas, esp = partir(toks, fn, fk, (X_MAX - X_MIN) * SS, d)
        if len(lineas) <= max(forzadas, 4) and (forzadas == 1 or len(lineas) == forzadas):
            break
    interl = tam * 1.18 * SS
    y0 = CENTRO_HOOK * SS - interl * (len(lineas) - 1) / 2 + tam * 0.33 * SS
    ct, ck, _ = dibujar(lineas, esp, fn, fk, y0, interl)
    # une couche par mot, pour les faire apparaître au rythme de la voix
    mots, k = [], 0
    for i, linea in enumerate(lineas):
        total = sum(w for _, w in linea) + esp * (len(linea) - 1)
        x = (W * SS - total) / 2
        yb = y0 + i * interl
        for segs, w in linea:
            ct2, ck2 = capa(), capa()
            dt2, dk2 = ImageDraw.Draw(ct2), ImageDraw.Draw(ck2)
            for t, es in segs:
                f = fk if es else fn
                wt = dt2.textlength(t, font=f)
                if es:
                    x += fk.size * PAD_S
                    dk2.text((x, yb + interl * 0.04), t, font=fk, fill=255, anchor="ls")
                    x += fk.size * PAD_S
                else:
                    dt2.text((x, yb), t, font=fn, fill=255, anchor="ls")
                x += wt
            x += esp
            mots.append((mascara(ct2), mascara(ck2), sum(len(t) for t, _ in segs) + 1))
    return mascara(ct), mascara(ck), mots


def cuerpo(parrafos, d):
    """Maqueta el texto: elige el mayor tamaño que cabe en ZONA_TEXTO."""
    alto_zona = (ZONA_TEXTO[1] - ZONA_TEXTO[0]) * SS
    for tam in range(66, 37, -1):
        fn, fk = f_texto(tam * SS), f_script(tam * 1.4 * SS)
        interl, hueco = tam * 1.36 * SS, tam * 0.62 * SS
        bloques = [sin_viuda(tokens(tipografia(p)), fn, fk, d) for p in parrafos]
        alto = sum(len(l) for l, _ in bloques) * interl + hueco * (len(bloques) - 1)
        if alto <= alto_zona:
            break
    y = ZONA_TEXTO[0] * SS + (alto_zona - alto) / 2 + tam * 0.9 * SS
    piezas = []
    for (lineas, esp), p in zip(bloques, parrafos):
        ct, ck, cajas = dibujar(lineas, esp, fn, fk, y, interl)
        palabras = len([t for t in tokens(p) if t])
        piezas.append((mascara(ct), mascara(ck), [(a / SS, b / SS) for a, b, _ in cajas], palabras))
        y += len(lineas) * interl + hueco
    return piezas, tam


def etiqueta(numero, d):
    c = capa()
    dd = ImageDraw.Draw(c)
    f = fuente(F_SANS, 30 * SS, [430])
    txt = f"VÉRITÉ N° {numero}" if numero else "101 VÉRITÉS"
    sep = 8 * SS
    ancho = sum(dd.textlength(ch, font=f) for ch in txt) + sep * (len(txt) - 1)
    x = (W * SS - ancho) / 2
    for ch in txt:
        dd.text((x, Y_ETIQUETA * SS), ch, font=f, fill=255, anchor="ls")
        x += dd.textlength(ch, font=f) + sep
    dd.line([(W * SS / 2 - 26 * SS, (Y_ETIQUETA + 40) * SS), (W * SS / 2 + 26 * SS, (Y_ETIQUETA + 40) * SS)],
            fill=255, width=2 * SS)
    return mascara(c)


def firma(d):
    cn, cf = capa(), capa()
    fn = f_script(92 * SS)
    ImageDraw.Draw(cn).text((W * SS / 2, Y_FIRMA * SS), NOMBRE, font=fn, fill=255, anchor="ms")
    an = d.textlength(NOMBRE, font=fn) / SS
    ImageDraw.Draw(cf).text((W * SS / 2, (Y_FIRMA + 60) * SS), FIRMA, font=fuente(F_SANS, 27 * SS, [380]),
                            fill=255, anchor="ms")
    return mascara(cn), mascara(cf), (W / 2 - an / 2 - 20, W / 2 + an / 2 + 20)


# ---------------------------------------------------------------- audio
def duracion_audio(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def duracion_parlee(ruta):
    """Durée jusqu'à la fin de la dernière parole (le silence de fin du MP3 Azure n'est pas compté)."""
    total = duracion_audio(ruta)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", ruta, "-af", "silencedetect=noise=-45dB:d=0.12",
                        "-f", "null", "-"], capture_output=True, text=True)
    debuts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    fins = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    # dernier silence qui court jusqu'à la fin du fichier (selon la version de ffmpeg, avec ou sans silence_end)
    if debuts and debuts[-1] > 0.5 and (len(debuts) > len(fins) or fins[-1] >= total - 0.08):
        return min(total, debuts[-1] + 0.08)
    return total


def entrada_audio(pistas, duracion):
    """Argumentos ffmpeg: silencio si no hay voz; si no, cada frase colocada en su instante."""
    if not pistas:
        return ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                "-shortest", "-map", "0:v", "-map", "1:a"]
    args, filtros = [], []
    for k, (ruta, t0) in enumerate(pistas, start=1):
        args += ["-i", ruta]
        ms = int(t0 * 1000)
        filtros.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[a{k}]")
    mezcla = "".join(f"[a{k}]" for k in range(1, len(pistas) + 1))
    filtros.append(f"{mezcla}amix=inputs={len(pistas)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,"
                   f"aresample=48000,apad,atrim=0:{duracion:.3f}[voz]")
    return args + ["-filter_complex", ";".join(filtros), "-map", "0:v", "-map", "[voz]"]


# ---------------------------------------------------------------- animación
def suav(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def generar(hook_txt, parrafos, destino_mp4, destino_jpg, seed=1, numero=None, espera=4.0, voces=None,
            fin_livre=None):
    """Crea el Reel y su portada (el hook). Devuelve (duración, instante de portada en ms).

    voces: lista opcional de archivos de audio [hook, párrafo 1, párrafo 2, …] leídos por la voz.
    Si se dan, el texto se sincroniza con la voz.
    fin_livre: foto del libro (jpg 9:16) que aparece al final con un fundido y un zoom lento.
    """
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    base = papel(seed)
    ruido = granos(seed)
    m_hook, m_hook_k, mots_hook = hook(hook_txt, d)
    m_et = etiqueta(numero, d)
    piezas, _ = cuerpo(parrafos, d)
    m_nom, m_fir, (fx0, fx1) = firma(d)
    sol_a, sol_c = sol()
    re_a, re_c = resplandor()
    mo_a, mo_c = montes()
    la_a, la_c = lago()
    fr_a, fr_c = frente()
    re_a3, mo_a3, la_a3, fr_a3 = re_a[..., None], mo_a[..., None], la_a[..., None], fr_a[..., None]
    cielo = base * (1 - re_a3) + re_c * re_a3

    agenda, pistas = [], []
    if voces:
        assert len(voces) == len(piezas) + 1, "hace falta un audio para el hook y uno por párrafo"
        durs = [duracion_parlee(v) for v in voces]       # sans le silence de fin du MP3
        t = 0.0                                        # la voz arranca al primer fotograma
        pistas.append((voces[0], t))
        t_hook = t + durs[0] + 0.25
        dur_mots = durs[0] * 0.92
        t = t_hook + 0.3
        for (m_t, m_k, cajas, _), v, dv in zip(piezas, voces[1:], durs[1:]):
            agenda.append((t - 0.15, m_t, m_k, cajas))
            pistas.append((v, t))
            t += dv + PAUSE_PARA
        espera = min(espera, 3.0)
    else:
        t_hook = T_HOOK
        t = T_HOOK + 0.35
        for m_t, m_k, cajas, palabras in piezas:   # ≈ 0,19 s por palabra, mínimo 1,1 s
            agenda.append((t, m_t, m_k, cajas))
            t += max(1.1, 0.19 * palabras)
    if not voces:
        dur_mots = 1.6
    car = [c for _, _, c in mots_hook]
    tot = float(sum(car))
    t_mots, acc = [], 0.0
    for c in car:
        t_mots.append(dur_mots * acc / tot)
        acc += c
    t_mots_fin = dur_mots + 0.15
    t_firma = t + 0.2
    fin_anim = t_firma + 1.6
    duracion = fin_anim + espera
    t_libro = None
    if fin_livre:                                  # la página se queda 1,8 s y llega el libro
        t_libro = fin_anim + min(espera, ATTENTE_LIVRE)
        duracion_texto = t_libro
        duracion = t_libro + T_LIBRO
        foto = foto_vertical(fin_livre)
    else:
        duracion_texto = duracion
    n = int(round(duracion * FPS))
    xs = np.arange(W, dtype=np.float32)[None, :]
    C = {k: np.array(v, dtype=np.float32) for k, v in
         dict(rojo=ROJO, verde=VERDE, tinta=TINTA, terra=TERRA).items()}

    def poner(img, a, col):
        a = a[..., None] * 0.96
        return img * (1 - a) + col * a

    def trazo(m, t0, x0, x1, dur, tt):
        p = (tt - t0) / dur
        if p <= 0:
            return None
        return m if p >= 1 else m * np.clip((x0 + (x1 - x0) * p - xs) / 40.0 + 1.0, 0, 1)

    t_sol_fin = min(duracion, 8.0)

    def fondo(tt):
        """Papel + cielo melocotón + sol (subiendo) + montañas + lago con reflejo + cipreses y olivo + etiqueta."""
        img = cielo.copy()
        k = suav(tt / t_sol_fin)
        y_sol = SOL_Y0 + (SOL_Y1 - SOL_Y0) * k
        off = int(round(y_sol - H / 2))
        if off < H:
            a = np.zeros((H, W, 1), dtype=np.float32)
            c = np.zeros((H, W, 3), dtype=np.float32)
            if off >= 0:
                a[off:, :, 0] = sol_a[:H - off]
                c[off:] = sol_c[:H - off]
            else:
                a[:H + off, :, 0] = sol_a[-off:]
                c[:H + off] = sol_c[-off:]
            img = img * (1 - a) + c * a
        img = img * (1 - mo_a3) + mo_c * mo_a3
        img = img * (1 - la_a3) + la_c * la_a3
        r = reflejo(min(tt, t_sol_fin) * 2.0, 0.25 + 0.75 * k)[..., None]
        img = img * (1 - r) + REFLEJO * r
        img = img * (1 - fr_a3) + fr_c * fr_a3
        return poner(img, m_et, C["terra"])

    def caja(cajas):
        return min(c[0] for c in cajas) - 10, max(c[1] for c in cajas) + 10

    def terminado(item, tt):
        t0, _, _, cajas = item
        return tt >= t0 + 0.55 and (not cajas or tt >= t0 + 1.0)

    cache = {"img": None, "k": 0}          # párrafos ya completos, « horneados » sobre el fondo fijo

    def pagina(tt):
        if tt < t_sol_fin:
            img, desde = fondo(tt), 0
        else:
            if cache["img"] is None:
                cache["img"] = fondo(t_sol_fin)
            while cache["k"] < len(agenda) and terminado(agenda[cache["k"]], tt):
                _, m_t, m_k, cajas = agenda[cache["k"]]
                cache["img"] = poner(cache["img"], m_t, C["tinta"])
                if cajas:
                    cache["img"] = poner(cache["img"], m_k, C["rojo"])
                cache["k"] += 1
            img, desde = cache["img"].copy(), cache["k"]
        a_h = 1.0 - suav((tt - t_hook) / 0.4)                       # hook: visible desde el fotograma 1
        if a_h > 0:
            if tt >= t_mots_fin:
                img = poner(img, m_hook * a_h, C["verde"])
                img = poner(img, m_hook_k * a_h, C["rojo"])
            else:
                for (mt, mk, _), t0m in zip(mots_hook, t_mots):
                    # tout le hook est lisible dès la 1re image (pâle), chaque mot fonce quand la voix le lit
                    p = suav((tt - t0m) / 0.12) if t0m > 0 else 1.0
                    p = HOOK_PALE + (1 - HOOK_PALE) * p
                    img = poner(img, mt * p * a_h, C["verde"])
                    img = poner(img, mk * p * a_h, C["rojo"])
        for t0, m_t, m_k, cajas in agenda[desde:]:
            p = suav((tt - t0) / 0.55)
            if p <= 0:
                break                                               # la agenda va en orden
            desp = int(round((1 - p) * 14))
            a = m_t * p
            if desp:
                a = np.roll(a, desp, axis=0)
                a[:desp] = 0
            img = poner(img, a, C["tinta"])
            if cajas:
                x0, x1 = caja(cajas)
                ak = trazo(m_k, t0 + 0.3, x0, x1, 0.7, tt)
                if ak is not None:
                    img = poner(img, ak, C["rojo"])
        an = trazo(m_nom, t_firma, fx0, fx1, 1.0, tt)
        if an is not None:
            img = poner(img, an, C["rojo"])
            img = poner(img, m_fir * suav((tt - t_firma - 0.8) / 0.8), C["terra"])
        return img

    def camara(img, tt, i):
        z = 1.0 + ZOOM * suav(min(tt, duracion_texto) / duracion_texto) + 0.06 * (1 - suav(tt / 0.6))
        im = Image.fromarray(np.clip(img + ruido[(i // 3) % len(ruido)], 0, 255).astype(np.uint8))
        cw, ch = W / z, H / z
        x0, y0 = (W - cw) / 2, (H - ch) * 0.47
        return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

    def libro(tt, pg, i):
        """Foto del libro con zoom lento; fundido desde la página al principio."""
        k = (tt - t_libro) / T_LIBRO
        z = 1.0 + 0.04 * k
        cw, ch = W / z, H / z
        x0, y0 = (W - cw) / 2, (H - ch) / 2
        im = foto.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        a = suav((tt - t_libro) / FUNDIDO_LIBRO)
        if a < 1:
            im = Image.blend(camara(pg, tt, i), im, float(a))
        return im

    portada_t = round(min(t_mots_fin + 0.05, t_hook - 0.05), 2)
    camara(pagina(portada_t), portada_t, 0).save(destino_jpg, "JPEG", quality=93)

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           *entrada_audio(pistas, duracion),
           "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "1200k", "-bufsize", "2400k",
           "-pix_fmt", "yuv420p",
           "-g", str(FPS * 2), "-profile:v", "high",
           "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
           "-movflags", "+faststart", destino_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    final = None
    for i in range(n):
        tt = i / FPS
        if tt >= fin_anim:
            final = final if final is not None else pagina(fin_anim)
            pg = final
        else:
            pg = pagina(tt)
        if t_libro is not None and tt >= t_libro:
            p.stdin.write(libro(tt, pg, i).tobytes())
        else:
            p.stdin.write(camara(pg, tt, i).tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("ffmpeg falló")
    return duracion, int(portada_t * 1000)


if __name__ == "__main__":
    HOOK = "Si un coucher de soleil\npeut te faire pleurer,\nc'est une *bonne* nouvelle."
    TEXTO = [
        "Le capteur qui te fait souffrir dans une pièce bruyante, c'est le même qui te fait pleurer devant un morceau de musique.",
        "Celui qui absorbe la tristesse des autres, c'est le même qui te fait vibrer devant un ciel que personne autour de toi ne lève les yeux pour voir.",
        "Ta sensibilité n'a pas deux réglages. Elle n'en a qu'un, et il est réglé sur intense.",
        "Tu ne portes pas seulement le poids du monde. Tu en reçois aussi toute la *lumière.*",
    ]
    print(generar(HOOK, TEXTO, os.path.join(AQUI, "prueba.mp4"), os.path.join(AQUI, "prueba.jpg"),
                  seed=89, numero=89))
