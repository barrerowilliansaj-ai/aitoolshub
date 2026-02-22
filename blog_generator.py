#!/usr/bin/env python3
"""
AI Tools Blog - Static Site Generator
Genera un blog estático completo con artículos SEO-optimizados sobre herramientas de IA
y los publica automáticamente en GitHub Pages.
"""

import os
import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from openai import OpenAI

# ============================================================
# CONFIGURACIÓN
# ============================================================
BLOG_TITLE = "AI Tools Hub"
BLOG_TAGLINE = "Reviews, Comparisons & Guides for the Best AI Tools"
BLOG_DESCRIPTION = "Your trusted source for honest AI tool reviews, comparisons, and guides to boost your productivity and business."
BLOG_URL = "https://aitoolshub.github.io"  # Se actualizará con el dominio real
BLOG_AUTHOR = "AI Tools Hub Team"

# Programas de afiliados (se insertan naturalmente en el contenido)
AFFILIATE_LINKS = {
    "writesonic": "https://writesonic.com/?via=aitoolshub",
    "jasper": "https://www.jasper.ai/?fpr=aitoolshub",
    "surfer_seo": "https://surferseo.com/?fp_ref=aitoolshub",
    "semrush": "https://www.semrush.com/",
    "hostinger": "https://www.hostinger.com/",
    "canva": "https://www.canva.com/",
    "grammarly": "https://grammarly.go2cloud.org/aff_c?offer_id=7&aff_id=156f1f6b",
}

# Rutas relativas al directorio del script (funciona tanto local como en GitHub Actions)
_BASE_DIR = Path(__file__).parent
OUTPUT_DIR = _BASE_DIR / "output"
POSTS_DIR = _BASE_DIR / "posts"

# ============================================================
# CLIENTE OPENAI
# ============================================================
client = OpenAI()

def generate_article(topic: dict) -> dict:
    """Genera un artículo SEO-optimizado usando GPT."""
    
    prompt = f"""Write a comprehensive, SEO-optimized blog article about: "{topic['title']}"

Target keyword: {topic['keyword']}
Secondary keywords: {', '.join(topic.get('secondary_keywords', []))}
Article type: {topic.get('type', 'review')}
Word count: approximately 1200-1500 words

Requirements:
1. Write in a helpful, authoritative tone
2. Include an engaging introduction that hooks the reader
3. Use H2 and H3 subheadings for structure
4. Include practical tips and actionable advice
5. Mention specific AI tools naturally (Writesonic, Jasper AI, Grammarly, etc.)
6. Include a clear conclusion with a call-to-action
7. Optimize for the target keyword naturally (don't stuff)
8. Write for freelancers and small business owners
9. Include a "Quick Summary" or "TL;DR" section near the top

Format the response as JSON with these fields:
- title: SEO-optimized article title
- meta_description: 150-160 character meta description
- content: Full article in Markdown format
- tags: array of 5-7 relevant tags
- estimated_read_time: reading time in minutes
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an expert content writer specializing in AI tools, productivity, and technology. You write engaging, SEO-optimized articles that genuinely help readers make informed decisions about AI tools."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        max_tokens=3000
    )
    
    article_data = json.loads(response.choices[0].message.content)
    article_data['keyword'] = topic['keyword']
    article_data['slug'] = generate_slug(article_data['title'])
    article_data['date'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    article_data['category'] = topic.get('category', 'AI Tools')
    
    return article_data


def generate_slug(title: str) -> str:
    """Genera un slug URL-friendly desde el título."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:60]


def insert_affiliate_links(content: str) -> str:
    """Inserta links de afiliados de forma natural en el contenido."""
    replacements = {
        r'\bWritesonic\b': f'[Writesonic]({AFFILIATE_LINKS["writesonic"]})',
        r'\bJasper AI\b': f'[Jasper AI]({AFFILIATE_LINKS["jasper"]})',
        r'\bJasper\.ai\b': f'[Jasper.ai]({AFFILIATE_LINKS["jasper"]})',
        r'\bSurfer SEO\b': f'[Surfer SEO]({AFFILIATE_LINKS["surfer_seo"]})',
        r'\bGrammarly\b': f'[Grammarly]({AFFILIATE_LINKS["grammarly"]})',
        r'\bCanva\b': f'[Canva]({AFFILIATE_LINKS["canva"]})',
    }
    
    for pattern, replacement in replacements.items():
        # Solo reemplazar la primera ocurrencia para no saturar
        content = re.sub(pattern, replacement, content, count=2)
    
    return content


