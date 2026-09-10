"""
URL configuration for Tandu Leisure Hotel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse

from tandj_app.sitemaps import (
    StaticViewSitemap,
    RoomSitemap,
    ActivitySitemap,
    NearbyDestinationSitemap,
    BlogSitemap,
)

sitemaps = {
    "static": StaticViewSitemap,
    "rooms": RoomSitemap,
    "activities": ActivitySitemap,
    "nearby_destinations": NearbyDestinationSitemap,
    "blog": BlogSitemap,
}


def robots_txt(request):
    """Serve robots.txt for search engine crawlers"""
    content = """User-agent: *
Disallow: /login/
Disallow: /dashboard/
Disallow: /admin-logout/
Disallow: /blogs/
Disallow: /testimonials/
Disallow: /add-review
Disallow: /categories/
Disallow: /list-images/
Disallow: /add_image/
Disallow: /delete-image/
Disallow: /rooms/
Disallow: /activities/
Disallow: /nearby-destinations/
Disallow: /reservations/
Disallow: /enquiries/
Disallow: /contact/
Disallow: /media/private/
Allow: /static/
Allow: /

Sitemap: https://tanduleisurehotel.in/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    # SEO
    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    
    # App URLs
    path('', include('tandj_app.urls')),
]

# Media files (user uploads)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static files (only in DEBUG mode for development)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom 404 handler
handler404 = "tandj_app.views.page_404"