from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate_queryset(request, queryset, items_per_page):
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj