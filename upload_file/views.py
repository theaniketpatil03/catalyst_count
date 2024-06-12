
from django.shortcuts import render
from django.http import JsonResponse
import os
from .models import CompanyData
from loguru import logger
import csv
import threading
import threading
import asyncio
import concurrent.futures
import pandas as pd
from collections import deque
import math


background_lock = threading.Lock()

def home(request):
    if request.method == 'POST':
        file = request.FILES['file'].read()
        fileName = request.POST['filename']
        existingPath = request.POST['existingPath']
        end = request.POST['end']
        nextSlice = request.POST['nextSlice']

        # Decode file content
        decoded_file = file.decode('utf-8')
        rows = decoded_file.strip().split('\n')
        csv_data = [row.split(',') for row in rows]

        logger.info(f"Chunk received: {len(csv_data)} lines")

        if file == "" or fileName == "" or existingPath == "" or end == "" or nextSlice == "":
            res = JsonResponse({'data': 'Invalid Request'})
            return res
        else:
            if existingPath == 'null':
                path = os.path.join('media', fileName)
                mode = 'wb+'
            else:
                path = os.path.join('media', existingPath)
                mode = 'ab+'

            with background_lock:
                with open(path, mode) as destination:
                    destination.write(file)

            if int(end):
                asyncio.run(process_csv_data(path))
                res = JsonResponse({'data': 'Uploaded Successfully', 'existingPath': fileName})
            else:
                res = JsonResponse({'existingPath': fileName})
            return res

    return render(request, 'index.html')


async def process_csv_data(file_path):
    logger.info(f"Starting CSV data processing for {file_path}")
    loop = asyncio.get_event_loop()

    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, create_users_from_csv_parallel, file_path)

def process_csv_batch(batch):
    logger.info('inside batch storing')
    batch_data = []
    file_entry = None
    for _, row in batch.iterrows():
        # logger.info(row)
        try:
            file_entry = CompanyData(
                id =  row.iloc[0],
                name = row.get('name', None),
                domain = row.get('domain', None),
                year_founded = int(row.get('year founded')) if not math.isnan(row.get('year founded')) else None,
                industry = row.get('industry', None),
                size_range = row.get('size range', None),
                locality = row.get('locality', None),
                country = row.get('country', None),
                linkedin_url = row.get('linkedin url', None),
                current_employee_estimate = row.get('current employee estimate', None),
                total_employee_estimate = row.get('total employee estimate', None),
            )

            # logger.critical(file_entry)
            batch_data.append(file_entry)
            # logger.debug(row[0])
            # logger.debug(row['name'])
        except Exception as e:
            logger.error(e)
    # Bulk create entries for better performance
    if file_entry:
        result = CompanyData.objects.bulk_create(batch_data)
        logger.warning(result)

def create_users_from_csv_parallel(csv_file):
    chunk_size = 100000
    max_workers = 4

    with pd.read_csv(csv_file, chunksize=chunk_size) as reader:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            tasks = [executor.submit(process_csv_batch, chunk) for chunk in reader]
            concurrent.futures.wait(tasks)

    logger.info(f"CSV data processed and stored for {csv_file}")


def quer_data(request):
    try:
        unique_years = list(CompanyData.objects.values_list('year_founded', flat=True).distinct())
        unique_industry = list(CompanyData.objects.values_list('industry', flat=True).distinct())
        unique_size_range = list(CompanyData.objects.values_list('size_range', flat=True).distinct())
        unique_locality = list(CompanyData.objects.values_list('locality', flat=True).distinct())
        unique_country = list(CompanyData.objects.values_list('country', flat=True).distinct())
        unique_current_employee = list(CompanyData.objects.values_list('current_employee_estimate', flat=True).distinct())
        unique_total_employee = list(CompanyData.objects.values_list('total_employee_estimate', flat=True).distinct())

        context = {
            'unique_years': unique_years,
            'unique_industry': unique_industry,
            'unique_size_range': unique_size_range,
            'unique_locality': unique_locality,
            'unique_country': unique_country,
            'unique_current_employee': unique_current_employee,
            'unique_total_employee': unique_total_employee,
        }

        if request.method == 'POST':
            funded_year = request.POST.get('funded_year')
            industry = request.POST.get('industry')
            size_range = request.POST.get('size_range')
            locality = request.POST.get('locality')
            country = request.POST.get('country')
            current_employee = request.POST.get('current_employee')
            total_employee = request.POST.get('total_employee')
            # logger.debug(funded_year)


            filters = {}
            if funded_year is not None:
                filters['year_founded'] = funded_year
            if industry is not None:
                filters['industry'] = industry
            if size_range is not None:
                filters['size_range'] = size_range
            if locality is not None:
                filters['locality'] = locality
            if country is not None:
                filters['country'] = country
            if current_employee is not None:
                filters['current_employee_estimate'] = current_employee
            if total_employee is not None:
                filters['total_employee_estimate'] = total_employee

            filters = {key: value for key, value in filters.items() if value is not None}


            results = list(CompanyData.objects.filter(**filters))
            context['table_data'] = results
            # logger.warning(results)

            # return render(request, 'query_data.html', context)


        return render(request, 'query_data.html', context)
    except Exception as e:
        logger.error(e)
        return e