"""TDD-Tests für die Value Objects im Bounded Context ``identity``."""

import dataclasses

import pytest
from modernesoftwarentwicklungws26.identity.value_objects import (
    Adresse,
    EinladungscodeWert,
    EmailAdresse,
)

# --------------------------------------------------------------------------- #
# EmailAdresse
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "eingabe",
    [
        pytest.param("max.mustermann@example.de", id="standard"),
        pytest.param("anna+wahl@sub.example.com", id="plus-und-subdomain"),
        pytest.param("info@example.museum", id="lange-tld"),
        pytest.param("a@b.de", id="kuerzeste-form"),
        pytest.param("x_y-z%1@my-domain.de", id="erlaubte-sonderzeichen"),
        pytest.param("123@456.de", id="nur-ziffern"),
    ],
)
def test_email_gueltig_bleibt_unveraendert(eingabe: str) -> None:
    assert EmailAdresse(eingabe).wert == eingabe


@pytest.mark.parametrize(
    ("eingabe", "erwartet"),
    [
        pytest.param("Max.Mustermann@Example.DE", "max.mustermann@example.de", id="gemischt"),
        pytest.param("MAX@EXAMPLE.DE", "max@example.de", id="nur-gross"),
    ],
)
def test_email_wird_klein_geschrieben_gespeichert(eingabe: str, erwartet: str) -> None:
    assert EmailAdresse(eingabe).wert == erwartet


def test_email_gleich_und_gleicher_hash_unabhaengig_von_gross_klein() -> None:
    assert len({EmailAdresse("Max@Example.de"), EmailAdresse("max@example.de")}) == 1


@pytest.mark.parametrize(
    "eingabe",
    [
        pytest.param("", id="leer"),
        pytest.param("   ", id="nur-leerzeichen"),
        pytest.param("max", id="ohne-at"),
        pytest.param("max@", id="ohne-domain"),
        pytest.param("@example.de", id="ohne-lokalteil"),
        pytest.param("max@example", id="ohne-tld"),
        pytest.param("max@@example.de", id="doppeltes-at"),
        pytest.param("max@exa mple.de", id="leerzeichen-in-domain"),
        pytest.param(".max@example.de", id="punkt-am-anfang"),
        pytest.param("max.@example.de", id="punkt-am-ende-lokalteil"),
        pytest.param("max..m@example.de", id="doppelter-punkt-lokalteil"),
        pytest.param("max@example..de", id="doppelter-punkt-domain"),
        pytest.param("max@example.de.", id="punkt-am-ende-domain"),
        pytest.param("max@-example.de", id="bindestrich-label-anfang"),
        pytest.param("max@example-.de", id="bindestrich-label-ende"),
        pytest.param("max@sub_domain.de", id="unterstrich-in-domain"),
        pytest.param("max@example.d", id="tld-ein-zeichen"),
        pytest.param("max@example.d3", id="tld-mit-ziffer"),
        pytest.param("jürgen@example.de", id="umlaut-lokalteil"),
        pytest.param("max@müller.de", id="umlaut-domain"),
        # U+212A (Kelvin) wird durch .lower() zu "k" -> Prüfung muss vor .lower() erfolgen
        pytest.param("Karl@example.de", id="kelvin-zeichen"),
        pytest.param(" max@example.de", id="fuehrendes-leerzeichen"),
        pytest.param("max@example.de\n", id="newline-am-ende"),
    ],
)
def test_email_ungueltig_wirft_value_error(eingabe: str) -> None:
    with pytest.raises(ValueError):
        EmailAdresse(eingabe)


def test_email_ist_unveraenderlich() -> None:
    email = EmailAdresse("max@example.de")
    with pytest.raises(dataclasses.FrozenInstanceError):
        email.wert = "anna@example.de"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# Adresse
# --------------------------------------------------------------------------- #

GUELTIGE_ADRESSE = {"strasse": "Hauptstraße", "hausnummer": "1", "plz": "26721", "ort": "Emden"}
ADRESSE_FELDER = list(GUELTIGE_ADRESSE)


def adresse(**abweichung: object) -> Adresse:
    """Baut eine gültige Adresse und überschreibt einzelne Felder."""
    return Adresse(**{**GUELTIGE_ADRESSE, **abweichung})  # type: ignore[arg-type]


def test_adresse_gueltig() -> None:
    a = adresse()
    assert (a.strasse, a.hausnummer, a.plz, a.ort) == ("Hauptstraße", "1", "26721", "Emden")


def test_adresse_gleichheit_nach_wert() -> None:
    assert adresse() == adresse()


