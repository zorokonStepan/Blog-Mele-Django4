from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Post


def post_list(request: HttpRequest) -> HttpResponse:
    posts = Post.published.all()
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request: HttpRequest, post_id: int) -> [HttpResponse, None]:
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    return render(request, 'blog/post/detail.html', {'post': post})