def markdown_to_html(md_content: str) -> str:
    """Convierte Markdown básico a HTML."""
    import markdown
    return markdown.markdown(md_content, extensions=['extra', 'toc', 'codehilite'])


def save_post(article: dict) -> Path:
    """Guarda el artículo como archivo JSON para procesamiento."""
    POSTS_DIR.mkdir(exist_ok=True)
    
    # Insertar links de afiliados
    article['content'] = insert_affiliate_links(article['content'])
    
    post_file = POSTS_DIR / f"{article['date']}-{article['slug']}.json"
    with open(post_file, 'w', encoding='utf-8') as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Post saved: {post_file.name}")
    return post_file


def generate_html_post(article: dict) -> str:
    """Genera el HTML completo de un artículo."""
    content_html = markdown_to_html(article['content'])
    tags_html = ' '.join([f'<span class="tag">{tag}</span>' for tag in article.get('tags', [])])
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} | {BLOG_TITLE}</title>
    <meta name="description" content="{article['meta_description']}">
    <meta name="keywords" content="{', '.join(article.get('tags', []))}">
    <meta property="og:title" content="{article['title']}">
    <meta property="og:description" content="{article['meta_description']}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{BLOG_URL}/posts/{article['slug']}.html">
    <link rel="canonical" href="{BLOG_URL}/posts/{article['slug']}.html">
    <link rel="stylesheet" href="../static/css/style.css">
    <!-- Impact Site Verification -->
    <meta name='impact-site-verification' value='156f1f6b-4545-4796-a756-2851be9ca640'>
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9333843804849647" crossorigin="anonymous"></script>
</head>
<body>
    <header>
        <nav>
            <a href="../index.html" class="logo">{BLOG_TITLE}</a>
            <ul>
                <li><a href="../index.html">Home</a></li>
                <li><a href="../categories/reviews.html">Reviews</a></li>
                <li><a href="../categories/comparisons.html">Comparisons</a></li>
                <li><a href="../categories/guides.html">Guides</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="article-container">
        <article>
            <header class="article-header">
                <div class="article-meta">
                    <span class="category">{article['category']}</span>
                    <span class="date">{article['date']}</span>
                    <span class="read-time">⏱ {article.get('estimated_read_time', 6)} min read</span>
                </div>
                <h1>{article['title']}</h1>
                <p class="article-description">{article['meta_description']}</p>
                <div class="tags">{tags_html}</div>
            </header>
            
            <!-- Ad placeholder (top) -->
            <div class="ad-container ad-top">
                <ins class="adsbygoogle"
                     style="display:block"
                     data-ad-client="ca-pub-9333843804849647"
                     data-ad-slot="auto"
                     data-ad-format="auto"
                     data-full-width-responsive="true"></ins>
                <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
            </div>
            
            <div class="article-content">
                {content_html}
            </div>
            
            <!-- Ad placeholder (middle) -->
            <div class="ad-container ad-middle">
                <ins class="adsbygoogle"
                     style="display:block"
                     data-ad-client="ca-pub-9333843804849647"
                     data-ad-slot="auto"
                     data-ad-format="auto"
                     data-full-width-responsive="true"></ins>
                <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
            </div>
            
            <footer class="article-footer">
                <div class="author-bio">
                    <h3>About {BLOG_AUTHOR}</h3>
                    <p>We test and review the latest AI tools to help freelancers and small businesses make informed decisions. Our reviews are honest, thorough, and based on real-world usage.</p>
                </div>
                <div class="tags">{tags_html}</div>
            </footer>
        </article>
        
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-widget">
                <h3>Top AI Writing Tools</h3>
                <ul class="tool-list">
                    <li><a href="{AFFILIATE_LINKS['writesonic']}" target="_blank" rel="nofollow">🤖 Writesonic - Best for Blogs</a></li>
                    <li><a href="{AFFILIATE_LINKS['jasper']}" target="_blank" rel="nofollow">✍️ Jasper AI - Best for Marketing</a></li>
                    <li><a href="{AFFILIATE_LINKS['grammarly']}" target="_blank" rel="nofollow">📝 Grammarly - Best for Editing</a></li>
                    <li><a href="{AFFILIATE_LINKS['surfer_seo']}" target="_blank" rel="nofollow">🔍 Surfer SEO - Best for SEO</a></li>
                </ul>
            </div>
            <div class="sidebar-widget">
                <h3>Popular Posts</h3>
                <div id="popular-posts">Loading...</div>
            </div>
        </aside>
    </main>
    
    <footer class="site-footer">
        <div class="footer-content">
            <p>&copy; 2026 {BLOG_TITLE}. All rights reserved.</p>
            <p><small>Some links on this site are affiliate links. We may earn a commission at no extra cost to you.</small></p>
            <nav>
                <a href="../about.html">About</a> |
                <a href="../privacy.html">Privacy Policy</a> |
                <a href="../disclaimer.html">Affiliate Disclaimer</a>
            </nav>
        </div>
    </footer>
    
    <script src="../static/js/main.js"></script>
