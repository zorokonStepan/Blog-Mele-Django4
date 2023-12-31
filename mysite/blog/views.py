from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings

from .models import Post
from .forms import EmailPostForm, CommentForm


def post_list(request: HttpRequest) -> HttpResponse:
    posts_list = Post.published.all()

    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)

    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request: HttpRequest, year: int, month: int, day: int, post: str) -> HttpResponse:
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)

    form = CommentForm()

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'form': form})


def post_share(request, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['subject']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['subject']}\'s comments: {cd['comments']}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['email_to']])

            sent = True

    elif request.method == 'GET':
        form = EmailPostForm()
    else:
        form = None

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # Comment has been posted
    form = CommentForm(data=request.POST)

    if form.is_valid():
        # Create a Comment class object without storing it in the database
        comment = form.save(commit=False)
        # Assign post to comment
        comment.post = post
        # Save comment to database
        comment.save()

    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})
