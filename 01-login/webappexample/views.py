import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect, get_object_or_404
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.db import transaction
from Userdata.models import Goal, Step, SubTask, Progress
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta


oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def index(request):

    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )


def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("userhome")))


# def login(request):
#     # return oauth.auth0.authorize_redirect(
#     #     request, request.build_absolute_uri(reverse("callback"))
#     # )
#     callback_url = request.build_absolute_uri(reverse("callback"))
#     print(f"Constructed callback URL: {callback_url}")  # Or use a logger

#     return oauth.auth0.authorize_redirect(
#         request, callback_url)

def login(request):
    callback_url = request.build_absolute_uri(reverse("callback"))
    print(f"Constructed callback URL: {callback_url}")  # For debugging
    return oauth.auth0.authorize_redirect(request, callback_url)


def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def userhome(request):
    return render(request, "userhome.html", context={"session": request.session.get("user")})

def creategoaltitle(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        stepoption = request.POST.get('stepOption')

        request.session['title'] = title
        request.session['startdate'] = startdate
        request.session['enddate'] = enddate

        if stepoption == 'manual':
            return render(request, 'manualtaskcreation.html', context={"session": request.session.get("user")})
        elif stepoption =='automatic':
            return render(request, 'automatictaskcreation.html', context={"session": request.session.get("user")})

    return redirect('userhome')

def save_manual_goal_with_steps(request):
    if request.method == 'POST':
        title = request.session.get('title')
        startdate = request.session.get('startdate')
        enddate = request.session.get('enddate')
        user = request.session.get("user")["userinfo"]["sub"]

        with transaction.atomic():
            # Create the goal entry
            goal = Goal.objects.create(user=user, title=title, start_date=startdate, end_date=enddate)

            # Iterate over the steps based on how many steps were submitted
            step_counter = 0
            while True:
                step_name_key = f'stepname_{step_counter + 1}'
                step_weightage_key = f'stepweightage_{step_counter + 1}'

                if step_name_key not in request.POST:
                    break

                step_name = request.POST.get(step_name_key)
                step_weightage = request.POST.get(step_weightage_key)

                # Create a step entry
                step = Step.objects.create(goal=goal, name=step_name, weightage=step_weightage)

                # Retrieve subtasks for this specific step
                subtask_names = request.POST.getlist(f'subtaskname_{step_counter + 1}[]')
                subtask_weightages = request.POST.getlist(f'subtaskweightage_{step_counter + 1}[]')

                # Create subtask entries
                for subtask_name, subtask_weightage in zip(subtask_names, subtask_weightages):
                    if subtask_name and subtask_weightage:
                        SubTask.objects.create(step=step, name=subtask_name, weightage=subtask_weightage)

                step_counter += 1

        return redirect('goal_list')

    return render(request, 'manualtaskcreation.html')


def save_goal_with_steps(request):
    if request.method == 'POST':
        title = request.session.get('title')
        startdate = request.session.get('startdate')
        enddate = request.session.get('enddate')
        user = request.session.get("user")["userinfo"]["sub"]

        # Create the goal entry
        goal = Goal.objects.create(user=user, title=title, start_date=startdate, end_date=enddate)

        step_names = request.POST.getlist('stepname[]')
        step_weightages = request.POST.getlist('stepweightage[]')

        # Iterate over each step and handle the associated subtasks
        for i in range(len(step_names)):
            step = Step.objects.create(goal=goal, name=step_names[i], weightage=step_weightages[i])

            # Dynamically generate the names for the subtask fields
            subtask_names = request.POST.getlist(f'subtaskname_step{i+1}[]')
            subtask_weightages = request.POST.getlist(f'subtaskweightage_step{i+1}[]')

            # Iterate over the subtasks associated with this step
            for j in range(len(subtask_names)):
                if subtask_names[j] and subtask_weightages[j]:
                    SubTask.objects.create(step=step, name=subtask_names[j], weightage=subtask_weightages[j])

        return redirect('goal_list')

    return render(request, 'manualtaskcreation.html')


@csrf_exempt
@require_POST
def update_progress(request):
    goal_id = request.POST.get('goal_id')
    step_id = request.POST.get('step_id')
    subtask_id = request.POST.get('subtask_id')
    completed = 'completed' in request.POST

    user = request.session["user"]["userinfo"]["sub"]

    progress, created = None, None
    if subtask_id:
        progress, created = Progress.objects.get_or_create(
            user=user, goal_id=goal_id, step_id=step_id, subtask_id=subtask_id
        )
    elif step_id:
        progress, created = Progress.objects.get_or_create(
            user=user, goal_id=goal_id, step_id=step_id
        )
    else:
        progress, created = Progress.objects.get_or_create(
            user=user, goal_id=goal_id
        )

    progress.completed = completed
    progress.save()

    return redirect('goal_list')

def goal_list(request):
    user = request.session.get("user")["userinfo"]["sub"]
    goals = Goal.objects.filter(user=user)
    
    goal_progress = []
    for goal in goals:
        steps = goal.steps.all()
        
        total_weight = sum(step.weightage for step in steps)
        completed_weight = 0
        
        step_progress = []
        for step in steps:
            subtasks = step.subtasks.all()
            
            step_total_weight = sum(subtask.weightage for subtask in subtasks)
            step_completed_weight = sum(
                subtask.weightage for subtask in subtasks 
                if subtask.progress_set.filter(completed=True).exists()
            )
            
            step_completed_percentage = (step_completed_weight / step_total_weight) * 100 if step_total_weight > 0 else 0
            step_progress.append({
                'step': step,
                'completed_percentage': step_completed_percentage,
            })
            
            completed_weight += (step.weightage * (step_completed_percentage / 100))
        
        goal_completed_percentage = (completed_weight / total_weight) * 100 if total_weight > 0 else 0
        
        goal_progress.append({
            'goal': goal,
            'completed_percentage': goal_completed_percentage,
            'steps': step_progress,
        })

    return render(request, 'goal_list.html', {
        'goal_progress': goal_progress,
        'session': request.session.get("user"),
    })

@require_POST
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    goal.delete()
    return redirect('goal_list')

def userprogress(request):
    user = request.session.get("user")["userinfo"]["sub"]
    goals = Goal.objects.filter(user=user)

    goal_data = []

    for goal in goals:
        steps = goal.steps.all()
        total_subtasks = sum(step.subtasks.count() for step in steps)
        duration_days = (goal.end_date - goal.start_date).days + 1
        required_per_day = total_subtasks / duration_days

        completed_subtasks = Progress.objects.filter(goal=goal, completed=True).count()
        days_since_start = (datetime.now().date() - goal.start_date).days + 1
        required_completed_by_now = required_per_day * days_since_start

        if completed_subtasks >= required_completed_by_now:
            progress_color = 'green'
        elif completed_subtasks >= required_per_day * (days_since_start - 1):
            progress_color = 'orange'
        else:
            progress_color = 'red'

        completed_percentage = (completed_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0

        goal_data.append({
            'goal': goal,
            'total_subtasks': total_subtasks,
            'completed_subtasks': completed_subtasks,
            'required_per_day': required_per_day,
            'completed_percentage': completed_percentage,
            'progress_color': progress_color,
        })

    return render(request, 'userprogress.html', {
        'goal_data': goal_data,
        'session': request.session.get("user"),
    })