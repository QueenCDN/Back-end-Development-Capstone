from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req


def songs(request):
    songurl = "http://localhost:5000/song"
    response = req.get(songurl)
    songs = response.json()
    return render(request, "songs.html", {"songs": songs["songs"]})


def photos(request):
    phourl = "http://localhost:3000/picture"
    response = req.get(phourl)
    photos = response.json()
    return render(request, "photos.html", {"photos": photos})


def index(request):
    return render(request, "index.html")


def signup(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            try:
                user = User.objects.get(username=username)
                return render(request, "signup.html", {"form": form, "message": "User already exists"})
            except User.DoesNotExist:
                user = User.objects.create(username=username, password=make_password(password))
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
    return render(request, "signup.html", {"form": form})


def login_view(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "login.html", {"form": form, "message": "Invalid username or password"})
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def concerts(request):
    if request.user.is_authenticated:
        concert_list = Concert.objects.all()
        attending = {}
        for concert in concert_list:
            try:
                status = concert.attendee.filter(user=request.user).first().attending
            except:
                status = "-"
            attending[concert.id] = status
        return render(request, "concerts.html", {"concerts": concert_list, "attending": attending})
    else:
        return HttpResponseRedirect(reverse("login"))


def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = Concert.objects.get(pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)
        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
