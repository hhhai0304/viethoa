#!/usr/bin/env python3
"""Build the static việt-hóa site from content/*.json.

    python3 build.py            # write index.html, <slug>/index.html, sitemap, robots

Output is committed, so GitHub Pages serves it with no CI step. Adding a game is
one JSON file under content/games/ — no template edits.
"""

from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600'
    "&family=Newsreader:opsz,wght@6..72,600;6..72,700&display=swap\" rel=\"stylesheet\">"
)


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def ui_lang(tag: str) -> str:
    return {"windows": "Windows", "deck": "Steam Deck", "linux": "Linux"}.get(tag, tag.title())


def render_tabs(game: dict) -> str:
    steps = game["install"]
    order = [k for k in ("windows", "deck", "linux") if k in steps]
    if not order:
        return ""
    buttons, panes = [], []
    for i, key in enumerate(order):
        on = i == 0
        tid = f"tab-{key}"
        buttons.append(
            f'<button role="tab" type="button" aria-selected="{"true" if on else "false"}" '
            f'aria-controls="{tid}">{escape(ui_lang(key))}</button>'
        )
        items = "".join(f"<li>{s}</li>" for s in steps[key])
        panes.append(f'<div class="tabpane" id="{tid}" role="tabpanel"{"" if on else " hidden"}>'
                     f"<ol>{items}</ol></div>")
    return ('<div class="tabs"><div class="tabbar" role="tablist">'
            + "".join(buttons) + "</div>" + "".join(panes) + "</div>")


def render_downloads(game: dict) -> str:
    rel = game.get("release_url", "").replace("/releases/latest", "/releases/latest/download")
    cards = []
    for os_name, fname, hint in (
        ("Windows", "Temtem_Windows.zip", "install.bat — tự dò thư mục Steam"),
        ("Steam Deck / Linux", "Temtem_Linux.tar.gz", "bash install.sh — không cần sudo"),
    ):
        cards.append(
            f'<a class="card" href="{escape(rel)}/{escape(fname)}" rel="noopener">'
            f'<div class="os">{escape(os_name)}</div>'
            f'<div class="file">{escape(fname)}</div>'
            f'<div class="hint">{escape(hint)}</div></a>'
        )
    return '<div class="dl">' + "".join(cards) + "</div>"


def render_screens(game: dict) -> str:
    shots = game.get("screens") or []
    if not shots:
        return ('<div class="shots"><div class="empty">Ảnh chụp màn hình tiếng Việt trong game '
                "sẽ được cập nhật sau khi bản phát hành lên sóng.</div></div>")
    figs = "".join(
        f'<figure><img src="{escape(s["src"])}" alt="{escape(s.get("alt", ""))}" loading="lazy">'
        f'<figcaption>{escape(s.get("caption", ""))}</figcaption></figure>'
        for s in shots
    )
    return f'<div class="shots">{figs}</div>'


def render_faq(game: dict) -> tuple[str, dict | None]:
    faq = game.get("faq") or []
    if not faq:
        return "", None
    html = "".join(
        f"<details><summary>{escape(q['q'])}</summary><p>{escape(q['a'])}</p></details>"
        for q in faq
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q["q"],
             "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in faq
        ],
    }
    return html, schema


def render_changelog(game: dict) -> str:
    entries = []
    for rel in game.get("changelog") or []:
        items = "".join(f"<li>{escape(i)}</li>" for i in rel["items"])
        entries.append(
            f'<div class="cl"><h3>{escape(rel["version"])}</h3>'
            f'<div class="when">{escape(rel["date"])}</div><ul>{items}</ul></div>'
        )
    return "".join(entries)


def donate_dialog(site: dict, game_name: str) -> str:
    d = site.get("donate") or {}
    if not d.get("enabled") or not d.get("account"):
        return ""
    note = (d.get("note_template") or "Viet Hoa {game}").format(game=game_name)
    from urllib.parse import quote_plus
    qr = (f"https://img.vietqr.io/image/{d['bank_id']}-{d['account']}-compact2.png"
          f"?addInfo={quote_plus(note)}&accountName={quote_plus(d['holder'])}")
    return f"""
<dialog id="moi-cafe" class="cafe" aria-labelledby="moi-cafe-h">
  <div class="inner">
    <button type="button" class="close" aria-label="Đóng">&times;</button>
    <h2 id="moi-cafe-h">Mời mình một ly cà phê</h2>
    <p>Bản Việt hóa luôn miễn phí và sẽ luôn miễn phí. Nếu bạn thấy vui khi chơi, một ly cà phê là
    lời cảm ơn rất ấm — chơi hết game và báo lỗi giúp cũng đã là quý lắm rồi.</p>
    <img class="qr" src="{escape(qr)}" alt="Mã QR chuyển khoản" loading="lazy">
    <dl>
      <dt>Ngân hàng</dt><dd>{escape(d['bank'])}</dd>
      <dt>Số tài khoản</dt><dd><code>{escape(d['account'])}</code><button type="button" class="copy" data-copy="{escape(d['account'])}">Chép</button></dd>
      <dt>Chủ tài khoản</dt><dd>{escape(d['holder'])}</dd>
      <dt>Nội dung</dt><dd>{escape(note)}<button type="button" class="copy" data-copy="{escape(note)}">Chép</button></dd>
    </dl>
  </div>
</dialog>"""


