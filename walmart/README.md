# Cornershop's backend integrations test

## Requirements
- Docker & Docker Compose
- Python 3

## Summary
- There are two spiders that need to run sequentially.
```
scrapy crawl grocery_products
scrapy crawl product_branches
```
- Branches desired to extract are specified in settings file.
```
BRANCHES_TO_EXTRACT = {
    '3106': {
        'coords': ('43.6560592651', '-79.434173584')
    },
    '3124': {
        'coords': ('48.4114837646', '-89.2452468872')
    }
}
```
