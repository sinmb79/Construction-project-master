from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from civilplan_mcp.updater.standard_updater import update_standard_prices
from civilplan_mcp.updater.wage_updater import update_wage_rates
from civilplan_mcp.updater.waste_updater import update_waste_prices


def build_scheduler(*, start: bool = False) -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(update_wage_rates, CronTrigger(month="1", day="2", hour="9"), id="wage_h1", kwargs={"period": "상반기"})
    scheduler.add_job(update_waste_prices, CronTrigger(month="1", day="2", hour="9"), id="waste_annual")
    scheduler.add_job(update_standard_prices, CronTrigger(month="1", day="2", hour="9"), id="standard_h1", kwargs={"period": "상반기"})
    scheduler.add_job(update_standard_prices, CronTrigger(month="7", day="10", hour="9"), id="standard_h2", kwargs={"period": "하반기"})
    scheduler.add_job(update_wage_rates, CronTrigger(month="9", day="2", hour="9"), id="wage_h2", kwargs={"period": "하반기"})
    if start:
        scheduler.start()
    return scheduler
