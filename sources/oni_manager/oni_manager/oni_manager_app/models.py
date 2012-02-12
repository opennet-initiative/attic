# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

SATUS_CHOICES = ((10, 'nicht freigeschaltet'),
                 (20, 'normal'),
                 (30, 'aktiv'),
                 (40, 'Vorstand'),
                 (50, 'ausgeschieden'),
                 (60, 'nicht freigeschaltet')
                 )

class Bankkonto(models.Model):
    kontonummer = models.IntegerField()
    blz = models.IntegerField()
    class Meta:
        verbose_name_plural="Bankkonten"
    
class Anschrift(models.Model):
    strasse = models.CharField(max_length=100)
    hausnummer = models.CharField(max_length=100)
    plz = models.CharField(max_length=10)
    ort = models.CharField(max_length=100)
    class Admin:
        list_display = ('ort','strasse')
    class Meta:
        verbose_name_plural="Anschriften"
    
class RegistrationSession(models.Model):
    key = models.CharField(max_length=40)
    user = models.OneToOneField(User)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Mitglied(models.Model):
    user = models.OneToOneField(User)
    telefon = models.CharField(max_length=100)
    geburtsdatum = models.DateField()
    mitgliedseit = models.DateField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    foerdermitglied = models.BooleanField("Fördermitglied")
    bankkonto = models.OneToOneField(Bankkonto)
    anschrift = models.OneToOneField(Anschrift)
    bemerkung = models.TextField()
    nickname = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='avatars')
    
    def __unicode__(self):
        return self.nickname

    class Meta:
        ordering = ['status']
        verbose_name_plural="Mitglieder"
