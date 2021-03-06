from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Post, Tag, Category
from .forms import PostForm
from .httphelp import getPostList, getPostDetail, postPostDetail, putPostDetail, deletePostDetail
import json
from comments.forms import CommentForm
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView, DeleteView
from django.views.generic.base import RedirectView
from django.urls import reverse

# Create your views here.
"""
def post_list(request):
    # post_list = Post.objects.all().order_by('-created_time')
    post_list = getPostList()
    return render(request, 'blog/post_list.html', context={'post_list': post_list})
"""

class PostView(ListView):
    # model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'post_list'

    def get_queryset(self):
    	# cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        # return super(CategoryView, self).get_queryset().filter(category=cate)
        return getPostList()

"""
def post_detail(request, pk):
    # post = get_object_or_404(Post, pk=pk)
	post = getPostDetail(pk=pk)
	# post_ob = Post(title=post['title'], abstract=post['abstract'], body=post['body'], author=post['author'], category=post['category'], pub_time=post['pub_time'], update_time=post['update_time'], pk=post['pk'])

	# 记得在顶部导入 CommentForm
	form = CommentForm()
	# 获取这篇 post 下的全部评论
    # comment_list = post.comment_set.all()
	comment_list = post.get('comments')

	# 将文章、表单、以及文章下的评论列表作为模板变量传给 detail.html 模板，以便渲染相应数据。
	context	=	{'post': post,
				'form': form,
				'comment_list': comment_list
				}
	return render(request, 'blog/post_detail.html', context=context)
	# return render(request, 'blog/post_detail.html', context={'post': post})
"""

class PostDetailView(DetailView):
    # 这些属性的含义和 ListView 是一样的
    # model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    """
    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response
    """

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        # post = super(PostDetailView, self).get_object(queryset=None)
        post = getPostDetail(pk=self.kwargs.get('pk'))
        return post

    def get_context_data(self, **kwargs):
        # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（DetailView 已经帮我们完成），
        # 还要把评论表单、post 下的评论列表传递给模板。
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = context['post'].get('comments')
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context

"""
def post_new(request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			ori_post = form.save(commit=False)
			str_json = json.dumps(ori_post.to_dict())
			bytes = str_json.encode('utf-8')
			post = postPostDetail(bytes)
			# post = form.save()
			# post.author = request.user
			# post.save()
			# return redirect('blog:post_list')
			return redirect('blog:post_detail', pk=post['pk'])
	else:
		form = PostForm()
	return render(request, 'blog/post_edit.html', {'form': form})
"""

class PostNewView(FormView):
    template_name = 'blog/post_edit.html'
    form_class = PostForm

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        ori_post = form.save(commit=False)
        str_json = json.dumps(ori_post.to_dict())
        bytes = str_json.encode('utf-8')
        post = postPostDetail(bytes)
        return redirect('blog:post_detail', pk=post['pk'])
        # return super(PostNewView, self).form_valid(form)

"""
def post_edit(request, pk):
	# post = get_object_or_404(Post, pk=pk)
	post = getPostDetail(pk)
	post_ob = Post(title=post['title'], abstract=post['abstract'], body=post['body'], author=post['author'], category=post['category'], pub_time=post['pub_time'], update_time=post['update_time'], pk=post['pk'])
	if request.method == "POST":
		form = PostForm(request.POST, instance=post_ob)
		if form.is_valid():
			ori_post = form.save(commit=False)
			str_json = json.dumps(ori_post.to_dict())
			bytes = str_json.encode('utf-8')
			post = putPostDetail(pk, bytes)
			# post = form.save()
			# post = form.save(commit=False)
			# post.author = request.user
			# post.save()
			return redirect('blog:post_detail', pk=post['pk'])
	else:
		form = PostForm(instance=post_ob)
	return render(request, 'blog/post_edit.html', {'form': form})
"""

class PostEditView(FormView):
	template_name = 'blog/post_edit.html'
	form_class = PostForm

	def form_valid(self, form):
		ori_post = form.save(commit=False)
		str_json = json.dumps(ori_post.to_dict())
		bytes = str_json.encode('utf-8')
		post = putPostDetail(pk=self.kwargs.get('pk'), data=bytes)
		return redirect('blog:post_detail', pk=post['pk'])

	def get_initial(self):
		"""
    	Returns the initial data to use for forms on this view.
    	"""
		post = getPostDetail(pk=self.kwargs.get('pk'))
		return post

"""
def post_delete(request, pk):
	deletePostDetail(pk)
	return redirect('blog:post_list')
"""
class PostDeleteView(RedirectView):
	def get_redirect_url(self, *args, **kwargs):
		deletePostDetail(pk=self.kwargs.get('pk'))
		return reverse('blog:post_list')








