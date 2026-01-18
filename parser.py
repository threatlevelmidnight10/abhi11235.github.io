import re
import os

def classify_link(link):
    """Return category based on URL domain."""
    link_lower = link.lower()
    
    if 'twitter.com' in link_lower or 'x.com' in link_lower:
        return 'twitter'
    
    # Only these tech domains - rest ignored
    tech_domains = [
        'github.com',
        'news.ycombinator.com',
        'ycombinator.com',
        'medium.com',
        'arxiv.org',
        'notion.site',
        'notion.so',
    ]
    
    # Also include *.net domains
    if '.net' in link_lower:
        return 'tech'
    
    for domain in tech_domains:
        if domain in link_lower:
            return 'tech'
    
    # Everything else is ignored
    return 'ignore'

def extract_tweet_id(url):
    """Extract tweet ID from URL."""
    match = re.search(r'/status/(\d+)', url)
    if match:
        return match.group(1)
    return None

def extract_link_info(url):
    """Extract meaningful display info from URL."""
    info = {
        'url': url,
        'title': '',
        'description': '',
        'source': ''
    }
    
    # GitHub
    if 'github.com' in url:
        match = re.search(r'github\.com/([^/]+)/([^/?#]+)', url)
        if match:
            info['source'] = 'GitHub'
            info['title'] = f"{match.group(1)}/{match.group(2)}"
            info['description'] = 'Repository'
        else:
            info['source'] = 'GitHub'
            info['title'] = url.split('github.com/')[-1].split('?')[0][:50]
            info['description'] = 'GitHub Link'
    
    # Medium
    elif 'medium.com' in url:
        info['source'] = 'Medium'
        # Try to extract article title from URL
        parts = url.split('/')
        if len(parts) > 3:
            slug = parts[-1].split('?')[0]
            info['title'] = slug.replace('-', ' ').title()[:60]
        else:
            info['title'] = 'Article'
        info['description'] = 'Blog Post'
    
    # arXiv
    elif 'arxiv.org' in url:
        info['source'] = 'arXiv'
        match = re.search(r'(\d+\.\d+)', url)
        if match:
            info['title'] = f"Paper {match.group(1)}"
        else:
            info['title'] = 'Research Paper'
        info['description'] = 'Academic Paper'
    
    # Hacker News / YC
    elif 'ycombinator.com' in url or 'news.ycombinator.com' in url:
        info['source'] = 'Hacker News'
        if 'item?id=' in url:
            match = re.search(r'id=(\d+)', url)
            info['title'] = f"Discussion #{match.group(1)}" if match else 'Discussion'
        elif '/companies/' in url:
            info['title'] = url.split('/companies/')[-1].split('/')[0].replace('-', ' ').title()
            info['description'] = 'YC Company'
        else:
            info['title'] = 'Hacker News'
        info['description'] = info['description'] or 'HN Link'
    
    # Notion
    elif 'notion' in url:
        info['source'] = 'Notion'
        info['title'] = 'Notion Document'
        info['description'] = 'Shared Page'
    
    # .net domains
    elif '.net' in url:
        domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
        info['source'] = domain.group(1) if domain else 'Web'
        path = url.split(info['source'])[-1] if info['source'] else ''
        info['title'] = path.split('?')[0].replace('/', ' ').strip()[:50] or 'Link'
        info['description'] = 'Article'
    
    else:
        domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
        info['source'] = domain.group(1) if domain else 'Web'
        info['title'] = 'Link'
        info['description'] = ''
    
    return info

