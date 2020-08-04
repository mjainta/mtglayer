import scrapy


class CkbuylistSpider(scrapy.Spider):
    name = "ckbl"

    start_urls = ['https://www.cardkingdom.com/purchasing/mtg_singles?filter%5Bsort%5D=price_buy_desc&filter%5Bsearch%5D=mtg_advanced&filter%5Bname%5D=&filter%5Bcategory_id%5D=3146&filter%5Bnonfoil%5D=1&filter%5Brarity%5D%5B0%5D=M&filter%5Bprice_op%5D=&filter%5Bprice%5D=&page=1']
    allowed_domains = ["cardkingdom.com"]
    # rules = [  # Get all links on start url
    #     Rule(
    #         link_extractor=LinkExtractor(
    #             deny=r"\?",
    #         ),
    #         follow=False,
    #         callback="parse_page",
    #     )
    # ]
    # def start_requests(self):
    #     urls = [
    #         # 'https://www.cardkingdom.com/purchasing/mtg_singles',
    #         'https://www.cardkingdom.com/purchasing/mtg_singles?filter%5Bsort%5D=price_buy_desc&filter%5Bsearch%5D=mtg_advanced&filter%5Bname%5D=&filter%5Bcategory_id%5D=3146&filter%5Bnonfoil%5D=1&filter%5Brarity%5D%5B0%5D=M&filter%5Bprice_op%5D=&filter%5Bprice%5D=&page=1',
    #     ]
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.css('div[class="itemContentWrapper"]'):
            yield {
                'card-name': quote.css('span[class="productDetailTitle"]::text').get(),
                'set-name': quote.css('div[class="productDetailSet"] a::text').get(),
                'dollar-amount': quote.css('span[class="sellDollarAmount"]::text').get(),
                'cent-amount': quote.css('span[class="sellCentsAmount"]::text').get(),
            }

        next_link = response.css('ul[class="pagination"]').xpath('li[last()]/a').attrib['href']
        self.log(next_link)
        yield scrapy.Request(next_link, callback=self.parse)

        self.log('Following %s' % next_link)
