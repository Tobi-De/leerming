from .models import ScheduleManager
from django_q.models import Task

def run_schedule_manager(manager_id: int):
    try:
        manager = ScheduleManager.objects.get(pk=manager_id)
    except ScheduleManager.DoesNotExist:
        return

    manager.notify_reviewers()

def update_manager_result_task(task:Task):
    try:
        manager = ScheduleManager.objects.get(pk=task.kwargs["manager_id"])
    except ScheduleManager.DoesNotExist:
        return
    manager.result_task = task
    manager.save()