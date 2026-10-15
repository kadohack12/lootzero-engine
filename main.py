import json
import os
from datetime import datetime
from pathlib import Path

import requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL", "").strip()
CACHE_FILE = Path("claimed_games.json")
TIMEOUT = 15

EPIC_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=fr&country=FR&allowCountries=FR"
CHEAPSHARK_URL = "https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=0"
REDDIT_URL = "https://www.reddit.com/r/FreeGameFindings/new.json?limit=10"

session = requests.Session()
# Remplace TON_PSEUDO_REDDIT par ton pseudo Reddit
session.headers.update({"User-Agent": "linux:lootzero.gamealert:v1.0 (by /u/TON_PSEUDO_REDDIT)"})


def load_cache() -> set[str]:
    try:
        return set(json.loads(CACHE_FILE.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_cache(cache: set[str]) -> None:
    tmp = CACHE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(sorted(cache), ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CACHE_FILE)


def format_discord_countdown(end_date: str | None) -> str | None:
    """Convertit une date ISO (ex: 2026-10-22T15:00:00.000Z) en compte à rebours Discord."""
    if not end_date:
        return None
    try:
        dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        ts = int(dt.timestamp())
        return f"<t:{ts}:R> (<t:{ts}:f>)"
    except ValueError:
        return end_date


def send_make_alert(
    title: str,
    store: str,
    original_price: str,
    url: str,
    end_date: str | None = None,
    game_id: str | None = None,
    image_url: str | None = None,
) -> None:
    """Send a normalized new-deal payload to Make for multi-platform routing."""
    if not MAKE_WEBHOOK_URL:
        return

    payload = {
        "game_id": game_id,
        "title": title,
        "store": store,
        "original_price": original_price,
        "url": url,
        "expires_at": end_date,
        "image_url": image_url,
        "message": (
            f"🎁 {title}\n"
            f"Boutique : {store}\n"
            f"Prix d'origine : {original_price}\n"
            f"Lien : {url}\n"
            f"Fin de l'offre : {end_date or 'Non précisée'}"
        ),
    }
    try:
        session.post(MAKE_WEBHOOK_URL, json=payload, timeout=TIMEOUT).raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur envoi Make: {e}")


def send_alert(
    title: str,
    store: str,
    original_price: str,
    url: str,
    end_date: str | None = None,
    game_id: str | None = None,
    image_url: str | None = None,
) -> None:
    print(f"🔥 [NOUVEAU JEU GRATUIT] {store}: {title} (Était à {original_price})")
    send_make_alert(title, store, original_price, url, end_date, game_id, image_url)
    if not WEBHOOK_URL:
        return

    lines = [
        f"**Boutique :** {store}",
        f"**Prix d'origine :** {original_price}",
        f"**Lien :** [Récupérer le jeu]({url})",
    ]
    countdown = format_discord_countdown(end_date)
    if countdown:
        lines.append(f"**Fin de l'offre :** {countdown}")

    payload = {
        "embeds": [{
            "title": f"🎁 Jeu Gratuit : {title}",
            "description": "\n".join(lines),
            "color": 3066993 if "Epic" in store else 1584435,
            "footer": {"text": "Bot Alerte Jeux Gratuits"},
        }]
    }
    try:
        session.post(WEBHOOK_URL, json=payload, timeout=TIMEOUT).raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur envoi Discord: {e}")
def fetch_json(url: str):
    res = session.get(url, timeout=TIMEOUT)
    res.raise_for_status()
    return res.json()


def check_epic(cache: set[str]) -> None:
    try:
        elements = fetch_json(EPIC_URL)["data"]["Catalog"]["searchStore"]["elements"]
    except (requests.RequestException, KeyError, TypeError, ValueError) as e:
        print(f"Erreur Epic Games: {e}")
        return

    for item in elements:
        promos = (item.get("promotions") or {}).get("promotionalOffers") or []
        if not promos:
            continue
        offers = promos[0].get("promotionalOffers") or []
        if not offers:
            continue

        price = (item.get("price") or {}).get("totalPrice") or {}
        orig, disc = price.get("originalPrice", 0), price.get("discountPrice", 0)
        if disc != 0 or orig <= 0:
            continue

        game_id = f"epic_{item.get('id')}"
        if game_id in cache:
            continue

        mappings = (item.get("catalogNs") or {}).get("mappings") or []
        slug = (
            item.get("productSlug")
            or ((item.get("offerMappings") or [{}])[0].get("pageSlug"))
            or item.get("urlSlug")
            or (mappings[0].get("pageSlug") if mappings else None)
        )
        url = f"https://store.epicgames.com/fr/p/{slug}" if slug else "https://store.epicgames.com/fr/free-games"

        send_alert(
            item.get("title", "Sans titre"),
            "Epic Games",
            f"{orig / 100:.2f} €",
            url,
            offers[0].get("endDate"),
            game_id,
            next((image.get("url") for image in item.get("keyImages", []) if image.get("url")), None),
        )
        cache.add(game_id)


def check_steam(cache: set[str]) -> None:
    try:
        deals = fetch_json(CHEAPSHARK_URL)
    except (requests.RequestException, ValueError) as e:
        print(f"Erreur Steam: {e}")
        return

    for deal in deals:
        retail = float(deal.get("retailPrice") or 0)
        if retail <= 0:
            continue

        app_id = deal.get("steamAppID")
        deal_id = deal.get("dealID")
        game_id = f"steam_{app_id or deal_id}"
        if game_id in cache:
            continue

        url = (f"https://store.steampowered.com/app/{app_id}/" if app_id
               else f"https://www.cheapshark.com/redirect?dealID={deal_id}")
        send_alert(
            deal.get("title", "Sans titre"),
            "Steam",
            f"{retail:.2f} $",
            url,
            game_id=game_id,
            image_url=deal.get("thumb"),
        )
        cache.add(game_id)


def check_reddit(cache: set[str]) -> None:
    try:
        posts = fetch_json(REDDIT_URL)["data"]["children"]
    except (requests.RequestException, KeyError, TypeError, ValueError) as e:
        print(f"Erreur Reddit backup: {e}")
        return

    for post in posts:
        data = post.get("data", {})
        title = data.get("title", "")
        low = title.lower()
        if "free" not in low:
            continue

        if "[steam]" in low:
            store = "Steam"
        elif "[epic games]" in low or "[epic]" in low:
            store = "Epic Games"
        else:
            continue

        post_id = f"reddit_{data.get('id')}"
        if post_id in cache:
            continue

        send_alert(
            title,
            f"{store} (Alerte Reddit)",
            "Gratuit temporaire",
            data.get("url"),
            game_id=post_id,
            image_url=data.get("thumbnail") if data.get("thumbnail", "").startswith("http") else None,
        )
        cache.add(post_id)


if __name__ == "__main__":
    cache = load_cache()
    print("Vérification en cours...")
    try:
        check_epic(cache)
        check_steam(cache)
        check_reddit(cache)
    finally:
        save_cache(cache)
    print("Terminé !")
