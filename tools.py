from monday_api import get_board_items, normalize_item, safe_float, get_column_titles, monday_query
from config import WORK_ORDERS_BOARD_ID, DEALS_BOARD_ID


def fetch_deals() -> list:
    """Fetch all deals with correct column titles"""
    col_map = get_column_titles(DEALS_BOARD_ID)
    items = get_board_items(DEALS_BOARD_ID)
    result = []
    for item in items:
        row = {"name": item.get("name", "Unknown")}
        for col in item.get("column_values", []):
            col_id = col.get("id", "")
            title = col_map.get(col_id, col_id).strip()
            text = col.get("text", "") or ""
            if text.strip() in ["", "null", "None", "-", "N/A", "n/a"]:
                text = None
            row[title] = text
        result.append(row)
    result = [r for r in result if r.get("name") not in ["Deal Name", "name", None]]
    return result


def fetch_work_orders() -> list:
    """Fetch all work orders with correct column titles"""
    col_map = get_column_titles(WORK_ORDERS_BOARD_ID)
    items = get_board_items(WORK_ORDERS_BOARD_ID)
    result = []
    for item in items:
        row = {"name": item.get("name", "Unknown")}
        for col in item.get("column_values", []):
            col_id = col.get("id", "")
            title = col_map.get(col_id, col_id).strip()
            text = col.get("text", "") or ""
            if text.strip() in ["", "null", "None", "-", "N/A", "n/a"]:
                text = None
            row[title] = text
        result.append(row)
    result = [r for r in result if r.get("name") not in ["Deal name masked", "name", None]]
    return result


def tool_get_work_orders(sector=None, status=None):
    trace = {
        "tool": "get_work_orders",
        "params": {"sector": sector, "status": status},
        "board": f"Work Orders (ID: {WORK_ORDERS_BOARD_ID})"
    }
    data = fetch_work_orders()
    if sector:
        data = [d for d in data if d.get("Sector") and sector.lower() in str(d["Sector"]).lower()]
    if status:
        data = [d for d in data if d.get("Execution Status") and status.lower() in str(d["Execution Status"]).lower()]
    trace["records_returned"] = len(data)
    return {"data": data, "trace": trace}


def tool_get_deals(sector=None, stage=None, status=None):
    trace = {
        "tool": "get_deals",
        "params": {"sector": sector, "stage": stage, "status": status},
        "board": f"Deals (ID: {DEALS_BOARD_ID})"
    }
    data = fetch_deals()
    if sector:
        data = [d for d in data if d.get("Sector/service") and sector.lower() in str(d["Sector/service"]).lower()]
    if stage:
        data = [d for d in data if d.get("Deal Stage") and stage.lower() in str(d["Deal Stage"]).lower()]
    if status:
        data = [d for d in data if d.get("Deal Status") and status.lower() in str(d["Deal Status"]).lower()]
    trace["records_returned"] = len(data)
    return {"data": data, "trace": trace}


def tool_pipeline_summary():
    trace = {"tool": "pipeline_summary", "params": {}, "board": "Both boards"}
    deals = fetch_deals()
    work_orders = fetch_work_orders()

    stage_counts = {}
    status_counts = {}
    total_deal_value = 0.0
    open_deals = 0

    for d in deals:
        stage = d.get("Deal Stage") or "Unknown"
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        status = d.get("Deal Status") or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        total_deal_value += safe_float(d.get("Masked Deal value"))
        if str(d.get("Deal Status", "")).strip().lower() == "open":
            open_deals += 1

    sector_counts = {}
    exec_status_counts = {}
    for wo in work_orders:
        sector = wo.get("Sector") or "Unknown"
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
        es = wo.get("Execution Status") or "Unknown"
        exec_status_counts[es] = exec_status_counts.get(es, 0) + 1

    summary = {
        "total_deals": len(deals),
        "open_deals": open_deals,
        "total_deal_value": total_deal_value,
        "deal_stage_distribution": stage_counts,
        "deal_status_distribution": status_counts,
        "total_work_orders": len(work_orders),
        "wo_sector_distribution": sector_counts,
        "wo_execution_status": exec_status_counts,
        "total_billed_value": sum(safe_float(wo.get("Billed Value Incl GST")) for wo in work_orders),
        "total_collected": sum(safe_float(wo.get("Collected Amount")) for wo in work_orders),
        "total_receivable": sum(safe_float(wo.get("Amount Receivable")) for wo in work_orders),
    }
    trace["records_returned"] = len(deals) + len(work_orders)
    return {"data": summary, "trace": trace}


