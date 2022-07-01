from scrapy import Spider, Request


class CLCarsTrucks(Spider):
    name = 'CLCarsTrucks'
    #cl url city name
    proto = 'https://'
    domain = 'craigslist.org'
    idx = 0
    city="saskatoon"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
    }

    def start_requests(self):
        #build the initial request
            yield Request(self.proto + self.city+ '.' + self.domain + '/search/cta?')





    def parse(self, response):

        #grab the next page url from the paginator
        nextp =  response.css('a.next::attr(href)').extract_first()
        if nextp:
            yield Request(self.proto + self.city + '.' + self.domain + nextp, callback=self.parse)

        #get all the links for the adds
        links = response.css('li.result-row a.hdrlnk::attr(href)').extract()
        for link in links:
            #links are relative

            yield Request(link, callback=self.parse_detail_page)

    def parse_detail_page(self, response):
        item = {}

        item['title'] = response.xpath('//*[@id = "titletextonly"]/text()').extract_first()
        #if we have a title, we can continue, otherwise get out
        if not item['title'] or len(item['title']) < 1:
            return

        try:
            item['price'] = response.xpath('//*[@class = "price"]/text()').extract_first().replace("$", "")
        except AttributeError:
            item['price'] = ""

        item['post_url'] = response._url

        #item['post_time'] = response.css('p.postinginfo time::attr(datetime)').extract_first()

        attrs_l = response.xpath('//*[@class = "attrgroup"]/span').extract()
        item = self.processATTRS(attrs_l, item)

        if item['title']:
            self.idx += 1
            item['idx'] = self.idx
            yield item

    def processATTRS(self, attrs, item):
        '''ATTRS are the attrgoup items at the right hand side that describe a car'''
        #we only care about these attributes
        allowed = ['odometer', 'VIN', 'title status', 'transmission', 'auto_descr_short','drive','type','cylinders']
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

        comapany_names=["Abarth","Alfa Romeo","Aston Martin","Audi","Bentley","BMW","Bugatti","Cadillac","Chevrolet","Chrysler","Citroën","Dacia","Daewoo","Daihatsu","Dodge",
                        "Donkervoort","DS","Ferrari","Fiat","Fisker","Ford","Honda","Hummer","Hyundai","Infiniti","Iveco","Jaguar","Jeep",
                         "Kia","KTM","Lada","Lamborghini","Lancia","Land Rover","Landwind","Lexus","Lotus","Maserati","Maybach","Mazda","McLaren",
                         "Mercedes-Benz","MG","Mini","Mitsubishi","Morgan","Nissan","Opel","Peugeot","Porsche","Renault","Rolls-Royce","Rover",
                        "Saab","Seat","Skoda","Smart","SsangYong","Subaru","Suzuki","Tesla","Toyota","Volkswagen","Volvo"]


        for i in allowed:
            try:
                item[i] = attr_found[i]
            except KeyError:
                item[i] = ""


        return item