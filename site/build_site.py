from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE_SRC = ROOT / "site"
DEFAULT_DATA_FILE = SITE_SRC / "site_data.json"
PORTFOLIO = ROOT / "PORTFOLIO.md"
ASSETS = ROOT / "assets"


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def repo_url() -> str:
    explicit = os.environ.get("PORTFOLIO_REPOSITORY_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if repo:
        return f"https://github.com/{repo}"
    return ""


def render_tags(tags: list[str]) -> str:
    return "".join(f'<span class="tag">{esc(t)}</span>' for t in tags)


def project_detail_href(project: dict) -> str:
    anchor = project.get("anchor", "")
    return f"portfolio.html#{esc(anchor)}" if anchor else "portfolio.html"


def landing_html(data: dict) -> str:
    profile = data["profile"]
    links = data["links"]["profile"]
    github = links.get("github", "")
    hero_journey = str(profile.get("journey", "")).removeprefix("이후 ")

    capabilities = "".join(
        f'<article class="capability"><h3>{esc(x["title"])}</h3><p>{esc(x["description"])}</p></article>'
        for x in data["capabilities"]
    )

    projects = []
    for p in data["featured_projects"]:
        cover = p.get("cover_asset")
        cover_html = (
            f'<div class="project-cover"><img src="{esc(cover)}" alt="{esc(p["title"])} 대표 이미지" loading="lazy"></div>'
            if cover else ""
        )
        repo = p.get("repository")
        repo_link = f'<a href="{esc(repo)}">Repository</a>' if repo else ""
        projects.append(f'''
        <article class="project-card">
          {cover_html}
          <div class="project-body">
            <div class="project-meta"><span>{esc(p["category"])}</span><span>{esc(p["period"])}</span></div>
            <h3>{esc(p["title"])}</h3>
            <p>{esc(p["summary"])}</p>
            <div class="tags">{render_tags(p.get("tags", []))}</div>
            <div class="card-links"><a href="{project_detail_href(p)}">Details</a>{repo_link}</div>
          </div>
        </article>''')

    career = "".join(f'''
      <article class="timeline-item">
        <div class="timeline-period">{esc(x["period"])}</div>
        <div>
          <h3>{esc(x["company"])}</h3>
          <div class="timeline-role">{esc(x["role"])}</div>
          <p>{esc(x["summary"])}</p>
        </div>
      </article>''' for x in data["career"])

    competitions = "".join(f'''
      <article class="compact-card">
        <h3><a href="{project_detail_href(x)}">{esc(x["title"])}</a></h3>
        <p class="result">{esc(x.get("result", ""))}</p>
        <p>{esc(x["summary"])}</p>
      </article>''' for x in data["competitions"])

    publications = "".join(f'''
      <article class="compact-card">
        <h3>{f'<a href="{esc(x["url"])}">{esc(x["title"])}</a>' if x.get("url") else esc(x["title"])}</h3>
        <p>{esc(x["year"])} · {esc(x["journal"])}</p>
        <p>{esc(x["authors"])}</p>
      </article>''' for x in data["publications"])

    education = "".join(f'''
      <article class="compact-card">
        <h3>{esc(x["school"])}</h3>
        <p>{" · ".join(esc(d) for d in x["details"])}</p>
      </article>''' for x in data["education"])

    repo_base = repo_url()
    source_links = ""
    if repo_base:
      source_links = f'<a class="button" href="{esc(repo_base)}/blob/main/PORTFOLIO.md">Portfolio Markdown</a>'
    else:
      source_links = '<a class="button" href="portfolio.html">Portfolio Markdown View</a>'

    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(profile["name"])} · ML Engineer Portfolio</title>
  <meta name="description" content="Research-minded Applied ML Engineer portfolio covering medical biosignals, manufacturing time-series, security UEBA and ML Systems.">
  <meta property="og:title" content="{esc(profile["name"])} · ML Engineer Portfolio">
  <meta property="og:description" content="Time-Series · Anomaly Detection · ML Systems">
  <meta property="og:type" content="website">
  <link rel="stylesheet" href="assets/site.css">
