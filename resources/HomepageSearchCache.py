from flask import request

from middleware.homepage_search_cache import (
    get_agencies_without_homepage_urls,
    update_search_cache,
)
from middleware.security import api_required
from resources.PsycopgResource import PsycopgResource


class HomepageSearchCache(PsycopgResource):

    @api_required
    def get(self):
        """
        Retrieve 100 agencies without homepage urls
        :return:
        """
        with self.psycopg2_connection.cursor() as cursor:
            return get_agencies_without_homepage_urls(cursor)

    @api_required
    def post(self):
        """
        Update search cache
        :return:
        """
        with self.psycopg2_connection.cursor() as cursor:
            return update_search_cache(
                cursor=cursor,
                agency_uid=request.json["agency_uid"],
                search_results=request.json["search_results"],
            )
