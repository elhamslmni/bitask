import json

from django.contrib.auth.models import User
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Post, Rating
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .rating import get_average_ratings


@csrf_exempt
@require_http_methods(["PUT"])
def register(request):

        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required.'}, status=401)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return JsonResponse({'message': 'User registered successfully'})




@csrf_exempt
@require_http_methods(["POST"])
def login(request):

        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required.'}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'User logged in successfully'})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)



@csrf_exempt
@login_required
@require_http_methods(["POST"]) # CHANGE
def logout(request):

        logout(request)
        return JsonResponse({'message': 'User logged out successfully'})


@require_http_methods(["GET"])
@login_required
def all_posts(request):

    user = request.user
    user_rating_subquery = Rating.objects.filter(
        post=OuterRef('pk'), user=user
    ).values('rating')[:1]


    """we can also store posts in cache to avoid db load"""

    posts = Post.objects.all()              # in a better practice we shouldn't send any direct request to db in view
    posts_vs_user_rate = posts.annotate(user_rating=Subquery(user_rating_subquery))
    post_ids = posts.values_list('id', flat=True)

    overall_average_ratings = get_average_ratings(post_ids)


    data = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_rating": post.user_rating or -1,
            "average_rating": overall_average_ratings[post.id] or 0
        }
        for post in posts_vs_user_rate
    ]
    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def rate_post(request, post_id):
    data = json.loads(request.body)
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    rating_value = int(data.get('rating', 0))

    if 0 <= rating_value <= 5:
        rating, created = Rating.objects.update_or_create(user=user, post=post, defaults={"rating": rating_value})
        return JsonResponse({"message": "Rating submitted successfully", "user_rating": rating.rating})
    return JsonResponse({"error": "Invalid rating"}, status=400)


@login_required
@require_http_methods(["GET"])
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    """we can store user ratings in clickhouse"""

    user_rating = Rating.objects.filter(user=request.user, post=post).first()
    if user_rating is None:
        rate = -1
    else: rate = user_rating.rating
    data = {
        "title": post.title,
        "content": post.content,
        "user_rate": rate,
        "average_rating": get_average_ratings(list(post_id)),
    }
    return JsonResponse(data)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_post(request):

    """this function creates a new post, we can do this directly in admin panel,
     it is just for making it more convenient, thus we don't assign user to posts
    """

    data = json.loads(request.body)
    title = data.get('title')
    content = data.get('content')

    if title and content:
        post = Post.objects.create(title=title, content=content)
        return JsonResponse({'message': 'Post created successfully', 'post_id': post.id})
    else:
         return JsonResponse({'error': 'Title and content are required.'}, status=400)


