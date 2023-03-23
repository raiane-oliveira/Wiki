import random

from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from . import util
from markdown2 import Markdown

# Template text of future HTML pages created, with minimal extra space
textLayout = '''
{% extends 'encyclopedia/layout.html' %}

{% block title %}
    {{ titleEntry }}
{% endblock %}

{% block body %}
    {{ entryHTML | safe }}
    <a href="{% url 'editPage' titleEntry %}">Edit Page</a>
{% endblock %}
'''

# Creates a new page Form
class PageForm(forms.Form):
    titleNewPage = forms.CharField(label="Title of page:")
    contentNewPage = forms.CharField(label="Content of page in Markdown:", widget=forms.Textarea)

# Creates a new search Form
class SearchForm(forms.Form):

    # Remove label
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].label = ""

    q = forms.CharField(widget=forms.TextInput(attrs={
        "class": "search",
        "placeholder": "Search Encyclopedia",
    }))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "searchForm": SearchForm(auto_id=False)
    })


def wiki(request, titleEntry):
    if not util.get_entry(titleEntry):
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found (404)",
            "searchForm": SearchForm(auto_id=False)
        })

    # Convert the entry markdown to HTML content
    contentEntry = util.get_entry(titleEntry)
    entryHTML = Markdown().convert(contentEntry)

    return render(request, f"encyclopedia/{titleEntry}.html", {
        "entryHTML": entryHTML,
        "titleEntry": titleEntry,
        "searchForm": SearchForm(auto_id=False)
    })


def createPage(request):
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = PageForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            titlePage = form.cleaned_data['titleNewPage']
            contentPage = form.cleaned_data['contentNewPage']
            filepath = f"encyclopedia/templates/encyclopedia/{titlePage}.html"

            # Enter a error message if the page already exists
            if default_storage.exists(filepath):
                return render(request, "encyclopedia/error.html", {
                    "message": "This page already exists!",
                    "searchForm": SearchForm(auto_id=False)
                })

            # Save user input as markdown and HTML file
            util.save_entry(titlePage, contentPage)
            default_storage.save(filepath, ContentFile(textLayout))

            # Redirect to the new page created
            return HttpResponseRedirect(reverse("wiki", args=(titlePage,)))

        # If the form is invalid, re-render the page with existing information
        else:
            return render(request, "encyclopedia/newpage.html", {
                "form": form,
                "searchForm": SearchForm(auto_id=False)
            })

    # Render the page via GET method with the form class
    return render(request, "encyclopedia/newpage.html", {
        "form": PageForm(),
        "searchForm": SearchForm(auto_id=False)
    })


def randomPage(request):

    # Return a random entry
    randomEntry = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse("wiki", args=(randomEntry,)))


def editPage(request, titleEntry):
    if not util.get_entry(titleEntry):
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found (404)",
            "searchForm": SearchForm(auto_id=False)
        })

    # Gets entry markdown content
    entryContent = util.get_entry(titleEntry)

    # Create a form and update it with the original content page
    originalForm = PageForm()
    originalForm["titleNewPage"].initial = titleEntry
    originalForm["contentNewPage"].initial = entryContent

    if request.POST:
        editedForm = PageForm(request.POST)

        if editedForm.is_valid():

            # Gets clean data from edited form
            editedTitlePage = editedForm.cleaned_data["titleNewPage"]
            editedContentPage = editedForm.cleaned_data["contentNewPage"]

            # Checks if the title changed and deletes the markdown file if so
            if titleEntry != editedTitlePage:
                if default_storage.exists(f"entries/{titleEntry}.md"):
                    default_storage.delete(f"entries/{titleEntry}.md")

            # Saves edited content as markdown file
            util.save_entry(editedTitlePage, editedContentPage)

            # Path of files HTML
            filePathOriginalTitle = f"encyclopedia/templates/encyclopedia/{titleEntry}.html"
            filePathEditedTitle = f"encyclopedia/templates/encyclopedia/{editedTitlePage}.html"

            # Replaces the edited HTML page from original
            if default_storage.exists(filePathOriginalTitle):
                default_storage.delete(filePathOriginalTitle)
            default_storage.save(filePathEditedTitle, ContentFile(textLayout))

            return HttpResponseRedirect(reverse("wiki", args=(editedTitlePage,)))

        else:
            return render(request, "encyclopedia/editPage.html", {
                "form": editedForm,
                "searchForm": SearchForm(auto_id=False)
            })
    
    # Shows the existing pre-populated content of the Markdown page
    return render(request, "encyclopedia/editPage.html", {
        "titleEntry": titleEntry,
        "form": originalForm,
        "searchForm": SearchForm(auto_id=False)
    })


def search(request):
    form = SearchForm(request.POST)
    if request.POST and form.is_valid():
            
        # Gets clean data from search form and list of entries
        querySearched = form.cleaned_data["q"].upper()
        entries = util.list_entries()

        # Converts all entries to uppercase
        entries = list(map(lambda entry: entry.upper(), entries))

        # Checks if query searched match entries
        if querySearched in entries:
            return HttpResponseRedirect(reverse("wiki", args=(querySearched.capitalize(),)))
        else:

            # Finds all results, in list format, from the substring of entries
            resultsSearch = list(filter(lambda entry: querySearched in entry, entries))

            return render(request, "encyclopedia/search.html", {
                "results": resultsSearch,
                "searchForm": SearchForm(auto_id=False)
            })