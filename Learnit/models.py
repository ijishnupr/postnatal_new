from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model() 


# Learning module
class Modules(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Learnit module'
    
class Videos(models.Model):
    module = models.ForeignKey(Modules, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/', null=True,blank=True)
    url = models.URLField(null=True,blank=True)
    faq = models.TextField(null=True, blank=True)   
    relatedPost = models.TextField(null=True, blank=True)   
    
    def __str__(self):
        return self.module.name 


class Notes(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Modules, on_delete=models.CASCADE)

    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.customer.firstname + "'s note - "  + self.notes

    class Meta:
        unique_together = ['customer', 'module']


