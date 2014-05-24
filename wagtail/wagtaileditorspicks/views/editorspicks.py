from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext as _
from django.views.decorators.vary import vary_on_headers

from wagtail.wagtaileditorspicks import models, forms
from wagtail.wagtaileditorspicks.query import Query
from wagtail.wagtailadmin.forms import SearchForm


@permission_required('wagtailadmin.access_admin')
@vary_on_headers('X-Requested-With')
def index(request):
    page = request.GET.get('p', 1)
    query_string = request.GET.get('q', "")

    queries = models.EditorsPick.objects.values('query_string')

    # Search
    if query_string:
        queries = queries.filter(query_string__icontains=query_string)

    # Pagination
    paginator = Paginator(queries, 20)
    try:
        queries = paginator.page(page)
    except PageNotAnInteger:
        queries = paginator.page(1)
    except EmptyPage:
        queries = paginator.page(paginator.num_pages)

    if request.is_ajax():
        return render(request, "wagtaileditorspicks/editorspicks/results.html", {
            'queries': queries,
            'query_string': query_string,
        })
    else:
        return render(request, 'wagtaileditorspicks/editorspicks/index.html', {
            'queries': queries,
            'query_string': query_string,
            'search_form': SearchForm(data=dict(q=query_string) if query_string else None, placeholder=_("Search editor's picks")),
        })


def save_editorspicks(query_string, new_query_string, editors_pick_formset):
    # Set sort_order
    for i, form in enumerate(editors_pick_formset.ordered_forms):
        form.instance.sort_order = i

    # Save
    if editors_pick_formset.is_valid():
        editors_pick_formset.save()

        # If query string was changed, move all editors picks to the new query string
        if query_string != new_query_string:
            editors_pick_formset.get_queryset().update(query_string=new_query_string)

        return True
    else:
        return False


@permission_required('wagtailadmin.access_admin')
def add(request):
    if request.POST:
        # Get query
        query_form = forms.QueryForm(request.POST)
        if query_form.is_valid():
            query = Query.get(query_form['query_string'].value())

            # Save editors picks
            editors_pick_formset = forms.EditorsPickFormSet(request.POST)

            if save_editorspicks(query.query_string, query.query_string, editors_pick_formset):
                messages.success(request, _("Editor's picks for '{0}' created.").format(query))
                return redirect('wagtaileditorspicks_editorspicks_index')
        else:
            editors_pick_formset = forms.EditorsPickFormSet()
    else:
        query_form = forms.QueryForm()
        editors_pick_formset = forms.EditorsPickFormSet()

    return render(request, 'wagtaileditorspicks/editorspicks/add.html', {
        'query_form': query_form,
        'editors_pick_formset': editors_pick_formset,
    })


@permission_required('wagtailadmin.access_admin')
def edit(request, query_slug):
    query = Query.from_slug(query_slug)

    if request.POST:
        # Get query
        query_form = forms.QueryForm(request.POST)
        if query_form.is_valid():
            new_query = Query.get(query_form['query_string'].value())

            # Save editors picks
            editors_pick_formset = forms.EditorsPickFormSet(request.POST)

            if save_editorspicks(query.query_string, new_query.query_string, editors_pick_formset):
                messages.success(request, _("Editor's picks for '{0}' updated.").format(new_query))
                return redirect('wagtaileditorspicks_editorspicks_index')
    else:
        query_form = forms.QueryForm(initial=dict(query_string=query.query_string))
        editors_pick_formset = forms.EditorsPickFormSet()

    return render(request, 'wagtaileditorspicks/editorspicks/edit.html', {
        'query_form': query_form,
        'editors_pick_formset': editors_pick_formset,
        'query': query,
    })


@permission_required('wagtailadmin.access_admin')
def delete(request, query_slug):
    query = Query.from_slug(query_slug)

    if request.POST:
        query.editors_picks.delete()
        messages.success(request, _("Editor's picks deleted."))
        return redirect('wagtaileditorspicks_editorspicks_index')

    return render(request, 'wagtaileditorspicks/editorspicks/confirm_delete.html', {
        'query': query,
    })
