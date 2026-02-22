// AI Tools Hub - Main JavaScript

// Track affiliate link clicks for analytics
document.addEventListener('DOMContentLoaded', function() {
    // Add nofollow to all external links
    const links = document.querySelectorAll('a[href^="http"]');
    links.forEach(link => {
        if (!link.href.includes(window.location.hostname)) {
            link.setAttribute('rel', 'nofollow noopener');
            link.setAttribute('target', '_blank');
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Reading progress bar
    const progressBar = document.createElement('div');
    progressBar.style.cssText = `
        position: fixed; top: 0; left: 0; height: 3px;
        background: #6366f1; z-index: 9999; transition: width 0.1s;
        width: 0%;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrolled = (window.scrollY / docHeight) * 100;
        progressBar.style.width = Math.min(scrolled, 100) + '%';
    });

    // Table of contents auto-generation for articles
    const articleContent = document.querySelector('.article-content');
    if (articleContent) {
        const headings = articleContent.querySelectorAll('h2, h3');
        if (headings.length > 2) {
            const toc = document.createElement('div');
            toc.className = 'toc-container';
            toc.innerHTML = '<h4>📋 Table of Contents</h4><ul></ul>';
            toc.style.cssText = `
                background: #f5f3ff; border: 1px solid #e5e7eb;
                border-radius: 8px; padding: 20px; margin: 24px 0;
            `;
            
            const tocList = toc.querySelector('ul');
            headings.forEach((heading, i) => {
                const id = 'heading-' + i;
                heading.id = id;
                const li = document.createElement('li');
                li.style.marginLeft = heading.tagName === 'H3' ? '16px' : '0';
                li.innerHTML = `<a href="#${id}" style="color: #6366f1;">${heading.textContent}</a>`;
                tocList.appendChild(li);
            });
            
            articleContent.insertBefore(toc, articleContent.firstChild);
        }
    }
});

// Google Analytics placeholder
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
// gtag('config', 'G-XXXXXXXXXX'); // Replace with real GA4 ID
