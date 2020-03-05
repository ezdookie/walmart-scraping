import json
import scrapy
from scrapy_splash import SplashRequest


class GroceryProductsSpider(scrapy.Spider):
    name = 'grocery_products'
    start_urls = ['https://www.walmart.ca/en/grocery/N-117']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse)

    def parse(self, response):
        category_links = response.css('.categoryTile a::attr(href)').getall()
        for href in category_links:
            yield SplashRequest(response.urljoin(href), self.parse_category)

    def parse_category(self, response):
        product_links = response.css('section#shelf-page article.product a.product-link')
        yield from response.follow_all(
            css='section#shelf-page article.product a.product-link',
            callback=self.parse_product
        )

        pagination_links = response.css('div#shelf-pagination li a::attr(href)').getall()
        for href in pagination_links:
            yield SplashRequest(response.urljoin(href), self.parse_category)

    def parse_product(self, response):
        json_text = response.xpath('//script[starts-with(., "window.__PRELOADED_STATE__")]/text()').get()
        obj_json = json.loads(json_text[json_text.find('{'):-1])
        obj_product = obj_json.get('product')
        active_sku_id = obj_product.get('activeSkuId')
        obj_entities_sku = obj_json.get('entities', {}).get('skus', {}).get(active_sku_id, {})
        bar_codes = obj_entities_sku.get('upc', [''])
        obj_images = obj_entities_sku.get('images', [])
        list_large_images = ['https://i5.walmartimages.ca/%s' % obj_img.get('large', {}).get('url') for obj_img in obj_images]
        category_list = [c.get('displayName', {}).get('en') for c in obj_product.get('item', {}).get('primaryCategories', [])[0].get('hierarchy', [])]
        category_list.reverse()
        category = 'Grocery|%s' % ('|'.join([c for c in category_list]))
        yield {
            'store': 'walmart',
            'name': obj_entities_sku.get('name'),
            'barcodes': ','.join(bar_codes),
            'sku': active_sku_id,
            'brand': obj_entities_sku.get('brand', {}).get('name'),
            'description': obj_entities_sku.get('longDescription'),
            'package': obj_entities_sku.get('description'),
            'image_urls': ','.join(list_large_images),
            'category': category,
            'product_url': response.request.url
        }
