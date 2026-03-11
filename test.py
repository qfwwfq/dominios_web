# --------------------------------------------------------------------
# Busca la cantidad de días hasta la expiración de un dominio de la www
# consultando la URL https://rdap.nic.ar/domain/nombre_del_dominio
#---------------------------------------------------------------------
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
# -------------------------------------------------------------------
base_url = "https://rdap.nic.ar/domain"
dominios= ["allianz.com.ar", "miallianz.com.ar", "allianznet.com.ar"]
#tz_str  = "America/Buenos_Aires"
# -------------------------------------------------------------------

for dominio in dominios:
    url = f'{base_url}/{dominio}'
    #print(url)
    r = requests.get(url)
    dias_heast_expiracion = 9999
    if r.status_code != 200:
        print(f'No se pudo determinar el vencimiento de {dominio}')
        continue
    else:
        eventos = r.json()["events"]
        fecha_de_expiracion =  ""
        # En el caso de que no pueda determinar la fecha de expiración, le asigno un valor muy grande
        # de modo de garantizar salga un alerta
        for e in eventos:
            if e["eventAction"] != "expiration":
                continue
            else:
                fecha_de_expiracion_str = e["eventDate"]

        if fecha_de_expiracion_str:
            # Uso timedelta para calcular la diferencia de días entre el momento de ejecución y la fecha de expiración
            # Como datetime.fromisoformat abajo da una fecha timezone aware, uso el timezone de esa fecha para
            # utilizar la misma en el momento presente.
            fecha_de_expiracion = datetime.fromisoformat(fecha_de_expiracion_str)
            tz = fecha_de_expiracion.tzinfo
            ahora = datetime.now(tz)
            dias_heast_expiracion = (fecha_de_expiracion - ahora).days
    print(f'El dominio "{dominio}" vence en {dias_heast_expiracion} dias')