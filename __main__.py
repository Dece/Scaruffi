#!/usr/bin/env python3
"""A simple library to get data from scaruffi.com."""

import logging

from bs4 import BeautifulSoup as Soup

import requests

import log


LOG = log.get_logger("scaruffi", level=logging.WARNING)
GENERAL_INDEX_URL = "https://scaruffi.com/music/groups.html"


def main():
    print(get_musicians())


def _get_url(url):
    LOG.debug(f"GET {url}")
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as exc:
        LOG.error(f"An exception occured during HTTP GET: {exc}")
        return None
    sc = response.status_code
    if sc != 200:
        LOG.error(f"Server returned HTTP response {sc} to {url}.")
        return None
    return response.text


def get_musicians(offset=0, limit=20):
    """Get a list of musicians."""
    html = _get_url(GENERAL_INDEX_URL)
    if not html:
        return None

    soup = Soup(html, 'html5lib')
    # Semantic Web? Just find the fattest table.
    mu_table = max(soup.find_all('table'), key=lambda t: len(t.text))
    return [a_tag.text for a_tag in mu_table.find_all("a")]


if __name__ == "__main__":
    main()
