import random
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters,
)

# ── Token del bot ────────────────────────────────────────────
TOKEN = "8868233156:AAHlSpVn3MOxex2OaSAGFdjz-b_7uNVedXI"

# ══════════════════════════════════════════════════════════════
#  DATOS SIMULADOS ADRES
# ══════════════════════════════════════════════════════════════
EPS_LIST = [
    "COOSALUD EPS S.A.",
    "NUEVA EPS S.A.",
    "SANITAS EPS",
    "SURA EPS",
    "FAMISANAR EPS",
    "COMPENSAR EPS",
    "SALUD TOTAL EPS",
    "MEDIMAS EPS",
    "ALIANSALUD EPS",
    "CAPRESOCA EPS",
]
REGIMENES = ["SUBSIDIADO", "CONTRIBUTIVO"]
TIPOS_AFILIADO = ["CABEZA DE FAMILIA", "BENEFICIARIO", "COTIZANTE INDEPENDIENTE"]
ESTADOS_EPS = ["ACTIVO", "ACTIVO", "ACTIVO", "SUSPENDIDO", "RETIRADO"]

NOMBRES_ADRES = [
    ("LAURA PATRICIA",  "MENDEZ TORRES"),
    ("JORGE IVAN",      "CASTILLO RIOS"),
    ("PATRICIA",        "GOMEZ SILVA"),
    ("ANDRES CAMILO",   "VARGAS PEREZ"),
    ("DIANA MARCELA",   "LOPEZ HERRERA"),
    ("OSCAR JULIAN",    "MORENO CASTRO"),
    ("CAROLINA",        "SUAREZ JIMENEZ"),
    ("FABIO ANDRES",    "RAMIREZ ORTIZ"),
    ("NATALIA",         "GUTIERREZ ALBA"),
    ("WILLIAM",         "SANCHEZ MORA"),
]

MUNICIPIOS_ADRES = [
    ("CARTAGENA",    "BOLIVAR"),
    ("MEDELLIN",     "ANTIOQUIA"),
    ("BOGOTA",       "CUNDINAMARCA"),
    ("CALI",         "VALLE DEL CAUCA"),
    ("BARRANQUILLA", "ATLANTICO"),
    ("BUCARAMANGA",  "SANTANDER"),
    ("PEREIRA",      "RISARALDA"),
    ("MANIZALES",    "CALDAS"),
    ("NEIVA",        "HUILA"),
    ("CUCUTA",       "NORTE DE SANTANDER"),
]


def generar_adres(cedula: str) -> dict:
    seed = sum(int(d) * (i + 3) for i, d in enumerate(cedula))
    rng  = random.Random(seed)
    nombres, apellidos = rng.choice(NOMBRES_ADRES)
    municipio, departamento = rng.choice(MUNICIPIOS_ADRES)
    eps     = rng.choice(EPS_LIST)
    regimen = rng.choice(REGIMENES)
    estado  = rng.choice(ESTADOS_EPS)
    tipo    = rng.choice(TIPOS_AFILIADO)
    year    = rng.randint(2000, 2023)
    month   = rng.randint(1, 12)
    day     = rng.randint(1, 28)
    cel     = f"3{rng.randint(100000000, 999999999)}"
    return {
        "cedula":          cedula,
        "adres_encontrado": True,
        "adres_tipo":      "CC",
        "nombres":         nombres,
        "apellidos":       apellidos,
        "departamento":    departamento,
        "municipio":       municipio,
        "telefono":        cel,
        "eps": {
            "estado":          estado,
            "entidad":         eps,
            "regimen":         regimen,
            "fecha_afiliacion": f"{day:02d}/{month:02d}/{year}",
            "tipo_afiliado":   tipo,
        },
    }


