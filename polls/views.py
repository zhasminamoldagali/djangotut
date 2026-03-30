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
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

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
            status=400
        )

    account=Account.objects.create(
        login=login,
        password=password
    )

    return JsonResponse(
        {
            "message":"registered successfully",
            "id":account.id,
            "login": account.login
        },
        status=201
    )

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
    return HttpResponse("You're voting on question %s." % question_id)
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
def acc_id_view(req, id):
    if req.method == "GET":
        a = get_object_or_404(Account, pk = id)
        return JsonResponse({
            "Account": a.get_dict()
        })
    if req.method == "DELETE":
        a = get_object_or_404(Account, pk = id)
        a.delete()
        return JsonResponse({
            "message": "Account deleted"
        })
    if req.method == "PUT":
        data = json.loads(req.body)
        a = get_object_or_404(Account, pk=id)

        a.name = data.get("name", a.name)
        a.balance = data.get("balance", a.balance)

        return JsonResponse({
            "message":"Account updated",
            "Account": a.get_dict()
        })

    if req.method == "POST":
        data = json.loads(req.body)
        a = get_object_or_404(Account, pk=id)

        a.name = data.get("name", a.name)
        a.balance = data.get("balance", a.balance)
        a.save()

        return JsonResponse({
            "message": "account updated",
            "Account": a.get_dict
        })
    return JsonResponse({
        "error": "Method not allowed"
    }, status=405)