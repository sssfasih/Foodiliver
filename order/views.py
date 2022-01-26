from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from .models import User, Category, Dish, DishImage
from markdown2 import markdown
from django.utils.text import slugify


# Create your views here.


def index(request):
    latest = Dish.objects.all().order_by('Modified')
    return render(request, 'order/index.html', {'recipes': latest})


def category(request, cat):
    cats = []
    for eachCat in Category.objects.all():
        cats.append(eachCat.Name.lower())

    if cat.lower() in cats:

        cat_obj = Category.objects.get(Name__contains=cat.lower())
        recipes = cat_obj.recipes.all()

        if cat_obj.Name == 'lunch':
            cat_obj.Name = "Lunch/Dinner"
    else:
        recipes = Dish.objects.none()
        cat_obj = Category.objects.none()

    return render(request, 'order/category.html', {'category': cat_obj, 'recipes': recipes})


def view_recipe(request, name):
    slug = name
    # name = name.replace("-",' ').strip().lower()
    # check = name.replace(' ','')
    # if check.isalnum():
    # print("alphabet")
    #    pass
    # else:return HttpResponseRedirect(reverse('all_category'))
    # print("SLUGGGGGG")
    # print(slug)
    # print("SLUGGGGGG")
    recipe_obj = Dish.objects.get(Slug=slug)
    details = recipe_obj.Details
    price = recipe_obj.Price
    images = recipe_obj.images.all()
    # print(images)

    return render(request, 'order/view_recipe.html',
                  {'recipe': recipe_obj, 'details': details, 'price': price, 'img_objs': images})


def all_categories(request):
    all_cats = Category.objects.all()
    return render(request, 'order/all_cats.html', {'all_cats': all_cats})


@login_required
def add_recipe(request):
    cats = (cat.Name for cat in Category.objects.all())
    if request.method == 'POST':

        name = request.POST.get('name').strip()
        slug = slugify(name)
        ingredients = request.POST.get('ingredients').strip()
        method = request.POST.get('method').strip()
        files = request.FILES.getlist('uploaded_images')
        if name == "" or ingredients == "" or method == "":
            print("BLANK DATA")

        else:
            new_rec = Dish(Name=name, Ingredients=ingredients, Directions=method, Posted_by=request.user, Slug=slug)
            new_rec.save()
            for loop in files:
                img = DishImage(recipe=new_rec, image=loop)
                img.save()
            for loop in cats:
                if request.POST.get(loop) == "True":
                    cat_obj = Category.objects.get(Name=loop)
                    new_rec.Tags.add(cat_obj)
            return HttpResponseRedirect(reverse('view_recipe', args=[slug]))

    return render(request, 'order/add_recipe.html', {'cats': cats})


@login_required
def view_profile(request):
    id = request.user.id

    requested_user = User.objects.get(pk=id)

    fav_recipes = requested_user.Tray_Items.all()

    # r = request.GET.get('page')

    # p = Paginator(posts, 10)

    # if r:
    #    page_posts = p.page(r)
    # else:
    #    page_posts = p.page(1)

    return render(request, 'order/view_profile.html', {'recipes': fav_recipes})


def recipe_addfav(request, id):
    recipe = Dish.objects.get(pk=id)
    request.user.Tray_Items.add(recipe)
    return HttpResponseRedirect(reverse('view_recipe', args=[recipe.Slug]))


def recipe_remfav(request, id):
    recipe = Dish.objects.get(pk=id)
    if recipe in request.user.Tray_Items.all():
        request.user.Tray_Items.remove(recipe)
        # print("Removed")
    else:
        # print("recipe not in favs")
        pass
    return HttpResponseRedirect(reverse('view_recipe', args=[recipe.Slug]))


def recipe_edit(request, id):
    recipe = Dish.objects.get(pk=id)
    cats = (cat.Name for cat in Category.objects.all())
    if request.method == "POST":
        name = request.POST.get('name').strip()
        ingredients = request.POST.get('ingredients').strip()
        method = request.POST.get('method').strip()
        files = request.FILES.getlist('uploaded_images')
        if name == "" or ingredients == "" or method == "":
            print("BLANK DATA")

        else:
            recipe.Name = name
            recipe.Ingredients = ingredients
            recipe.Directions = method

            for loop in cats:
                cat_obj = Category.objects.get(Name=loop)
                if request.POST.get(loop) == "True":
                    if cat_obj not in recipe.Tags.all(): recipe.Tags.add(cat_obj)
                else:
                    if cat_obj in recipe.Tags.all(): recipe.Tags.remove(cat_obj)

            recipe.save()
            """
            for loop in files:
                img = RecipeImage(recipe=new_rec, image=loop)
                img.save()

            """
            return HttpResponseRedirect(reverse('view_recipe', args=[recipe.Slug]))
    else:

        cats = (cat.Name for cat in Category.objects.all())
        recipe_cats = recipe.Tags.values_list('Name', flat=True)
        return render(request, 'order/add_recipe.html',
                      {'editMode': True, 'cats': cats, 'recipe_obj': recipe, 'recipe_cats': recipe_cats})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "order/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        return render(request, "order/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def signup(request):
    if request.method == "POST":
        name = request.POST["Name"]
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "order/signup.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, first_name=name)
            user.save()
        except IntegrityError:
            return render(request, "order/signup.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "order/signup.html")