def fmt_adres(d: dict) -> str:
    eps   = d["eps"]
    emoji = "✅" if eps["estado"] == "ACTIVO" else "⚠️"
    return (
        f"{'='*40}\n"
        f"🏥 *CONSULTA ADRES - COLOMBIA*\n"
        f"{'='*40}\n\n"
        f"🪪 Cédula: `{d['cedula']}`\n"
        f"📌 Tipo: {d['adres_tipo']}\n"
        f"{'─'*40}\n\n"
        f"*DATOS PERSONALES:*\n"
        f"👤 Nombres:      `{d['nombres']}`\n"
        f"👤 Apellidos:    `{d['apellidos']}`\n"
        f"🗺  Departamento: {d['departamento']}\n"
        f"🏙  Municipio:    {d['municipio']}\n"
        f"📱 Teléfono:     {d['telefono']}\n"
        f"{'─'*40}\n\n"
        f"*DATOS EPS:*\n"
        f"{emoji} Estado:          *{eps['estado']}*\n"
        f"🏥 Entidad:          {eps['entidad']}\n"
        f"📋 Régimen:          {eps['regimen']}\n"
        f"📅 Fecha afiliación: {eps['fecha_afiliacion']}\n"
        f"👥 Tipo afiliado:    {eps['tipo_afiliado']}\n\n"
        f"{'='*40}"
    )

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ══════════════════════════════════════════════════════════════
#  DATOS SIMULADOS RUI/SISBÉN
# ══════════════════════════════════════════════════════════════
DEPARTAMENTOS = {
    "05": "ANTIOQUIA",       "08": "ATLÁNTICO",
    "11": "BOGOTÁ D.C.",     "13": "BOLÍVAR",
    "15": "BOYACÁ",          "17": "CALDAS",
    "19": "CAUCA",           "20": "CESAR",
    "25": "CUNDINAMARCA",    "41": "HUILA",
    "47": "MAGDALENA",       "50": "META",
    "52": "NARIÑO",          "54": "NORTE DE SANTANDER",
    "63": "QUINDÍO",         "66": "RISARALDA",
    "68": "SANTANDER",       "73": "TOLIMA",
    "76": "VALLE DEL CAUCA",
}
MUNICIPIOS = {
    "05001": ("MEDELLÍN",            "05"),
    "08001": ("BARRANQUILLA",        "08"),
    "11001": ("BOGOTÁ D.C.",         "11"),
    "13001": ("CARTAGENA DE INDIAS", "13"),
    "15001": ("TUNJA",               "15"),
    "17001": ("MANIZALES",           "17"),
    "19001": ("POPAYÁN",             "19"),
    "41001": ("NEIVA",               "41"),
    "47001": ("SANTA MARTA",         "47"),
    "50001": ("VILLAVICENCIO",       "50"),
    "52001": ("PASTO",               "52"),
    "54001": ("CÚCUTA",              "54"),
    "63001": ("ARMENIA",             "63"),
    "66001": ("PEREIRA",             "66"),
    "68001": ("BUCARAMANGA",         "68"),
    "73001": ("IBAGUÉ",              "73"),
    "76001": ("CALI",                "76"),
}
GRUPOS_SISBEN = {
    "A1": ("A", "Pobreza extrema - sin ingresos"),
    "A2": ("A", "Pobreza extrema"),
    "A3": ("A", "Pobreza extrema - ingresos mínimos"),
    "B1": ("B", "Pobreza moderada"),
    "B2": ("B", "Pobreza moderada - ingresos bajos"),
    "B3": ("B", "Pobreza moderada"),
    "B4": ("B", "Pobreza moderada - en transición"),
    "C1": ("C", "Vulnerable"),
    "C2": ("C", "Vulnerable"),
    "C3": ("C", "Vulnerable"),
    "C4": ("C", "Vulnerable"),
    "D1": ("D", "No clasificado como vulnerable"),
    "D2": ("D", "No clasificado como vulnerable"),
}
NOMBRES = [
    ("CARLOS ANDRES",   "PEREZ GOMEZ"),
    ("DIANA PATRICIA",  "RODRIGUEZ SILVA"),
    ("JOSE LUIS",       "MARTINEZ VARGAS"),
    ("MARIA FERNANDA",  "LOPEZ CASTILLO"),
    ("ANDRES FELIPE",   "GARCIA TORRES"),
    ("LUCIA ESPERANZA", "HERRERA MENDEZ"),
    ("JUAN PABLO",      "SANCHEZ RIOS"),
    ("VALENTINA",       "MORENO CRUZ"),
    ("SANTIAGO",        "JIMENEZ PARDO"),
    ("ISABELLA",        "RAMIREZ ACOSTA"),
    ("MIGUEL ANGEL",    "CASTRO REYES"),
    ("CAMILA ANDREA",   "ORTIZ NAVARRO"),
    ("DAVID ALEJANDRO", "VARGAS LEON"),
    ("SARA LUCIA",      "GUTIERREZ ALBA"),
    ("SEBASTIAN",       "MORA PINEDA"),
]
SEXOS = {
    "CARLOS ANDRES": "Masculino", "DIANA PATRICIA": "Femenino",
    "JOSE LUIS": "Masculino",     "MARIA FERNANDA": "Femenino",
    "ANDRES FELIPE": "Masculino", "LUCIA ESPERANZA": "Femenino",
    "JUAN PABLO": "Masculino",    "VALENTINA": "Femenino",
    "SANTIAGO": "Masculino",      "ISABELLA": "Femenino",
    "MIGUEL ANGEL": "Masculino",  "CAMILA ANDREA": "Femenino",
    "DAVID ALEJANDRO": "Masculino","SARA LUCIA": "Femenino",
    "SEBASTIAN": "Masculino",
}
GRUPOS_INGRESOS = [
    "Sin ingresos declarados", "Ingreso observado",
    "Ingreso estimado", "Ingreso observado y estimado",
    "Ingreso por transferencias",
]
DATOS_FIJOS = {
    "1043969772": {
        "nombre": "ORIANA LUZ SUMOSA MARTINEZ", "sexo": "Femenino", "edad": 26,
        "departamento": "BOLÍVAR", "municipio": "CARTAGENA DE INDIAS",
        "grupo_rui": "C", "nivel_rui": "C17",
        "grupo_ingresos": "Ingreso observado y estimado",
        "codigo_municipio": "13001", "sisben_grupo": "C4",
        "sisben_desc": "Vulnerable", "fecha_encuesta": "2022-08-15",
    },
}


