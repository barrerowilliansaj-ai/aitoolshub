#!/usr/bin/env python3
"""
AI Tools Hub - Initial Setup Script
Genera los primeros 10 artículos del blog para tener contenido desde el día 1.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from blog_generator import generate_article, save_post, build_site
from content_topics import CONTENT_TOPICS
from daily_automation import log


def generate_static_pages():
    """Genera las páginas estáticas del blog (About, Privacy, Disclaimer)."""
    output_dir = Path(__file__).parent / "output"
    
    # About page
    about_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About Us | AI Tools Hub</title>
    <meta name="description" content="AI Tools Hub is your trusted source for honest AI tool reviews, comparisons, and guides.">
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <header>
        <nav>
            <a href="index.html" class="logo">AI Tools Hub</a>
            <ul>
                <li><a href="index.html">Home</a></li>
                <li><a href="categories/reviews.html">Reviews</a></li>
                <li><a href="categories/comparisons.html">Comparisons</a></li>
                <li><a href="categories/guides.html">Guides</a></li>
            </ul>
        </nav>
    </header>
    <main style="max-width:800px;margin:60px auto;padding:0 20px;">
        <h1>About AI Tools Hub</h1>
        <p>AI Tools Hub is an independent blog dedicated to helping freelancers, content creators, and small business owners navigate the rapidly growing world of AI tools.</p>
        <h2>Our Mission</h2>
        <p>We test, review, and compare the best AI tools on the market so you don't have to. Our goal is to save you time and money by providing honest, thorough, and practical reviews.</p>
        <h2>What We Cover</h2>
        <ul>
            <li>AI Writing Tools (Jasper, Writesonic, Copy.ai, etc.)</li>
            <li>AI SEO Tools (Surfer SEO, Clearscope, etc.)</li>
            <li>AI Productivity Tools</li>
            <li>AI Marketing Tools</li>
        </ul>
        <h2>Affiliate Disclosure</h2>
        <p>Some links on this site are affiliate links. If you click through and make a purchase, we may earn a small commission at no extra cost to you. This helps us keep the site running and producing quality content. See our full <a href="disclaimer.html">Affiliate Disclaimer</a>.</p>
    </main>
    <footer class="site-footer">
        <div class="footer-content">
            <p>&copy; 2026 AI Tools Hub. All rights reserved.</p>
            <nav><a href="about.html">About</a> | <a href="privacy.html">Privacy Policy</a> | <a href="disclaimer.html">Affiliate Disclaimer</a></nav>
        </div>
    </footer>
</body>
</html>"""
    
    # Privacy Policy
    privacy_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy | AI Tools Hub</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <header>
        <nav>
            <a href="index.html" class="logo">AI Tools Hub</a>
            <ul><li><a href="index.html">Home</a></li></ul>
        </nav>
    </header>
    <main style="max-width:800px;margin:60px auto;padding:0 20px;">
        <h1>Privacy Policy</h1>
        <p><em>Last updated: February 2026</em></p>
        <h2>Information We Collect</h2>
        <p>We use Google Analytics to collect anonymous usage data to improve our content. We do not collect personally identifiable information.</p>
        <h2>Cookies</h2>
        <p>We use cookies for analytics purposes only. You can disable cookies in your browser settings.</p>
        <h2>Third-Party Links</h2>
        <p>Our site contains links to third-party websites. We are not responsible for their privacy practices.</p>
        <h2>Contact</h2>
        <p>If you have questions about this privacy policy, please contact us through our website.</p>
    </main>
    <footer class="site-footer">
        <div class="footer-content">
            <p>&copy; 2026 AI Tools Hub. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
    
    # Affiliate Disclaimer
    disclaimer_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Affiliate Disclaimer | AI Tools Hub</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <header>
        <nav>
            <a href="index.html" class="logo">AI Tools Hub</a>
            <ul><li><a href="index.html">Home</a></li></ul>
        </nav>
    </header>
    <main style="max-width:800px;margin:60px auto;padding:0 20px;">
        <h1>Affiliate Disclaimer</h1>
        <p><em>Last updated: February 2026</em></p>
        <p>AI Tools Hub participates in affiliate marketing programs. This means that when you click on certain links on our site and make a purchase, we may earn a commission.</p>
        <h2>Our Commitment</h2>
        <p>Our affiliate relationships do not influence our reviews or recommendations. We only recommend products and services we genuinely believe are valuable to our readers.</p>
        <h2>Programs We Participate In</h2>
        <ul>
            <li>Amazon Associates Program</li>
            <li>Writesonic Affiliate Program</li>
            <li>Jasper AI Affiliate Program</li>
            <li>Surfer SEO Affiliate Program</li>
            <li>Various other SaaS affiliate programs</li>
        </ul>
        <p>Affiliate commissions help us keep this site running and producing free, high-quality content for our readers. Thank you for your support!</p>
    </main>
    <footer class="site-footer">
        <div class="footer-content">
            <p>&copy; 2026 AI Tools Hub. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
    
    with open(output_dir / "about.html", 'w') as f:
        f.write(about_html)
    with open(output_dir / "privacy.html", 'w') as f:
        f.write(privacy_html)
    with open(output_dir / "disclaimer.html", 'w') as f:
        f.write(disclaimer_html)
    
    # robots.txt
    robots_txt = f"""User-agent: *
Allow: /

Sitemap: https://aitoolshub.github.io/sitemap.xml
"""
    with open(output_dir / "robots.txt", 'w') as f:
        f.write(robots_txt)
    
    log("✓ Static pages generated (About, Privacy, Disclaimer, robots.txt)")


def run_initial_setup(num_articles: int = 5):
    """Genera los primeros artículos del blog."""
    log("=" * 60)
    log("🚀 AI Tools Hub - Initial Setup")
    log(f"   Generating first {num_articles} articles...")
    log("=" * 60)
    
    # Tomar los primeros N temas de mayor prioridad
    priority_topics = sorted(CONTENT_TOPICS, key=lambda x: x.get('priority', 99))
    selected_topics = priority_topics[:num_articles]
    
    for i, topic in enumerate(selected_topics, 1):
        log(f"\n[{i}/{num_articles}] Generating: {topic['title']}")
        try:
            article = generate_article(topic)
            save_post(article)
            log(f"   ✓ Generated: {article['title']}")
        except Exception as e:
            log(f"   ❌ Error: {e}")
            continue
    
    # Construir el sitio
    log("\n🔨 Building complete site...")
    posts = build_site()
    
    # Generar páginas estáticas
    generate_static_pages()
    
    log("\n" + "=" * 60)
    log(f"✅ Initial setup complete!")
    log(f"   Articles generated: {len(posts)}")
    log(f"   Output directory: /home/ubuntu/aitoolsblog/output/")
    log("=" * 60)
    
    return posts


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--articles', type=int, default=5, help='Number of initial articles to generate')
    args = parser.parse_args()
    
    run_initial_setup(args.articles)