</head>
<body>
<a class="skip-link" href="#main">본문으로 이동</a>
<nav class="site-nav" aria-label="주요 탐색">
  <div class="inner">
    <a class="brand" href="#top">{esc(profile["name"])}</a>
    <div class="nav-links">
      <a href="#projects">Projects</a>
      <a href="#experience">Experience</a>
      <a href="#research">Research</a>
      <a href="#competitions">Competitions</a>
    </div>
  </div>
</nav>
<main id="main">
  <section class="hero" id="top">
    <div>
      <p class="eyebrow">Applied ML · Research · ML Systems</p>
      <h1>{esc(profile["name"])}</h1>
      <p class="hero-role">{esc(profile["role"])}</p>
      <p class="hero-lead">{esc(profile["lead"])}</p>
      <div class="actions">
        <a class="button primary" href="#projects">Selected Projects</a>
        {source_links}
        <a class="button" href="{esc(github)}">GitHub</a>
      </div>
    </div>
    <aside class="hero-side">
      <p>{esc(hero_journey)}</p>
      <div class="domain-list" aria-label="주요 도메인">
        <span>Medical Biosignal</span><span>Manufacturing Sensor</span><span>Security Behavior Log</span><span>ML Systems</span>
      </div>
    </aside>
  </section>

  <section class="section" id="capabilities">
    <div class="section-head">
      <p class="section-kicker">Core capabilities</p>
      <div><h2>데이터 이해에서 모델 운영 구조까지</h2><p class="section-intro">도메인이 달라도 데이터의 구조와 품질을 파악하고 Feature/Input을 설계한 뒤 모델을 검증·설명하고 실제 활용 구조로 연결하는 흐름을 중심으로 일해 왔다.</p></div>
    </div>
    <div class="capability-grid">{capabilities}</div>
  </section>

  <section class="section" id="projects">
    <div class="section-head">
      <p class="section-kicker">Selected projects</p>
      <div><h2>대표 프로젝트</h2><p class="section-intro">Security AI, ML/Data Pipeline, Serving, Manufacturing Time-Series, Medical AI, Graduate Research의 대표 사례다. 전체 {esc(data["project_count"])}개 프로젝트는 상세 문서에서 확인할 수 있다.</p></div>
    </div>
    <div class="project-grid">{"".join(projects)}</div>
  </section>

  <section class="section" id="experience">
    <div class="section-head">
      <p class="section-kicker">Experience</p>
      <div><h2>의료 · 제조 · 보안으로 확장한 Applied ML 경험</h2></div>
    </div>
    <div class="timeline">{career}</div>
  </section>

  <section class="section" id="research">
    <div class="section-head">
      <p class="section-kicker">Research</p>
      <div><h2>연구 및 논문</h2><p class="section-intro">fNIRS 기반 Alzheimer 관련 연구와 현재 데이터사이언스 석사과정을 병행하고 있다.</p></div>
    </div>
    <div class="compact-grid">{publications}</div>
  </section>

  <section class="section" id="competitions">
    <div class="section-head">
      <p class="section-kicker">Competitions</p>
      <div><h2>경진대회 프로젝트</h2><p class="section-intro">대회 성적보다 데이터 표현, Feature 구성, 모델 검증 과정을 프로젝트 관점에서 정리했다.</p></div>
    </div>
    <div class="compact-grid">{competitions}</div>
  </section>

  <section class="section" id="education">
    <div class="section-head">
      <p class="section-kicker">Education</p>
      <div><h2>학력</h2></div>
    </div>
    <div class="compact-grid">{education}</div>
  </section>
</main>
<footer class="footer">
  <div class="footer-links">
    <a href="portfolio.html">Portfolio View</a>
    <a href="{esc(github)}">GitHub</a>
  </div>
  <div>Version {esc(data["version"])} · GitHub Pages build output is generated, not maintained as source.</div>