def generar_datos_rui(cedula: str) -> dict:
    seed = sum(int(d) * (i + 1) for i, d in enumerate(cedula))
    rng  = random.Random(seed)
    pn, ap  = rng.choice(NOMBRES)
    cod_mun = rng.choice(list(MUNICIPIOS.keys()))
    mun, cod_dep = MUNICIPIOS[cod_mun]
    gk = rng.choice(list(GRUPOS_SISBEN.keys()))
    gr, desc = GRUPOS_SISBEN[gk]
    return {
        "nombre": f"{pn} {ap}",
        "sexo": SEXOS.get(pn, "Masculino"),
        "edad": rng.randint(18, 75),
        "departamento": DEPARTAMENTOS[cod_dep],
        "municipio": mun,
        "grupo_rui": gr,
        "nivel_rui": gk,
        "grupo_ingresos": rng.choice(GRUPOS_INGRESOS),
        "codigo_municipio": cod_mun,
        "sisben_grupo": gk,
        "sisben_desc": desc,
        "fecha_encuesta": f"{rng.randint(2019,2023)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
    }


def consultar_rui(cedula: str) -> dict:
    return DATOS_FIJOS.get(cedula) or generar_datos_rui(cedula)


def fmt_rui(cedula: str, d: dict) -> str:
    grupo = d["sisben_grupo"][0]
    emoji = {"A": "🔴", "B": "🟡", "C": "🟠", "D": "🟢"}.get(grupo, "⚪")
    return (
        f"{'='*40}\n"
        f"📋 *CONSULTA RUI/SISBÉN*\n"
        f"{'='*40}\n\n"
        f"🪪 Documento: `{cedula}`\n"
        f"📌 Tipo: CC (Cédula de Ciudadanía)\n"
        f"✅ Estado: ACTIVO\n"
        f"{'─'*40}\n\n"
        f"*DATOS RUI:*\n"
        f"👤 Nombre:         `{d['nombre']}`\n"
        f"⚥  Sexo:           {d['sexo']}\n"
        f"🎂 Edad:           {d['edad']} años\n"
        f"🗺  Departamento:   {d['departamento']}\n"
        f"🏙  Municipio:      {d['municipio']}\n"
        f"📊 Grupo RUI:      {d['grupo_rui']}\n"
        f"📈 Nivel RUI:      {d['nivel_rui']}\n"
        f"💵 Grupo Ingresos: {d['grupo_ingresos']}\n"
        f"🔢 Cód. Municipio: {d['codigo_municipio']}\n"
        f"📅 Fecha encuesta: {d['fecha_encuesta']}\n"
        f"{'─'*40}\n\n"
        f"*DATOS SISBÉN:*\n"
        f"{emoji} Grupo:       *{d['sisben_grupo']}*\n"
        f"{emoji} Descripción: {d['sisben_desc']}\n\n"
        f"{'='*40}"
    )