def shell(site: dict, *, title: str, description: str, path: str, body: str,
          extra_head: str = "", canonical: str | None = None, depth: int = 0) -> str:
    base = site["base_url"].rstrip("/")
    url = canonical or f"{base}/{path}"
    og_image = f"{base}/static/og-default.png"
    rel = "../" * depth
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{escape(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{escape(site['site_name'])}">
<meta property="og:locale" content="vi_VN">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{escape(url)}">
<meta property="og:image" content="{escape(og_image)}">
<meta name="twitter:card" content="summary_large_image">
{FONTS}
<link rel="stylesheet" href="{rel}static/style.css">
{extra_head}
</head>
<body>
{body}
<script src="{rel}static/app.js" defer></script>
</body>
</html>
"""


def game_page(site: dict, game: dict) -> str:
    slug = game["slug"]
    faq_html, faq_schema = render_faq(game)
    app_schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": f"{game['name']} Việt Hóa",
        "operatingSystem": "Windows, Linux",
        "applicationCategory": "GameApplication",
        "softwareVersion": game["version"],
        "inLanguage": "vi",
        "url": f"{site['base_url'].rstrip('/')}/{slug}/",
        "description": game["summary"],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "VND"},
    }
    schema = json.dumps([app_schema] + ([faq_schema] if faq_schema else []),
                        ensure_ascii=False, indent=None)
    screens = render_screens(game)
    intro = "".join(f"<p>{escape(p)}</p>" for p in game.get("intro") or [])
    highlights = "".join(f"<li>{escape(h)}</li>" for h in game.get("highlights") or [])
    uninstall = "".join(f"<li>{u}</li>" for u in game.get("uninstall") or [])
    donate = donate_dialog(site, game["name"])
    donate_btn = ('<button type="button" class="cafe" data-open="moi-cafe">'
                  '☕ Mời mình một ly cà phê</button>') if donate else ""

    body = f"""<header class="hero"><div class="wrap">
  <p class="kicker">{escape(site['tagline'])} · {escape(game['platform'])}</p>
  <h1>{escape(game['name'])} Việt Hóa</h1>
  <p class="sub">Bản dịch tiếng Việt cho {escape(game['name'])} trên PC — Windows và Steam Deck.</p>
  <p class="meta">Phiên bản <strong>{escape(game['version'])}</strong> · cập nhật {escape(game['updated'])}
     · khớp game build <strong>{escape(game.get('game_build', '—'))}</strong></p>
  <div class="btns">
    <a class="btn primary" href="{escape(game.get('release_url', '#'))}" rel="noopener">Tải và cài đặt</a>
    <a class="btn" href="#cai-dat">Hướng dẫn cài</a>
    <a class="btn" href="{escape(game.get('steam_url', '#'))}" rel="noopener">Trang Steam</a>
  </div>
</div></header>

<nav class="toc"><div class="wrap">
  <a href="#gioi-thieu">Giới thiệu</a>
  <a href="#anh">Hình ảnh</a>
  <a href="#tai-ve">Tải về</a>
  <a href="#cai-dat">Cài đặt</a>
  <a href="#go-cai">Gỡ cài</a>
  <a href="#hoi-dap">Hỏi đáp</a>
  <a href="#thay-doi">Thay đổi</a>
</div></nav>

<main class="wrap">
<section id="gioi-thieu">
  <h2>Giới thiệu</h2>
  {intro}
  <div class="note"><p>{escape(game.get('naming_policy', ''))}</p></div>
  <ul>{highlights}</ul>
</section>

<section id="anh">
  <h2>Hình ảnh trong game</h2>
  {screens}
</section>

<section id="tai-ve">
  <h2>Tải về</h2>
  <p>Gói cài chỉ chứa phần chữ tiếng Việt và script cài — không kèm file game. Bạn cần sở hữu
  {escape(game['name'])} trên Steam để cài được.</p>
  {render_downloads(game)}
</section>

<section id="cai-dat">
  <h2>Hướng dẫn cài</h2>
  <p>Installer tự tìm thư mục cài game, kiểm tra đúng phiên bản, sao lưu file gốc rồi mới áp bản dịch.
  Nếu game của bạn khác phiên bản, nó sẽ dừng lại và báo rõ thay vì làm hỏng game.</p>
  {render_tabs(game)}
  <div class="note warn"><p>Bản dịch áp lên hai file dữ liệu của game. Mỗi lần Steam cập nhật game,
  các file đó bị ghi đè và bản dịch sẽ mất — chạy lại installer là xong (nếu phiên bản đã được hỗ trợ).</p></div>
</section>

<section id="go-cai">
  <h2>Gỡ cài đặt</h2>
  <ol>{uninstall}</ol>
</section>

<section id="hoi-dap">
  <h2>Hỏi đáp</h2>
  {faq_html}
</section>

<section id="thay-doi">
  <h2>Lịch sử thay đổi</h2>
  {render_changelog(game)}
</section>

<hr class="sep">
<p class="lang">Bản Việt hóa do người hâm mộ thực hiện, không liên kết với nhà phát hành hay Steam.
Vui lòng mua game để ủng hộ nhà phát triển.</p>
</main>

<footer><div class="wrap">
  <p><strong>{escape(game['name'])} Việt Hóa</strong> · {escape(game['version'])} · Việt hóa bởi {escape(site['author'])}</p>
  <p><a href="{site['base_url'].rstrip('/')}/">Tất cả bản Việt hóa</a> · <a href="{escape(game.get('steam_url', '#'))}" rel="noopener">Steam</a></p>
  <p style="margin-top:14px">{donate_btn}</p>
</div></footer>
{donate}
"""
    title = f"{game['name']} Việt Hóa — Patch tiếng Việt cho PC & Steam Deck ({game['updated'][:4]})"
    return shell(site, title=title, description=game["summary"], path=f"{slug}/", body=body,
                 extra_head=f'<script type="application/ld+json">{schema}</script>', depth=1)


def hub_page(site: dict, games: list[dict]) -> str:
    cards = []
    for g in sorted(games, key=lambda x: x["updated"], reverse=True):
        cards.append(
            f'<a href="{escape(g["slug"])}/"><h3>{escape(g["name"])}'
            f'<span class="badge">{escape(g["platform"])}</span></h3>'
            f'<p>{escape(g["summary"][:150])}…</p></a>'
        )
    body = f"""<header class="hero"><div class="wrap">
  <p class="kicker">{escape(site['tagline'])}</p>
  <h1>Các bản Việt hóa</h1>
  <p class="sub">Bản dịch tiếng Việt cho game PC, cài tự động trên Windows và Steam Deck.</p>
</div></header>
<main class="wrap">
<section>
  <h2>Danh sách</h2>
  <div class="games">{''.join(cards)}</div>
</section>
</main>
<footer><div class="wrap"><p>Việt hóa bởi {escape(site['author'])}. Bản dịch miễn phí; vui lòng mua game để ủng hộ nhà phát triển.</p></div></footer>
"""
    return shell(site, title=f"Việt hóa game PC — {site['site_name']}",
                 description="Danh sách bản Việt hóa game PC của " + site["author"]
                 + ": patch tiếng Việt cài tự động cho Windows và Steam Deck.",
                 path="", body=body)


def main() -> None:
    site = load(CONTENT / "site.json")
    games = [load(p) for p in sorted((CONTENT / "games").glob("*.json"))]

    (ROOT / "index.html").write_text(hub_page(site, games), encoding="utf-8")
    for game in games:
        d = ROOT / game["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(game_page(site, game), encoding="utf-8")

    base = site["base_url"].rstrip("/")
    urls = [f"{base}/"] + [f"{base}/{g['slug']}/" for g in games]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for g, u in zip([None] + games, urls):
        last = g["updated"] if g else max(x["updated"] for x in games)
        sitemap.append(f"  <url><loc>{escape(u)}</loc><lastmod>{last}</lastmod></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")

    if site.get("custom_domain"):
        (ROOT / "CNAME").write_text(site["custom_domain"] + "\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")

    dest = ROOT / "static"
    print(f"built: index.html + {len(games)} game page(s), sitemap, robots")
    print(f"static: {dest}")


if __name__ == "__main__":
    main()
