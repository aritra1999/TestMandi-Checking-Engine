from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Question, Submission, IO, MCQQuestion, MCQSolution
from .utils import code_checker, gen_hit


def dashboard_view(request):
    context = {
        "title": "Dashboard"
    }
    return render(request, 'dashboard/dashboard.html', context)


def question_list_view(request):
    questions = Question.objects.all()
    context = {
        "title": "Dashboard",
        "questions": questions
    }

    return render(request, 'dashboard/question-list.html', context)


def question_details_view(request, hit):
    question = Question.objects.get(hit=hit)
    context = {
        "title": hit,
        "question": question
    }

    user = request.user

    if request.method == "POST":
        if request.user.is_authenticated:
            question_hit = hit
            solution = request.POST.get('solution')
            language = request.POST.get('language')

            time_taken, verdict = code_checker(request, solution, language, question_hit, username=user.username)

            if verdict == "error":
                context["error"] = "There's some error in your code. Please check and retry."
                context["code"] = solution
                context["language"] = language

                return render(request, 'dashboard/question.html', context)
            else:
                if verdict == True:
                    context["result"] = "Correct Answer"
                else:
                    context["result"] = "Wrong Answer"

                context["time_taken"] = round(time_taken, 2)
                Submission.objects.create(user=user.username, question_hit=question_hit, time_taken=time_taken,
                                          verdict=verdict, solution=solution, language=language).save()
        else:
            return redirect('/auth/')
    code = Submission.objects.filter(user=user.username, question_hit=hit).order_by('-time_stamp')
    if code.count() > 0:
        context["code"] = code.first().solution
        context["language"] = code.first().language
    else:
        context["code"] = ""
        context["language"] = "c_cpp"

    return render(request, 'dashboard/question.html', context)


@login_required
def submissions_view(request):
    user = request.user
    context = {
        "title": "Submissions",
        "submissions": Submission.objects.filter(user=user).order_by('-time_stamp')
    }

    return render(request, "dashboard/submissions.html", context)


@login_required
def staff_view(request):
    questions = Question.objects.all().order_by("-time_stamp")
    mcqquestions = MCQQuestion.objects.all().order_by("-time_stamp")
    if request.user.is_staff:
        context = {
            "title": "Staff Dashboard",
            "questions": questions,
            "mcqquestions": mcqquestions
        }
        return render(request, "dashboard/staffdash.html", context)
    else:
        return redirect("/dashboard/")


@login_required
def add_code_question_view(request):
    if request.user.is_staff:
        context = {
            "title": "Add Question"
        }
        if request.method == "POST":
            title = request.POST.get('title')
            difficulty = request.POST.get('difficulty')
            topic = request.POST.get('topic')
            subtopic = request.POST.get('subtopic')
            subsubtopic = request.POST.get('subsubtopic')
            category = request.POST.get('category')
            subcategory = request.POST.get('subcategory')
            subsubcategory = request.POST.get('subsubcategory')
            question = request.POST.get('question')
            input1 = request.POST.get('input1')
            input2 = request.POST.get('input2')
            output1 = request.POST.get('output1')
            output2 = request.POST.get('output2')

            time_limit = 1
            hit = gen_hit(title)

            Question.objects.create(title=title, question=question, difficulty=difficulty, hit=hit, topic=topic,
                                    subtopic=subtopic, subsubtopic=subsubtopic, category=category, subcategory=subcategory, subsubcategory=subsubcategory,
                                    time_limit=time_limit).save()
            IO.objects.create(question_hit=hit, io_number=1, input=input1, output=output1)
            IO.objects.create(question_hit=hit, io_number=2, input=input2, output=output2)

            return redirect('/staff/')
        return render(request, "dashboard/add_code_question.html", context)
    else:
        return redirect("/")

@login_required
def add_mcq_question_view(request):
    if request.user.is_staff:
        context = {
            "title": "Add Question"
        }

        if request.method == "POST":
            question = request.POST.get('question')
            difficulty = request.POST.get('difficulty')
            topic = request.POST.get('topic')
            subtopic = request.POST.get('subtopic')
            subsubtopic = request.POST.get('subsubtopic')
            category = request.POST.get('category')
            subcategory = request.POST.get('subcategory')
            subsubcategory = request.POST.get('subsubcategory')
            hit = gen_hit(question)

            MCQQuestion.objects.create(question=question, difficulty=difficulty, hit=hit, topic=topic,
                                    subtopic=subtopic, subsubtopic=subsubtopic, category=category,
                                    subcategory=subcategory, subsubcategory=subsubcategory).save()
            return redirect('/staff/add_mcq_solution/' + hit)

        return render(request, "dashboard/add_mcq_question.html", context)
    else:
        return redirect("/")


@login_required
def add_mcq_solution_view(request, hit):
    try:
        question = MCQQuestion.objects.get(hit=hit)
    except:
        return redirect('/')
    other_solutions = MCQSolution.objects.filter(question_hit=hit)

    context = {
        'title': 'Add Solution',
        'question': question,
        'solutions': other_solutions
    }

    if request.method == "POST":
        solution = request.POST.get('solution')
        correctness = request.POST.get('correctness')

        MCQSolution.objects.create(question_hit=hit, solution=solution, correctness=correctness).save()

        if request.POST.get('submit') == 'Finish':
            return redirect('/')

    return render(request, "dashboard/add_mcq_solution.html", context)