# ══════════════════════════════════════════════════════════════
#  DATOS SIMULADOS NEQUI
# ══════════════════════════════════════════════════════════════
# Almacena cuentas por chat_id
cuentas_nequi: dict = {}

# Estados conversación Nequi
(
    NEQUI_MENU, NEQUI_CREAR_CEL, NEQUI_CREAR_NOMBRE,
    NEQUI_ENVIAR_DEST, NEQUI_ENVIAR_MONTO, NEQUI_ENVIAR_CONCEPTO,
    NEQUI_RECIBIR_ORIGEN, NEQUI_RECIBIR_MONTO, NEQUI_RECIBIR_CONCEPTO,
    NEQUI_BUSCAR_CEL,
) = range(10)

# Estado conversación RUI
ESPERANDO_CEDULA = 10

# Estado conversación ADRES
ESPERANDO_CEDULA_ADRES = 11


NOMBRES_NEQUI = [
    "LAURA TORRES",      "CARLOS PEREZ",     "DIANA RODRIGUEZ",
    "ANDRES GARCIA",     "MARIA LOPEZ",      "JOSE MARTINEZ",
    "VALENTINA MORENO",  "SEBASTIAN MORA",   "ISABELLA RAMIREZ",
    "MIGUEL CASTRO",     "CAMILA ORTIZ",     "JUAN SANCHEZ",
    "SARA GUTIERREZ",    "DAVID VARGAS",     "LUCIA HERRERA",
]


def buscar_cuenta_nequi(celular: str) -> dict:
    """Simula consulta de cuenta Nequi por número de celular."""
    seed  = sum(int(d) * (i + 7) for i, d in enumerate(celular))
    rng   = random.Random(seed)
    # 85% de probabilidad de que la cuenta exista
    existe = rng.random() < 0.85
    if not existe:
        return {"encontrado": False}
    nombre = rng.choice(NOMBRES_NEQUI)
    estado = rng.choice(["ACTIVA", "ACTIVA", "ACTIVA", "SUSPENDIDA"])
    return {
        "encontrado": True,
        "celular":    celular,
        "nombre":     nombre,
        "estado":     estado,
        "tipo":       "Cuenta Nequi Personal",
        "banco":      "Bancolombia S.A.",
    }



    return f"$ {m:,.0f}".replace(",", ".")


def get_cuenta(chat_id: int) -> dict | None:
    return cuentas_nequi.get(chat_id)


def teclado_principal():
    return ReplyKeyboardMarkup(
        [["🔍 Consultar RUI/Sisbén", "🏥 Consultar ADRES"],
         ["💜 Nequi"]],
        resize_keyboard=True,
    )


def teclado_nequi(tiene_cuenta: bool):
    if tiene_cuenta:
        botones = [
            ["💰 Ver saldo", "📤 Enviar plata"],
            ["📥 Recibir plata", "📋 Historial"],
            ["🔎 Buscar cuenta", "🔙 Menú principal"],
        ]
    else:
        botones = [["➕ Crear cuenta Nequi"], ["🔎 Buscar cuenta"], ["🔙 Menú principal"]]
    return ReplyKeyboardMarkup(botones, resize_keyboard=True)


# ══════════════════════════════════════════════════════════════
#  HANDLERS PRINCIPALES
# ══════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Hola *{nombre}*\n\n"
        f"Bienvenido al sistema integrado:\n"
        f"📋 *RUI/Sisbén Colombia*\n"
        f"💜 *Nequi (Pagos simulados)*\n\n"
        f"Selecciona una opción:",
        parse_mode="Markdown",
        reply_markup=teclado_principal(),
    )


