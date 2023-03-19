"""
OBJETIVO:
 - Extraer titulo, precio y descripcion de los automoviles disponibles en la pagina
ELABORADO POR: Daniel Saavedra
FECHA: 11/03/23
"""
from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

class Autos(Item):
    nombre = Field()
    precio = Field()
    descripcion = Field()

class MercadoLibre(CrawlSpider):
    name = "autosmercadolibre"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'CLOSESPIDER_PAGECOUNT': 40 # Numero maximo de paginas en las cuales voy a descargar items (cada pagina es un item del cual extraeremos la info). Scrapy se cierra cuando alcanza este numero,
                                    # puede haber problemas de concurrencia, scrapy suele obtener mas items que el numero que le colocamos.
    }
    start_urls = ['https://listado.mercadolibre.com.pe/vehiculos/_NoIndex_True']
    download_delay = 1

    #Dominio de paginas en las cuales srapy se debe limitar a buscar para traer informacion redundante
    allowed_domains = ['listado.mercadolibre.com.pe','auto.mercadolibre.com.pe',
                       'vehiculo.mercadolibre.com.pe','moto.mercadolibre.com.pe']

    rules = (
        # Paginación => HORIZONTALIDAD
        Rule(
            LinkExtractor(
                allow=r"/_Desde_"
            ), follow=True #Aqui no ponemos callback ya que no queremos extraer nada de acá, solo queremos que entre y recorra las paginas
        ),
        # Detalles de los productos => VERTICALIDAD
        Rule(
            LinkExtractor(
                allow=r"/MPE-"
            ), follow=True, callback="parse_auto"
        ),
    )

    def limpiartexto(self, texto):
        nuevotexto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
        return nuevotexto

    #Cada "item" es una pagina individual (la que contiene los detalles) por ello no se realiza bucles con for.
    def parse_auto(self, response):
        sel = Selector(response)
        item = ItemLoader(Autos(), sel)
        item.add_xpath('nombre', '//h1[@class="ui-pdp-title"]/text()', MapCompose(self.limpiartexto))
        item.add_xpath('precio', '//span[@class="andes-money-amount__fraction"]/text()')
        item.add_xpath('descripcion', '//p[@class="ui-pdp-description__content"]/text()',
                       MapCompose(self.limpiartexto))

        yield item.load_item()

# EJECUCION
# scrapy runspider WS_Horizontal_vertical_MERCADOLIBRE.py -o mercadolibre_miversion.json -t json
# Ctrl + C para forzar la detencion en la terminal.