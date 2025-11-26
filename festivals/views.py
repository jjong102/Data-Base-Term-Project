from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm
from .models import Festival


def festival_list(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    festivals = Festival.objects.all().order_by("title")
    if query:
        festivals = festivals.filter(title__icontains=query)
    if category:
        festivals = festivals.filter(category__icontains=category)

    paginator = Paginator(festivals, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = (
        Festival.objects.exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    context = {
        "page_obj": page_obj,
        "query": query,
        "category": category,
        "categories": categories,
    }
    return render(request, "festivals/festival_list.html", context)


def festival_detail(request, pk: int):
    festival = get_object_or_404(Festival, pk=pk)
    comments = festival.comments.all()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.festival = festival
            comment.save()
            messages.success(request, "댓글이 등록되었습니다.")
            return redirect(f"{reverse('festival_detail', args=[festival.id])}#comments")
        messages.error(request, "입력값을 확인해주세요.")
    else:
        form = CommentForm()

    return render(
        request,
        "festivals/festival_detail.html",
        {"festival": festival, "comments": comments, "form": form},
    )