async def menu_principal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Selecciona una opción:",
        reply_markup=teclado_principal(),
    )


# ── RUI ──────────────────────────────────────────────────────

async def rui_inicio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 *Consulta RUI/Sisbén*\n\nIngresa el número de cédula:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["❌ Cancelar"]], resize_keyboard=True),
    )
    return ESPERANDO_CEDULA


async def adres_inicio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏥 *Consulta ADRES/EPS*\n\nIngresa el número de cédula:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["❌ Cancelar"]], resize_keyboard=True),
    )
    return ESPERANDO_CEDULA_ADRES


async def adres_consultar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    if texto == "❌ Cancelar":
        await update.message.reply_text("Cancelado.", reply_markup=teclado_principal())
        return ConversationHandler.END
    cedula = "".join(c for c in texto if c.isdigit())
    if not (6 <= len(cedula) <= 10):
        await update.message.reply_text(
            "⚠️ Cédula inválida. Debe tener entre 6 y 10 dígitos. Intenta de nuevo:"
        )
        return ESPERANDO_CEDULA_ADRES
    await update.message.reply_text("⏳ Consultando base de datos ADRES...")
    datos = generar_adres(cedula)
    await update.message.reply_text(
        fmt_adres(datos),
        parse_mode="Markdown",
        reply_markup=teclado_principal(),
    )
    return ConversationHandler.END


async def rui_consultar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()

    if texto == "❌ Cancelar":
        await update.message.reply_text("Cancelado.", reply_markup=teclado_principal())
        return ConversationHandler.END

    cedula = "".join(c for c in texto if c.isdigit())

    if not (6 <= len(cedula) <= 10):
        await update.message.reply_text(
            "⚠️ Cédula inválida. Debe tener entre 6 y 10 dígitos. Intenta de nuevo:"
        )
        return ESPERANDO_CEDULA

    await update.message.reply_text("⏳ Consultando base de datos RUI/Sisbén...")
    datos = consultar_rui(cedula)
    await update.message.reply_text(
        fmt_rui(cedula, datos),
        parse_mode="Markdown",
        reply_markup=teclado_principal(),
    )
    return ConversationHandler.END


# ── NEQUI ────────────────────────────────────────────────────

async def nequi_inicio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    cuenta  = get_cuenta(chat_id)
    if cuenta:
        await update.message.reply_text(
            f"💜 *NEQUI*\n\n"
            f"👤 {cuenta['nombre']}\n"
            f"📱 {cuenta['celular']}\n"
            f"💰 Saldo: *{fmt_monto(cuenta['saldo'])}*",
            parse_mode="Markdown",
            reply_markup=teclado_nequi(True),
        )
    else:
        await update.message.reply_text(
            "💜 *NEQUI*\n\nNo tienes cuenta. ¿Deseas crear una?",
            parse_mode="Markdown",
            reply_markup=teclado_nequi(False),
        )
    return NEQUI_MENU


