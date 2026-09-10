from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Blog, Room, Activity, NearbyDestination


class TanduLeisureSitemap(Sitemap):
    """Base sitemap class for Tandu Leisure Hotel"""
    protocol = "https"

    def get_domain(self, site=None):
        return "tanduleisurehotel.in"


# --------- Static Pages ---------
class StaticViewSitemap(TanduLeisureSitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return [
            "tandj_app:index",
            "tandj_app:about",
            "tandj_app:rooms",
            "tandj_app:activities",
            "tandj_app:blogs",
            "tandj_app:contact",
            "tandj_app:gallery_public",
            "tandj_app:nearby_destinations",
            "tandj_app:restaurant",
        ]

    def location(self, item):
        return reverse(item)


# --------- Rooms ---------
class RoomSitemap(TanduLeisureSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Room.objects.filter(status="active")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("tandj_app:room_detail_public", kwargs={"slug": obj.slug})


# --------- Activities ---------
class ActivitySitemap(TanduLeisureSitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Activity.objects.filter(status="active")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("tandj_app:activity_detail_public", kwargs={"slug": obj.slug})


# --------- Nearby Destinations ---------
class NearbyDestinationSitemap(TanduLeisureSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return NearbyDestination.objects.filter(status="active")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse(
            "tandj_app:nearby_destination_detail_public", kwargs={"slug": obj.slug}
        )


# --------- Blog ---------
class BlogSitemap(TanduLeisureSitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Blog.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse("tandj_app:blog_detail_public", kwargs={"slug": obj.slug})