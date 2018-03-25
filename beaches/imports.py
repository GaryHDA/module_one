from dirt.models import Beaches, Densities, Source, Codes, Material, Totals, All_Data
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
import datetime
import math
import numpy as np
from numpy import convolve
from scipy.stats import norm
import scipy.stats
from datetime import date
import json
import decimal
from django.db import models
from django.db.models import Sum, Avg, Max, Min
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
