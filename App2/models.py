from django.db import models
import random


class Course(models.Model):
    name = models.CharField(primary_key=True, max_length=30)
    img = models.ImageField()
    info = models.CharField(max_length=100)
    price = models.IntegerField()

class AdminData(models.Model):
    email = models.EmailField(max_length=30,)
    username = models.CharField(max_length=30,primary_key=True)
    password = models.CharField(max_length=30)

class usrData(models.Model):
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    email = models.EmailField( max_length=30,unique=True,primary_key=True)
    mobile = models.IntegerField()
    gender = models.CharField(max_length=10)
    edu = models.CharField(max_length=40)
    cors = models.CharField(max_length=30)
    address = models.CharField(max_length=30)
    pswd = models.CharField(max_length=30)
    usr = models.CharField(unique=True, max_length=30)


class cart(models.Model):
    usrid = models.IntegerField()
    usr= models.CharField(max_length=30)
    course = models.CharField(max_length=30)
    