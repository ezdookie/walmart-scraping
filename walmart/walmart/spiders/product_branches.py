import json
import scrapy
from walmart.models import Product
from walmart.db import Session


class ProductBranchesSpider(scrapy.Spider):
    name = 'product_branches'

    def start_requests(self):
        session = Session()
        obj_products = session.query(Product).all()

        for obj_product in obj_products:
            for branch_id, branch_info in self.settings['BRANCHES_TO_EXTRACT'].items():
                if obj_product.barcodes is not None:
                    yield scrapy.Request('https://www.walmart.ca/api/product-page/find-in-store?latitude={}&longitude={}&lang=en&upc={}'.format(
                        branch_info['coords'][0], branch_info['coords'][1], obj_product.barcodes.split(',')[0]
                    ), callback=self.parse, meta={'product_id': obj_product.id})

    def parse(self, response):
        json_data = json.loads(response.body).get('info', [])
        req_branches = [b for b in json_data if str(b.get('id')) in self.settings['BRANCHES_TO_EXTRACT'].keys()]
        if len(req_branches) and req_branches[0].get('availabilityStatus') != 'NOT_SOLD':
            yield {
                'branch': req_branches[0].get('id'),
                'stock': req_branches[0].get('availableToSellQty'),
                'price': req_branches[0].get('sellPrice'),
                'product_id': response.meta['product_id']
            }
