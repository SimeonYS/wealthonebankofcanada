import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import WwealthonebankofcanadaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class WwealthonebankofcanadaSpider(scrapy.Spider):
	name = 'wealthonebankofcanada'
	start_urls = ['https://www.wealthonebankofcanada.com/Personal/AboutUs/WhatsNew/']

	def parse(self, response):
		post_links = response.xpath('//p/a/@href').getall()
		for link in post_links:
			if not 'pdf' in link:
				yield response.follow(link, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//div[@class="section simple Component-StandardContent "]/p[position()<4]//text()|//div[@class="section simple Component-StandardContent "]/span[position()<2]//text()').getall()
		date = re.findall(r'\b(?:\w+\s\d+\s)?\w+\S+(?:\s\d+(?:th)?)?\,\s\d+\S+', ' '.join(date))
		if not date:
			date = "Date is not published"
		title = response.xpath('//div[@class="section simple Component-StandardContent "]/strong/text()|//div[@class="section simple Component-StandardContent "]/p/strong/text()').get()
		content = response.xpath('//div[@class="section simple Component-StandardContent "]//text()[not (ancestor::strong)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=WwealthonebankofcanadaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
