import re
import html

def parse_articles(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        full_text = f.read()

    normalized = full_text.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')

    known_titles = [
        "Barrow Launches 36.1km of Road Projects in Brikama as Connect Gambia Drive Expands",
        "Hadigala College Briefs VP on Expansion, Awards Scholarships to Security Forces",
        "Gambia Hosts ECOWAS Naval Chiefs to Strengthen Regional Maritime Security",
        "VP Jallow Backs Teaching Legacy Summit as Educators Mobilise for Education Transformation",
        "Government, WFP Deepen Partnership on School Feeding",
        "Government Awards Master's Scholarships to 36 Civil Servants",
        "Geological Department Sensitizes The Public on Illegal Sand Mining",
        "Cabinet Secretary Calls for Stronger Accountability and Teamwork at Gender Ministry Retreat",
        "Gov't Revenue Reaches GMD7.68 Billion in First Quarter of 2026",
        "Scouting in The Gambia: Preparing Youth for Climate Action and Future Jobs",
        "North Bank Red Cross Concludes 10-Day Summer Camp in Njaba Kunda",
        "Government Reaffirms Support for Young Entrepreneurs",
        "Efforts to Extend Gambia's Tourism Season Gather Momentum",
        "WAFFEST 2026: A Golden Opportunity for The Gambia",
    ]

    articles = []

    for i, title in enumerate(known_titles):
        pos = normalized.find(title)
        if pos == -1:
            print(f"  WARNING: Could not find title: {title}")
            continue

        if i + 1 < len(known_titles):
            next_pos = normalized.find(known_titles[i + 1])
            if next_pos == -1:
                next_pos = len(normalized)
        else:
            next_pos = len(normalized)

        block = normalized[pos:next_pos].strip()
        block_after_title = block[len(title):].strip()

        author = ''
        body = block_after_title
        by_match = re.match(r'By\s+(.+?)(?:\n|$)', block_after_title)
        if by_match:
            author = by_match.group(1).strip()
            body = block_after_title[by_match.end():].strip()

        articles.append({
            'title': title,
            'author': author,
            'body': body
        })

    return articles

def format_body_html(body):
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
    html_parts = []
    for p in paragraphs:
        p_clean = p.replace('\n', ' ')
        html_parts.append(f'<p>{p_clean}</p>')
    return '\n'.join(html_parts)

def cdata(text):
    return f'<![CDATA[{text}]]>'

def generate_wxr(articles, output_path):
    image_map = {
        "Hadigala College Briefs VP on Expansion, Awards Scholarships to Security Forces": "Hadigala College .jpg",
        "Gambia Hosts ECOWAS Naval Chiefs to Strengthen Regional Maritime Security": "Gambia Hosts ECOWAS .jpg",
        "Government, WFP Deepen Partnership on School Feeding": "Government, WFP.jpg",
        "Government Awards Master's Scholarships to 36 Civil Servants": "Government Awards.jpg",
        "Cabinet Secretary Calls for Stronger Accountability and Teamwork at Gender Ministry Retreat": "Cabinet Secretary .jpg",
        "Gov't Revenue Reaches GMD7.68 Billion in First Quarter of 2026": "Gov't Revenue.jpg",
        "North Bank Red Cross Concludes 10-Day Summer Camp in Njaba Kunda": "North Bank Red.jpg",
        "Efforts to Extend Gambia's Tourism Season Gather Momentum": "Efforts.jpg",
        "WAFFEST 2026: A Golden Opportunity for The Gambia": "WAFFEST 2026.jpg",
    }

    post_id = 100
    items = []
    count = 0

    for article in articles:
        if 'Barrow Launches' in article['title']:
            print(f"  [SKIPPED] {article['title']}")
            continue

        post_id += 1
        count += 1
        content_html = format_body_html(article['body'])
        author_text = article['author'] if article['author'] else 'admin'

        item = f'''    <item>
        <title>{cdata(article["title"])}</title>
        <link></link>
        <pubDate>Tue, 20 Aug 2026 10:00:00 +0000</pubDate>
        <dc:creator>{cdata(author_text)}</dc:creator>
        <guid isPermaLink="false"></guid>
        <description></description>
        <content:encoded>{cdata(content_html)}</content:encoded>
        <wp:post_id>{post_id}</wp:post_id>
        <wp:post_date><![CDATA[2026-08-20 10:00:00]]></wp:post_date>
        <wp:post_date_gmt><![CDATA[2026-08-20 10:00:00]]></wp:post_date_gmt>
        <wp:post_name><![CDATA[]]></wp:post_name>
        <wp:status><![CDATA[publish]]></wp:status>
        <wp:post_parent>0</wp:post_parent>
        <wp:menu_order>0</wp:menu_order>
        <wp:post_type><![CDATA[post]]></wp:post_type>
        <wp:post_password><![CDATA[]]></wp:post_password>
        <wp:is_sticky>0</wp:is_sticky>
        <category domain="category" nicename="news">{cdata("News")}</category>
    </item>'''
        items.append(item)

    items_xml = '\n'.join(items)

    wxr = f'''<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.2/"
>
<channel>
    <title>Web Stories Edition 60</title>
    <link></link>
    <description></description>
    <wp:wxr_version>1.2</wp:wxr_version>
    <wp:base_site_url></wp:base_site_url>
    <wp:base_blog_url></wp:base_blog_url>
    <wp:author>
        <wp:author_id>1</wp:author_id>
        <wp:author_login><![CDATA[admin]]></wp:author_login>
    </wp:author>
{items_xml}
</channel>
</rss>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(wxr)

    print(f"\nGenerated WXR file: {output_path}")
    print(f"Total posts: {count}")

    print("\nPosts and image assignments:")
    for article in articles:
        if 'Barrow Launches' in article['title']:
            continue
        img = image_map.get(article['title'], '')
        print(f"  - {article['title'][:70]} -> {img if img else '(no image)'}")

if __name__ == '__main__':
    input_file = r'C:\Users\maste\Desktop\DOI\Website\Web stories Edition 60\Web stories Edition 60\Stories.txt'
    output_file = r'C:\Users\maste\Documents\Default Project\wordpress_import.xml'
    articles = parse_articles(input_file)
    generate_wxr(articles, output_file)
