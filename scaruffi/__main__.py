#!/usr/bin/env python3
"""A simple library to get data from scaruffi.com."""

import argparse
import logging

from scaruffi.api import ScaruffiApi


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
    api = ScaruffiApi(log_level=log_level)

    if args.musicians:
        musicians = api.get_musicians(args.offset, args.limit)
        for musician in musicians:
            print(musician)
    elif args.ratings is not None:
        ratings = api.get_ratings(args.ratings)
        if ratings:
            for rating, releases in ratings.items():
                print(rating)
                for rel in releases:
                    print(f"- {rel.artist} - {rel.title} ({rel.year})")


if __name__ == "__main__":
    main()
