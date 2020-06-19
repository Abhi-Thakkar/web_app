from django.shortcuts import render,redirect, get_object_or_404
from .models import Book , OrderItem, Order , BookImage
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin 
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView, View)
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django import template
from django.core.exceptions import ObjectDoesNotExist
from .forms import BookForm ,ImageForm
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect

posts = 'This is a basic signin signup web application'

def about(request):
	context={
		'posts': posts ,
		'title' : 'About Us page',
		
	}
	return render(request,'ui/about.html',context)
	


def home(request):
	context ={
		'books':Book.objects.all()
	}
	return render(request,'ui/home.html',context)

# def delete_image(request):
#     image= Image.objects.get().delete()
#     return HttpResponseRedirect(reverse(""))


class BookListView(ListView):
	model = Book
	template_name = 'ui/home.html'
	context_object_name = 'books'
	ordering = ['title','price']

class BookDetailView(DetailView):
	model = Book
	template_name = 'ui/book_detail.html'

# class BookCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
# 	model = Book
# 	form_class=BookForm   
# 	template_name = 'ui/book_form.html'
# 	success_message = "Book has been Added!"

# 	def form_valid(self, form):
# 		form.instance.seller = self.request.user
# 		return super().form_valid(form)

def post(request):

    ImageFormSet = modelformset_factory(BookImage,
                                        form=ImageForm, extra=3)

    if request.method == 'POST':

        bookForm = BookForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES,
                               queryset=BookImage.objects.none())


        if bookForm.is_valid() and formset.is_valid():
            book_form = bookForm.save(commit=False)
            book_form.seller = request.user
            book_form.save()

            for form in formset.cleaned_data:
                image = form['image']
                photo = BookImage(book=book_form, image=image)
                photo.save()
            messages.success(request,
                             "Posted!")
            return HttpResponseRedirect("/")
        else:
            print (bookForm.errors, formset.errors)
    else:
        bookForm = BookForm()
        formset = ImageFormSet(queryset=BookImage.objects.none())
    return render(request, 'ui/book_form.html',
                  {'bookForm': bookForm, 'formset': formset},
                  )

class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView ):
	model = Book
	fields = ['isbn','title', 'authors','publication_date','quantity','price']
	template_name = 'ui/book_form.html'
	success_message = "Book has been updated!"

	def test_func(self):
		book = self.get_object()
		if self.request.user == book.seller:
			return True

		return False

class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
	model = Book
	template_name = 'ui/product_confirm_delete.html'
	success_url = '/'

	def test_func(self):
		book = self.get_object()
		if self.request.user == book.seller:
			return True
		return False

# class ImageDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
# 	model = BookImage
# 	template_name = 'ui/product_confirm_delete.html'
# 	success_url = '/'

# 	def test_func(self):
# 		bookimage = self.get_object()
# 		if self.request.book == bookimage.book:
# 			return True
# 		return False

def update_cart(request, pk):
	item = get_object_or_404(Book, id=pk)
	order_item, created = OrderItem.objects.get_or_create(item = item,user= request.user,ordered=False)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__id=item.pk).exists():
			if item.quantity == 0:
				messages.info(request, "No more books to add")
				return redirect("product-summary")
			order_item.quantity +=1
			order_item.save()
			item.quantity -=1
			item.save()
			messages.info(request, "Product added to the cart")
			return redirect("product-summary")
		else:
			order.items.add(order_item)
			item.quantity -=1
			item.save()
			messages.info(request, "Product added to the cart")
			return redirect ("book-detail", pk=pk)
	
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date = ordered_date)
		order_items.add(order_items)
		item.quantity -= 1
		item.save()
		messages.info(request, "Product has been added to the cart")
		return redirect("product-summary")


def delete_from_cart(request, pk):
	item = get_object_or_404(Book, pk=pk)
	order_qs = Order.objects.filter(user=request.user , ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__id=item.pk).exists():
			order_item = OrderItem.objects.filter(item = item, user= request.user, ordered=False)[0]
			item.quantity += order_item.quantity
			item.save()
			order.items.remove(order_item)
			order_item.delete()
			messages.info(request, "Product removed from the cart")
			return redirect("product-summary")
		else:
			messages.info(request, "Product is not in the cart")
			return redirect("book-detail", pk=pk)
	else:
		messages.info(request, "No Orders")
		return redirect("book-detail", pk=pk)

def delete_single_item(request, pk):
	item = get_object_or_404(Book, pk=pk)
	order_qs = Order.objects.filter(user=request.user , ordered=False)
	if order_qs.exists():
		order= order_qs[0]
		if order.items.filter(item__id=item.pk).exists():
			order_item = OrderItem.objects.filter(item=item , user= request.user, ordered =False)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
				item.quantity +=1
				item.save()
				messages.info(request, "Product removed from the cart")
				return redirect("product-summary")

			else:
				order.items.remove(order_item)
				messages.info(request, "Product removed from the cart")
				item.quantity +=1
				item.save()
				return redirect("product-summary")
		else:
			messages.info(request, "The item is not in the cart")
			return redirect("product-summary")
	else:
		messages.info(request, "The item is not in the cart")
		return redirect("product-summary")



register = template.Library()


@register.filter
def item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0


class ProductSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'ui/product_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")