</body>
</html>"""


def generate_homepage(posts: list) -> str:
    """Genera la página principal del blog."""
    posts_html = ""
    for post in posts[:12]:  # Mostrar los últimos 12 artículos
        tags_preview = ' '.join([f'<span class="tag-small">{t}</span>' for t in post.get('tags', [])[:3]])
        posts_html += f"""
        <article class="post-card">
            <div class="post-card-content">
                <span class="post-category">{post.get('category', 'AI Tools')}</span>
                <h2><a href="posts/{post['slug']}.html">{post['title']}</a></h2>
                <p class="post-excerpt">{post['meta_description']}</p>
                <div class="post-meta">
                    <span class="post-date">{post['date']}</span>
                    <span class="post-read-time">⏱ {post.get('estimated_read_time', 6)} min</span>
                </div>
                <div class="post-tags">{tags_preview}</div>
                <a href="posts/{post['slug']}.html" class="read-more">Read More →</a>
            </div>
        </article>"""
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{BLOG_TITLE} - {BLOG_TAGLINE}</title>
    <meta name="description" content="{BLOG_DESCRIPTION}">
    <meta property="og:title" content="{BLOG_TITLE}">
    <meta property="og:description" content="{BLOG_DESCRIPTION}">
    <meta property="og:type" content="website">
    <link rel="canonical" href="{BLOG_URL}">
    <link rel="stylesheet" href="static/css/style.css">
    <!-- Impact Site Verification -->
    <meta name='impact-site-verification' value='156f1f6b-4545-4796-a756-2851be9ca640'>
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9333843804849647" crossorigin="anonymous"></script>
</head>
<body>
    <header>
        <nav>
            <a href="index.html" class="logo">{BLOG_TITLE}</a>
            <ul>
                <li><a href="index.html">Home</a></li>
                <li><a href="categories/reviews.html">Reviews</a></li>
                <li><a href="categories/comparisons.html">Comparisons</a></li>
                <li><a href="categories/guides.html">Guides</a></li>
            </ul>
        </nav>
    </header>
    
    <section class="hero">
        <div class="hero-content">
            <h1>{BLOG_TITLE}</h1>
            <p>{BLOG_TAGLINE}</p>
            <p class="hero-sub">Helping freelancers and small businesses choose the right AI tools to save time and grow faster.</p>
        </div>
    </section>
    
    <!-- Top Ad Banner -->
    <div class="ad-container ad-banner">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-9333843804849647"
             data-ad-slot="auto"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>
    
    <main class="homepage-main">
        <section class="featured-tools">
            <h2>🏆 Top Recommended AI Tools</h2>
            <div class="tools-grid">
                <a href="{AFFILIATE_LINKS['writesonic']}" target="_blank" rel="nofollow" class="tool-card">
                    <h3>Writesonic</h3>
                    <p>Best AI writing tool for blogs & content</p>
                    <span class="cta-btn">Try Free →</span>
                </a>
                <a href="{AFFILIATE_LINKS['jasper']}" target="_blank" rel="nofollow" class="tool-card">
                    <h3>Jasper AI</h3>
                    <p>Best for marketing copy & long-form content</p>
                    <span class="cta-btn">Try Free →</span>
                </a>
                <a href="{AFFILIATE_LINKS['surfer_seo']}" target="_blank" rel="nofollow" class="tool-card">
                    <h3>Surfer SEO</h3>
                    <p>Best AI-powered SEO optimization tool</p>
                    <span class="cta-btn">Try Free →</span>
                </a>
                <a href="{AFFILIATE_LINKS['grammarly']}" target="_blank" rel="nofollow" class="tool-card">
                    <h3>Grammarly</h3>
                    <p>Best AI writing assistant & grammar checker</p>
                    <span class="cta-btn">Try Free →</span>
                </a>
            </div>
        </section>
        
        <section class="latest-posts">
            <h2>Latest Articles</h2>
            <div class="posts-grid">
                {posts_html}
            </div>
        </section>
    </main>
    
    <footer class="site-footer">
        <div class="footer-content">
            <p>&copy; 2026 {BLOG_TITLE}. All rights reserved.</p>
            <p><small>Some links on this site are affiliate links. We may earn a small commission at no extra cost to you. <a href="disclaimer.html">Read our affiliate disclaimer.</a></small></p>
            <nav>
                <a href="about.html">About</a> |
                <a href="privacy.html">Privacy Policy</a> |
                <a href="disclaimer.html">Affiliate Disclaimer</a> |
                <a href="sitemap.xml">Sitemap</a>
            </nav>
        </div>
    </footer>
    
    <script src="static/js/main.js"></script>
</body>
</html>"""


