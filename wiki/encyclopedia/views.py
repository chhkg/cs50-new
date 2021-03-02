from django import forms
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

import markdown2
import random
import re

from . import util

def index(request):
    search = request.GET.get('q')
    record = f"entries/{search}.md"
    full_list = util.list_entries()

    if search:
        if not default_storage.exists(record):
            searchlist = [str for str in full_list if any(sub in str.lower() for sub in [search.lower()])]
            if len(searchlist) == 0:
                return render(request, "encyclopedia/error.html", {
                    "errorMessage": "Be the first to create this entry"
                })
            return render(request, "encyclopedia/index.html", {
                "entries": searchlist
            })
        else:
            return redirect('encyclopedia:entry', title=search)
    else:
        return render(request, "encyclopedia/index.html", {
        "entries": full_list
    })

def entry(request, title):
    record = f"entries/{title}.md"
    if not default_storage.exists(record):
        return render(request, "encyclopedia/error.html", {
            "errorMessage": "Be the first to create this entry"
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(util.get_entry(title)),
            "title": title
        })
        

def newpage(request):
    if request.method == 'POST':
        title = request.POST.get("eTitle")
        content = request.POST.get("eContent")
        record = f"entries/{title}.md"
        if default_storage.exists(record):
            return render(request, "encyclopedia/error.html", {
                "errorMessage": "Someone has created this entry before"
            })
        else:
            util.save_entry(title, content)
            return redirect('encyclopedia:entry', title=title)
    return render(request, "encyclopedia/newpage.html")

def editpage(request):
    if request.method == 'POST':
        title = request.POST.get("eTitle")
        content = request.POST.get("eContent")
        util.save_entry(title, content)
        return redirect('encyclopedia:entry', title=title)
    else:
        title = request.GET.get("title")
        content = util.get_entry(title)
        print(title)
        print(content)
        return render(request, 'encyclopedia/editpage.html', {
            "title": title,
            "content": content
        })

def randompage(request):
    full_list = util.list_entries()
    random_entry = random.choice(full_list)
    print(full_list)
    print(random_entry)
    return redirect('encyclopedia:entry', title=random_entry)