from django.db import models

# Create your models here.

SATUS_CHOICES = ((1, 'nicht freigeschaltet'),
                 (2, 'normal'),
                 (3, 'aktiv'),
                 (4, 'Vorstand'),
                 (5, 'ausgeschieden')
                 )

class Bankkonto(models.Model):
    kontonummer = models.IntegerField()
    blz = models.IntegerField()
    
class Anschrift(models.Model):
    strasse = models.CharField(max_length=100)
    hausnummer = models.CharField(max_length=100)
    plz = models.CharField(max_length=10)
    ort = models.CharField(max_length=100)
    
class Mitglied(models.Model):
    vorname = models.CharField(max_length=100)
    nachname = models.CharField(max_length=100)
    email = models.CharField(max_length=300)
    passwordHash = models.CharField(max_length=100)
    telefon = models.CharField(max_length=100)
    geburtsdatum = models.DateField()
    mitgliedseit = models.DateField()
    status = models.IntegerField(choices=SATUS_CHOICES, default=1)
    foerdermitglied = models.BooleanField()
    bankkonto = models.OneToOneField(Bankkonto)
    anschrift = models.OneToOneField(Anschrift)
    bemerkung = models.TextField()
    nickname = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='avatars')