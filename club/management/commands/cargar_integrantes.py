from django.core.management.base import BaseCommand
from club.models import Integrante

INTEGRANTES = [
    {"nombre": "Roberto Fernando Alcaraz Garay", "whatsapp": "0981-427-603"},
    {"nombre": "Sara Carolina Almeida Sanchez", "whatsapp": "0975-272-584"},
    {"nombre": "Robert Gabriel Ramirez Gomez", "whatsapp": "0976-593-475"},
    {"nombre": "Yolanda Soledad Montenegro Cohene", "whatsapp": "0984-000-220"},
    {"nombre": "Derlis Fabian Ullon Escobar", "whatsapp": "0962-130-164"},
    {"nombre": "Enzo Samuel Molas Diaz", "whatsapp": "0993-494-800"},
    {"nombre": "Jessica Pufal", "whatsapp": "0976-188-306"},
    {"nombre": "Marco Charles Sosa Bogado", "whatsapp": "0972-449-291"},
    {"nombre": "Sicinio Ramon Franco Lopez", "whatsapp": "0972-268-489"},
    {"nombre": "Pablo Ruben Duarte Rotela", "whatsapp": "0973-372-420"},
    {"nombre": "Derlis Enrique Duarte Ramirez", "whatsapp": "0975-230-198"},
    {"nombre": "Oscar Gabriel Galeano Chavez", "whatsapp": "0992-508-073"},
    {"nombre": "Jazmin Silvero Baez", "whatsapp": "0991-641-939"},
    {"nombre": "Lynnett Wy", "whatsapp": "0972-979-202"},
    {"nombre": "Felix Rene Villalba Paniagua", "whatsapp": "0971-849-649"},
    {"nombre": "Silvia Angelacio", "whatsapp": "0981-313-202"},
    {"nombre": "Francisco Ramon Rodriguez Benitez", "whatsapp": "0973-557-552"},
    {"nombre": "Yousel Mateo Venialgo Palacios", "whatsapp": "0985-877-635"},
    {"nombre": "Emerson Willan Prates de Olive", "whatsapp": "0983-666-167"},
    {"nombre": "Gean Carlos Silveira", "whatsapp": "0993-510-284"},
    {"nombre": "Diego Alberto Ferreira Villalba", "whatsapp": "0984-645-057"},
    {"nombre": "Nathalia Aylin Sanchez Caceres", "whatsapp": "0982-909-265"},
    {"nombre": "Fredy Barrios", "whatsapp": "0983-115-963"},
    {"nombre": "Jose David Ocampos Aquino", "whatsapp": "0993-274-032"},
    {"nombre": "Richard Zaracho", "whatsapp": "0984-776-139"},
    {"nombre": "Luis Miguel Rodas Quintana", "whatsapp": "0991-382-753"},
    {"nombre": "Fernando Ezequiel Pena", "whatsapp": "0984-301-044"},
    {"nombre": "Maria Jose Candido Segovia", "whatsapp": "0983-964-788"},
    {"nombre": "Leila Giselle Gamarra", "whatsapp": "0982-408-960"},
    {"nombre": "Elba Maria Machado Espinola", "whatsapp": "0994-123-683"},
    {"nombre": "Chiara Nicole Ovelar Silva", "whatsapp": "0985-556-061"},
    {"nombre": "Jesus Maria Alzueta", "whatsapp": "0985-579-574"},
    {"nombre": "Santiago Rene Martinez", "whatsapp": "0971-639-532"},
    {"nombre": "Armando Ariel Franco Moreno", "whatsapp": "0976-408-983"},
    {"nombre": "Alexis Albino David Morinigo Alonso", "whatsapp": "0983-550-304"},
    {"nombre": "Ulises Daniel Rojas Gonzalez", "whatsapp": "0991-212-475"},
    {"nombre": "Marcos Ezequiel Britez Barrios", "whatsapp": "0976-387-269"},
    {"nombre": "Sanie Cardenas Villalba", "whatsapp": "0981-657-005"},
    {"nombre": "David Samuel Britez Barrios", "whatsapp": "0976-999-610"},
    {"nombre": "Miguel Francia", "whatsapp": "0982-919-888"},
    {"nombre": "Friederike Angersbach Blankenstein", "whatsapp": "0985-963-833"},
    {"nombre": "Jorge Ireneo Viveros", "whatsapp": "0986-698-222"},
    {"nombre": "Orlando Rene Ovelar Silva", "whatsapp": "0985-120-175"},
    {"nombre": "Angel Matias Aquino Santacruz", "whatsapp": "0991-293-391"},
    {"nombre": "Alexis Nicolas De Jesus Vargas Benitez", "whatsapp": "0981-072-615"},
    {"nombre": "Lidice Ojeda", "whatsapp": "0984-208-822"},
]


class Command(BaseCommand):
    help = 'Carga los 46 integrantes iniciales del club'

    def handle(self, *args, **kwargs):
        creados = 0
        for data in INTEGRANTES:
            obj, created = Integrante.objects.get_or_create(
                nombre=data['nombre'],
                defaults={
                    'whatsapp': data['whatsapp'],
                    'ciudad': 'Paraguay',
                    'pais': 'Paraguay',
                    'activo': True,
                }
            )
            if created:
                creados += 1
                self.stdout.write(f'  + {obj.nombre}')
            else:
                self.stdout.write(f'  = {obj.nombre} (ya existe)')

        self.stdout.write(self.style.SUCCESS(f'\n{creados} integrantes creados de {len(INTEGRANTES)} total.'))
