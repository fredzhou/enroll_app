from django.db import models

# Create your models here.
class ContactModel(models.Model):
    business_unit = models.CharField(max_length=100)
    nsn_intra_id =  models.CharField(max_length=10)
    employee_number = models.IntegerField()
    co_author_info = models.CharField(max_length=100)
    email_address = models.CharField(max_length=50)
    gitlab_repository = models.CharField(max_length=100)

    def __unicode__(self):
        return nsn_intra_id + ', ' + str(self.employee_number)
