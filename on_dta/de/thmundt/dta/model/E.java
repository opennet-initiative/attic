package de.thmundt.dta.model;

import static de.thmundt.dta.tools.Formatter.fit;

public class E {
    private static final String e1satzlaenge = "0128";

    private static final String e2satzart = "E";

    private static final String e3 = "     ";

    private String e4anzahlDatensaetze;

    private static final String e5 = "0000000000000";

    private String e6summeKontonummern;

    private String e7summeBLZ;

    private String e8summeBetraege;

    private static final String e9 = "                                                   ";

    public static String getE1satzlaenge() {
        return fit("N", 4, e1satzlaenge);
    }

    public static String getE2satzart() {
        return fit("A", 1, e2satzart);
    }

    public static String getE3() {
        return fit("A", 5, e3);
    }

    public static String getE5() {
        return fit("N", 13, e5);
    }

    public static String getE9() {
        return fit("A", 51, e9);
    }

    public String getE4anzahlDatensaetze() {
        return fit("N", 7, e4anzahlDatensaetze);
    }

    public void setE4anzahlDatensaetze(String datensaetze) {
        e4anzahlDatensaetze = datensaetze;
    }

    public String getE6summeKontonummern() {
        return fit("N", 17, e6summeKontonummern);
    }

    public void setE6summeKontonummern(String kontonummern) {
        e6summeKontonummern = kontonummern;
    }

    public String getE7summeBLZ() {
        return fit("N", 17, e7summeBLZ);
    }

    public void setE7summeBLZ(String e7summeblz) {
        e7summeBLZ = e7summeblz;
    }

    public String getE8summeBetraege() {
        return fit("N", 13, e8summeBetraege);
    }

    public void setE8summeBetraege(String betraege) {
        e8summeBetraege = betraege;
    }

    public String getAll() {
        return getE1satzlaenge() + getE2satzart() + getE3()
                + getE4anzahlDatensaetze() + getE5() + getE6summeKontonummern()
                + getE7summeBLZ() + getE8summeBetraege() + getE9();
    }
}
