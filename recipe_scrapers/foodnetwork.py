# mypy: disallow_untyped_defs=False
import re

from bs4 import BeautifulSoup

from ._abstract import AbstractScraper


class FoodNetwork(AbstractScraper):
    @classmethod
    def host(cls):
        return "foodnetwork.com"

    def title(self):
        return self.schema.title()

    def author(self):
        return self.schema.author()

    def total_time(self):
        return self.schema.total_time()

    def yields(self):
        return self.schema.yields()

    def ingredients(self):
        return self.schema.ingredients()

    def instructions(self):
        return self.schema.instructions()

    @classmethod
    def process_html_content(cls, current_page: int, html_content: bytes):
        soup = BeautifulSoup(html_content, "html.parser")
        links_html = soup.findAll("a", href=True)

        page_links = [
            link["href"] for link in links_html if "/recipes-a-z/" in link["href"] and "/p/" in link["href"]
        ]
        next_page = None
        for page_link in page_links:
            match = re.search(r'\/p\/(?P<page_num>[0-9]+)', page_link)
            if match:
                local_page = int(match.groupdict().get("page_num"))
                if local_page == current_page + 1:
                    next_page = local_page
                    break

        recipe_links = [link["href"] for link in links_html if "/recipes/" in link["href"] and "/recipes-a-z/"
                        not in link["href"]]

        return recipe_links, next_page

    @classmethod
    def get_all_recipes_urls(cls, *args, **kwargs):
        index_base_url = "https://www.foodnetwork.com/recipes/recipes-a-z"
        partitions = [
            "123", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
            "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "xyz"
        ]
        all_recipe_urls = set()

        for partition in partitions:
            page = 1
            url = f"{index_base_url}/{partition}/p/{page}"
            while page:
                content = cls.get_response(url)
                recipe_urls, next_page = cls.process_html_content(page, content)
                all_recipe_urls.update(recipe_urls)
                page = next_page

        return list(all_recipe_urls)
