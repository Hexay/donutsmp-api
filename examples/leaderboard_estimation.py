import asyncio
import math
import os
import time

from dotenv import load_dotenv

from donut import DonutClient, format_number

load_dotenv()

leaderboard_type = "money"
start_page = 1
end_page = 40000

client: DonutClient = None
request_count = 0


async def main():
    global client, request_count
    keys = os.getenv("API_KEYS").split("\n")
    async with DonutClient(keys) as client:
        request_count = 0
        start_time = time.perf_counter()
        total_estimation, uncertainty = await estimate_leaderboard(leaderboard_type, start_page, end_page)
        elapsed = time.perf_counter() - start_time
        
        pct_uncertainty = (uncertainty / total_estimation * 100) if total_estimation else 0
        print(f"Total: {format_number(total_estimation)} ± {pct_uncertainty:.2f}%")
        print(f"Requests: {request_count} | Time: {elapsed:.2f}s")


async def estimate_leaderboard(leaderboard_type, start_page, end_page):
    start_total, start_max, start_min = await sum_page(leaderboard_type, start_page, min_max=True)
    
    if start_page == end_page:
        return start_total, 0
    
    end_total, end_max, end_min = await sum_page(leaderboard_type, end_page, min_max=True)
    inner_total, inner_uncertainty = await estimate_inner(
        leaderboard_type, start_page + 1, end_page - 1, start_min, end_max
    )
    return start_total + end_total + inner_total, inner_uncertainty


async def estimate_inner(leaderboard_type, start_page, end_page, start_value, end_value):
    if start_page > end_page:
        return 0, 0
    
    if start_page == end_page:
        return await sum_page(leaderboard_type, start_page), 0

    final_threshold = find_threshold(start_page, start_value, end_value)
    if end_value / start_value > final_threshold:
        return exponential_regression_estimate(start_value, end_value, end_page - start_page + 1)

    golden_ratio = 0.382
    split_page = start_page + int((end_page - start_page + 1) * golden_ratio)
    split_total, split_min, split_max = await sum_page(leaderboard_type, split_page, min_max=True)
    
    left, right = await asyncio.gather(
        estimate_inner(leaderboard_type, start_page, split_page - 1, start_value, split_max),
        estimate_inner(leaderboard_type, split_page + 1, end_page, split_min, end_value)
    )
    
    total = split_total + left[0] + right[0]
    uncertainty = left[1] + right[1]
    return total, uncertainty

PAGE_THRESHOLDS = [(1000, 0.95), (5000, 0.94), (15000, 0.85), (float('inf'), 0.84)]
ROC_ADJUSTMENTS = [(0.5, 0.03), (0.2, 0.01), (0.05, -0.01), (float('-inf'), -0.03)]
def find_threshold(page, start_value, end_value):
    base = next(t for p, t in PAGE_THRESHOLDS if page < p)
    roc = (start_value - end_value) / start_value if start_value else 0
    adj = next(a for r, a in ROC_ADJUSTMENTS if roc > r)
    return max(0.80, min(1, base + adj))

async def sum_page(leaderboard_type, page, min_max=False):
    leaderboard = await get_page(leaderboard_type, page)
    total = sum(entry.value for entry in leaderboard)
    
    if min_max:
        return total, leaderboard[0].value, leaderboard[-1].value
    
    return total

async def get_page(leaderboard_type, page):
    global request_count
    request_count += 1
    leaderboard = await client.leaderboards(leaderboard_type, page)
    return leaderboard

def exponential_regression_estimate(start_value, end_value, num_pages):
    if start_value <= 0 or end_value <= 0:
        return start_value * num_pages * 45, 0
    
    ln_start = math.log(start_value)
    ln_end = math.log(end_value)
    decay_rate = (ln_start - ln_end) / num_pages
    total = (start_value / decay_rate) * (1 - math.exp(-decay_rate * num_pages)) * 45
    uncertainty = (start_value-end_value)*0.5*num_pages*45
    
    return total, uncertainty

if __name__ == "__main__":
    asyncio.run(main())
