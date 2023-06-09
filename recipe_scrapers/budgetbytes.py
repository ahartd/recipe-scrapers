# mypy: disallow_untyped_defs=False
import re
from typing import Dict, Optional, Tuple, Union

from bs4 import BeautifulSoup

from ._abstract import AbstractScraper


class BudgetBytes(AbstractScraper):
    @classmethod
    def host(cls):
        return "budgetbytes.com"

    def title(self):
        return self.schema.title()

    def total_time(self):
        return self.schema.total_time()

    def yields(self):
        return self.schema.yields()

    def ingredients(self):
        return self.schema.ingredients()

    def instructions(self):
        return self.schema.instructions()

    def ratings(self):
        return self.schema.ratings()

    @classmethod
    def process_html_content(cls, current_page: int, html_content: bytes):
        soup = BeautifulSoup(html_content, "html.parser")
        links_html = soup.findAll("a", href=True)

        page_links = [
            link["href"] for link in links_html if "/recipe-catalog/page/" in link["href"]
        ]
        next_page = None
        for page_link in page_links:
            match = re.search(r'catalog\/page\/(?P<page_num>[0-9]+)', page_link)
            if match:
                local_page = int(match.groupdict().get("page_num"))
                if local_page == current_page + 1:
                    next_page = local_page
                    break

        recipe_links = [link["href"] for link in links_html if
                        link["href"].startswith("https://www.budgetbytes.com/") and
                        link.find("img")]

        return recipe_links, next_page

    @classmethod
    def get_all_recipes_urls(
        cls, proxies: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, Tuple[float, float], Tuple[float, None]]] = None
    ):
        index_base_url = "https://www.budgetbytes.com/recipe-catalog/"
        all_recipe_urls = set()

        page = 1
        while page:
            url = f"{index_base_url}/page/{page}/"
            content = cls.get_response(url)
            recipe_urls, next_page = cls.process_html_content(page, content)
            all_recipe_urls.update(recipe_urls)
            page = next_page

        return list(all_recipe_urls)
