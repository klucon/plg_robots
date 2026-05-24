# plg_robots — Robots.txt

Spravuje `/robots.txt`. Obsah je plně editovatelný v administraci.

## Admin

`/admin/plg_robots` — nastavení:
- **Aktivovat** — zapne/vypne endpoint `/robots.txt`
- **Obsah** — editovatelný textarea s celým obsahem souboru

## Výchozí obsah

```
User-agent: *
Disallow: /admin/
Disallow: /internal/
Disallow: /api/

Sitemap: /sitemap.xml
```

## Vývoj a testy

```bash
cd plugin/plg_robots
pip install -e ".[dev]"
pytest -q
```
