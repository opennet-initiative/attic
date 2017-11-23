package de.thmundt.dta.model;

import static de.thmundt.dta.tools.Formatter.fit;

public class C {
	private String c1satzlaenge;

	private static final String c2satzart = "C";

	private String c3bankleitzahl;

	private String c4bankleitzahlBeguenstigter;

	private String c5kontonummer;

	private String c6interneKundennummer;

	private String c7atextschluessel;

	private String c7btextschluesselErgaenzung;

	private static final String c8bankintern = " ";

	private static final String c9 = "00000000000";

	private String c10bankleitzahlUeberweisender;

	private String c11kontonummerUeberweisender;

	private String c12betrag;

	private static final String c13reserve = "   ";

	private String c14anameEmpfaenger;

	private static final String c14b = "        ";

	private String c15name;

	private String c16verwendungszwecke;

	private static final String c17a = "1";

	private static final String c17b = "  ";

	private String c18erweiterungskennzeichen;

	private String c19kennzeichenerw;

	private String c20daten;

	private String c21kennzeichenerw;

	private String c22daten;

	private static final String c23 = "           ";

	private String c24kennzeichenerw;

	private String c25daten;

	private String c26kennzeichenerw;

	private String c27daten;

	private String c28kennzeichenerw;

	private String c29daten;

	private String c30kennzeichenerw;

	private String c31daten;

	private static final String c32 = "            ";

	public static String getC13reserve() {
		return fit("A", 3, c13reserve);
	}

	public static String getC14b() {
		return fit("A",8, c14b);
	}

	public static String getC17a() {
		return fit("A", 1, c17a);
	}

	public static String getC17b() {
		return fit("A", 2, c17b);
	}

	public static String getC23() {
		return fit("A", 11, c23);
	}

	public static String getC2satzart() {
		return fit("A", 1, c2satzart);
	}

	public static String getC32() {
		return fit("A", 12, c32);
	}

	public static String getC8bankintern() {
		return fit("A", 1, c8bankintern);
	}

	public static String getC9() {
		return fit("N", 11, c9);
	}

	public String getC10bankleitzahlUeberweisender() {
		return fit("N", 8, c10bankleitzahlUeberweisender);
	}

	public void setC10bankleitzahlUeberweisender(String ueberweisender) {
		c10bankleitzahlUeberweisender = ueberweisender;
	}

	public String getC11kontonummerUeberweisender() {
		return fit("N", 10, c11kontonummerUeberweisender);
	}

	public void setC11kontonummerUeberweisender(String ueberweisender) {
		c11kontonummerUeberweisender = ueberweisender;
	}

	public String getC12betrag() {
		return fit("N", 11, c12betrag);
	}

	public void setC12betrag(String c12betrag) {
		this.c12betrag = c12betrag;
	}

	public String getC14anameEmpfaenger() {
		return fit("A", 27, c14anameEmpfaenger);
	}

	public void setC14anameEmpfaenger(String empfaenger) {
		c14anameEmpfaenger = empfaenger;
	}

	public String getC15name() {
		return fit("A", 27, c15name);
	}

	public void setC15name(String c15name) {
		this.c15name = c15name;
	}

	public String getC16verwendungszwecke() {
		return fit("A", 27, c16verwendungszwecke);
	}

	public void setC16verwendungszwecke(String c16verwendungszwecke) {
		this.c16verwendungszwecke = c16verwendungszwecke;
	}

	public String getC19kennzeichenerw() {
		return fit("S", 2, c19kennzeichenerw);
	}

	public void setC19kennzeichenerw(String c19kennzeichenerw) {
		this.c19kennzeichenerw = c19kennzeichenerw;
	}

	public String getC1satzlaenge() {
		return fit("N", 4, c1satzlaenge);
	}

	public void setC1satzlaenge(String c1satzlaenge) {
		this.c1satzlaenge = c1satzlaenge;
	}

	public String getC20daten() {
		return fit("A", 27, c20daten);
	}

	public void setC20daten(String c20daten) {
		this.c20daten = c20daten;
	}

	public String getC21kennzeichenerw() {
		return fit("S", 2, c21kennzeichenerw);
	}

	public void setC21kennzeichenerw(String c21kennzeichenerw) {
		this.c21kennzeichenerw = c21kennzeichenerw;
	}

	public String getC22daten() {
		return fit("A", 27, c22daten);
	}

	public void setC22daten(String c22daten) {
		this.c22daten = c22daten;
	}