async def nequi_menu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    texto   = update.message.text
    chat_id = update.effective_chat.id
    cuenta  = get_cuenta(chat_id)

    if texto == "🔙 Menú principal":
        await update.message.reply_text("Menú principal:", reply_markup=teclado_principal())
        return ConversationHandler.END

    elif texto == "➕ Crear cuenta Nequi":
        await update.message.reply_text(
            "📱 Ingresa tu número de celular (10 dígitos, empieza por 3):",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancelar"]], resize_keyboard=True),
        )
        return NEQUI_CREAR_CEL

    elif texto == "🔎 Buscar cuenta":
        await update.message.reply_text(
            "🔎 *Buscar cuenta Nequi*\n\nIngresa el número de celular a buscar:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancelar"]], resize_keyboard=True),
        )
        return NEQUI_BUSCAR_CEL

    elif texto == "💰 Ver saldo" and cuenta:
        await update.message.reply_text(
            f"💰 *Saldo disponible*\n\n"
            f"👤 {cuenta['nombre']}\n"
            f"📱 {cuenta['celular']}\n"
            f"💵 *{fmt_monto(cuenta['saldo'])}*\n"
            f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            parse_mode="Markdown",
            reply_markup=teclado_nequi(True),
        )
        return NEQUI_MENU

    elif texto == "📤 Enviar plata" and cuenta:
        await update.message.reply_text(
            "📤 *Enviar plata*\n\nIngresa el celular del destinatario:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancelar"]], resize_keyboard=True),
        )
        return NEQUI_ENVIAR_DEST

    elif texto == "📥 Recibir plata" and cuenta:
        await update.message.reply_text(
            "📥 *Recibir plata*\n\nIngresa el celular de quien te envía:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancelar"]], resize_keyboard=True),
        )
        return NEQUI_RECIBIR_ORIGEN

    elif texto == "📋 Historial" and cuenta:
        txs = cuenta.get("transacciones", [])
        if not txs:
            msg = "📋 *Historial*\n\nNo hay movimientos aún."
        else:
            msg = "📋 *Historial de movimientos*\n\n"
            for tx in reversed(txs[-10:]):
                signo = "➖" if tx["tipo"] == "ENVÍO" else "➕"
                msg += (
                    f"{signo} *{tx['tipo']}* — {fmt_monto(tx['monto'])}\n"
                    f"   Ref: `{tx['ref']}`\n"
                    f"   {tx['concepto']} — {tx['fecha']}\n\n"
                )
            msg += f"💰 Saldo actual: *{fmt_monto(cuenta['saldo'])}*"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=teclado_nequi(True))
        return NEQUI_MENU

    return NEQUI_MENU


# Buscar cuenta
async def nequi_buscar_cel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tiene   = get_cuenta(chat_id) is not None
    if update.message.text == "❌ Cancelar":
        await update.message.reply_text("Cancelado.", reply_markup=teclado_nequi(tiene))
        return NEQUI_MENU
    cel = "".join(c for c in update.message.text if c.isdigit())
    if not (len(cel) == 10 and cel.startswith("3")):
        await update.message.reply_text("⚠️ Número inválido. Debe tener 10 dígitos y empezar por 3:")
        return NEQUI_BUSCAR_CEL
    await update.message.reply_text("⏳ Consultando cuenta Nequi...")
    r = buscar_cuenta_nequi(cel)
    if not r["encontrado"]:
        msg = (
            f"❌ *Cuenta no encontrada*\n\n"
            f"📱 Celular: `{cel}`\n"
            f"No existe una cuenta Nequi activa con este número."
        )
    else:
        emoji = "✅" if r["estado"] == "ACTIVA" else "⚠️"
        msg = (
            f"{'='*38}\n"
            f"💜 *CONSULTA CUENTA NEQUI*\n"
            f"{'='*38}\n\n"
            f"📱 Celular:  `{r['celular']}`\n"
            f"👤 Titular:  *{r['nombre']}*\n"
            f"{emoji} Estado:   *{r['estado']}*\n"
            f"🏦 Tipo:     {r['tipo']}\n"
            f"🏛  Banco:    {r['banco']}\n\n"
            f"{'='*38}"
        )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=teclado_nequi(tiene))
    return NEQUI_MENU


# Crear cuenta
async def nequi_crear_cel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Cancelar":
        await update.message.reply_text("Cancelado.", reply_markup=teclado_principal())
        return ConversationHandler.END
    cel = "".join(c for c in update.message.text if c.isdigit())
    if not (len(cel) == 10 and cel.startswith("3")):
        await update.message.reply_text("⚠️ Número inválido. Debe tener 10 dígitos y empezar por 3:")
        return NEQUI_CREAR_CEL
    ctx.user_data["cel_nuevo"] = cel
    await update.message.reply_text("👤 Ingresa tu nombre completo:")
    return NEQUI_CREAR_NOMBRE


