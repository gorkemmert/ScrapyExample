from scrapy.loader.processors import MapCompose
from scrapy import Spider
from scrapy import Request
from scrapy.selector import Selector
from w3lib.html import remove_tags
from tutorial.loader import MapleLoader
import json
import dateparser


class MySpider(Spider):
    name = 'rentvalley_nl'
    start_urls = ['https://www.rentvalley.nl/nl/realtime-listings/consumer']  # LEVEL 1

    # 1. FOLLOWING
    def parse(self, response):
        
        data = json.loads(response.body)
        
        for item in data:
            follow_url = response.urljoin(item["url"])
            lat = item["lat"]
            lng = item["lng"]
            
            yield Request(follow_url, callback=self.populate_item, meta={"lat":lat, "lng":lng})


    # 2. SCRAPING level 2
    def populate_item(self, response):
        item_loader = MapleLoader(response=response)
        

        lat = response.meta.get("lat")
        lng = response.meta.get("lng")

        #Title

        title = response.xpath("normalize-space(//h1/text())").extract_first()

        item_loader.add_value("title", title)

        #external link

        item_loader.add_value("external_link", response.url)
        
        #Available date
        
        available_date="".join(response.xpath("//dl[@class='details-simple']/dd/text()").extract()[-1])
        if available_date:
            item_loader.add_value("available_date", available_date)
        
        #price
        
        price=response.xpath("//dl[@class='details-simple']/dd[1]/text()").extract_first()
        if price:
            item_loader.add_value("rent", price.rstrip("p.m. ex.").lstrip("€ "))
            item_loader.add_value("currency", "EUR")

        
        #deposit

        deposit=response.xpath("//dl[@class='details-simple']/dd[3]/text()").extract_first()
        if deposit:
            item_loader.add_value("deposit", deposit.lstrip("€ "))
        
        #property_type
        typ=response.xpath("//dl[dt[.='Type']]/dd[8]/text()[. !='[]']").extract_first()
        item_loader.add_value("property_type",typ)

        #square_meters

        square=response.xpath("//dl[@class='details-simple']/dd/text()").extract()[-2]
        if square:
            item_loader.add_value("square_meters", square.split("m²")[0])

        #room_count

        room=response.xpath("//dl[dt[.='Kamers']]/dd/text()[. !='[]']").extract()[-6]

        item_loader.add_value("room_count",room)

        #zipcode
        item_loader.add_xpath("zipcode","//dl[@class='details-simple']/dd[5]/text()")
        '''
        a=response.xpath("//dl[@class='details-simple']//dt/text()").extract()
        b=response.xpath("//dl[@class='details-simple']//dd/text()").extract()
        for i,j in zip(a,b):
            if i=="zipcode":
                zip=j
        item_loader.add_value("zipcode",j)


        '''
        #city
        item_loader.add_xpath("city", "//dl[@class='details-simple']/dd[6]")

        #adress
        item_loader.add_xpath("address", "//dl[@class='details-simple']/dd[6]")

       
        #item_loader.add_css("", "")

        yield item_loader.load_item()