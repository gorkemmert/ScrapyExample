#
# This file was created by Maple Software
#
#
# This template is usable for TWO-LEVEL DEEP scrapers with pagination on the 1st level.
#
# HOW THE LOOP WORKS:
#
# 1. FOLLOWING LEVEL 1: Follow item urls.
# 2. SCRAPING LEVEL 2: Scrape the fields and populate item.
# 3. PAGINATION LEVEL 1: Go to the next page with the "next button" if any.
# 1. ...
#
#



from scrapy import Spider

from tutorial.loader import MapleLoader
import dateparser


class MySpider(Spider):
    name = "brickvastgoed_nl"
    start_urls = [
        "https://www.brickvastgoed.nl/aanbod"
    ]  # LEVEL 1

    # 1. FOLLOWING LEVEL 1
    def parse(self, response):
        for follow_url in response.css("a.item::attr(href)").extract():
            yield response.follow(follow_url, self.populate_item)
        yield self.paginate(response)

    # 2. SCRAPING LEVEL 2
    def populate_item(self, response):
        item_loader = MapleLoader(response=response)

        item_loader.add_css("title", "h1")
        item_loader.add_value("external_link", response.url)

        available_date ="".join(response.xpath("//tr[td[.='beschikbaar:']]/td[2]/text()").extract())
        if available_date:
            ava = available_date.split(" ")[-1]
            date_parsed = dateparser.parse(ava, date_formats=["%d %B %Y"])
            date2 = date_parsed.strftime("%Y-%m-%d")
            item_loader.add_value("available_date", date2)

        price = response.xpath("//tr[td[.='Huurprijs per maand:']]/td/text()[contains(., '€')]").extract_first()
        if price:
            item_loader.add_value("rent", price.split("€")[1].split(",")[0])
            item_loader.add_value("currency", "EUR")

        deposit = response.xpath("//tr[td[.='Borgsom:']]/td/text()[contains(., '€')]").extract_first()
        if price:
            item_loader.add_value("deposit", price.split("€")[1].split(",")[0])

        item_loader.add_xpath("property_type","//tr[td[.='Type woning:']]/td[2]/text()[. !='[]']")

        square = response.xpath("//tr[td[.='Woonoppervlakte:']]/td[2]/text()").get()
        if square:
            item_loader.add_value("square_meters", square.split("m²")[0])

        images = [response.urljoin(x)for x in response.xpath("//div[@class='item']/img/@src").extract()]
        if images:
                item_loader.add_value("images", images)

        item_loader.add_xpath("room_count","//tr[td[.='Aantal kamers:']]/td[2]/text()")

        desc = "".join(response.xpath("//div[@class='description-content']/text()").extract())
        item_loader.add_value("description", desc)

        energ_label = response.xpath("//tr[td[.='Energie label:']]/td/span/@class").extract_first()
        if energ_label:
            item_loader.add_value("energy_label", energ_label.split("l_")[-1])

        terrace = "".join(response.xpath("//td[@class='extras']/text()[contains(.,' Balkon / dakterras')]/preceding::i[1][@class='fa fa-check']").extract())
        if terrace:
                item_loader.add_value("balcony", False)

        terrace = response.xpath("//td[@class='extras']/text()[contains(.,'Garage') or contains(.,'Parkeergelegenheid') ]/preceding::i[1][@class='fa fa-check']").get()
        if terrace:
            item_loader.add_value("parking", True)

        terrace = response.xpath("//td[@class='extras']/text()[contains(.,'  Lift')]/preceding::i[1][@class='fa fa-check']").get()
        if terrace:
            item_loader.add_value("elevator", True)

        item_loader.add_xpath("zipcode","//tr[td[.='Postcode:']]/td[2]/text()")
        item_loader.add_xpath("city", "//tr[td[.='Adres:']]/td[2]/text()")

        item_loader.add_xpath("address","//tr[td[.='Adres:']]/td[2]/text()")

        item_loader.add_value("landlord_phone", "040-2116149")
        item_loader.add_value("landlord_email", "info@brickvastgoed.nl")
        item_loader.add_value("landlord_name", "Brick Vastgoed")
        

        yield item_loader.load_item()

    # 3. PAGINATION LEVEL 1
    def paginate(self, response):
        next_page_url = response.css(
            "div.pagination a::attr(href)"
        ).extract_first()  # pagination("next button") <a> element here
        if next_page_url is not None:
            return response.follow(next_page_url, self.parse)
