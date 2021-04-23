from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.models import Permission
from apps.users.models import MyUser
from .models import Post, Comment
from .forms import PostCommentForm
from django.core.paginator import Paginator
from client_side_image_cropping import ClientsideCroppingWidget


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        user.discussions_viewed = len(Post.objects.all())
        user.save()
        return super().dispatch(request,*args, **kwargs)


class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/user-posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(MyUser, name=self.kwargs.get('name'), surname=self.kwargs.get('surname'))
        return Post.objects.filter(author=user).order_by('-date_posted')


@login_required()
def post_detail(request, pk):
    template_name = 'blog/post-detail.html'
    post = get_object_or_404(Post, pk=pk)
    author = request.user
    new_comment = None

    if request.method == 'POST':
        form = PostCommentForm(data=request.POST)
        if form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = form.save(commit=False)
            # Assign the current post and author to the comment
            new_comment.post = post
            new_comment.author = author
            # Save the comment to the database
            new_comment.save()
            messages.success(request, str("Commentaire publié."))
        form = PostCommentForm()
    else:
        form = PostCommentForm()

    # Paginator
    comments = post.comment_set.all()
    comment_count = len(comments)
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, template_name, {'title': 'Discussion', 'post': post, 'form': form, 'page_obj': page_obj, 'comment_count': comment_count})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post-create.html'
    fields = ['title', 'content', 'image']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request = self.request
        form.fields['image'].widget = ClientsideCroppingWidget(
                width=1000,
                height=600,
                preview_width=120,
                preview_height=72,
            )
        return form
        
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'blog/post-update.html'
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, str("La discussion a bien été modifiée."))
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post-delete.html'
    context_object_name = 'post'

    def get_success_url(self):
        messages.success(self.request, str("La discussion a bien été supprimée."))
        return '/blog/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment-update.html'
    fields = ['content', 'image']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.request = self.request
        form.fields['image'].widget = ClientsideCroppingWidget(
                width=1000,
                height=600,
                preview_width=120,
                preview_height=72,
            )
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, str("Le commentaire a bien été modifié."))
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment-delete.html'
    context_object_name = 'comment'

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            messages.success(self.request, str("Le commentaire a bien été supprimé."))
            return next_url # return next url for redirection
        return '/blog/' # return some other url if next parameter not present

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False
