from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, FestivalForm
from .models import Festival


def festival_list(request):
    query = request.GET.get("q", "").strip()

    festivals = Festival.objects.all().order_by("start_date", "title")
    if query:
        festivals = festivals.filter(title__icontains=query)

    paginator = Paginator(festivals, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
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


def _is_staff(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(_is_staff)
def festival_create(request):
    if request.method == "POST":
        form = FestivalForm(request.POST)
        if form.is_valid():
            festival = form.save()
            messages.success(request, "축제가 생성되었습니다.")
            return redirect("festival_detail", pk=festival.pk)
    else:
        form = FestivalForm()
    return render(request, "festivals/festival_form.html", {"form": form, "mode": "create"})


@login_required
@user_passes_test(_is_staff)
def festival_update(request, pk: int):
    festival = get_object_or_404(Festival, pk=pk)
    if request.method == "POST":
        form = FestivalForm(request.POST, instance=festival)
        if form.is_valid():
            form.save()
            messages.success(request, "축제 정보가 수정되었습니다.")
            return redirect("festival_detail", pk=festival.pk)
    else:
        form = FestivalForm(instance=festival)
    return render(request, "festivals/festival_form.html", {"form": form, "mode": "update", "festival": festival})


@login_required
@user_passes_test(_is_staff)
def festival_delete(request, pk: int):
    festival = get_object_or_404(Festival, pk=pk)
    if request.method == "POST":
        festival.delete()
        messages.success(request, "축제가 삭제되었습니다.")
        return redirect("festival_list")
    return render(request, "festivals/festival_confirm_delete.html", {"festival": festival})
