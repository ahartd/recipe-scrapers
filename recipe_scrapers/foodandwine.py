# mypy: disallow_untyped_defs=False
from bs4 import BeautifulSoup

from ._abstract import AbstractScraper


class FoodAndWine(AbstractScraper):
    @classmethod
    def host(cls):
        return "foodandwine.com"

    def title(self):
        return self.schema.title()

    def total_time(self):
        return self.schema.total_time()

    def yields(self):
        return self.schema.yields()

    def image(self):
        return self.schema.image()

    def ingredients(self):
        return self.schema.ingredients()

    def instructions(self):
        return self.schema.instructions()

    @classmethod
    def process_html_content_recurse(cls, html_content: bytes, categories_visited: list, recipe_urls: set):
        soup = BeautifulSoup(html_content, "html.parser")
        category_links = [l["href"] for l in
                          soup.findAll("a", class_=lambda x: x and "taxonomy-nodes__link" in x.split(), href=True)]

        if len(category_links) > 0:
            for category_link in category_links:
                if category_link not in categories_visited:
                    print(category_link)
                    categories_visited.append(category_link)
                    cls.process_html_content_recurse(cls.get_response(category_link).content, categories_visited,
                                                     recipe_urls)
        else:
            # Just return recipe URLs
            recipe_urls.update([l["href"] for l in
                                soup.findAll("a", class_=lambda x: x and "mntl-card-list-items" in x.split(), href=True)
                                if "/recipes/" in l["href"]])

        return recipe_urls

    @classmethod
    def get_all_recipes_urls(cls, *args, **kwargs):
        index_base_url = "https://www.foodandwine.com/recipes/"
        content = cls.get_response(index_base_url).content
        return cls.process_html_content_recurse(content, [index_base_url], set())
