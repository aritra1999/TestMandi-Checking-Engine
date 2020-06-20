from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def auth_view(request):

    context = {
        "title": "Authentication",
        "reg_error": [],
        "login_error": []
    }

    if request.method == "POST":
        if request.POST.get('form-type') == "login":
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                context['login_error'].append("Username and password do not match!")

        elif request.POST.get('form-type') == "register":
            username = request.POST.get('username')
            f_name = request.POST.get('f_name')
            l_name = request.POST.get('l_name')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')


            if password1 == password2:
                if User.objects.filter(username=username).exists():
                    context["reg_error"].append("Username already in use!")
                else:
                    if User.objects.filter(email=email).exists():
                        context["reg_error"].append("Username already in use!")
                    else:
                        User.objects.create_user(username=username, first_name=f_name, last_name=l_name, email=email, password=password1)
                        user = authenticate(request, username=username, password=password1)
                        if user is not None:
                            login(request, user)
                            return redirect("/")
            else:
                context["reg_error"].append("Passwords don't match!")


    return render(request, 'users/auth.html', context)