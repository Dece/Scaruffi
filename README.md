Scaruffi
========

Get some data from scaruffi.com from Python.

Piero Scaruffi has written a lot about rock music, jazz, classical, whether it
is reviews or history. It is a valuable ressource for a variety of reasons and
this script aims to make data fetching easier for personal usage.

Features:

- Get a big list of musicians.
- Get best albums per decade, grouped by rating.

This is a work in progress, I would like to add more content to be usable!



Install
-------

This library is available on PyPI:

```bash
pip install scaruffi
```



Usage
-----

Check out the `ScaruffiApi` for all available methods.

```python
from scaruffi.api import ScaruffiApi
api = ScaruffiApi()
api.get_ratings(1960)
# { 9.5: [ Release(title='Trout Mask Replica', ...
```

This module can also be used as a command-line tool:

```bash
scaruffi --help
scaruffi --musicians --offset 5555 --limit 5
# Mooseheart Faith
# Morbid Angel
# Morcheeba
# Morgan Fisher
# Morning 40 Federation
scaruffi --ratings 1960
# 9.5
# - Captain Beefheart - Trout Mask Replica (1969)
# 9.0
# - Bob Dylan - Blonde On Blonde (1966)
# - Captain Beefheart - Safe As Milk (1967)
# ...
```
