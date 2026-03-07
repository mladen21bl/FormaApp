from django.shortcuts import render, redirect
from .forms import StudentForm
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.conf import settings

def index(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            # Spremamo podatke u session
            request.session["ime"] = form.cleaned_data["ime"]
            request.session["prezime"] = form.cleaned_data["prezime"]
            request.session["broj_indeksa"] = form.cleaned_data["broj_indeksa"]

            # Preusmjeravanje na test.html
            return redirect("test")  # "test" je ime URL-a koji pokazuje na test.html
    else:
        form = StudentForm()

    return render(request, "FormaApp/index.html", {"form": form})





def test(request):
    # Preuzimanje podataka iz session-a
    ime = request.session.get("ime", "")
    prezime = request.session.get("prezime", "")
    broj_indeksa = request.session.get("broj_indeksa", "")

    if request.method == "POST":
        # Skupljanje osnovnih polja
        podaci = {
            "ime": ime,
            "prezime": prezime,
            "broj_indeksa": broj_indeksa,
            "naziv": request.POST.get("naziv", ""),
            "oblik": request.POST.get("oblik", ""),
            "neto_kolicina": request.POST.get("neto_kolicina", ""),
            "jedinica_kolicina": request.POST.get("jedinica_kolicina", ""),
            "tip_ambalaze": request.POST.get("tip_ambalaze", ""),
            "materijal_ambalaze": request.POST.get("materijal_ambalaze", ""),
            "temp_min": request.POST.get("temp_min", ""),
            "temp_max": request.POST.get("temp_max", ""),
            "cuva_od_svjetlosti": "Da" if request.POST.get("cuva_od_svjetlosti") else "Ne",
            "cuva_od_vlage": "Da" if request.POST.get("cuva_od_vlage") else "Ne",
            "serija": request.POST.get("serija", ""),
            "rok_trajanja": request.POST.get("rok_trajanja", ""),
            "proizvodjac": request.POST.get("proizvodjac", ""),
            "uvoznik": request.POST.get("uvoznik", ""),
            "distributer": request.POST.get("distributer", ""),
            "zemlja_porijekla": request.POST.get("zemlja_porijekla", ""),
            "namena": request.POST.get("namena", ""),
            "doza": request.POST.get("doza", ""),
            "jedinica_doza": request.POST.get("jedinica_doza", ""),
            "nacin_uzimanja": request.POST.get("nacin_uzimanja", ""),
            "opis_uzimanja": request.POST.get("opis_uzimanja", ""),
            "trajanje_primjene": request.POST.get("trajanje_primjene", ""),
            "all_ingredients": request.POST.get("all_ingredients", ""),
            "disclaimer": request.POST.get("disclaimer", ""),
            "nutrient_comment": request.POST.get("nutrient_comment", "")
        }

        # Dinamičke tabele: sastojci
        sastojci = []
        i = 0
        while f"sastojak_{i}" in request.POST:
            sastojci.append({
                "naziv": request.POST.get(f"sastojak_{i}", ""),
                "kolicina_doz": request.POST.get(f"kolicina_doz_{i}", ""),
                "percent_nrv": request.POST.get(f"percent_nrv_{i}", ""),
                "na_100g": request.POST.get(f"na_100g_{i}", ""),
            })
            i += 1
        podaci["sastojci"] = sastojci

        # Dinamičke tabele: nutritivna vrijednost
        nutrienti = []
        i = 0
        while f"nutrient_{i}" in request.POST:
            nutrienti.append({
                "naziv": request.POST.get(f"nutrient_{i}", ""),
                "kolicina_doz": request.POST.get(f"kolicina_doz_nutrient_{i}", ""),
                "percent_nrv": request.POST.get(f"percent_nrv_nutrient_{i}", ""),
                "na_100g": request.POST.get(f"na_100g_nutrient_{i}", ""),
            })
            i += 1
        podaci["nutrienti"] = nutrienti

        # Dinamičke sekcije: biljna droga
        # Biljna droga
        biljne_droge = []
        i = 0
        while f"biljka_sr_{i}" in request.POST:
            biljne_droge.append({
                "sr": request.POST.get(f"biljka_sr_{i}", ""),
                "lat": request.POST.get(f"biljka_lat_{i}", ""),
                "dio": request.POST.get(f"dio_biljke_{i}", ""),
                "stanje": request.POST.get(f"stanje_biljke_{i}", ""),
                "rastvarac": request.POST.get(f"rastvarac_{i}", ""),
                "der": request.POST.get(f"der_{i}", ""),
                "standardizacija_proc": request.POST.get(f"standardizacija_proc_{i}", ""),
                "standardizacija_supstanca": request.POST.get(f"standardizacija_supstanca_{i}", ""),
                "zemlja": request.POST.get(f"zemlja_porijekla_{i}", ""),
                "kolicina": request.POST.get(f"kolicina_biljna_{i}", ""),
                "jedinica": request.POST.get(f"jedinica_biljna_{i}", ""),
                "poruka": request.POST.get(f"poruka_{i}", "")
            })
            i += 1
        podaci["biljna_droga"] = biljne_droge

        # Aktivne supstance
        aktivne = []
        i = 0
        while f"aktivna_naziv_{i}" in request.POST:
            aktivne.append({
                "naziv": request.POST.get(f"aktivna_naziv_{i}", ""),
                "hemijski_oblik": request.POST.get(f"hemijski_oblik_{i}", ""),
                "kolicina": request.POST.get(f"kolicina_aktivna_{i}", ""),
                "jedinica": request.POST.get(f"jedinica_aktivna_{i}", "")
            })
            i += 1
        podaci["aktivne_supstance"] = aktivne

        # Sastavljanje emaila koristeći template
        html_content = render_to_string("FormaApp/email_template.html", podaci)
        email = EmailMessage(
            subject=f"Prijava dodatka prehrani - {ime} {prezime}",
            body=html_content,
            from_email=settings.CENTRAL_EMAIL,        # tvoj centralni mejl
            to=[settings.PROFESOR_EMAIL],             # testni “profesorov” mejl
        )
        email.content_subtype = "html"  # omogućava HTML
        email.send()

        return redirect("success")

    return render(request, "FormaApp/test.html", {
        "ime": ime,
        "prezime": prezime,
        "broj_indeksa": broj_indeksa
    })

def success(request):
    return render(request, "FormaApp/success.html")