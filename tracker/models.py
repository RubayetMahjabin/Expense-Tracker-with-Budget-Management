from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Sum

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Budget(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f'{self.category.name} - {self.amount}'

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, default='')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    alert_sent = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.check_budget()

    def check_budget(self):
        total_expenses = Expense.objects.filter(category=self.category, user=self.user).aggregate(models.Sum('amount'))['amount__sum'] or 0
        try:
            budget = Budget.objects.get(category=self.category, user=self.user).amount
            if total_expenses > budget and not self.alert_sent:
                self.alert_sent = True  
                self.save()  
        except Budget.DoesNotExist:
            pass

    def __str__(self):
        return f'{self.description} - {self.amount}'