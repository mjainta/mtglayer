import scrapy
import re


class MbbuylistSpider(scrapy.Spider):
    name = "mbbl"

    def start_requests(self):
        urls = [
            # 'https://www.bazaarofmagic.eu/',
            'https://www.bazaarofmagic.eu/en-WW/buylist/most-wanted?page=1&items=144&view=table',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.css('div[class="product-list-visual"] div[class="row"] tbody tr'):
            print(quote.xpath('td[2]/a/text()').get())
            match = re.search('set-([a-zA-Z0-9]+)_', quote.xpath('td[3]/i/@class').get())
            setName = match.group(1)
            cardNameRaw = quote.xpath('td[2]/a/text()').get()
            cardName = cardNameRaw

            match = re.search(r"\(foil\)", cardNameRaw)
            foil = match != None
            if foil:
                cardName = re.sub(r" \(foil\)", '', cardName)

            match = re.search(r"\(extended art\)", cardNameRaw)
            extendedArt = match != None
            if extendedArt:
                cardName = re.sub(r" \(extended art\)", '', cardName)

            yield {
                'card-name': cardName,
                'set-name': setName,
                'euro-amount': quote.xpath('td[6]/span/text()').get().replace("\u20ac ", ''),
                'foil': foil,
                'extended-art': extendedArt,
            }

        next_link = response.css('div[class="pagination"] div[class="clearfix"] ul').xpath('li[last()]/a').attrib['href']
        self.log(next_link)
        yield scrapy.Request('https://www.bazaarofmagic.eu/en-WW/buylist/most-wanted' + next_link, callback=self.parse)

        self.log('Following %s' % next_link)
