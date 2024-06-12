from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.


# valid year

def valid_year(value):
    if value < 1400 or value > 2100:
        raise ValidationError(f'{value} is not a vlaide year')

class CompanyData(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, default=None, null=True)
    domain = models.CharField(max_length=100, default=None, null=True)
    year_founded = models.IntegerField(validators=[valid_year], default=None, null=True)
    industry = models.CharField(max_length=100, default=None, null=True)
    size_range = models.CharField(max_length=50, default=None, null=True)
    locality = models.CharField(max_length=100, default=None, null=True)
    country = models.CharField(max_length=50, default=None, null=True)
    linkedin_url = models.URLField(max_length=200, default=None, null=True)
    current_employee_estimate = models.IntegerField(default=None, null=True)
    total_employee_estimate = models.IntegerField(default=None, null=True)


    def __str__(self) -> str:
        return str(self.id)