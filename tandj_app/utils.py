from html.parser import HTMLParser


class _LinkifyParser(HTMLParser):
    """
    Walks the HTML tag-by-tag using only the stdlib.
    Replaces the FIRST occurrence of each keyword with an <a> tag,
    skipping any text that's already inside an <a>...</a>.
    """

    def __init__(self, keyword_url_map):
        super().__init__(convert_charrefs=False)
        self.keyword_url_map = dict(keyword_url_map)  # keyword -> url
        self.a_depth = 0
        self.out = []

    def handle_starttag(self, tag, attrs):
        self.out.append(self.get_starttag_text())  # preserves original attrs exactly
        if tag == "a":
            self.a_depth += 1

    def handle_startendtag(self, tag, attrs):
        self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.out.append(f"</{tag}>")
        if tag == "a" and self.a_depth > 0:
            self.a_depth -= 1

    def handle_data(self, data):
        if self.a_depth > 0 or not self.keyword_url_map:
            self.out.append(data)
            return

        remaining = data
        used = []
        for keyword, url in self.keyword_url_map.items():
            if keyword in remaining:
                before, _, after = remaining.partition(keyword)
                remaining = f'{before}<a href="{url}">{keyword}</a>{after}'
                used.append(keyword)

        for k in used:
            self.keyword_url_map.pop(k, None)  # only link it once, anywhere in the doc

        self.out.append(remaining)

    def handle_entityref(self, name):
        self.out.append(f"&{name};")

    def handle_charref(self, name):
        self.out.append(f"&#{name};")

    def handle_comment(self, data):
        self.out.append(f"<!--{data}-->")

    def get_html(self):
        return "".join(self.out)


def linkify_description(html, keyword_url_map):
    """
    keyword_url_map: dict like
        {"MaxiMunnar T&U Leisure Hotel": "/", "Top Station": "/our-nearby-destinations/top-station/"}
    """
    if not html:
        return html
    parser = _LinkifyParser(keyword_url_map)
    parser.feed(html)
    parser.close()
    return parser.get_html()