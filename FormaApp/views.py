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
            "porijeklo": request.POST.get("porijeklo", ""),
            "all_ingredients": request.POST.get("all_ingredients", ""),
            "disclaimer": request.POST.get("disclaimer", ""),
            "nutrient_comment": request.POST.get("nutrient_comment", "")
        }

        # 3. Namena i način primjene
        namena = request.POST.get("namena", "")
        doza = request.POST.get("doza", "")
        jedinica_doza = request.POST.get("jedinica_doza", "")
        nacin_uzimanja = request.POST.get("nacin_uzimanja", "")
        opis_uzimanja = request.POST.get("opis_uzimanja", "")
        trajanje_primjene = request.POST.get("trajanje_primjene", "")

        podaci["namena_i_primjena"] = {
            "namena": namena,
            "doza": doza,
            "jedinica_doza": jedinica_doza,
            "nacin_uzimanja": nacin_uzimanja,
            "opis_uzimanja": opis_uzimanja,
            "trajanje_primjene": trajanje_primjene,
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

        # 5. Ograničenja i upozorenja

        ogranicenja = {
            "djeca": bool(request.POST.get("ogranicenja_djeca")),
            "trudnice": bool(request.POST.get("ogranicenja_trudnice")),
            "dojilje": bool(request.POST.get("ogranicenja_dojilje")),
            "hronicni": bool(request.POST.get("ogranicenja_hronicni")),
        }

        mjere_opreza = {
            "djeca": bool(request.POST.get("mjera_djeca")),
            "doziranje": bool(request.POST.get("mjera_doziranje")),
            "zamjena_ishrana": bool(request.POST.get("mjera_zamjena")),
            "obrok": bool(request.POST.get("mjera_obrok")),
            "skladistenje": bool(request.POST.get("mjera_skladistenje")),
        }

        upozorenja = {
            "alergije": bool(request.POST.get("upozorenje_alergije")),
            "lijekovi": bool(request.POST.get("upozorenje_lijekovi")),
            "gi": bool(request.POST.get("upozorenje_gi")),
            "pritisak": bool(request.POST.get("upozorenje_pritisak")),
            "secer": bool(request.POST.get("upozorenje_secer")),
        }

        disclaimer = request.POST.get("disclaimer", "")

        podaci["ogranicenja_i_upozorenja"] = {
            "ogranicenja": ogranicenja,
            "mjere_opreza": mjere_opreza,
            "upozorenja": upozorenja,
            "disclaimer": disclaimer,
        }

        # Dinamičke sekcije: biljna droga
        # Biljna droga
        biljne_droge = []

        biljka_sr = request.POST.getlist("biljka_sr")
        biljka_lat = request.POST.getlist("biljka_lat")
        dio_biljke = request.POST.getlist("dio_biljke")
        stanje_biljke = request.POST.getlist("stanje_biljke")
        rastvarac = request.POST.getlist("rastvarac")
        der = request.POST.getlist("der")
        poruka = request.POST.getlist("poruka")

        standard_proc = request.POST.getlist("standardizacija_proc")
        standard_sup = request.POST.getlist("standardizacija_supstanca")

        zemlja = request.POST.getlist("zemlja_porijekla")

        kolicina = request.POST.getlist("kolicina_biljna")
        jedinica = request.POST.getlist("jedinica_biljna")

        for i in range(len(biljka_sr)):
            # preskoči prazne unose
            if not biljka_sr[i].strip() and not biljka_lat[i].strip():
                continue

            biljne_droge.append({
                "biljka_sr": biljka_sr[i],
                "biljka_lat": biljka_lat[i] if i < len(biljka_lat) else "",
                "dio_biljke": dio_biljke[i] if i < len(dio_biljke) else "",
                "stanje": stanje_biljke[i] if i < len(stanje_biljke) else "",
                "rastvarac": rastvarac[i] if i < len(rastvarac) else "",
                "der": der[i] if i < len(der) else "",
                "poruka": poruka[i] if i < len(poruka) else "",
                "standard_proc": standard_proc[i] if i < len(standard_proc) else "",
                "standard_sup": standard_sup[i] if i < len(standard_sup) else "",
                "zemlja": zemlja[i] if i < len(zemlja) else "",
                "kolicina": kolicina[i] if i < len(kolicina) else "",
                "jedinica": jedinica[i] if i < len(jedinica) else ""
            })

        podaci["biljne_droge"] = biljne_droge

        # Aktivne supstance
        aktivne_supstance = []

        nazivi = request.POST.getlist("aktivna_naziv")
        oblici = request.POST.getlist("hemijski_oblik")
        kolicine = request.POST.getlist("kolicina_aktivna")
        jedinice = request.POST.getlist("jedinica_aktivna")

        for i in range(len(nazivi)):
            if nazivi[i].strip():  # preskoči prazne
                aktivne_supstance.append({
                    "naziv": nazivi[i],
                    "hemijski_oblik": oblici[i] if i < len(oblici) else "",
                    "kolicina": kolicine[i] if i < len(kolicine) else "",
                    "jedinica": jedinice[i] if i < len(jedinice) else ""
                })

        podaci["aktivne_supstance"] = aktivne_supstance

        # BSE/TSE i GMO
        bse_status = request.POST.get("bse_status", "nije_potrebno")
        bse_napomena = request.POST.get("bse_napomena", "")
        podaci["bse_tse"] = {
            "status": bse_status,
            "napomena": bse_napomena
        }

        # Klinička istraživanja
        studije = []

        study_naziv = request.POST.getlist("study_naziv")
        study_tip = request.POST.getlist("study_tip")
        study_godina = request.POST.getlist("study_godina")
        study_doi = request.POST.getlist("study_doi")

        for i in range(len(study_naziv)):
            if not study_naziv[i].strip():
                continue  # preskoči prazne unose
            studije.append({
                "naziv": study_naziv[i],
                "tip": study_tip[i] if i < len(study_tip) else "",
                "godina": study_godina[i] if i < len(study_godina) else "",
                "doi": study_doi[i] if i < len(study_doi) else ""
            })

        podaci["klinicke_studije"] = studije

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