def tool_sector_analysis(sector):
    trace = {"tool": "sector_analysis", "params": {"sector": sector}, "board": "Both boards"}
    all_deals = fetch_deals()
    deals = [d for d in all_deals if d.get("Sector/service") and sector.lower() in str(d["Sector/service"]).lower()]
    all_wo = fetch_work_orders()
    work_orders = [d for d in all_wo if d.get("Sector") and sector.lower() in str(d["Sector"]).lower()]

    deal_statuses = {}
    for d in deals:
        s = d.get("Deal Status") or "Unknown"
        deal_statuses[s] = deal_statuses.get(s, 0) + 1

    deal_stages = {}
    for d in deals:
        s = d.get("Deal Stage") or "Unknown"
        deal_stages[s] = deal_stages.get(s, 0) + 1

    wo_statuses = {}
    for wo in work_orders:
        s = wo.get("Execution Status") or "Unknown"
        wo_statuses[s] = wo_statuses.get(s, 0) + 1

    analysis = {
        "sector": sector,
        "total_deals": len(deals),
        "total_deal_value": sum(safe_float(d.get("Masked Deal value")) for d in deals),
        "deal_status_breakdown": deal_statuses,
        "deal_stage_breakdown": deal_stages,
        "total_work_orders": len(work_orders),
        "total_billed": sum(safe_float(wo.get("Billed Value Incl GST")) for wo in work_orders),
        "total_receivable": sum(safe_float(wo.get("Amount Receivable")) for wo in work_orders),
        "total_collected": sum(safe_float(wo.get("Collected Amount")) for wo in work_orders),
        "wo_status_breakdown": wo_statuses,
    }
    trace["records_returned"] = len(deals) + len(work_orders)
    return {"data": analysis, "trace": trace}


def tool_revenue_analysis():
    trace = {"tool": "revenue_analysis", "params": {}, "board": "Work Orders board"}
    work_orders = fetch_work_orders()

    total_billed = sum(safe_float(wo.get("Billed Value Incl GST")) for wo in work_orders)
    total_collected = sum(safe_float(wo.get("Collected Amount")) for wo in work_orders)

    billing_status = {}
    sector_revenue = {}
    for wo in work_orders:
        s = (wo.get("Billing Status") or wo.get("Invoice Status") or "Unknown").strip()
        if s.lower() in ["billed", "biled", "bllied"]:
            s = "Billed"
        billing_status[s] = billing_status.get(s, 0) + 1
        sector = wo.get("Sector") or "Unknown"
        sector_revenue[sector] = sector_revenue.get(sector, 0) + safe_float(wo.get("Billed Value Incl GST"))

    wo_status_counts = {}
    for wo in work_orders:
        s = wo.get("Execution Status") or "Unknown"
        wo_status_counts[s] = wo_status_counts.get(s, 0) + 1

    analysis = {
        "total_contract_value": sum(safe_float(wo.get("Amount Incl GST")) for wo in work_orders),
        "total_billed": total_billed,
        "total_collected": total_collected,
        "total_receivable": sum(safe_float(wo.get("Amount Receivable")) for wo in work_orders),
        "total_unbilled": sum(safe_float(wo.get("Amount to Bill Incl GST")) for wo in work_orders),
        "collection_rate_pct": round((total_collected / total_billed * 100) if total_billed > 0 else 0, 1),
        "billing_status_breakdown": billing_status,
        "revenue_by_sector": sector_revenue,
        "execution_status_breakdown": wo_status_counts,
        "total_work_orders": len(work_orders),
    }
    trace["records_returned"] = len(work_orders)
    return {"data": analysis, "trace": trace}


TOOLS = {
    "get_work_orders": tool_get_work_orders,
    "get_deals": tool_get_deals,
    "pipeline_summary": tool_pipeline_summary,
    "sector_analysis": tool_sector_analysis,
    "revenue_analysis": tool_revenue_analysis,
}

TOOL_DESCRIPTIONS = """
You have access to these tools. Call them by responding ONLY with JSON like:
{"tool": "tool_name", "params": {"key": "value"}}

1. get_work_orders(sector=None, status=None)
   - Known sectors: Mining, Powerline, Renewables, Railways, Tender, DSP
   - Known statuses: Completed, Not Started, Ongoing, Executed until current month

2. get_deals(sector=None, stage=None, status=None)
   - Known stages: Sales Qualified Leads, Proposal/Commercials Sent, Feasibility,
     Work Order Received, Negotiations, Demo Done, Lead Generated,
     Project Won, Project Lost, Projects On Hold
   - Known statuses: Open, On Hold, Dead

3. pipeline_summary()
   - Full overview of entire pipeline across both boards

4. sector_analysis(sector)
   - Deep dive into one specific sector

5. revenue_analysis()
   - Billing, collection rates, receivables, unbilled amounts
"""