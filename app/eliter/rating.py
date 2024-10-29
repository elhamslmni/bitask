from math import floor

from django.core.cache import cache
from django.db.models import Avg, Subquery, OuterRef
from django.db.models.functions import TruncDate
from typing import List

from .models import Rating



def get_average_ratings(post_ids : List[int]):

    cache_keys = [f'post_{post_id}_average_rating' for post_id in post_ids]
    cached_data = cache.get_many(cache_keys)

    averages = {}
    missing_post_ids = []


    for post_id, cache_key in zip(post_ids, cache_keys):
        if cache_key in cached_data:
            averages[post_id] = cached_data[cache_key]
        else:
            missing_post_ids.append(post_id)

    if missing_post_ids:
        calculate_avg_rate(missing_post_ids, averages)


    return averages


def calculate_avg_rate(post_ids:List[int], averages):
    daily_averages = Rating.objects.filter(post_id__in=post_ids).annotate(
        day=TruncDate('created_at')
    ).values('post_id', 'day').annotate(
        daily_avg=Avg('rating')
    ).values('post_id', 'daily_avg')

    post_daily_avgs = {}
    for entry in daily_averages:
        post_id = entry['post_id']
        daily_avg = entry['daily_avg']
        if post_id not in post_daily_avgs:
            post_daily_avgs[post_id] = []
        post_daily_avgs[post_id].append(daily_avg)


    overall_averages = {
        post_id: sum(daily_avgs) / len(daily_avgs) if daily_avgs else 0
        for post_id, daily_avgs in post_daily_avgs.items()
    }

    for post_id, rate in overall_averages.items():
        overall_averages[post_id] = floor(rate)


    for post_id, rate in overall_averages.items():
        averages[post_id] = rate
        cache.set(f'post_{post_id}_average_rating', floor(rate), timeout=3600)  # batch set instead


    return averages
