from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

 
    return render(request, 'game/register.html', {'form': form})

@login_required
def profile_settings(request):
    if request.method == "POST":

        if 'update_profile' in request.POST:

            form = UserUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('profile')
            
        elif 'delete_account' in request.POST:
            user = request.user
            logout(request)
            user.delete()
            return redirect('register')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'game/profile.html', {'form': form})