def generate_sitemap(posts: list) -> str:
    """Genera el sitemap XML para SEO."""
    urls = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{BLOG_URL}/index.html</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>"""
    
    for post in posts:
        urls += f"""
    <url>
        <loc>{BLOG_URL}/posts/{post['slug']}.html</loc>
        <lastmod>{post['date']}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>"""
    
    urls += "\n</urlset>"
    return urls


def build_site():
    """Construye el sitio completo desde los posts guardados."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "posts").mkdir(exist_ok=True)
    (OUTPUT_DIR / "static" / "css").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "static" / "js").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "categories").mkdir(exist_ok=True)
    
    # Cargar todos los posts
    posts = []
    for post_file in sorted(POSTS_DIR.glob("*.json"), reverse=True):
        with open(post_file, 'r', encoding='utf-8') as f:
            posts.append(json.load(f))
    
    print(f"Building site with {len(posts)} posts...")
    
    # Generar páginas de artículos
    for post in posts:
        html = generate_html_post(post)
        post_path = OUTPUT_DIR / "posts" / f"{post['slug']}.html"
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✓ Generated: {post['slug']}.html")
    
    # Generar homepage
    homepage = generate_homepage(posts)
    with open(OUTPUT_DIR / "index.html", 'w', encoding='utf-8') as f:
        f.write(homepage)
    print("  ✓ Generated: index.html")
    
    # Generar sitemap
    sitemap = generate_sitemap(posts)
    with open(OUTPUT_DIR / "sitemap.xml", 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print("  ✓ Generated: sitemap.xml")
    
    # Copiar CSS y JS
    copy_assets()
    
    print(f"\n✅ Site built successfully! {len(posts)} articles.")
    return posts


def copy_assets():
    """Copia los archivos CSS y JS al directorio de output."""
    css_src = Path("/home/ubuntu/aitoolsblog/static/css/style.css")
    js_src = Path("/home/ubuntu/aitoolsblog/static/js/main.js")
    
    if css_src.exists():
        import shutil
        shutil.copy(css_src, OUTPUT_DIR / "static" / "css" / "style.css")
    if js_src.exists():
        import shutil
        shutil.copy(js_src, OUTPUT_DIR / "static" / "js" / "main.js")


if __name__ == "__main__":
    print("🚀 AI Tools Blog Generator")
    print("=" * 50)
    build_site()
