from walmart.models import Base, Product, BranchProduct
from walmart.db import engine, Session


class WalmartPipeline(object):
    def __init__(self):
        Base.metadata.create_all(engine)
        self.session = Session()

    def process_item(self, item, spider):
        if spider.name == 'grocery_products':
            product = Product(**item)
            if not self.session.query(Product).filter_by(
                    sku=product.sku).scalar():
                self.session.add(product)
                self.session.commit()
        elif spider.name == 'product_branches':
            branch_product = BranchProduct(**item)
            if not self.session.query(BranchProduct).filter_by(
                    product_id=branch_product.product_id,
                    branch=branch_product.branch).scalar():
                self.session.add(branch_product)
                self.session.commit()
        return item
