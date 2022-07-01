import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from craigslistScraping.items import Vehicle



MAPPING = {'Exterior Color': 'exterior', 'Interior Color': 'interior', 'Drive Type': 'drive', 'Fuel Type': 'fuel', 'Engine': 'engine', 'Transmission': 'transmission'}

NEXT_PAGE_SELECTOR = 'ul.pagination > li:nth-last-child(2) > .pagination-link'

SPIDER_NAME = 'truecar_spider'

DOMAIN = 'www.truecar.com'

INFO_LI_SELECTOR = '.margin-bottom-3 > li'

VEHICLE_SELECTOR = '.vehicleCardLink'

TITLE_SELECTOR = '._176r2bw::text'

MODIFICATION_SELECTOR = '._ip7nj36::text'

VEHICHEL_SELECTOR = '.vehicle-card-info .vdp-link::attr(href)'

ROOT_PATH = 'https://www.truecar.com%s'


class TrueCarSpider(scrapy.Spider):
    name = SPIDER_NAME
    start_urls = ['https://www.truecar.com/used-cars-for-sale/listings/location-ontario-ca/']
    allowed_domains = [DOMAIN]

    def parse(self, response):
        self.logger.info('Processing ... %s' % response.url)
        vehicles = response.xpath('//div[@data-test="allVehicleListings"]/a/@href')
        print(vehicles)
        print("Hello")
        for vehicle in vehicles:
            title = vehicle.css(TITLE_SELECTOR).extract_first()
            modification = vehicle.css(MODIFICATION_SELECTOR).extract_first()
            url = ROOT_PATH % vehicle.css(VEHICHEL_SELECTOR).extract_first()
            self.logger.info('Processing vehicle ... %s %s %s' % (title, modification, url))
            item = Vehicle()
            item['name'] = title
            title = title.split(' ', 2)
            item['year'] = title[0]
            item['make'] = title[1]
            item['model'] = title[2]
            item['modification'] = modification
            item['url'] = url
            item['price'] = vehicle.css('.price::text').extract()
            for info in vehicle.css(INFO_LI_SELECTOR):
                info = info.css('::text').extract()
                del info[1:3]
                self.logger.debug(info)
                item[info[0].lower()] = info[1]
            yield item
            request = scrapy.Request(response.urljoin(url), callback=self.parse_details, errback=self.errback_httpbin)
            request.meta['item'] = item
            yield request
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse, errback=self.errback_httpbin)

    def parse_details(self, response):
        item = response.meta['item']
        self.logger.info("Visited %s", response.url)
        overview = response.css('div.media h4')
        for prop in overview:
            title = prop.css('.emphasized-feature-title::text').extract_first()
            description = prop.css('.emphasized-feature-description::text').extract_first()
            self.logger.debug('Property %s - %s' % (title, description))
            key = MAPPING.get(title)
            if key:
                item[key.lower()] = description
        yield item

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)