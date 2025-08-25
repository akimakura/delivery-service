from fastapi import APIRouter
from app.schemas import Envelope
from app.tasks.jobs import compute_costs as compute_costs_task


router = APIRouter(tags=["tasks"])

@router.post("/tasks/compute-costs", response_model=Envelope)
def manual_compute():
    """
    Ручной запуск пересчёта стоимости доставки.
    """
    res = compute_costs_task.delay()
    return {"success": True, "data": {"task_id": res.id}}
