from .models import Blog, Testimonial, Category, GalleryImage
from django import forms


# --------- Blog Form ---------
class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["image", "title", "description"]


# --------- Testimonial Form ---------
class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ["name", "image", "review", "rating"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class GalleryImageForm(forms.ModelForm):  # no need
    class Meta:
        model = GalleryImage
        fields = ["category", "title", "image"]


 
from .models import Room, RoomImage


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            "room_category",
            "description",
            "price_per_night",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price_per_night"].required = False
# --------- Multiple Gallery Images for a Room ---------

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, "getlist"):
            return files.getlist(name)
        return files.get(name)


class MultipleFileField(forms.FileField):
    """
    Django's FileField only cleans a single file by default.
    This subclass makes it accept and validate a list of files
    from a <input type="file" multiple> field.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class RoomImageForm(forms.Form):
    room_images = MultipleFileField(required=False)

    def clean_room_images(self):
        files = self.cleaned_data.get("room_images")
        if files:
            for f in files:
                if not f.content_type.startswith("image/"):
                    raise forms.ValidationError(f"'{f.name}' is not a valid image file.")
                if f.size > 5 * 1024 * 1024:
                    raise forms.ValidationError(f"'{f.name}' exceeds the 5MB size limit.")
        return files


from django.forms import inlineformset_factory
from .models import Activity, ActivityImage


from .models import Activity, ActivityImage


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["name", "description"]
        # image is no longer a form field — it's set programmatically
        # from the first file in activity_images (see views.py)
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


class ActivityGalleryUploadForm(forms.Form):
    """Single multi-file field. The FIRST file becomes Activity.image
    (the cover image); any additional files become ActivityImage gallery rows."""
    activity_images = MultipleFileField(required=False)

    def clean_activity_images(self):
        files = self.cleaned_data.get("activity_images")
        if files:
            for f in files:
                if not f.content_type.startswith("image/"):
                    raise forms.ValidationError(f"'{f.name}' is not a valid image file.")
                if f.size > 5 * 1024 * 1024:  # 5MB limit
                    raise forms.ValidationError(f"'{f.name}' exceeds the 5MB size limit.")
        return files
from .models import NearbyDestination, NearbyDestinationImage


class NearbyDestinationForm(forms.ModelForm):
    class Meta:
        model = NearbyDestination
        fields = [
            "name",
            "description",
            "distance",
            # image is no longer a form field — one file from
            # destination_images is picked at random in the view and
            # becomes NearbyDestination.image (the cover/hero image).
            # status and location are intentionally excluded from the form.
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "distance": forms.TextInput(attrs={"class": "form-control"}),
        }


class NearbyDestinationGalleryUploadForm(forms.Form):
    """Single multi-file field. One randomly chosen file becomes
    NearbyDestination.image (the cover/hero image); the rest become
    NearbyDestinationImage gallery rows."""
    destination_images = MultipleFileField(required=False)

    def clean_destination_images(self):
        files = self.cleaned_data.get("destination_images")
        if files:
            for f in files:
                if not f.content_type.startswith("image/"):
                    raise forms.ValidationError(f"'{f.name}' is not a valid image file.")
                if f.size > 5 * 1024 * 1024:  # 5MB limit
                    raise forms.ValidationError(f"'{f.name}' exceeds the 5MB size limit.")
        return files
import re



from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            "guest_name", "guest_email", "guest_phone",
             "check_in", "check_out",
            "num_guests", "special_requests",
        ]
        widgets = {
            "guest_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter full name"}),
            "guest_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
            "guest_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 9876543210"}),
            
            "check_in": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "check_out": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "num_guests": forms.NumberInput(attrs={"class": "form-control", "min": 1, "placeholder": "Number of guests"}),
            "special_requests": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Any special requests (optional)"}),
        }
from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    """Public-facing form matching the fields in the enquiry widget:
    First Name, Last Name, Phone Number, Email Address, Send Message."""

    class Meta:
        model = Contact
        fields = ["first_name", "last_name", "phone_number", "email", "message"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First Name", "class": "form-control"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name", "class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "Phone Number", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email Address", "class": "form-control"}),
            "message": forms.Textarea(attrs={"placeholder": "Send Message", "class": "form-control", "rows": 5}),
        }


class ReplyForm(forms.Form):
    """Admin/staff-facing form used to reply to an enquiry.
    Submitting this sends an email directly to the enquirer's email address."""

    reply_message = forms.CharField(
        label="Reply",
        widget=forms.Textarea(attrs={"rows": 6, "class": "form-control", "placeholder": "Type your reply..."}),
    )