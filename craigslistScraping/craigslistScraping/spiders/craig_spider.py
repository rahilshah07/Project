import scrapy

import scrapy


class craigslist_car(scrapy.Spider):
    name = "craig_spider"

    allowed_domains = ['craigslist.org']
    start_urls = ['https://windsor.craigslist.org/search/cta']  # cta is cars + trucks by ALL
    base_url = 'https://windsor.craigslist.org'

    # Get all the vehicle_url
    def parse(self, response):
        all_vehicles = response.xpath('//li[@class="result-row"]')

        for vehicle in all_vehicles:
            vehicle_url = vehicle.xpath('.//a/@href').extract_first()
            yield scrapy.Request(vehicle_url, callback=self.parse_vehicle)

        next_page_partial_url = response.xpath('//a[@class="button next"]/@href').extract_first()
        next_page_url = self.base_url + next_page_partial_url
        yield scrapy.Request(next_page_url, callback=self.parse)

    # Parse the vehicle_url data
    def parse_vehicle(self, response):
        url_vehicle = response.url
        print("####URL_VEHICLE", url_vehicle)
        title = response.xpath('//span[@id="titletextonly"]/text()').extract_first()
        price = response.xpath('//span[@class="price"]/text()').extract_first()
        subLocation = response.xpath('//span[@class="price"]/following-sibling::small/text()').extract_first()
        body = response.xpath('//section[@id="postingbody"]/text()').extract()
        attribDict = {}
        attrs= response.xpath('//p[@class="attrgroup"]/span/b').extract()
        print(attrs)
        print(len(attrs))
        for i in range(0, len(attrs)):
            allowed = ['odometer', 'VIN', 'title status', 'transmission', 'auto_descr_short']
            attr_found = {}
            for a in attrs:
                a = a.replace("<span>", "").replace("</span>", "")
                parts = a.split("<b>", 1)
                if len(parts) > 1 or parts[0] == '':
                    prop = parts[0].rstrip(": ")
                    if prop == '':
                        prop = "auto_descr_short"
                    val = parts[1].replace("</b>", "")
                    attr_found[prop] = val
            for i in allowed:
                try:
                    attribDict[i] = attr_found[i]
                except KeyError:
                    attribDict[i] = ""
            return attribDict
            ##attribDict[i] = response.xpath('//p[@class="attrgroup"]/span').extract()[i]

        imageDict = {}
        for i in range(0, len(response.xpath('//div[@id="thumbs"]/a/@href').extract())):
            imageDict[i] = response.xpath('//div[@id="thumbs"]/a/@href').extract()[i]
        yield {
            'URL_Vehicle': url_vehicle,
            'Title': title,
            'Price': price,
            'SubLoc': subLocation,
            'Body': body,
            'AttribDictionary': attribDict,
            'ImageDictionary': imageDict
        }