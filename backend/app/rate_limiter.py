"""
Rate limiter partagé entre main.py et les routers.

Centralise la création de l'instance Limiter pour permettre aux routers
d'utiliser @limiter.limit(...) sans importer main.py (qui créerait un
import circulaire).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Instance unique du limiter - partagée entre main.py et tous les routers.
# La clé d'identification est l'IP du client (get_remote_address).
# Les limites par endpoint sont définies via le décorateur @limiter.limit().
limiter = Limiter(key_func=get_remote_address)
