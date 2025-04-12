from enum import Enum

# Enum for Mexico States
class MexicoStates(Enum):
    AGS = "Aguascalientes"
    BC = "Baja California"
    BCS = "Baja California Sur"
    CAMP = "Campeche"
    CHIS = "Chiapas"
    CHIH = "Chihuahua"
    COAH = "Coahuila"
    COL = "Colima"
    CDMX = "Ciudad de México"
    DGO = "Durango"
    EDOMEX = "Estado de México"
    GTO = "Guanajuato"
    GRO = "Guerrero"
    HGO = "Hidalgo"
    JAL = "Jalisco"
    MICH = "Michoacán"
    MOR = "Morelos"
    NAY = "Nayarit"
    NL = "Nuevo León"
    OAX = "Oaxaca"
    PUE = "Puebla"
    QRO = "Querétaro"
    QR = "Quintana Roo"
    SLP = "San Luis Potosí"
    SIN = "Sinaloa"
    SON = "Sonora"
    TAB = "Tabasco"
    TAM = "Tamaulipas"
    TLAX = "Tlaxcala"
    VER = "Veracruz"
    YUC = "Yucatán"
    ZAC = "Zacatecas"

class Genero(str, Enum):
    macho = "Macho"
    hembra = "Hembra"

class Tamano(str, Enum):
    pequeno = "Pequeño"
    mediano = "Mediano"
    grande = "Grande"
    extragrande = "Extra grande"

class Temperamento(str, Enum):
    muy_reactivo = "Muy Reactivo"
    reactivo = "Reactivo"
    neutro = "Neutro"
    poco_reactivo = "Poco Reactivo"
    muy_tranquilo = "Muy Tranquilo"

class PricingType(str, Enum):
    FLAT = "Fijo"
    VOLUME = "Volumen"
    SUBSCRIPTION = "Suscripción"


# class SubscriptionFrequency(str, Enum):
#     WEEKLY = "flat"
#     MONTHLY = "volume"
#     YEARLY = "subscription"

