from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Choice, Question
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Account

@csrf_exempt
def reg(request):
    if request.method == "POST":
        body = json.loads(request.body)
        try:
            data=json.loads(request.body)

            login = data.get("login")
            password = data.get("password")

            if not login or not password:
                return JsonResponse(
                    {"error": "login and password required"},
                    status=400
                )

            if Account.objects.filter(login=login).exists():
                return JsonResponse(
                    {"error": "user already exists"},
                )
        
            account = Account.objects.create(
                login=login,
                password=password
            )

            return JsonResponse(
                {
                    "message": "registered successfully",
                    "id": account.id,
                    "login": account.login
                },
                status=201
            )
    
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid json"}, status=400)
    return HttpResponse("Only POST method allowed")

    

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :5
        ]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

@csrf_exempt
def acc_list_create(request):
    if request.method == "GET":
        accounts = Choice.objects.all()
        data = []

        for a in accounts:
            data.append({
                "id": a.id,
                "username": a.username,
                "email": a.email,
                "choice_text": a.choice_text,
                "votes": a.votes,
            })

        return JsonResponse(data, safe=False)

    elif request.method == "POST":
        body = json.loads(request.body)

        a = Choice.objects.create(
            question_id=body.get("question_id"),
            choice_text=body.get("choice_text"),
            votes=body.get("votes", 0),
            username=body.get("username"),
            email=body.get("email"),
        )

        return JsonResponse({
            "id": a.id,
            "username": a.username,
            "email": a.email,
            "choice_text": a.choice_text,
            "votes": a.votes,
        }, status=201)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def acc_detail(request, id):
    try:
        a = Choice.objects.get(id=id)
    except Choice.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    if request.method == "GET":
        return JsonResponse({
            "id": a.id,
            "username": a.username,
            "email": a.email,
            "choice_text": a.choice_text,
            "votes": a.votes,
        })

    elif request.method == "PATCH":
        body = json.loads(request.body)

        if "username" in body:
            a.username = body["username"]
        if "email" in body:
            a.email = body["email"]
        if "choice_text" in body:
            a.choice_text = body["choice_text"]
        if "votes" in body:
            a.votes = body["votes"]

        a.save()

        return JsonResponse({
            "id": a.id,
            "username": a.username,
            "email": a.email,
            "choice_text": a.choice_text,
            "votes": a.votes,
        })

    elif request.method == "DELETE":
        a.delete()
        return JsonResponse({"message": "Deleted"})

    return JsonResponse({"error": "Method not allowed"}, status=405)