import scrapy
import re


class CkbuylistSpider(scrapy.Spider):
    name = "ckbl"

    start_urls = [
        # Search for Edition:pioneer, non-foil, mythic, no-price-restriction, sort:price-high-to-low
        #'https://www.cardkingdom.com/purchasing/mtg_singles?filter%5Bsort%5D=price_buy_desc&filter%5Bsearch%5D=mtg_advanced&filter%5Bname%5D=&filter%5Bcategory_id%5D=3146&filter%5Bnonfoil%5D=1&filter%5Brarity%5D%5B0%5D=M&filter%5Bprice_op%5D=&filter%5Bprice%5D=&page=1'
        # Seach for Edition: All, non-foil, mythic/rare, price <= 19.99, sort: price-high-to-low, per-page: 100
        'https://www.cardkingdom.com/purchasing/mtg_singles?filter%5Bipp%5D=100&filter%5Bsort%5D=price_buy_desc&filter%5Bsearch%5D=mtg_advanced&filter%5Bname%5D=&filter%5Bcategory_id%5D=0&filter%5Bnonfoil%5D=1&filter%5Brarity%5D%5B0%5D=M&filter%5Brarity%5D%5B1%5D=R&filter%5Bprice_op%5D=%3C%3D&filter%5Bprice%5D=19.99&page=1'
    ]
    allowed_domains = ["cardkingdom.com"]

    def parse(self, response):
        for quote in response.css('div[class="itemContentWrapper"]'):

            dollarAmountCash = quote.css('div[class="usdSellPrice"] span[class="sellDollarAmount"]::text').get()

            if int(dollarAmountCash) < 4:
                return

            cardName = quote.css('span[class="productDetailTitle"]::text').get()
            match = re.search(r"\(Extended Art\)", cardName)
            specialArt = match != None

            if not specialArt:
                match = re.search(r"Godzilla Series\)", cardName)
                specialArt = match != None

            if not specialArt:
                match = re.search(r"Alternate Art\)", cardName)
                specialArt = match != None

            if not specialArt:
                match = re.search(r"\(Borderless\)", cardName)
                specialArt = match != None

            yield {
                'card_name': cardName,
                'set_name': quote.css('div[class="productDetailSet"] a::text').get(),
                'dollar_amount_cash': quote.css('div[class="usdSellPrice"] span[class="sellDollarAmount"]::text').get(),
                'cent_amount_cash': quote.css('div[class="usdSellPrice"] span[class="sellCentsAmount"]::text').get(),
                'dollar_amount_credit': quote.css('div[class="creditSellPrice"] span[class="sellDollarAmount"]::text').get(),
                'cent_amount_credit': quote.css('div[class="creditSellPrice"] span[class="sellCentsAmount"]::text').get(),
                'max_quantity': quote.css('input[class="maxQty"]').attrib['value'],
                'product_id': quote.css('input[class="product_id"]').attrib['value'],
                'foil': False,
                'special_art': specialArt,
            }

        next_link = response.css('ul[class="pagination"]').xpath('li[last()]/a').attrib['href']
        self.log(next_link)
        yield scrapy.Request(next_link, callback=self.parse)

        self.log('Following %s' % next_link)
