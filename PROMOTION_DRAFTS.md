# LootZero — Promotion drafts

These drafts are intentionally **not published**. Adapt the links, screenshots, metrics, and wording before posting.

## Reddit — r/Python

### Title

I got tired of game deal scrapers getting blocked, so I built a free serverless tracker for paid games going free

### Draft

I built [LootZero Engine](https://github.com/kadohack12/lootzero-engine), an open-source Python project that tracks genuine paid PC games temporarily becoming free-to-keep.

The project currently checks structured endpoints from Epic Games and CheapShark/Steam, with a Reddit fallback for community alerts. It runs every 30 minutes on GitHub Actions, persists a deduplication cache in Git, and can broadcast new deals to Discord, Telegram, and Make.com.

The design goal was simple: avoid noisy F2P promotions, reduce fragile DOM scraping, and run without an always-on server or hosting bill.

Technical details:

- Epic Games backend ingestion
- Steam deal filtering through CheapShark
- Reddit fallback monitoring
- Atomic `claimed_games.json` cache persistence
- Discord relative expiry timestamps
- Telegram Bot API and Make.com adapters

Feedback is welcome, especially around source reliability, rate limits, and additional stores worth supporting.

**Repository:** https://github.com/kadohack12/lootzero-engine

### Posting checklist

- Replace the generic link with the repository URL.
- Add one terminal screenshot or a redacted Discord alert screenshot.
- Mention real run duration and alert counts only if measured.
- Follow subreddit self-promotion rules and disclose that it is your project.

## Reddit — r/selfhosted

### Title

LootZero: a zero-cost GitHub Actions engine for paid games that temporarily become free

### Draft

LootZero is a small serverless alternative to running a permanent deal-alert service. GitHub Actions runs the checker every 30 minutes, deduplicates deals using a committed cache, and broadcasts only newly detected offers.

It supports Discord, direct Telegram delivery, and Make.com routing for destinations such as Facebook. No VPS or database is required for the core workflow.

Repository: https://github.com/kadohack12/lootzero-engine

## LinkedIn

I wanted a reliable way to detect paid PC games that temporarily become free without maintaining a server.

So I built **LootZero Engine**: an open-source Python tracker running on GitHub Actions.

It combines structured Epic Games and Steam deal sources, a Reddit fallback, atomic cache persistence, and multi-channel alerts through Discord, Telegram, and Make.com.

The key idea: **zero F2P noise, zero always-on hosting, and no repeated alerts for the same deal.**

Repository: https://github.com/kadohack12/lootzero-engine

#Python #OpenSource #GitHubActions #Automation #Cybersecurity #Gaming

## X / Twitter

### Short version

I built LootZero Engine: a free, serverless tracker for paid PC games that temporarily become free.

- Epic + Steam deal sources
- Reddit fallback
- Git-backed deduplication
- Discord + Telegram + Make.com alerts
- GitHub Actions every 30 min

Open source: https://github.com/kadohack12/lootzero-engine

### Technical thread draft

1/ I wanted alerts for real paid games becoming free — not F2P promotions and not a fragile HTML scraper.

2/ LootZero checks structured Epic Games and CheapShark/Steam endpoints, then uses Reddit as a fallback signal.

3/ A committed `claimed_games.json` cache prevents duplicate alerts while keeping the project serverless and free to run.

4/ New deals can be sent to Discord, Telegram, and Make.com for downstream publishing.

5/ The project is open source. Feedback, source adapters, and PRs are welcome:
https://github.com/kadohack12/lootzero-engine

## Claims and privacy checklist

- Do not claim specific uptime, star counts, or alert volume without measurements.
- Remove screenshots containing tokens, webhook URLs, email addresses, or private channel IDs.
- Never publish `TELEGRAM_BOT_TOKEN`, Discord webhook URLs, or Make webhook URLs.
- Confirm that every screenshot and example deal is safe to share publicly.
