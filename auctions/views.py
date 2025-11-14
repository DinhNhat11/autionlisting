from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *

# Homepage view
# Displays all active listings (is_close=False)
def index(request):
    active = Listing.objects.filter(is_close=False)
    return render(request, "auctions/index.html",{
        "listings": active
    })


# Login view
# Handles both GET and POST requests
# GET: renders login form
# POST: authenticates user and logs them in
def login_view(request):
    if request.method == "POST":

        # Retrieve username and password from POST request
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # If authentication is successful, log user in and redirect to index
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            # If authentication fails, reload login page with error message
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        # GET request: render login form
        return render(request, "auctions/login.html")


# Logout view
# Logs out the user and redirects to homepage
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Register view
# Handles user registration
# GET: renders registration form
# POST: validates and creates new user
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            # Handle case when username already exists
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        # Log in newly created user and redirect to homepage
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        # GET request: render registration form
        return render(request, "auctions/register.html")


# Create listing view
# Only accessible by logged-in users
@login_required    
def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            # Save listing object but do not commit to DB yet
            newlisting = form.save(commit=False)
            newlisting.user = request.user

            # Assign selected category
            category_id = int(request.POST["category"])
            category = Categories.objects.get(pk=category_id)
            newlisting.category = category

            # Create new category if provided
            if request.POST["newcategory"]:
                newcategory = Categories(category=request.POST["newcategory"])
                newcategory.save()
                newlisting.category = newcategory

            # Save the listing
            newlisting.save()
            return HttpResponseRedirect(reverse("listing", args=(newlisting.id,)))
        else:
            # If form is invalid, reload the form with errors
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        # GET request: render empty listing form with available categories
        return render(request, "auctions/create.html", {
            "form": ListingForm(),
            "categories": Categories.objects.all()
        })     


# Individual listing view
# Displays listing details, comments, current bid, and allows interaction
def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = listing.comments.all()
    bidlast = listing.listingbids.last()
    added = False
    closePermit = False
    won = False

    # Check if user is authenticated to show user-specific actions
    if request.user.is_authenticated:
        if request.user in listing.watchlist.all():
            added = True
        if listing.user == request.user:
            closePermit = True
        if listing.is_close:
            wonbid = listing.listingbids.last()
            if wonbid:
                won = f"This auction listing is won by {wonbid.user}"
            else:
                won = "Nobody bid this auction."

    # Handle watchlist add/remove actions
    if request.method == "POST":
        if "addwatchlist" in request.POST:
            listing.watchlist.add(request.user)
            added = True
        elif "removewatchlist" in request.POST:
            listing.watchlist.remove(request.user)
            added = False

    # Render listing page with relevant context
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "added": added,
        "formComment": CommentForm(),
        "closePermit": closePermit,
        "won": won,
        "bidlast": bidlast,
        "comments": comments,
        "formBid": BidForm()
    })


# Close bid view
# Allows listing creator to close auction
@login_required
def closeBid(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        listing.is_close = True
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


# Categories view
# Displays all categories to authenticated users
@login_required
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Categories.objects.all()
    })


# View listings of a single category
def onecategory(request, category_id):
    category = Categories.objects.get(pk=int(category_id))
    return render(request, "auctions/index.html", {
        "listings": category.categories.all()
    })


# Add comment to a listing
@login_required
def comment(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=int(listing_id))
        comments = listing.comments.all()
        bidlast = listing.listingbids.last()
        form = CommentForm(request.POST)
        if form.is_valid():
            newcomment = form.save(commit=False)
            newcomment.user = request.user
            newcomment.listing = listing
            newcomment.save()
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))

        # If form invalid, render listing page with errors
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "formComment": form,
            "bidlast": bidlast,
            "formBid": BidForm(),
            "comments": comments
        })


# Place a bid on a listing
@login_required
def bid(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=int(listing_id))
        comments = listing.comments.all()
        bidlast = listing.listingbids.last()
        form = BidForm(request.POST)
        if form.is_valid():
            price = request.POST['price']

            # Ensure bid is at least starting price and greater than last bid
            if int(price) >= listing.starting:
                if bidlast:
                    int(price) > bidlast.price  # Validation, but no error handling

                # Save new bid
                newBid = form.save(commit=False)
                newBid.user = request.user
                newBid.listing = listing
                newBid.save()
                return HttpResponseRedirect(reverse("listing", args=[listing_id]))
            else:
                # Show error if bid invalid
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "formBid": form,
                    "bidlast": bidlast,
                    "error": "Bid must be as large as starting bid, and must be greater than any other bids that have been placed.",
                    "formComment": CommentForm(),
                    "comments": comments
                })

        # If form invalid, reload listing page with errors
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "formBid": form,
            "bidlast": bidlast,
            "formComment": CommentForm(),
            "comments": comments
        })

    # Catch-all for unexpected access
    return HttpResponse("Unexpected error occurred", status=500)


# Watchlist view
# Displays all listings added by current user
@login_required
def watchlist(request):
    return render(request, "auctions/index.html", {
        "listings": request.user.watchlist.all()
    })
