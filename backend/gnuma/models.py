from django.db import models
from django.contrib.auth.models import User

class Office(models.Model):
    name = models.CharField(max_length = 50)
    cap = models.CharField(max_length = 5)
    MD = 'MD'
    SP = 'SP'
    LEVEL = (
        (SP, 'Scuola superiore'),
        (MD, 'Scuola media')
    )
    level = models.CharField(max_length = 2, choices = LEVEL, default = SP)

    def is_highschool(self):
        return self.level is self.SP    
    
    def __str__(self):
        return self.name

class Class(models.Model):
    P  = '1'
    S = '2'
    T = '3'
    Q = '4'
    QU = '5'
    GRADE = (
        (P, 'Primo'),
        (S, 'Secondo'),
        (T, 'Terzo'),
        (Q, 'Quarto'),
        (QU, 'Quinto'),
    )
    grade = models.CharField(max_length = 1, choices = GRADE, default = P)
    A = 'A'
    B = 'B'
    C = 'C'
    DIVISION = (
        (A , 'Seziona A'),
        (B , 'Seziona B'),
        (C , 'Seziona C'),
    )
    division = models.CharField(max_length = 1, choices = DIVISION, default = A)
    office = models.ForeignKey(Office, on_delete = models.CASCADE)
    
    def __str__(self):
        return self.grade+" "+self.division+" "+self.office.name

class Book(models.Model):
    title = models.CharField(max_length = 50)
    author = models.CharField(max_length = 50, default = 'Sconosciuto', blank = True)
    isbn = models.CharField(max_length = 13, primary_key = True)
    classes = models.ManyToManyField(Class)

    def __str__(self):
        return self.title
    
class GnumaUser(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)
    classM = models.ForeignKey(Class, on_delete = models.CASCADE) 
    FREE = 'Free'
    PRO = 'Pro'
    BUSINESS = 'Business'
    LEVELS = (
        (FREE, 'Free user'),
        (PRO, 'Pro user'),
        (BUSINESS, 'Business user'),
    )
    # The following fields hasn't been migrated yet
    level = models.CharField(max_length = 8, choices = LEVELS, default = FREE)
    adsCreated = models.IntegerField(default = 0)
    def __str__(self):
        return User.__str__(self.user)

class Ad(models.Model):
    title = models.CharField(max_length = 200)
    image = models.CharField(max_length = 2000, blank = True, null = True) # 2000 ? IE MAX URL LENGTH
    price = models.FloatField()
    book = models.ForeignKey(Book, on_delete = models.CASCADE, blank = True, null = True)
    seller = models.ForeignKey(GnumaUser, on_delete = models.CASCADE)
    enabled = models.BooleanField(default = True)
    def __str__(self):
        return GnumaUser.__str__(self.seller)+":"+self.title

class Queue_ads(models.Model):
    ad = models.ForeignKey(Ad, on_delete = models.CASCADE)
    isbn = models.CharField(max_length = 13)
    book_title = models.CharField(max_length = 50)
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.ad.__str__()+" "+self.book_title+" "+str(self.created)
