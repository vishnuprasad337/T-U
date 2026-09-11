from .models import Room  # <-- confirm this import path is correct

def booking_modal_rooms(request):
    """
    Makes the full room list available site-wide so the shared
    #bookNowModal in base.html can always populate its Room dropdown
    and correctly preselect whichever room a page's 'Book Now'
    button was for.
    """
    return {
        'rooms': Room.objects.all()  # <-- add .filter(...) here if you need to exclude inactive/draft rooms
    }