import scrapy
from urllib.parse import urljoin

class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/"]

    # ──────────────────────────────────────────────
    #  Project‑local settings (only for this spider)
    # ──────────────────────────────────────────────
    custom_settings = {

        # Export *two* feeds with different columns
        "FEEDS": {
            "books.csv": {
                "format": "csv",
                "fields": ["title", "price", "availability"],
            },
            "images_info.csv": {
                "format": "csv",
                "fields": ["title", "image_urls", "images"],
            },
        },

        # Turn on Scrapy’s built‑in image pipeline
        "ITEM_PIPELINES": {"scrapy.pipelines.images.ImagesPipeline": 1},
        "IMAGES_STORE": "book_images",          # folder for JPEGs
    }

    def parse(self, response):
        for book in response.css("article.product_pod"):
            yield {
                "title":        book.css("h3 a::attr(title)").get(),
                "price":        book.css("p.price_color::text").get(),
                "availability": book.css("p.instock.availability::text")
                                   .getall()[-1].strip(),
                "image_urls": [
                    urljoin(response.url, book.css("img::attr(src)").get())
                ],
            }

        # follow pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
