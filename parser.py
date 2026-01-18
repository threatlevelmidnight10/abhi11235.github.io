import re
import os

def classify_link(link):
    """Return category based on URL domain."""
    link_lower = link.lower()
    
    if 'twitter.com' in link_lower or 'x.com' in link_lower:
        return 'twitter'
    
    tech_domains = [
        'github.com', 'stackoverflow.com', 'arxiv.org', 'huggingface.co', 
        'dev.to', 'medium.com', 'hashnode.com', 'kaggle.com', 
        'news.ycombinator.com', 'python.org', 'docs.google.com', 
        'youtube.com', 'youtu.be',
        'linkedin.com/jobs', 'linkedin.com/posts', 'careers'
    ]
    
    for domain in tech_domains:
        if domain in link_lower:
            return 'tech'
            
    return 'misc'

def extract_tweet_info(url):
    """Extract username and tweet ID from URL."""
    # Pattern: twitter.com/username/status/id or x.com/username/status/id
    match = re.search(r'(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)', url)
    if match:
        username = match.group(1)
        tweet_id = match.group(2)
        if username != 'i':  # 'i' is the redirect format, not a real username
            return username, tweet_id
    
    # Fallback: just get the ID
    id_match = re.search(r'/status/(\d+)', url)
    if id_match:
        return None, id_match.group(1)
    
    return None, None

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
    misc_links = []

    for link in unique_links:
        category = classify_link(link)
        if category == 'twitter':
            twitter_links.append(link)
        elif category == 'tech':
            tech_links.append(link)
        else:
            if "whatsapp.com" not in link:
                misc_links.append(link)

    tweets_per_page = 24  # 4x6 grid works well
    total_tweet_pages = (len(twitter_links) + tweets_per_page - 1) // tweets_per_page

    md_content = [
        "---",
        "layout: default",
        "title: Bookmarks",
        "---",
        "",
        "# Link Vault",
        "",
        "---",
        ""
    ]

    # Twitter Section with Card Grid
    if twitter_links:
        md_content.append("## X / Twitter")
        md_content.append("")
        md_content.append(f'<p class="small-text">{len(twitter_links)} saved posts</p>')
        md_content.append("")
        
        # Inline CSS for cards
        md_content.append("""
<style>
.tweet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  padding: 0;
  list-style: none;
}
.tweet-card {
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
}
.tweet-card:hover {
  border-color: #e06e2e;
  box-shadow: 0 2px 8px rgba(224, 110, 46, 0.1);
}
.tweet-card a {
  text-decoration: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.tweet-card .username {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}
.tweet-card .post-label {
  color: #888;
  font-size: 12px;
}
.tweet-card .icon {
  font-size: 18px;
  margin-bottom: 8px;
}
.page-nav { 
  margin: 30px 0; 
  text-align: center; 
}
.page-nav button { 
  background: #fff; 
  border: 1px solid #ddd; 
  padding: 8px 16px; 
  margin: 0 4px; 
  cursor: pointer; 
  border-radius: 4px; 
  font-size: 14px;
}
.page-nav button:hover { 
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
</style>
""")
        
        md_content.append('<div id="twitter-section">')
        
        # Generate pages
        for page_num in range(total_tweet_pages):
            start_idx = page_num * tweets_per_page
            end_idx = min(start_idx + tweets_per_page, len(twitter_links))
            page_tweets = twitter_links[start_idx:end_idx]
            
            active = " active" if page_num == 0 else ""
            md_content.append(f'<div class="tweet-page{active}" data-page="{page_num}">')
            md_content.append('<ul class="tweet-grid">')
            
            for idx, link in enumerate(page_tweets, start=start_idx + 1):
                username, tweet_id = extract_tweet_info(link)
                
                if username:
                    display_name = f"@{username}"
                else:
                    display_name = f"Post #{idx}"
                
                md_content.append(f'''<li class="tweet-card">
  <a href="{link}" target="_blank" rel="noopener">
    <span class="icon">𝕏</span>
    <span class="username">{display_name}</span>
    <span class="post-label">View post →</span>
  </a>
</li>''')
            
            md_content.append('</ul>')
            md_content.append('</div>')
        
        # Pagination controls
        md_content.append('<div class="page-nav" id="page-nav"></div>')
        md_content.append('</div>')
        
        # Pagination JS
        md_content.append(f"""
<script>
(function() {{
  const totalPages = {total_tweet_pages};
  const pages = document.querySelectorAll('.tweet-page');
  const nav = document.getElementById('page-nav');
  let current = 0;
  
  function show(idx) {{
    pages.forEach((p, i) => {{
      p.classList.toggle('active', i === idx);
    }});
    render(idx);
    current = idx;
    document.getElementById('twitter-section').scrollIntoView({{behavior: 'smooth', block: 'start'}});
  }}
  
  function render(idx) {{
    nav.innerHTML = '';
    
    const prev = document.createElement('button');
    prev.textContent = '← Prev';
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

    # Tech Section
    if tech_links:
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append("## Tech & Engineering")
        md_content.append("")
        md_content.append('<ul class="link-list">')
        for link in tech_links:
            # Extract domain for display
            domain = re.search(r'https?://(?:www\.)?([^/]+)', link)
            domain_name = domain.group(1) if domain else link
            md_content.append(f'<li><a href="{link}" target="_blank">{domain_name}</a></li>')
        md_content.append('</ul>')

    # Misc Section
    if misc_links:
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append("## Other Links")
        md_content.append("")
        md_content.append('<ul class="link-list">')
        for link in misc_links:
            domain = re.search(r'https?://(?:www\.)?([^/]+)', link)
            domain_name = domain.group(1) if domain else link
            md_content.append(f'<li><a href="{link}" target="_blank">{domain_name}</a></li>')
        md_content.append('</ul>')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    
    print(f"Generated bookmarks with {len(unique_links)} links:")
    print(f"  - Twitter: {len(twitter_links)} ({total_tweet_pages} pages)")
    print(f"  - Tech: {len(tech_links)}")
    print(f"  - Misc: {len(misc_links)}")

if __name__ == "__main__":
    generate_site()
