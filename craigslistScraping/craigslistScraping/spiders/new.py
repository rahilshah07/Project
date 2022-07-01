import scrapy
from craigslistScraping.items import Vehicle

class new_truecar(scrapy.Spider):

    name = "new_truecar_spider"

    start_urls = ['https://www.truecar.com/used-cars-for-sale/listings/location-ontario-ca/']


    def parse(self, response):

        vehicles= response.xpath('//div[@data-test="cardContent"]')

        for vehicle in vehicles:
            year = vehicle.xpath('//span[@class="vehicle-card-year font-size-1"]/text()').get()
            make = vehicle.xpath('//span[@class="vehicle-header-make-model text-truncate"]/text()').get()
            print(make)