def generate_site():
    input_file = './cht_history/_chat180626.txt'
    output_file = 'bookmarks.md'
    
    url_pattern = r'https?://\S+'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    raw_links = re.findall(url_pattern, content)
    clean_links = [link.strip(',').strip(')') for link in raw_links]
    unique_links = list(dict.fromkeys(clean_links))
    unique_links.reverse()

    twitter_links = []
    tech_links = []

    for link in unique_links:
        category = classify_link(link)
        if category == 'twitter':
            tweet_id = extract_tweet_id(link)
            if tweet_id:
                twitter_links.append((link, tweet_id))
        elif category == 'tech':
            if "whatsapp.com" not in link:
                tech_links.append(link)
        # 'ignore' category is silently dropped

    tweets_per_page = 6
    total_tweet_pages = (len(twitter_links) + tweets_per_page - 1) // tweets_per_page if twitter_links else 0

    md_content = [
        "---",
        "layout: default",
        "title: Bookmarks",
        "---",
        "",
        "# Bookmark Vault",
        "",
        "---",
        ""
    ]

    # Twitter Section
    if twitter_links:
        md_content.append("## X / Twitter")
        md_content.append("")
        md_content.append(f'<p class="small-text">{len(twitter_links)} posts • Page <span id="current-page">1</span> of {total_tweet_pages}</p>')
        md_content.append("")
        
        md_content.append("""
<style>
.tweet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}
.tweet-frame {
  border: 1px solid #e1e8ed;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}
.tweet-frame iframe {
  width: 100%;
  height: 350px;
  border: none;
}
.page-nav { 
  margin: 30px 0; 
  text-align: center; 
}
.page-nav button { 
  background: #fff; 
  border: 1px solid #ddd; 
  padding: 10px 20px; 
  margin: 0 4px; 
  cursor: pointer; 
  border-radius: 6px; 
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}
.page-nav button:hover:not(:disabled) { 
  border-color: #e06e2e; 
  color: #e06e2e; 
}
.page-nav button.active { 
  background: #e06e2e; 
  color: white; 
  border-color: #e06e2e; 
}
.page-nav button:disabled { 
  opacity: 0.4; 
  cursor: not-allowed; 
}
.tweet-page { 
  display: none; 
}
.tweet-page.active { 
  display: block; 
}
/* Tech Links - Google Docs style */
.link-card {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s;
  text-decoration: none;
}
.link-card:hover {
  border-color: #e06e2e;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.link-icon {
  width: 40px;
  height: 40px;
  background: #e06e2e;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
  margin-right: 14px;
  flex-shrink: 0;
}
.link-icon.github { background: #24292e; }
.link-icon.medium { background: #000; }
.link-icon.arxiv { background: #b31b1b; }
.link-icon.hn { background: #ff6600; }
.link-icon.notion { background: #000; }
.link-icon.net { background: #512bd4; }
.link-content {
  flex: 1;
  min-width: 0;
}
.link-title {
  font-weight: 600;
  color: #333;
  font-size: 15px;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.link-desc {
  color: #888;
  font-size: 13px;
}
.link-source {
  color: #e06e2e;
  font-size: 12px;
  margin-top: 4px;
}
@media (max-width: 768px) {
  .tweet-grid { grid-template-columns: 1fr; }
}
</style>
""")
        
        md_content.append('<div id="twitter-section">')
        
        for page_num in range(total_tweet_pages):
            start_idx = page_num * tweets_per_page
            end_idx = min(start_idx + tweets_per_page, len(twitter_links))
            page_tweets = twitter_links[start_idx:end_idx]
            
            active = " active" if page_num == 0 else ""
            md_content.append(f'<div class="tweet-page{active}" data-page="{page_num}">')
            md_content.append('<div class="tweet-grid">')
            
            for original_url, tweet_id in page_tweets:
                iframe_url = f"https://platform.twitter.com/embed/Tweet.html?id={tweet_id}&theme=light"
                md_content.append(f'''<div class="tweet-frame">
<iframe src="{iframe_url}" loading="lazy" allowtransparency="true"></iframe>
</div>''')
            
            md_content.append('</div>')
            md_content.append('</div>')
        
        md_content.append('<div class="page-nav" id="page-nav"></div>')
        md_content.append('</div>')
        
        md_content.append(f"""
<script>
(function() {{
  const totalPages = {total_tweet_pages};
  const pages = document.querySelectorAll('.tweet-page');
  const nav = document.getElementById('page-nav');
  const currentPageSpan = document.getElementById('current-page');
  
  function show(idx) {{
    pages.forEach((p, i) => p.classList.toggle('active', i === idx));
    render(idx);
    currentPageSpan.textContent = idx + 1;
    document.getElementById('twitter-section').scrollIntoView({{behavior: 'smooth', block: 'start'}});
  }}
  
  function render(idx) {{
    nav.innerHTML = '';
    const prev = document.createElement('button');
    prev.textContent = '← Previous';
    prev.disabled = idx === 0;
    prev.onclick = () => show(idx - 1);
    nav.appendChild(prev);
    
    let start = Math.max(0, idx - 2);
    let end = Math.min(totalPages - 1, start + 4);
    if (end - start < 4) start = Math.max(0, end - 4);
    
    for (let i = start; i <= end; i++) {{
      const btn = document.createElement('button');
      btn.textContent = i + 1;
      if (i === idx) btn.classList.add('active');
      btn.onclick = () => show(i);
      nav.appendChild(btn);
    }}
    
    const next = document.createElement('button');
    next.textContent = 'Next →';
    next.disabled = idx === totalPages - 1;
    next.onclick = () => show(idx + 1);
    nav.appendChild(next);
  }}
  
  render(0);
}})();
</script>
""")

    # Tech Section - Google Docs style cards
    if tech_links:
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append("## Tech & Reading")
        md_content.append("")
        md_content.append(f'<p class="small-text">{len(tech_links)} links</p>')
        md_content.append("")
        md_content.append('<div class="tech-links">')
        
        for link in tech_links:
            info = extract_link_info(link)
            
            # Determine icon class
            icon_class = ""
            icon_text = info['source'][:2].upper()
            if 'github' in link.lower():
                icon_class = "github"
                icon_text = "GH"
            elif 'medium' in link.lower():
                icon_class = "medium"
                icon_text = "M"
            elif 'arxiv' in link.lower():
                icon_class = "arxiv"
                icon_text = "Ar"
            elif 'ycombinator' in link.lower():
                icon_class = "hn"
                icon_text = "YC"
            elif 'notion' in link.lower():
                icon_class = "notion"
                icon_text = "N"
            elif '.net' in link.lower():
                icon_class = "net"
                icon_text = ".N"
            
            md_content.append(f'''<a href="{link}" target="_blank" class="link-card">
  <div class="link-icon {icon_class}">{icon_text}</div>
  <div class="link-content">
    <div class="link-title">{info['title']}</div>
    <div class="link-desc">{info['description']}</div>
    <div class="link-source">{info['source']}</div>
  </div>
</a>''')
        
        md_content.append('</div>')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    
    print(f"Generated Bookmark Vault:")
    print(f"  - Twitter: {len(twitter_links)} ({total_tweet_pages} pages)")
    print(f"  - Tech: {len(tech_links)}")
    print(f"  - Ignored: {len(unique_links) - len(twitter_links) - len(tech_links)} misc links")

if __name__ == "__main__":
    generate_site()
