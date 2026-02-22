#!/usr/bin/env python3
"""
AI Tools Hub - Daily Automation Script
Ejecutar diariamente para generar y publicar nuevos artículos.
Diseñado para ser ejecutado por cron job o GitHub Actions.
"""

import os
import sys
import json
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Agregar el directorio del blog al path
sys.path.insert(0, str(Path(__file__).parent))

from blog_generator import generate_article, save_post, build_site, POSTS_DIR
from content_topics import CONTENT_TOPICS, ADDITIONAL_TOPICS

# Ruta relativa al directorio del script (funciona tanto local como en GitHub Actions)
_BASE_DIR = Path(__file__).parent
LOG_FILE = _BASE_DIR / "automation.log"


def log(message: str):
    """Registra mensajes con timestamp."""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + "\n")


def get_published_topics() -> set:
    """Retorna el conjunto de keywords ya publicadas."""
    published = set()
    for post_file in POSTS_DIR.glob("*.json"):
        with open(post_file, 'r') as f:
            data = json.load(f)
            published.add(data.get('keyword', ''))
    return published


def select_next_topic(published_keywords: set) -> dict | None:
    """Selecciona el próximo tema a publicar basado en prioridad."""
    all_topics = CONTENT_TOPICS + ADDITIONAL_TOPICS
    
    # Filtrar los ya publicados
    available = [t for t in all_topics if t['keyword'] not in published_keywords]
    
    if not available:
        log("⚠️ All predefined topics published. Generating new topic...")
        return generate_new_topic()
    
    # Ordenar por prioridad (1 = más alta)
    available.sort(key=lambda x: x.get('priority', 99))
    
    # Tomar el de mayor prioridad (con algo de variación)
    top_priority = available[0]['priority']
    top_topics = [t for t in available if t.get('priority', 99) == top_priority]
    
    return random.choice(top_topics)


def generate_new_topic() -> dict:
    """Genera un nuevo tema usando IA cuando se agotan los predefinidos."""
    from google import genai
    from google.genai import types
    import os
    model_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = """You are an SEO expert specializing in AI tools content. Generate a new blog topic for an AI tools review blog targeting freelancers and small businesses.
            
Return JSON with: title, keyword, secondary_keywords (array of 3), type (review/comparison/guide/listicle), category (Reviews/Comparisons/Guides), priority (1-3)

Focus on: AI writing tools, productivity AI, SEO tools, content creation AI.
Make it specific and searchable."""
    
    response = model_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)


def publish_to_github(output_dir: Path):
    """Publica el sitio en GitHub Pages via git push."""
    try:
        # Verificar si hay un repo git configurado
        result = subprocess.run(
            ['git', 'remote', '-v'],
            cwd=output_dir,
            capture_output=True, text=True
        )
        
        if 'github' not in result.stdout.lower():
            log("⚠️ GitHub remote not configured. Skipping push.")
            log("   Run setup_github.sh to configure GitHub Pages deployment.")
            return False
        
        # Agregar todos los cambios
        subprocess.run(['git', 'add', '.'], cwd=output_dir, check=True)
        
        # Commit con fecha
        date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        subprocess.run(
            ['git', 'commit', '-m', f'Auto-publish: New article {date_str}'],
            cwd=output_dir, check=True
        )
        
        # Push
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=output_dir, check=True)
        
        log("✅ Successfully pushed to GitHub Pages!")
        return True
        
    except subprocess.CalledProcessError as e:
        log(f"❌ Git error: {e}")
        return False
    except Exception as e:
        log(f"❌ Unexpected error during publish: {e}")
        return False


def run_daily_automation():
    """Ejecuta el ciclo completo de automatización diaria."""
    log("=" * 60)
    log("🚀 Starting Daily Automation Cycle")
    log("=" * 60)
    
    try:
        # 1. Obtener temas ya publicados
        published = get_published_topics()
        log(f"📊 Already published: {len(published)} articles")
        
        # 2. Seleccionar próximo tema
        topic = select_next_topic(published)
        if not topic:
            log("❌ No topic available. Exiting.")
            return False
        
        log(f"📝 Selected topic: {topic['title']}")
        log(f"   Keyword: {topic['keyword']}")
        
        # 3. Generar artículo con IA
        log("🤖 Generating article with AI...")
        article = generate_article(topic)
        log(f"   Title: {article['title']}")
        log(f"   Words: ~{len(article['content'].split())} words")
        log(f"   Read time: {article.get('estimated_read_time', 'N/A')} min")
        
        # 4. Guardar el artículo
        post_file = save_post(article)
        log(f"💾 Saved: {post_file.name}")
        
        # 5. Reconstruir el sitio
        log("🔨 Building static site...")
        posts = build_site()
        log(f"   Total articles: {len(posts)}")
        
        # 6. Publicar en GitHub Pages
        output_dir = _BASE_DIR / "output"
        log("📤 Publishing to GitHub Pages...")
        publish_to_github(output_dir)
        
        log("=" * 60)
        log("✅ Daily automation completed successfully!")
        log(f"   New article: {article['title']}")
        log(f"   Total articles: {len(posts)}")
        log("=" * 60)
        
        return True
        
    except Exception as e:
        log(f"❌ CRITICAL ERROR: {e}")
        import traceback
        log(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = run_daily_automation()
    sys.exit(0 if success else 1)
