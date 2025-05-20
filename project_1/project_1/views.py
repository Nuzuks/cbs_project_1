# project_1/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .models import Note , CustomUser # Custom user doesn't need to be imported with the fix
from django.db import connection # For raw SQL queries
# import bleach # Used to sanitize user input
# from django.contrib.auth.models import User # fix
# from django.contrib.auth import authenticate, login # fix
# from django.contrib.auth.decorators import login_required, user_passes_test #fix

ALLOWED_TAGS = ['b', 'i', 'u', 'a', 'p', 'br', 'ul', 'ol', 'li', 'strong', 'em']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
}

def home(request):
    return render(request, 'home.html')

def register_user(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        pword = request.POST.get('password')
        
        if CustomUser.objects.filter(username=uname).exists():
            return render(request, 'register.html', {'error': 'Username already exists.'})
        user = CustomUser.objects.create(username=uname, password=pword) 
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        request.session['is_admin'] = user.is_admin
        # This code uses the Django User class
        #if User.objects.filter(username=uname).exists():
            # return render(request, 'register.html', {'error': 'Username already exists.'})
        # User.objects.create_user(username=uname, password=pword) #FIX
        return redirect('home')
    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        pword = request.POST.get('password')

        # This code works with the django User class
        # user = authenticate(request, username=uname, password=pword)
        # if user is not None:
        #     login(request, user)
        #     request.session['is_admin'] = user.is_superuser  
        #     return redirect('home')
        # else:
        #     return render(request, 'login.html', {'error': 'Invalid credentials'})      
        
        try:      
            user = CustomUser.objects.get(username=uname, password=pword) 
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['is_admin'] = user.is_admin
            return redirect('home')
        except CustomUser.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_user(request):
    request.session.flush() # Clear the session
    return redirect('home')

# @login_required FIX
def add_note(request):
    if not request.session.get('user_id'):
        return redirect('login')   
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content') 
        author_id = request.session.get('user_id')
        author = CustomUser.objects.get(id=author_id)

        # This code works with the django User class
        # author = request.user
        # content = bleach.clean(
        #     content,
        #     tags=ALLOWED_TAGS,
        #     attributes=ALLOWED_ATTRIBUTES,
        #     strip=True
        # )
        # Content is saved as is, without sanitization.
        Note.objects.create(author=author, title=title, content=content)
        return redirect('view_notes')
    return render(request, 'add_note.html')

def view_notes(request):
    notes = []
    search_term = request.GET.get('search', '')

    if search_term:
        query = f"SELECT id, title, content, created_at FROM project_1_note WHERE title LIKE '%{search_term}%' OR content LIKE '%{search_term}%'" # Directlty adding user input into a query makes SQL injection possible.
        
        # This query uses placeholders
        # query = """
        #     SELECT id, title, content, created_at
        #     FROM project_1_note
        #     WHERE title LIKE ? OR content LIKE ?
        # """
        # search_param = f"%{search_term}%" FIX
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                # cursor.execute(query, [search_param, search_param]) FIX
                rows = cursor.fetchall()
                for row in rows:
                    note_data = {'id': row[0], 'title': row[1], 'content': row[2]}
                    notes.append(note_data)
            except Exception as e:
                notes.append({'id':0, 'title': 'Error in query', 'content': str(e)})

    else:
        all_notes_obj = Note.objects.all().order_by('-created_at')
        for note_obj in all_notes_obj:
            # content = bleach.clean(
            # note_obj.content,
            # tags=ALLOWED_TAGS,
            # attributes=ALLOWED_ATTRIBUTES,
            # strip=True
            # )
            notes.append({
                'id': note_obj.id,
                'title': note_obj.title,
                'content': note_obj.content, # 'content': content, 
                'author_username': note_obj.author.username if note_obj.author else "Anonymous"
            })
    
    return render(request, 'view_notes.html', {
        'notes': notes,
        'search_term': search_term,
    })


# @login_required FIX
#@user_passes_test(lambda u: u.is_superuser) Checks admin status
def admin_panel_view(request):
    if not request.session.get('user_id'):
        return redirect('login')
    users = CustomUser.objects.all
    # users = User.objects.all() This works with the django User class
    return render(request, 'admin_panel.html', {'users': users})

