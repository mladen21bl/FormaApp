from django import forms

class StudentForm(forms.Form):
    ime = forms.CharField(max_length=100)
    prezime = forms.CharField(max_length=100)
    broj_indeksa = forms.CharField(max_length=20)