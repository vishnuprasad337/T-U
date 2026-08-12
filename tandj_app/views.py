from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import BlogForm,TestimonialForm,CategoryForm,GalleryImageForm,RoomForm
from .models import Blog,Testimonial,Category,GalleryImage,Room
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.db.models.functions import Lower
from django.conf import settings
from django.core.mail import send_mail
# --------- admin-authentication ---------
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Both fields are required.")
            return render(request, "authenticate/login.html")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # only staff users
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            print("login sucesfull")
            return redirect("tandj_app:dashboard")  # change this to your dashboard URL
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, "authenticate/login.html")


def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("tandj_app:admin_login")
# --------- admin-dashboard ---------
from django.db.models.functions import TruncMonth
from django.db.models import Count

@login_required
def admin_dashboard(request):
    # --- KPI Cards ---
    
    bookings_count = Reservation.objects.count()
    enquiries_count = Contact.objects.count()
    rooms_count = Room.objects.count()

    stats = {
       
        "bookings_count": bookings_count,
        "enquiries_count": enquiries_count,
        "rooms_count": rooms_count,
    }

    # --- Recent Bookings (Reservations) ---
    recent_bookings = Reservation.objects.order_by("-created_at")[:5]

    # --- Latest Enquiries (Contact) ---
    recent_enquiries = Contact.objects.order_by("-created_at")[:5]

    # --- Recently Added Rooms ---
    recent_rooms = Room.objects.order_by("-created_at")[:5]

    # --- Monthly Bookings chart data ---
    monthly_bookings = (
        Reservation.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    bookings_labels = [m["month"].strftime("%b") for m in monthly_bookings]
    bookings_counts = [m["count"] for m in monthly_bookings]

    # --- Monthly Testimonials chart data ---
    monthly_testimonials = (
        Testimonial.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    testimonials_labels = [m["month"].strftime("%b") for m in monthly_testimonials]
    testimonials_counts = [m["count"] for m in monthly_testimonials]

    return render(request, "admin_pages/admin-dashboard.html", {
        "stats": stats,
        "recent_bookings": recent_bookings,
        "recent_enquiries": recent_enquiries,
        "recent_rooms": recent_rooms,
        "bookings_labels": bookings_labels,
        "bookings_counts": bookings_counts,
        "testimonials_labels": testimonials_labels,
        "testimonials_counts": testimonials_counts,
    })




# --------- Blogs ---------
@login_required
def blog_list(request):
    blogs_qs = Blog.objects.all().order_by("title")  # newest first

    paginator = Paginator(blogs_qs, 6)
    page_number = request.GET.get("page")
    blogs = paginator.get_page(page_number)  # gives a Page object

    return render(request, "admin_pages/blog_list.html", {"blogs": blogs})


@login_required
def blog_create(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog added successfully!")
            return redirect("tandj_app:blog_list")
    else:
        form = BlogForm()
    return render(request, "admin_pages/create_blog.html", {"form": form})


@login_required
def blog_update(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog updated successfully!")
            return redirect("tandj_app:blog_list")
    else:
        form = BlogForm(instance=blog)
    return render(request, "admin_pages/create_blog.html", {"form": form, "blog": blog})


@login_required
def blog_delete(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted successfully!")
        return redirect("tandj_app:blog_list")
    return render(request, "admin_pages/create_blog.html", {"blog": blog})

# --------- Testimonial ---------
login_required
def testimonial_list(request):
    testimonials_list = Testimonial.objects.all().order_by(Lower("name"))
    paginator = Paginator(testimonials_list, 6)
    page_number = request.GET.get("page")
    testimonials = paginator.get_page(page_number)

    return render(
        request, "admin_pages/review_list.html", {"testimonials": testimonials}
    )


login_required
def testimonial_create(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial added successfully!")
            return redirect("tandj_app:testimonial_list")
    else:
        form = TestimonialForm()
    return render(request, "admin_pages/create_review.html", {"form": form})


login_required
def testimonial_update(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial updated successfully!")
            return redirect("tandj_app:testimonial_list")
    else:
        form = TestimonialForm(instance=testimonial)
    return render(
        request,
        "admin_pages/review_list.html",
        {"form": form, "testimonial": testimonial},
    )

login_required
def testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        testimonial.delete()
        messages.success(request, "Testimonial deleted successfully!")
        return redirect("tandj_app:testimonial_list")
    return render(request, "admin_pages/review_list.html", {"testimonial": testimonial})


# --------- Catergories and gallery ---------

login_required
def category_list(request):
    categories = Category.objects.all().order_by("-created_at")
    paginator = Paginator(categories, 10)
    page_number = request.GET.get("page")
    categories = paginator.get_page(page_number)
    return render(request, "admin_pages/category_list.html", {"categories": categories})


login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            return redirect("tandj_app:category_list")  
    return render(request, "admin_pages/add_category.html")


login_required
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.name = request.POST.get("name")
        category.save()
        return redirect("tandj_app:category_list")  
    return redirect("tandj_app:category_list")        


login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect("tandj_app:category_list")   
    return redirect("tandj_app:category_list")      


login_required
def gallery_images(request):
    categories = Category.objects.all().prefetch_related("images")

    category_pages = {}
    for category in categories:
        images_qs = category.images.all().order_by("-uploaded_at")
        paginator = Paginator(images_qs, 8)  # 8 images per page
        page_number = request.GET.get(f"page_{category.id}", 1)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        category_pages[category.id] = page_obj

    return render(
        request,
        "admin_pages/image_list.html",
        {
            "categories": categories,
            "category_pages": category_pages,
        },
    )


@login_required
def add_image(request):
    categories = Category.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        category = Category.objects.get(id=category_id)
        files = request.FILES.getlist("images")
        print("FILES:", request.FILES)  # Should show uploaded files
        print("FILES count:", len(request.FILES.getlist("images")))

        for file in files:
            GalleryImage.objects.create(
                category=category,
                title=file.name,  # default title = filename
                image=file,
            )
        messages.success(request, "Images uploaded succesfully")
        return redirect("tandj_app:list_image")
    return render(request, "admin_pages/add_image.html", {"categories": categories})

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id)

    if request.method == "POST":
        image.delete()
        messages.success(request, "Image deleted successfully")
        return redirect("tandj_app:list_image")

    return render(request, "admin_pages/image_list.html", {"image": image})

# --------- Room management ---------






@login_required
def room_list(request):
    rooms = Room.objects.all().order_by("-created_at")
    return render(request, "admin_pages/room_list.html", {"rooms": rooms})

@login_required
def room_detail(request, slug):
    room = get_object_or_404(Room, slug=slug)
    return render(request, "admin_pages/room_detail.html", {"room": room})


from .forms import RoomForm, RoomImageForm
from .models import Room, RoomImage


@login_required
def room_add(request):
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES)
        image_form = RoomImageForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            files = image_form.cleaned_data.get("room_images") or []
            if not files:
                messages.error(request, "Please upload at least one image.")
                return render(request, "admin_pages/room_form.html",
                              {"form": form, "image_form": image_form, "action": "Add"})

            room = form.save(commit=False)
            room.main_image = files[0]
            room.save()

            for order, f in enumerate(files[1:], start=1):
                RoomImage.objects.create(room=room, image=f, order=order)

            messages.success(request, "Room added successfully.")
            return redirect("tandj_app:room_detail", slug=room.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RoomForm()
        image_form = RoomImageForm()

    return render(
        request,
        "admin_pages/room_form.html",
        {"form": form, "image_form": image_form, "action": "Add"},
    )

from django.db.models import Max
@login_required
def room_edit(request, slug):
    room = get_object_or_404(Room, slug=slug)

    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES, instance=room)
        image_form = RoomImageForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            room = form.save(commit=False)

            files = image_form.cleaned_data.get("room_images") or []
            if files:
                # first newly-picked image replaces the cover; rest go to gallery
                room.main_image = files[0]

            room.save()

            if len(files) > 1:
                last_order = room.images.aggregate(Max("order"))["order__max"] or 0
                for i, f in enumerate(files[1:], start=1):
                    RoomImage.objects.create(room=room, image=f, order=last_order + i)

            delete_ids = request.POST.getlist("delete_images")
            if delete_ids:
                RoomImage.objects.filter(id__in=delete_ids, room=room).delete()

            messages.success(request, "Room updated successfully.")
            return redirect("tandj_app:room_detail", slug=room.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RoomForm(instance=room)
        image_form = RoomImageForm()

    return render(
        request,
        "admin_pages/room_form.html",
        {"form": form, "image_form": image_form, "action": "Edit", "room": room},
    )

@login_required
def room_delete(request, slug):
    room = get_object_or_404(Room, slug=slug)

    if request.method == "POST":
        room.delete()
        messages.success(request, "Room deleted successfully.")
        return redirect("tandj_app:room_list")

    return render(request, "admin_pages/room_confirm_delete.html", {"room": room})



# --------- Activity management ---------


from .models import Activity
from .forms import ActivityForm

@login_required
def activity_list(request):
    activities = Activity.objects.all()
    paginator = Paginator(activities, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "admin_pages/activity_list.html",
        {"activities": page_obj, "page_obj": page_obj},
    )
@login_required

def activity_detail(request, slug):
    activity = get_object_or_404(Activity, slug=slug)
    return render(request, "admin_pages/activity_detail.html", {"activity": activity})

from .forms import ActivityForm, ActivityGalleryUploadForm
from .models import ActivityImage
@login_required
def activity_create(request):
    if request.method == "POST":
        form = ActivityForm(request.POST, request.FILES)
        gallery_form = ActivityGalleryUploadForm(request.POST, request.FILES)

        if form.is_valid() and gallery_form.is_valid():
            files = gallery_form.cleaned_data.get("activity_images") or []
            if not files:
                messages.error(request, "Please upload at least one image.")
                return render(request, "admin_pages/activity_form.html",
                              {"form": form, "gallery_form": gallery_form, "is_edit": False})

            activity = form.save(commit=False)
            activity.image = files[0]
            activity.save()

            for order, f in enumerate(files[1:], start=1):
                ActivityImage.objects.create(activity=activity, image=f, order=order)

            messages.success(request, "Activity created successfully.")
            return redirect("tandj_app:activity_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ActivityForm()
        gallery_form = ActivityGalleryUploadForm()

    return render(
        request,
        "admin_pages/activity_form.html",
        {"form": form, "gallery_form": gallery_form, "is_edit": False},
    )


@login_required
def activity_update(request, slug):
    activity = get_object_or_404(Activity, slug=slug)

    if request.method == "POST":
        form = ActivityForm(request.POST, request.FILES, instance=activity)
        gallery_form = ActivityGalleryUploadForm(request.POST, request.FILES)

        if form.is_valid() and gallery_form.is_valid():
            activity = form.save(commit=False)

            files = gallery_form.cleaned_data.get("activity_images") or []
            if files:
                # first newly-picked image replaces the cover; rest go to gallery
                activity.image = files[0]

            activity.save()

            if len(files) > 1:
                last_order = activity.images.aggregate(Max("order"))["order__max"] or 0
                for i, f in enumerate(files[1:], start=1):
                    ActivityImage.objects.create(activity=activity, image=f, order=last_order + i)

            # Remove any existing gallery images the admin checked "Remove" on
            for img in activity.images.all():
                if request.POST.get(f"delete_image_{img.id}"):
                    img.delete()

            messages.success(request, "Activity updated successfully.")
            return redirect("tandj_app:activity_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ActivityForm(instance=activity)
        gallery_form = ActivityGalleryUploadForm()

    return render(
        request,
        "admin_pages/activity_form.html",
        {"form": form, "gallery_form": gallery_form, "is_edit": True, "activity": activity},
    
    )
@login_required
def activity_delete(request, slug):
    activity = get_object_or_404(Activity, slug=slug)
    if request.method == "POST":
        activity.delete()
        messages.success(request, "Activity deleted successfully.")
    return redirect("tandj_app:activity_list")


# --------- Nearest destinamtion ---------

import random

from .models import NearbyDestination
from .models import NearbyDestination, NearbyDestinationImage
from .forms import NearbyDestinationForm, NearbyDestinationGalleryUploadForm


def _apply_random_cover(destination, files):
    """
    Given a NearbyDestination instance and a list of freshly uploaded
    files, pick one at random to become the cover (hero) image and
    save the rest as NearbyDestinationImage gallery rows.

    Any new upload replaces the existing cover image (the old cover is
    NOT kept), since the whole point is "a random one becomes the hero".
    """
    if not files:
        return

    files = list(files)
    cover = random.choice(files)
    files.remove(cover)

    destination.image = cover
    destination.save()

    for f in files:
        NearbyDestinationImage.objects.create(destination=destination, image=f)


@login_required
def nearby_destination_list(request):
    destinations = NearbyDestination.objects.all()
    paginator = Paginator(destinations, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "admin_pages/nearby_destination_list.html",
        {"destinations": page_obj, "page_obj": page_obj},
    )


@login_required
def nearby_destination_detail(request, slug):
    destination = get_object_or_404(NearbyDestination, slug=slug)
    return render(
        request,
        "admin_pages/nearby_destination_detail.html",
        {"destination": destination},
    )


@login_required
def nearby_destination_create(request):
    if request.method == "POST":
        form = NearbyDestinationForm(request.POST, request.FILES)
        gallery_form = NearbyDestinationGalleryUploadForm(request.POST, request.FILES)

        if form.is_valid() and gallery_form.is_valid():
            new_files = gallery_form.cleaned_data.get("destination_images") or []

            if not new_files:
                # image is required on the model — creation needs at
                # least one uploaded file to become the cover image.
                messages.error(request, "Please upload at least one image.")
                return render(request, "admin_pages/nearby_destination_form.html", {
                    "form": form, "gallery_form": gallery_form, "action": "Add",
                })

            destination = form.save(commit=False)
            _apply_random_cover(destination, new_files)

            messages.success(request, "Nearby destination created successfully.")
            return redirect("tandj_app:nearby_destination_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = NearbyDestinationForm()
        gallery_form = NearbyDestinationGalleryUploadForm()

    return render(request, "admin_pages/nearby_destination_form.html", {
        "form": form, "gallery_form": gallery_form, "action": "Add",
    })


@login_required
def nearby_destination_update(request, slug):
    destination = get_object_or_404(NearbyDestination, slug=slug)

    if request.method == "POST":
        form = NearbyDestinationForm(request.POST, request.FILES, instance=destination)
        gallery_form = NearbyDestinationGalleryUploadForm(request.POST, request.FILES)

        if form.is_valid() and gallery_form.is_valid():
            form.save()

            # Remove any existing gallery images the admin checked "Remove" on
            for img in destination.images.all():
                if request.POST.get(f"delete_image_{img.id}"):
                    img.delete()

            # If new images were uploaded, one random one replaces the
            # cover image; the rest are added to the gallery.
            new_files = gallery_form.cleaned_data.get("destination_images") or []
            _apply_random_cover(destination, new_files)

            messages.success(request, "Nearby destination updated successfully.")
            return redirect("tandj_app:nearby_destination_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = NearbyDestinationForm(instance=destination)
        gallery_form = NearbyDestinationGalleryUploadForm()

    return render(request, "admin_pages/nearby_destination_form.html", {
        "form": form, "gallery_form": gallery_form, "action": "Edit", "destination": destination,
    })


@login_required
def nearby_destination_delete(request, slug):
    destination = get_object_or_404(NearbyDestination, slug=slug)
    if request.method == "POST":
        destination.delete()
        messages.success(request, "Nearby destination deleted successfully.")
    return redirect("tandj_app:nearby_destination_list")



# --------- Reservation ---------

from .models import Reservation
from .forms import ReservationForm


# --------- Public / Customer-facing ---------

def reservation_create(request):
    """Customers book a reservation from the public site."""
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your reservation request has been submitted!")
            return redirect("tandj_app:reservation_list")
    else:
        form = ReservationForm()

    return render(request, "admin_pages/reservation_form_public.html", {
        "form": form,
        "title": "Book a Reservation",
    })


# --------- Admin / Staff-facing (list + delete only) ---------
from .forms import ReservationForm

@login_required
def reservation_list(request):
    reservations = Reservation.objects.select_related("package").all()
    form = ReservationForm()
    return render(request, "admin_pages/reservation_list.html", {
        "reservations": reservations,
        "form": form,
    })

@login_required
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == "POST":
        reservation.delete()
        messages.success(request, "Reservation deleted.")
    return redirect("tandj_app:reservation_list")


# --------- Contacts---------

from .models import Contact
from .forms import ContactForm, ReplyForm
 
 
# ---------------------------------------------------------------------
# PUBLIC VIEW — visitor submits the contact form (CREATE)
def contact_view(request):
    """Handles new contact enquiry submissions from the Add Contact modal."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been received.")
            return redirect("tandj_app:home")
        else:
            messages.error(request, "Please correct the errors and try again.")
            return enquiry_list(request, add_form=form)
    return redirect("tandj_app:home")
 
# ---------------------------------------------------------------------
# STAFF VIEW — everything (list, reply, edit, delete) happens on ONE page
# via Bootstrap modals. Only enquiry_list renders a template; the rest
# just process POSTs and redirect back to the list.
# ---------------------------------------------------------------------

def enquiry_list(request, add_form=None):
    """Renders the list of contact enquiries, with an Add Contact modal."""
    enquiries = Contact.objects.all().order_by("-created_at")

    if add_form is None:
        add_form = ContactForm()

    return render(request, "admin_pages/enquiry_list.html", {
        "enquiries": enquiries,
        "add_form": add_form,
    })
 
@login_required
def enquiry_reply(request, pk):
    """Handles the Reply modal submit. Emails the enquirer directly
    (the 'email' field is the only field used as the send-to address)."""
    enquiry = get_object_or_404(Contact, pk=pk)
 
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply_text = form.cleaned_data["reply_message"]
            send_mail(
                subject="Re: Your enquiry to Ambady Estate",
                message=reply_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[enquiry.email],  # <-- reply goes only to the enquirer's email field
                fail_silently=False,
            )
            messages.success(request, f"Reply sent to {enquiry.email}.")
        else:
            messages.error(request, "Could not send reply — please enter a message.")
 
    return redirect("tandj_app:enquiry_list")
 
 
@login_required
def enquiry_update(request, pk):
    """Handles the Edit modal submit."""
    enquiry = get_object_or_404(Contact, pk=pk)
 
    if request.method == "POST":
        form = ContactForm(request.POST, instance=enquiry)
        if form.is_valid():
            form.save()
            messages.success(request, "Enquiry updated.")
        else:
            messages.error(request, "Could not update enquiry — please check the fields.")
 
    return redirect("tandj_app:enquiry_list")
 
 
@login_required
def enquiry_delete(request, pk):
    """Handles the Delete-confirm modal submit."""
    enquiry = get_object_or_404(Contact, pk=pk)
 
    if request.method == "POST":
        enquiry.delete()
        messages.success(request, "Enquiry deleted.")
 
    return redirect("tandj_app:enquiry_list")


from django.shortcuts import render
from .models import Room

from django.shortcuts import render
from .models import Room

def index(request):
    # Fetch rooms without status filter
    rooms = Room.objects.all()[:3]
    
    context = {
        'rooms': rooms,
    }
    
    return render(request, "frontends/index.html", context)
def about(request):
    return render(request,"frontends/about.html")

def rooms(request):
    """List all rooms."""
    room_list = Room.objects.prefetch_related("images")
    return render(request, "frontends/rooms.html", {"rooms": room_list})


def room_detail_public(request, slug):
    """Show a single room's details and gallery."""
    room = get_object_or_404(Room, slug=slug)
    room_images = room.images.all().order_by("order", "uploaded_at")
    other_rooms = Room.objects.exclude(pk=room.pk)[:5]  # adjust ordering/limit as you like
    return render(
        request,
        "frontends/room_details.html",
        {"room": room, "room_images": room_images, "other_rooms": other_rooms},

        
    )
def activities(request):
    """List all activities on the public site."""
    activity_list = Activity.objects.all().prefetch_related("images")
    return render(request, "frontends/activities.html", {"activities": activity_list})


def activity_detail_public(request, slug):
    """Show a single activity's details and gallery to visitors."""
    activity = get_object_or_404(Activity, slug=slug)
    activity_images = activity.images.all().order_by("order", "uploaded_at")
    other_activities = Activity.objects.exclude(pk=activity.pk)[:5]
    return render(
        request,
        "frontends/activity_details.html",
        {
            "activity": activity,
            "activity_images": activity_images,
            "other_activities": other_activities,
        },
    )
def nearby_destinations_public(request):
    destinations = NearbyDestination.objects.filter(status="active")
    return render(request, "frontends/nearby_destinations.html", {
        "destinations": destinations,
    })


def nearby_destination_detail_public(request, slug):
    destination = get_object_or_404(NearbyDestination, slug=slug, status="active")
    destination_images = destination.images.all()
    other_destinations = NearbyDestination.objects.filter(status="active").exclude(pk=destination.pk)[:5]

    return render(request, "frontends/nearby_destination_detail.html", {
        "destination": destination,
        "destination_images": destination_images,
        "other_destinations": other_destinations,
    })