</footer>
</body>
</html>
'''


def build_markdown_page(source: Path, output: Path, title: str) -> None:
    cmd = [
        "pandoc", str(source),
        "-f", "gfm+raw_html", "-t", "html5",
        "--standalone", "--section-divs", "--quiet",
        "--metadata", f"title={title}",
        "--metadata", "lang=ko",
        "--css", "assets/site.css",
        "--include-before-body", str(SITE_SRC / "detail_header.html"),
        "--include-after-body", str(SITE_SRC / "detail_footer.html"),
        "-o", str(output),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.ids: list[str] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("id"):
            self.ids.append(str(data["id"]))
        for key in ("href", "src", "poster"):
            val = data.get(key)
            if val:
                self.refs.append(str(val))


def validate_output(out: Path, data: dict) -> None:
    required = {
      "index.html", "portfolio.html",
        "assets"
    }
    actual_top = {p.name for p in out.iterdir()}
    missing = required - actual_top
    if missing:
        raise RuntimeError(f"site missing required output: {sorted(missing)}")
    extras = actual_top - required
    if extras:
        raise RuntimeError(f"site has unexpected top-level output: {sorted(extras)}")

    html_files = [out / "index.html", out / "portfolio.html"]
    portfolio_ids: set[str] = set()
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        if "sources/" in text or "_internal/" in text:
            raise RuntimeError(f"internal/evidence path leaked into site: {path.name}")
        parser = LinkCollector()
        parser.feed(text)
        if len(parser.ids) != len(set(parser.ids)):
            raise RuntimeError(f"duplicate HTML id in {path.name}")
        if path.name == "portfolio.html":
            portfolio_ids = set(parser.ids)
        for ref in parser.refs:
            parsed = urlparse(ref)
            if parsed.scheme in {"http", "https", "mailto", "tel"} or ref.startswith("#"):
                continue
            rel = parsed.path
            if not rel:
                continue
            target = (out / rel).resolve()
            try:
                target.relative_to(out.resolve())
            except ValueError as exc:
                raise RuntimeError(f"path escapes site root: {path.name}: {ref}") from exc
            if not target.exists():
                raise RuntimeError(f"broken local link in {path.name}: {ref}")

    for project in data["featured_projects"] + data["competitions"]:
        anchor = project.get("anchor")
        if anchor and anchor not in portfolio_ids:
            raise RuntimeError(f"project anchor missing from portfolio.html: {anchor}")



def build(out: Path, data_file: Path) -> None:
    data = json.loads(data_file.read_text(encoding="utf-8"))
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(ASSETS, out / "assets")
    shutil.copy2(SITE_SRC / "site.css", out / "assets" / "site.css")
    (out / "index.html").write_text(landing_html(data), encoding="utf-8")
    build_markdown_page(PORTFOLIO, out / "portfolio.html", "강동혁 · Portfolio")
    validate_output(out, data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the GitHub Pages portfolio site from public Career Wiki artifacts.")
    parser.add_argument("--output", type=Path, help="Output directory. Required unless --check is used.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_FILE, help="Generated site data JSON. Public projections default to site/site_data.json.")
    parser.add_argument("--check", action="store_true", help="Build into a temporary internal directory, validate, then remove it.")
    args = parser.parse_args()
    if args.check:
        out = ROOT / "_internal" / "_build" / "site-check"
        try:
            data_file = args.data if args.data.is_absolute() else ROOT / args.data
            build(out, data_file)
            print("SITE BUILD CHECK: PASS")
        finally:
            shutil.rmtree(ROOT / "_internal" / "_build", ignore_errors=True)
        return
    if not args.output:
        parser.error("--output is required unless --check is used")
    out = args.output if args.output.is_absolute() else ROOT / args.output
    data_file = args.data if args.data.is_absolute() else ROOT / args.data
    build(out, data_file)
    print(f"SITE: {out}")


if __name__ == "__main__":
    main()
