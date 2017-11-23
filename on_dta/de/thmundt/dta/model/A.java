package de.thmundt.dta.model;

import static de.thmundt.dta.tools.Formatter.fit;

public class A {

	private static final String a1satzlaenge = "0128";

	private static final String a2satzart = "A";

	private String a3dateikennzeichen;

	private String a4leitzahlEmpf;

	private static final String a5 = "00000000";

	private String a6bezeichnungAbsender;

	private String a7datumDateierstellung;

	private String a8 = "    ";

	private String a9kontoNummerAbsender;

	private String a10referenzEinreicher;

	private static final String a11a = "               ";

	private String a11bausfuehrungsdatum;

	private static final String a11c = "                        ";

	private static final String a12waehrung = "1";

	public static String getA12waehrung() {
		return fit("A", 1, a12waehrung);
	}

	public static String getA1satzlaenge() {
		return fit("N", 4, a1satzlaenge);
	}

	public static String getA2satzart() {
		return fit("A", 1, a2satzart);
	}

	public String getA10referenzEinreicher() {
		return fit("N", 10, a10referenzEinreicher);
	}

	public void setA10referenzEinreicher(String einreicher) {
		a10referenzEinreicher = einreicher;
	}

	public String getA11bausfuehrungsdatum() {
		return fit("A", 8, a11bausfuehrungsdatum);
	}

	public void setA11bausfuehrungsdatum(String a11bausfuehrungsdatum) {
		this.a11bausfuehrungsdatum = a11bausfuehrungsdatum;
	}

	public String getA3dateikennzeichen() {
		return fit("A", 2, a3dateikennzeichen);
	}

	public void setA3dateikennzeichen(String a3dateikennzeichen) {
		this.a3dateikennzeichen = a3dateikennzeichen;
	}

	public String getA4leitzahlEmpf() {
		return fit("N", 8, a4leitzahlEmpf);
	}

	public void setA4leitzahlEmpf(String empf) {
		a4leitzahlEmpf = empf;
	}

	public String getA6bezeichnungAbsender() {
		return fit("A", 27, a6bezeichnungAbsender);
	}

	public void setA6bezeichnungAbsender(String absender) {
		a6bezeichnungAbsender = absender;
	}

	public String getA7datumDateierstellung() {
		return fit("A", 6, a7datumDateierstellung);
	}

	public void setA7datumDateierstellung(String dateierstellung) {
		a7datumDateierstellung = dateierstellung;
	}

	public String getA9kontoNummerAbsender() {
		return fit("N", 10, a9kontoNummerAbsender);
	}

	public void setA9kontoNummerAbsender(String nummerAbsender) {
		a9kontoNummerAbsender = nummerAbsender;
	}

	public static String getA11a() {
		return fit("A", 15, a11a);
	}

	public static String getA11c() {
		return fit("A", 24, a11c);
	}

	public static String getA5() {
		return fit("N", 8, a5);
	}

	public String getA8() {
		return fit ("A", 4, a8);
	}

	public String getAll() {
		return getA1satzlaenge() + getA2satzart() + getA3dateikennzeichen()
				+ getA4leitzahlEmpf() + getA5() + getA6bezeichnungAbsender()
				+ getA7datumDateierstellung() + getA8()
				+ getA9kontoNummerAbsender() + getA10referenzEinreicher()
				+ getA11a() + getA11bausfuehrungsdatum() + getA11c()
				+ getA12waehrung();
	}
}
