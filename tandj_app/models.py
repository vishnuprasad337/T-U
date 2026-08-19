from django.db import models
from django.utils.text import slugify
# Create your models here.


from django.db import models
from PIL import Image, ImageOps
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.image_optimizer import optimize_image, optimize_flag
from django.utils.text import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

class OptimizedImageModel(models.Model):
    """
    Base class: any model inheriting this can declare image_fields = []
    to auto-optimize images on save.
    """

    image_fields = []  # override in child models

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Optimize all declared image fields
        for field in self.image_fields:
            image_field = getattr(self, field, None)
            if image_field and hasattr(image_field, "path"):
                optimize_image(image_field.path)


# --------- Blogs ---------
class Blog(OptimizedImageModel):
    image = models.ImageField(upload_to="blogs/", help_text="Blog cover image")
    slug = models.SlugField(unique=True, blank=True, null=True)
    title = models.CharField(max_length=200, help_text="Blog title")
    description = models.TextField(help_text="Blog description")
    created_at = models.DateTimeField(auto_now_add=True)

    # Tell base model which images to optimize
    image_fields = ["image"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Strip any accidental HTML tags from plain-text fields only.
        # description is intentionally NOT stripped — it holds CKEditor's
        # rich HTML (headings, paragraphs, bold, lists, etc.) and stripping
        # it here would silently delete all formatting on every save.
        if self.title:
            self.title = strip_tags(self.title).strip()

        if not self.slug:
            base_slug = slugify(self.title or "blog")
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

# ---------Testimonials ---------
class Testimonial(OptimizedImageModel):
    name = models.CharField(
        max_length=100, help_text="Name of the person giving the testimonial"
    )
    image = models.ImageField(
        upload_to="testimonials/", blank=True, null=True, help_text="Profile picture"
    )
    review = models.TextField(help_text="Customer or client review")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating out of 5 stars",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Tell base model which images to optimize
    image_fields = ["image"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.name} ({self.rating}⭐)"

    def save(self, *args, **kwargs):
        # review is plain text (not CKEditor) in the current admin form,
        # so stripping tags here is intentional. If review is ever switched
        # to a rich-text editor, remove the strip_tags call on it, same as
        # was done for description fields below.
        if self.review:
            self.review = strip_tags(self.review).strip()
        if self.name:
            self.name = strip_tags(self.name).strip()
        super().save(*args, **kwargs)



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
class GalleryImage(OptimizedImageModel):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="images"
    )
    title = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to="gallery/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Tell base model which images to optimize
    image_fields = ["image"]

    def __str__(self):
        return self.title if self.title else f"Image {self.id}"



class Room(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    slug = models.SlugField(max_length=170, unique=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )
    room_category = models.CharField(
        max_length=100, blank=True
    )

    bedroom_beds = models.CharField(
        max_length=255, blank=True
    )
    living_room_beds = models.CharField(
        max_length=255, blank=True
    )

    rating_average = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )

    description = models.TextField(blank=True)

    price_per_night = models.DecimalField(
    max_digits=10, decimal_places=2,
    blank=True, null=True,
)

    main_image = models.ImageField(upload_to="rooms/main/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rooms"

    def __str__(self):
        return f"{self.room_category or 'Room'} #{self.pk} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.room_category:
            self.room_category = strip_tags(self.room_category).strip()
        # description holds CKEditor's rich HTML (headings, paragraphs,
        # bold, lists, etc.) — do NOT strip_tags it, or all formatting
        # collapses into plain text on every save.
        if not self.slug:
            base_slug = slugify(self.room_category or "room")
            slug = base_slug
            counter = 1
            while Room.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class RoomImage(OptimizedImageModel):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="rooms/gallery/")
    caption = models.CharField(max_length=150, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Tell base model which images to optimize
    image_fields = ["image"]

    class Meta:
        ordering = ["order", "uploaded_at"]

    def __str__(self):
        return f"Image for {self.room.room_category or 'Room'} ({self.id})"


class Activity(OptimizedImageModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    slug = models.SlugField(max_length=170, unique=True, blank=True)
    name = models.CharField(max_length=200, help_text="Activity name")
    description = models.TextField(help_text="Activity description")
    image = models.ImageField(upload_to="activities/", help_text="Main activity image")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )
    duration = models.CharField(
        max_length=100, blank=True, help_text="e.g. '2 hours', 'Half day'"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    location = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image_fields = ["image"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = strip_tags(self.name).strip()
        # description holds CKEditor's rich HTML — do NOT strip_tags it,
        # or headings/formatting collapse into plain text on every save.
        if self.location:
            self.location = strip_tags(self.location).strip()
        if not self.slug:
            base_slug = slugify(self.name or "activity")
            slug = base_slug
            counter = 1
            while Activity.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class ActivityImage(OptimizedImageModel):
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="activities/gallery/")
    caption = models.CharField(max_length=150, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Tell base model which images to optimize
    image_fields = ["image"]

    class Meta:
        ordering = ["order", "uploaded_at"]

    def __str__(self):
        return f"Image for {self.activity.name} ({self.id})"


class NearbyDestination(OptimizedImageModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    slug = models.SlugField(max_length=170, unique=True, blank=True)
    name = models.CharField(max_length=200, help_text="Destination name")
    description = models.TextField(help_text="Destination description")
    image = models.ImageField(
        upload_to="nearby_destinations/", help_text="Main destination image"
    )
    distance = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. '5 km', '20 mins drive'",
    )
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image_fields = ["image"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Nearby Destination"
        verbose_name_plural = "Nearby Destinations"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # name/description are left as-is here (consistent with the
        # original file — description is CKEditor rich HTML and must
        # never be run through strip_tags).
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while (
                NearbyDestination.objects.filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class NearbyDestinationImage(OptimizedImageModel):
    destination = models.ForeignKey(
        NearbyDestination, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="nearby_destinations/gallery/")
    caption = models.CharField(max_length=150, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    image_fields = ["image"]

    class Meta:
        ordering = ["order", "uploaded_at"]

    def __str__(self):
        return f"Image for {self.destination.name} ({self.id})"


class Reservation(OptimizedImageModel):
    # Guest details
    guest_name = models.CharField(max_length=150)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=30, blank=True)
    num_guests = models.PositiveIntegerField(default=1)

    # What they're booking (optional — general inquiry if left blank)
    room = models.ForeignKey(
        "Room",
        on_delete=models.SET_NULL,
        related_name="reservations",
        null=True,
        blank=True,
        help_text="Leave blank for a general inquiry not tied to a specific room.",
    )

    # Dates
    check_in = models.DateField()
    check_out = models.DateField()

    special_requests = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image_fields = []

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"

    def __str__(self):
        target = self.room.room_category if self.room else "General Inquiry"
        return f"{self.guest_name} — {target} ({self.check_in} to {self.check_out})"

    


class Contact(models.Model):
    """Stores a single contact-form enquiry submitted by a site visitor."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Enquiry"
        verbose_name_plural = "Contact Enquiries"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"