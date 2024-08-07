from django.shortcuts import render, redirect
from ..models import Review
from ..forms import ReviewForm
from django.contrib import messages

def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'review_templates/review_list.html', {'reviews': reviews})

def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('review_list')
    else:
        form = ReviewForm()
    return render(request, 'review_templates/review_form.html', {'form': form})

def review_update(request, pk):

    try:
        review = Review.objects.get(id=pk)
    except Review.DoesNotExist:
        messages.error(request, 'Review not found')
        redirect("/")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review_list')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'review_templates/review_form.html', {'form': form})

def review_delete(request, pk):
    try:
        review = Review.objects.get(id=pk)
    except Review.DoesNotExist:
        messages.error(request, 'Review not found')
        redirect("/")

    if request.method == 'POST':
        review.delete()
        return redirect('review_list')
    return render(request, 'review_templates/review_confirm_delete.html', {'review': review})
