import posixpath
import re
from functools import lru_cache

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

# Matches url(...) that is relative (not data:, http(s):, //, /, or #)
URL_RE = re.compile(r'url\(\s*([\'"]?)(?!data:|https?:|//|/|#)([^\'")]+)\1\s*\)')


def _fix_urls(css, path):
    base = posixpath.dirname(path)

    def repl(m):
        rel = m.group(2)
        clean = rel.split("?")[0].split("#")[0]
        suffix = rel[len(clean):]
        target = posixpath.normpath(posixpath.join(base, clean))
        try:
            return 'url("%s%s")' % (static(target), suffix)
        except Exception:
            return m.group(0)

    return URL_RE.sub(repl, css)


def _read_uncached(path):
    try:
        found = finders.find(path)
        if found:
            with open(found, encoding="utf-8") as f:
                css = f.read()
        else:
            with staticfiles_storage.open(path) as f:
                css = f.read().decode("utf-8")
        return _fix_urls(css, path)
    except Exception:
        return None


_read_cached = lru_cache(maxsize=None)(_read_uncached)


@register.simple_tag
def inline_css(path):
    css = _read_uncached(path) if settings.DEBUG else _read_cached(path)
    # Safe fallback: use a normal <link> if the file can't be read
    if not css or "</style" in css.lower():
        return format_html('<link rel="stylesheet" href="{}">', static(path))
    return format_html("<style>{}</style>", mark_safe(css))