from django.db import models


# Create your models here.
class Currency(models.Model):
    currency_name = models.CharField(max_length=30, null=False)
    currency_buying = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    currency_selling = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    currency_rate_date = models.DateField(auto_now=True)

    def __int__(self):
        return f'{self.currency_name}, {self.currency_rate_date}, {self.currency_buying}, {self.currency_selling}'


#
# class Calculation(models.Model):
#     amount=models.DecimalField(max_digit=15,null=False,blank=True)
#     currency_conversion=models.DecimalField(max_digit=15,null=False,blank=True)
#
#



#
# obje olustuurp update etmek
# database bossa
# save methodyla yarat
# database doluysa güne bak aynı günse
# kaydettiğim son zamandaki
# aynı günse update etme
# objects.update
#
# currency namee göre çek