@pytest.mark.parametrize(
    ("feld", "wert"),
    [
        pytest.param("plz", "01067", id="plz-fuehrende-null"),
        pytest.param("plz", "00000", id="plz-untergrenze"),
        pytest.param("plz", "99999", id="plz-obergrenze"),
        pytest.param("hausnummer", "12a", id="hausnummer-mit-buchstabe"),
        pytest.param("hausnummer", "3-5", id="hausnummer-bereich"),
        pytest.param("strasse", "Straße des 17. Juni", id="strasse-mit-ziffern"),
        pytest.param("ort", "Halle (Saale)", id="ort-mit-klammern"),
        pytest.param("ort", "Lüdenscheid", id="ort-mit-umlaut"),
        pytest.param("ort", "A", id="ein-zeichen"),
    ],
)
def test_adresse_grenzfaelle_gueltig(feld: str, wert: str) -> None:
    assert getattr(adresse(**{feld: wert}), feld) == wert


@pytest.mark.parametrize("feld", ADRESSE_FELDER)
@pytest.mark.parametrize(
    "leer",
    [
        pytest.param("", id="leer"),
        pytest.param(" ", id="leerzeichen"),
        pytest.param(" \t\n ", id="gemischter-whitespace"),
        pytest.param(" ", id="geschuetztes-leerzeichen"),
    ],
)
def test_adresse_leeres_feld_wirft_value_error(feld: str, leer: str) -> None:
    with pytest.raises(ValueError):
        adresse(**{feld: leer})


@pytest.mark.parametrize(
    "plz",
    [
        pytest.param("2672", id="vier-ziffern"),
        pytest.param("267211", id="sechs-ziffern"),
        pytest.param("2672a", id="buchstabe"),
        pytest.param("-2672", id="vorzeichen"),
        pytest.param("D-26721", id="laenderkennung"),
        pytest.param("26 721", id="leerzeichen-innen"),
        pytest.param(" 26721", id="fuehrendes-leerzeichen"),
        pytest.param("26721 ", id="abschliessendes-leerzeichen"),
        pytest.param("26721\n", id="newline-am-ende"),
        pytest.param("٢٦٧٢١", id="arabisch-indische-ziffern"),
        pytest.param("２６７２１", id="vollbreite-ziffern"),
    ],
)
def test_adresse_ungueltige_plz_wirft_value_error(plz: str) -> None:
    with pytest.raises(ValueError):
        adresse(plz=plz)


def test_adresse_plz_als_int_wird_abgelehnt() -> None:
    # 01067 als int wäre 1067 – die führende Null ginge verloren
    with pytest.raises((TypeError, ValueError)):
        adresse(plz=1067)


def test_adresse_ist_unveraenderlich() -> None:
    a = adresse()
    with pytest.raises(dataclasses.FrozenInstanceError):
        a.ort = "Leer"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# EinladungscodeWert
# --------------------------------------------------------------------------- #

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford Base32
LAENGE = 12


@pytest.mark.parametrize(
    "eingabe",
    [
        pytest.param("7K3QX9M2HZ4R", id="typischer-code"),
        pytest.param("0123456789AB", id="ziffern-und-buchstaben"),
    ],
)
def test_einladungscode_gueltig(eingabe: str) -> None:
    assert EinladungscodeWert(eingabe).wert == eingabe


@pytest.mark.parametrize("zeichen", list(ALPHABET))
def test_einladungscode_jedes_erlaubte_zeichen(zeichen: str) -> None:
    assert EinladungscodeWert(zeichen * LAENGE).wert == zeichen * LAENGE


@pytest.mark.parametrize("zeichen", list("ILOU-_ *ä"))
def test_einladungscode_verbotenes_zeichen_wirft_value_error(zeichen: str) -> None:
    with pytest.raises(ValueError):
        EinladungscodeWert("7K3QX9M2HZ4" + zeichen)


@pytest.mark.parametrize(
    "eingabe",
    [
        pytest.param("", id="leer"),
        pytest.param(" " * LAENGE, id="nur-leerzeichen"),
        pytest.param("7K3QX9M2HZ4", id="eins-zu-kurz"),
        pytest.param("7K3QX9M2HZ4RA", id="eins-zu-lang"),
        pytest.param("7k3qx9m2hz4r", id="kleinbuchstaben"),
        pytest.param("7K3Q-X9M2-HZ4R", id="mit-trennzeichen"),
        pytest.param(" 7K3QX9M2HZ4R", id="fuehrendes-leerzeichen"),
        pytest.param("7K3QX9M2HZ4R\n", id="newline-am-ende"),
    ],
)
def test_einladungscode_ungueltig_wirft_value_error(eingabe: str) -> None:
    with pytest.raises(ValueError):
        EinladungscodeWert(eingabe)


def test_einladungscode_ist_unveraenderlich() -> None:
    code = EinladungscodeWert("7K3QX9M2HZ4R")
    with pytest.raises(dataclasses.FrozenInstanceError):
        code.wert = "000000000000"  # type: ignore[misc]
