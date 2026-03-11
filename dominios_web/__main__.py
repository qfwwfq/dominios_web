from dynatrace_extension import Extension, Status, StatusValue
from datetime import datetime, timedelta, timezone
import json
import requests

#--------------------------------------------------------------------------------------
# Para conocer el estado del dominio consulta a nic.ar con la siguiente url
# NIC_DOMEAIN_CHECL_URL/nombre_del_dominio
# Devuelve un json. En la respuesta, hay que buscar el array "events"
# En ese array, buscar el que tiene un valor de la forma
#     { "eventAction": "registration", "eventDate": "2000-11-17T00:00:00+00:00" },
#--------------------------------------------------------------------------------------
NIC_DOMEAIN_CHECL_URL = "https://rdap.nic.ar/domain"
KEY_PREFIX = "test.ar.com.allianz.dominios.v2"

class ExtensionImpl(Extension):
    def query(self):
        pass

    def dominios_custom_query(self):
        """
        The query method is automatically scheduled to run every minute
        """
        self.logger.info("query method started for dominios.")


        for endpoint in self.activation_config["endpoints"]:
            dominio = endpoint['dominio'] ### OJO
            url = f"{NIC_DOMEAIN_CHECL_URL}/{endpoint['dominio']}"
            # user = endpoint["user"]
            # password = endpoint["password"]
            self.logger.info(f"Consultando dominio {endpoint['dominio']} mediante '{url}'")
            #--------------------------------------------------------------------------------------
            # Averiguo la fecha de vencimiento
            #--------------------------------------------------------------------------------------
            r = requests.get(url)
            ######O JO chequear error r.status_code
            if r.status_code != 200:
                self.logger.error(f"Se obtuvo el error: {r.status_code} invocando el GET para {url}")
                continue
            events = r.json()["events"]
            expiration = ''
            for event in events:
                print(event)
                if event['eventAction'] == 'expiration':
                    expiration = event['eventDate']
            if expiration == '':
                self.logger.error(f"Error http_code={r.status_code} invocando el GET para {url}")
                continue
            n = datetime.now(timezone.utc)
            e = datetime.fromisoformat(expiration)
            days_diff = (e -n).days
########33
#            import random
#            days_diff = random.randint(1, 10)
#            expiration = datetime.now(timezone.utc) + timedelta(days=days_diff)
##########
            self.logger.info(f"En {days_diff} días expira el dominio '{dominio}' ('{expiration}')")


            # Report metrics with
            self.report_metric(f"{KEY_PREFIX}.vencimiento", days_diff, dimensions={"dominio": dominio})

        self.logger.info("query method ended for dominios.")

    def fastcheck(self) -> Status:
        """
        Use to check if the extension can run.
        If this Activegate cannot run this extension, you can
        raise an Exception or return StatusValue.ERROR.
        This does not run for OneAgent extensions.
        """
        return Status(StatusValue.OK)

    def initialize(self):
        # Por ahora el valor 15 está hardcodeado porque no me está funcionando el valor que viene en el activation_config. 
        # El error que me da es 
        # "TypeError: unsupported type for timedelta minutes component: dict"
        # Dejo la línea para retomar esto luego.
        # 
        #intervalo = self.activation_config["intervalo"]
        intervalo = 90
        self.schedule(self.dominios_custom_query, timedelta(minutes=intervalo))
        self.logger.info (f"La consulta de expiricón de dominios se realizará cada {intervalo} minutos")


def main():
    ExtensionImpl(name="dominios").run()


if __name__ == "__main__":
    main()
