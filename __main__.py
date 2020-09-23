#!/usr/bin/env python3
"""A simple library to get data from scaruffi.com."""

import argparse
import logging
import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, NavigableString
import requests

import log


LOG = None

SITE_URL = "https://scaruffi.com"
GENERAL_INDEX = SITE_URL + "/music/groups.html"
RATINGS_DECADES = SITE_URL + "/ratings/{:02}.html"



@dataclass
class Release:
    title: str
    artist: str = ""
    year: int = 0  # Usually the release year, not the recording year.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print debug logs")
    parser.add_argument("-r", "--ratings", type=int,
                        help="Get ratings for a decade (e.g. 60)")
    parser.add_argument("-m", "--musicians", action="store_true",
                        help="Get the list of musicians")
    parser.add_argument("--offset", type=int, default=0,
                        help="Offset for paginated queries (default is 0)")
    parser.add_argument("--limit", type=int, default=20,
                        help="Limit for paginated queries (default is 20)")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    global LOG
    LOG = log.get_logger("scaruffi", level=log_level)

    if args.musicians:
        musicians = get_musicians(args.offset, args.limit)
        for musician in musicians:
            print(musician)
    elif args.ratings is not None:
        ratings = get_ratings(args.ratings)
        if ratings:
            for rating, releases in ratings.items():
                print(rating)
                for rel in releases:
                    print(f"- {rel.artist} - {rel.title} ({rel.year})")


def _get_page(url):
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


def _get_soup(url):
    html = _get_page(url)
    if not html:
        return None
    return BeautifulSoup(html, "html5lib")


def get_musicians(offset=0, limit=20):
    """Get a list of musicians, or None on error."""
    soup = _get_soup(GENERAL_INDEX)
    if not soup:
        return None
    # Semantic Web? Just find the fattest table.
    mu_table = max(soup.find_all("table"), key=lambda t: len(t.text))
    musicians = [a_tag.text for a_tag in mu_table.find_all("a")]
    return musicians[offset : offset + limit]


def get_ratings(decade):
    """Get a dict of ratings to a release list for this decade.

    The decade must be an integer in the [0, 99] range, or a full year
    (1960 for example). Returns None on error.
    """
    if 1900 <= decade:
        decade %= 100
    if not (0 <= decade < 100 and decade % 10 == 0):
        LOG.error(f"Invalid decade value: {decade}.")
        return None
    soup = _get_soup(RATINGS_DECADES.format(decade))
    if not soup:
        return None
    ratings_table = max(soup.find_all("table"), key=lambda t: len(t.text))
    num_lists = len(ratings_table("ul"))
    if num_lists == 1:
        return _get_ratings_from_unique_list(ratings_table.ul)
    else:
        return _get_ratings_from_lists(ratings_table("ul"))


def _get_ratings_from_unique_list(messy_list):
    """Get ratings from decades where one list contains all ratings."""
    ratings = {}
    current_key = None
    for tag in messy_list:
        if isinstance(tag, NavigableString):
            continue
        # Get an entry for the current rating.
        if tag.name == "li":
            release = _parse_release(tag.text)
            if not current_key:
                LOG.critical(f"Found release {release} without rating.")
                return None
            ratings[current_key].append(release)
        # Detect a new rating list.
        # Do it after getting entries in tag due to bad HTML.
        text = tag.text.strip()
        if text:
            rating = _match_rating(text.split()[-1])
            if rating is not None:
                current_key = rating
                ratings[current_key] = []
    return ratings


def _get_ratings_from_lists(lists):
    """Get ratings from several lists, one per rating."""
    ratings = {}
    for ul in lists:
        rating_tag = ul.span
        if rating_tag:
            rating = _match_rating(rating_tag.text)
        if rating is None:
            LOG.critical("Failed to find rating tag in list.")
            return None
        releases = [_parse_release(li.text) for li in ul("li")]
        ratings[rating] = releases
    return ratings


RATING_RE = re.compile(r"\s*(\d(.\d)?)/10\s*")


def _match_rating(text):
    """Try to match text as a rating and return the rating, or None."""
    if not text.strip():
        return None
    match = RATING_RE.match(text.strip())
    if match:
        return float(match.group(1))


def _parse_release(entry):
    """Fill a release fields using entry, as well as we can."""
    entry = entry.strip("\r\n :")  # Remove bogus spaces and colons.
    parts = entry.split(": ")
    if len(parts) == 1:
        LOG.info(f"No colon in {entry}, using both as artist and title.")
        title_and_year = _parse_release_title_year(entry)
        if not title_and_year:
            return Release(title=entry)
        title, year = title_and_year
        artist = title
    else:
        # Usual case is 2 parts ("artist: title"), but in case one of them
        # contains ": " as well, assume that it is part of the title, not the
        # artist name.
        artist = parts[0]
        title_and_year_str = parts[1].strip()
        if len(parts) > 2:
            title_and_year_str += ": " + ": ".join(parts[2:])
        title_and_year = _parse_release_title_year(title_and_year_str)
        if not title_and_year:
            return Release(artist=artist, title=title_and_year_str)
        title, year = title_and_year
    return Release(artist=artist, title=title, year=year)


RATING_TITLE_AND_YEAR_RE = re.compile(r"(.+?)\s?\((\d{4})(?:-\d+)?\)")


def _parse_release_title_year(title_and_year):
    """Parse title and year in the approximate "title (year)" format.

    In some instances, the year is actually a range of years, in the YYYY-YY
    format. Sometimes there is no space between title and year."""
    match = RATING_TITLE_AND_YEAR_RE.match(title_and_year)
    if not match:
        LOG.error(f"Failed to split title and year in \"{title_and_year}\".")
        return None
    groups = match.groups()
    if len(groups) != 2 or None in groups:
        LOG.error(f"Failed to parse title and year in \"{title_and_year}\".")
        return None
    title, year = groups
    try:
        year = int(year)
    except ValueError:
        LOG.error(f"Failed to parse year string \"{year}\" as an integer.")
        year = 0
    return title, year


if __name__ == "__main__":
    main()
