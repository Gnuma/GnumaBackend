# django imports
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
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True, related_name = 'gnuma_user')
    classM = models.ForeignKey(Class, on_delete = models.CASCADE) 
    FREE = 'Free'
    PRO = 'Pro'
    BUSINESS = 'Business'
    LEVELS = (
        (FREE, 'Free user'),
        (PRO, 'Pro user'),
        (BUSINESS, 'Business user'),
    )
    level = models.CharField(max_length = 8, choices = LEVELS, default = FREE)
    adsCreated = models.IntegerField(default = 0)
    def __str__(self):
        return User.__str__(self.user)


class Ad(models.Model):
    description = models.CharField(max_length = 280)
    condition = models.IntegerField()
    price = models.FloatField()
    book = models.ForeignKey(Book, on_delete = models.CASCADE, blank = True, null = True)
    seller = models.ForeignKey(GnumaUser, on_delete = models.CASCADE)
    enabled = models.BooleanField(default = True)
    def __str__(self):
        return GnumaUser.__str__(self.seller)+":"+self.description


class Queue_ads(models.Model):
    ad = models.ForeignKey(Ad, on_delete = models.CASCADE)
    isbn = models.CharField(max_length = 13)
    book_title = models.CharField(max_length = 50)
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.ad.__str__()+" "+self.book_title+" "+str(self.created)


class ImageAd(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    ad = models.ForeignKey(Ad, on_delete = models.CASCADE, related_name = 'image_ad', blank = True, null = True)
    image = models.ImageField(upload_to = 'items/')

    def __str__(self):
        if self.ad == None:
            return '{}'.format(self.image.url)
        return '{} --> {}'.format(Ad.__str__(self.ad), self.image.url)

#
# V2 models
#
class Comment(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    is_edited = models.BooleanField(default = False)
    content = models.CharField(max_length = 200)
    item = models.ForeignKey(Ad, on_delete = models.CASCADE, related_name = 'comment_ad', blank = True, null = True)
    parent = models.ForeignKey("self", on_delete = models.CASCADE, related_name = 'parent_child', blank = True, null = True)
    user = models.ForeignKey(GnumaUser, on_delete = models.CASCADE)

    def __str__(self):
        if self.item == None:
            return self.parent.__str__()+" "+self.content
        else:
            return self.item.__str__()+" "+self.content


class Report(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    comment = models.ForeignKey(Comment, on_delete = models.CASCADE)
    sender = models.ForeignKey(GnumaUser, on_delete = models.CASCADE)
    content = models.CharField(max_length = 200)

    def __str__(self):
        return self.sender.__str__() + " " + self.content