	public String getC24kennzeichenerw() {
		return fit("S", 2, c24kennzeichenerw);
	}

	public void setC24kennzeichenerw(String c24kennzeichenerw) {
		this.c24kennzeichenerw = c24kennzeichenerw;
	}

	public String getC25daten() {
		return fit("A", 27, c25daten);
	}

	public void setC25daten(String c25daten) {
		this.c25daten = c25daten;
	}

	public String getC26kennzeichenerw() {
		return fit("S", 2, c26kennzeichenerw);
	}

	public void setC26kennzeichenerw(String c26kennzeichenerw) {
		this.c26kennzeichenerw = c26kennzeichenerw;
	}

	public String getC27daten() {
		return fit("A", 27, c27daten);
	}

	public void setC27daten(String c27daten) {
		this.c27daten = c27daten;
	}

	public String getC28kennzeichenerw() {
		return fit("S", 2, c28kennzeichenerw);
	}

	public void setC28kennzeichenerw(String c28kennzeichenerw) {
		this.c28kennzeichenerw = c28kennzeichenerw;
	}

	public String getC29daten() {
		return fit("A", 27, c29daten);
	}

	public void setC29daten(String c29daten) {
		this.c29daten = c29daten;
	}

	public String getC30kennzeichenerw() {
		return fit("S", 2, c30kennzeichenerw);
	}

	public void setC30kennzeichenerw(String c30kennzeichenerw) {
		this.c30kennzeichenerw = c30kennzeichenerw;
	}

	public String getC31daten() {
		return fit("A", 27, c31daten);
	}

	public void setC31daten(String c31daten) {
		this.c31daten = c31daten;
	}

	public String getC3bankleitzahl() {
		return fit("N", 8, c3bankleitzahl);
	}

	public void setC3bankleitzahl(String c3bankleitzahl) {
		this.c3bankleitzahl = c3bankleitzahl;
	}

	public String getC4bankleitzahlBeguenstigter() {
		return fit("N", 8, c4bankleitzahlBeguenstigter);
	}

	public void setC4bankleitzahlBeguenstigter(String beguenstigter) {
		c4bankleitzahlBeguenstigter = beguenstigter;
	}

	public String getC5kontonummer() {
		return fit("N", 10, c5kontonummer);
	}

	public void setC5kontonummer(String c5kontonummer) {
		this.c5kontonummer = c5kontonummer;
	}

	public String getC6interneKundennummer() {
		return fit("N", 13, c6interneKundennummer);
	}

	public void setC6interneKundennummer(String kundennummer) {
		c6interneKundennummer = kundennummer;
	}

	public String getC7atextschluessel() {
		return fit("N", 2, c7atextschluessel);
	}

	public void setC7atextschluessel(String c7atextschluessel) {
		this.c7atextschluessel = c7atextschluessel;
	}

	public String getC7btextschluesselErgaenzung() {
		return fit("N", 3, c7btextschluesselErgaenzung);
	}

	public void setC7btextschluesselErgaenzung(String ergaenzung) {
		c7btextschluesselErgaenzung = ergaenzung;
	}

	public String getC18erweiterungskennzeichen() {
		return fit("N", 2, c18erweiterungskennzeichen);
	}

	public void setC18erweiterungskennzeichen(String c18erweiterungskennzeichen) {
		this.c18erweiterungskennzeichen = c18erweiterungskennzeichen;
	}

	public String getAll() {
		return getC1satzlaenge() + getC2satzart() + getC3bankleitzahl()
				+ getC4bankleitzahlBeguenstigter() + getC5kontonummer()
				+ getC6interneKundennummer() + getC7atextschluessel()
				+ getC7btextschluesselErgaenzung() + getC8bankintern()
				+ getC9() + getC10bankleitzahlUeberweisender()
				+ getC11kontonummerUeberweisender() + getC12betrag()
				+ getC13reserve() + getC14anameEmpfaenger() + getC14b()
				+ getC15name() + getC16verwendungszwecke() + getC17a()
				+ getC17b() + getC18erweiterungskennzeichen()
				+ getC19kennzeichenerw() + getC20daten()
				+ getC21kennzeichenerw() + getC22daten() + getC23()
				+ getC24kennzeichenerw() + getC25daten()
				+ getC26kennzeichenerw() + getC27daten()
				+ getC28kennzeichenerw() + getC29daten()
				+ getC30kennzeichenerw() + getC31daten() + getC32();
	}
}