async def nequi_crear_nombre(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text.strip().upper()
    if len(nombre) < 3:
        await update.message.reply_text("⚠️ Nombre inválido. Intenta de nuevo:")
        return NEQUI_CREAR_NOMBRE
    chat_id = update.effective_chat.id
    saldo   = round(random.uniform(50000, 500000), -3)
    cuentas_nequi[chat_id] = {
        "celular": ctx.user_data["cel_nuevo"],
        "nombre":  nombre,
        "saldo":   saldo,
        "transacciones": [],
    }
    await update.message.reply_text(
        f"✅ *¡Cuenta creada exitosamente!*\n\n"
        f"👤 Titular: {nombre}\n"
        f"📱 Celular: {ctx.user_data['cel_nuevo']}\n"
        f"💰 Saldo inicial: *{fmt_monto(saldo)}*",
        parse_mode="Markdown",
        reply_markup=teclado_nequi(True),
    )
    return NEQUI_MENU


# Enviar plata
async def nequi_enviar_dest(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Cancelar":
        await update.message.reply_text("Cancelado.", reply_markup=teclado_nequi(True))
        return NEQUI_MENU
    cel = "".join(c for c in update.message.text if c.isdigit())
    chat_id = update.effective_chat.id
    if not (len(cel) == 10 and cel.startswith("3")):
        await update.message.reply_text("⚠️ Número inválido:")
        return NEQUI_ENVIAR_DEST
    if cel == get_cuenta(chat_id)["celular"]:
        await update.message.reply_text("⚠️ No puedes enviarte plata a ti mismo:")
        return NEQUI_ENVIAR_DEST
    ctx.user_data["dest"] = cel
    await update.message.reply_text(f"💵 ¿Cuánto quieres enviar a {cel}? (en pesos):")
    return NEQUI_ENVIAR_MONTO


async def nequi_enviar_monto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Cancelar":
        await update.message.reply_text("Cancelado.", reply_markup=teclado_nequi(True))
        return NEQUI_MENU
    try:
        monto = float(update.message.text.strip().replace(",", "").replace(".", "").replace("$", "").replace(" ", ""))
    except ValueError:
        await update.message.reply_text("⚠️ Monto inválido:")
        return NEQUI_ENVIAR_MONTO
    chat_id = update.effective_chat.id
    cuenta  = get_cuenta(chat_id)
    if monto <= 0:
        await update.message.reply_text("⚠️ El monto debe ser mayor a $0:")
        return NEQUI_ENVIAR_MONTO
    if monto > cuenta["saldo"]:
        await update.message.reply_text(
            f"⚠️ Saldo insuficiente. Disponible: *{fmt_monto(cuenta['saldo'])}*\nIngresa otro monto:",
            parse_mode="Markdown",
        )
        return NEQUI_ENVIAR_MONTO
    ctx.user_data["monto_envio"] = monto
    await update.message.reply_text("📝 Concepto (opcional, o escribe '-' para omitir):")
    return NEQUI_ENVIAR_CONCEPTO


async def nequi_enviar_concepto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id  = update.effective_chat.id
    cuenta   = get_cuenta(chat_id)
    concepto = update.message.text.strip()
    if concepto == "-":
        concepto = "Transferencia"
    monto = ctx.user_data["monto_envio"]
    dest  = ctx.user_data["dest"]
    ref   = f"NQ{random.randint(100000000, 999999999)}"
    cuenta["saldo"] -= monto
    cuenta["transacciones"].append({
        "tipo": "ENVÍO", "monto": monto, "destino": dest,
        "concepto": concepto, "ref": ref,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    await update.message.reply_text(
        f"✅ *¡Transferencia exitosa!*\n\n"
        f"📤 Para: {dest}\n"
        f"💸 Monto: *{fmt_monto(monto)}*\n"
        f"📝 Concepto: {concepto}\n"
        f"🔖 Ref: `{ref}`\n"
        f"💰 Nuevo saldo: *{fmt_monto(cuenta['saldo'])}*",
        parse_mode="Markdown",
        reply_markup=teclado_nequi(True),
    )
    return NEQUI_MENU


# Recibir plata
async def nequi_recibir_origen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Cancelar":
        await update.message.reply_text("Cancelado.", reply_markup=teclado_nequi(True))
        return NEQUI_MENU
    cel = "".join(c for c in update.message.text if c.isdigit())
    if not (len(cel) == 10 and cel.startswith("3")):
        await update.message.reply_text("⚠️ Número inválido:")
        return NEQUI_RECIBIR_ORIGEN
    ctx.user_data["origen"] = cel
    await update.message.reply_text(f"💵 ¿Cuánto te envió {cel}? (en pesos):")
    return NEQUI_RECIBIR_MONTO


async def nequi_recibir_monto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Cancelar":
        await update.message.reply_text("Cancelado.", reply_markup=teclado_nequi(True))
        return NEQUI_MENU
    try:
        monto = float(update.message.text.strip().replace(",", "").replace(".", "").replace("$", "").replace(" ", ""))
    except ValueError:
        await update.message.reply_text("⚠️ Monto inválido:")
        return NEQUI_RECIBIR_MONTO
    if monto <= 0:
        await update.message.reply_text("⚠️ El monto debe ser mayor a $0:")
        return NEQUI_RECIBIR_MONTO
    ctx.user_data["monto_recibo"] = monto
    await update.message.reply_text("📝 Concepto (opcional, o escribe '-' para omitir):")
    return NEQUI_RECIBIR_CONCEPTO


async def nequi_recibir_concepto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id  = update.effective_chat.id
    cuenta   = get_cuenta(chat_id)
    concepto = update.message.text.strip()
    if concepto == "-":
        concepto = "Transferencia recibida"
    monto  = ctx.user_data["monto_recibo"]
    origen = ctx.user_data["origen"]
    ref    = f"NQ{random.randint(100000000, 999999999)}"
    cuenta["saldo"] += monto
    cuenta["transacciones"].append({
        "tipo": "RECIBO", "monto": monto, "origen": origen,
        "concepto": concepto, "ref": ref,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    await update.message.reply_text(
        f"✅ *¡Pago recibido!*\n\n"
        f"📥 De: {origen}\n"
        f"💵 Monto: *{fmt_monto(monto)}*\n"
        f"📝 Concepto: {concepto}\n"
        f"🔖 Ref: `{ref}`\n"
        f"💰 Nuevo saldo: *{fmt_monto(cuenta['saldo'])}*",
        parse_mode="Markdown",
        reply_markup=teclado_nequi(True),
    )
    return NEQUI_MENU


async def cancelar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelado.", reply_markup=teclado_principal())
    return ConversationHandler.END


# ══════════════════════════════════════════════════════════════
#  ARRANQUE
# ══════════════════════════════════════════════════════════════

def main():
    app = Application.builder().token(TOKEN).build()

    # Conversación RUI
    conv_rui = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔍 Consultar RUI/Sisbén$"), rui_inicio)],
        states={ESPERANDO_CEDULA: [MessageHandler(filters.TEXT & ~filters.COMMAND, rui_consultar)]},
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    # Conversación Nequi
    conv_nequi = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💜 Nequi$"), nequi_inicio)],
        states={
            NEQUI_MENU:            [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_menu_handler)],
            NEQUI_CREAR_CEL:       [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_crear_cel)],
            NEQUI_CREAR_NOMBRE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_crear_nombre)],
            NEQUI_ENVIAR_DEST:     [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_enviar_dest)],
            NEQUI_ENVIAR_MONTO:    [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_enviar_monto)],
            NEQUI_ENVIAR_CONCEPTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_enviar_concepto)],
            NEQUI_RECIBIR_ORIGEN:  [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_recibir_origen)],
            NEQUI_RECIBIR_MONTO:   [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_recibir_monto)],
            NEQUI_RECIBIR_CONCEPTO:[MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_recibir_concepto)],
            NEQUI_BUSCAR_CEL:      [MessageHandler(filters.TEXT & ~filters.COMMAND, nequi_buscar_cel)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    # Conversación ADRES
    conv_adres = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🏥 Consultar ADRES$"), adres_inicio)],
        states={ESPERANDO_CEDULA_ADRES: [MessageHandler(filters.TEXT & ~filters.COMMAND, adres_consultar)]},
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_principal))
    app.add_handler(conv_rui)
    app.add_handler(conv_adres)
    app.add_handler(conv_nequi)

    print("=" * 50)
    print("  Bot RUI/Sisbén + Nequi corriendo...")
    print("  1. Abre Telegram")
    print("  2. Busca tu bot por su nombre")
    print("  3. Escribe /start para comenzar")
    print("  Ctrl+C para detener")
    print("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
