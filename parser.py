import re
import os

def generate_site():
    input_file = './cht_history/_chat180626.txt'
    output_file = 'bookmarks.md'
    
    # Updated regex: captures Twitter/X and general web links
    url_pattern = r'https?://\S+'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all links and remove trailing punctuation often found in WhatsApp exports
    raw_links = re.findall(url_pattern, content)
    unique_links = list(dict.fromkeys([link.strip(',').strip(')') for link in raw_links]))

    # Jekyll Setup
    md_content = [
        "---",
        "layout: default",
        "title: My Personal Link Vault",
        "---",
        "# 📚 Link Vault",
        "Generated from WhatsApp exports. [cite: 85, 87]",
        '<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>',
        "",
        "## 🐦 X / Twitter Posts"
    ]

    twitter_links = []
    other_links = []

    for link in unique_links:
        if 'twitter.com' in link or 'x.com' in link:
            twitter_links.append(link)
        else:
            # Filter out known non-content links like WhatsApp's internal learn more 
            if "whatsapp.com" not in link:
                other_links.append(link)

    # Render Twitter links as embeds
    for link in twitter_links:
        md_content.append(f'<blockquote class="twitter-tweet"><a href="{link}"></a></blockquote>')

    md_content.append("\n---\n## 🔗 Other Bookmarks")
    
    # Render other links as a clean list
    for link in other_links:
        md_content.append(f"* [{link}]({link})")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    print(f"Site updated with {len(unique_links)} total links.")

if __name__ == "__main__":
    generate_site()
