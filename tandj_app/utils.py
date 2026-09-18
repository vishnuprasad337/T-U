import html as html_lib
import re
from html.parser import HTMLParser


class _LinkifyParser(HTMLParser):
    """
    Replaces EVERY occurrence of EVERY keyword with an <a> tag,
    matching only real, whole-word phrases — never inside existing <a> tags.
    Longer keywords are tried first so short names don't get matched
    inside longer ones (e.g. "Munnar" inside "Munnar Tea Museum").
    """

    def __init__(self, keyword_url_map):
        super().__init__(convert_charrefs=True)  # decodes &amp; etc. so "T&U" matches correctly
        self.keyword_url_map = dict(keyword_url_map)
        self.a_depth = 0
        self.out = []

        keywords_sorted = sorted(self.keyword_url_map.keys(), key=len, reverse=True)
        pattern = "|".join(r"\b" + re.escape(k) + r"\b" for k in keywords_sorted)
        self._pattern = re.compile(pattern) if pattern else None

    def handle_starttag(self, tag, attrs):
        self.out.append(self.get_starttag_text())
        if tag == "a":
            self.a_depth += 1

    def handle_startendtag(self, tag, attrs):
        self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.out.append(f"</{tag}>")
        if tag == "a" and self.a_depth > 0:
            self.a_depth -= 1

    def handle_data(self, data):
        if self.a_depth > 0 or not self._pattern:
            self.out.append(html_lib.escape(data, quote=False))
            return

        pieces = []
        last_end = 0
        for m in self._pattern.finditer(data):
            keyword = m.group(0)
            url = self.keyword_url_map.get(keyword)
            if url is None:
                continue

            pieces.append(html_lib.escape(data[last_end:m.start()], quote=False))
            pieces.append(f'<a href="{url}">{html_lib.escape(keyword, quote=False)}</a>')
            last_end = m.end()

        pieces.append(html_lib.escape(data[last_end:], quote=False))
        self.out.append("".join(pieces))

    def handle_comment(self, data):
        self.out.append(f"<!--{data}-->")

    def get_html(self):
        return "".join(self.out)


def linkify_description(html, keyword_url_map):
    if not html:
        return html
    parser = _LinkifyParser(keyword_url_map)
    parser.feed(html)
    parser.close()
    return parser.get_html()


def build_destination_keyword_map(nearby_destination_qs, url_builder, min_words=2):
    """
    Builds {destination_name: url} but SKIPS single generic words
    (e.g. a destination literally named "Munnar") so they don't
    get auto-linked every time that word appears in blog text.
    """
    keyword_map = {}
    for dest in nearby_destination_qs:
        name = (dest.name or "").strip()
        if not name:
            continue
        if len(name.split()) < min_words:
            continue  # too generic — skip to avoid false positives
        keyword_map[name] = url_builder(dest.slug)
    return keyword_map