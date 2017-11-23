package de.thmundt.dta.main;

import java.util.Iterator;

import de.thmundt.dta.controller.CSVFile;
import de.thmundt.dta.controller.DTAFile;
import de.thmundt.dta.model.A;
import de.thmundt.dta.model.C;
import de.thmundt.dta.model.DTA;
import de.thmundt.dta.model.E;
import de.thmundt.dta.model.PersonDataSet;

public class Start {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		CSVFile file = new CSVFile(
				"c:\\members.csv");
		Iterator<PersonDataSet> it = file.iterator();
		DTA dta = new DTA();
		A a = new A();
		a.setA3dateikennzeichen("LK");
		a.setA4leitzahlEmpf("13070024");
		a.setA6bezeichnungAbsender("Opennet Initiative e.V.");
		a.setA7datumDateierstellung("160306");
		a.setA9kontoNummerAbsender("115588600");
		dta.setA(a);
		System.out.println(a.getAll());
		long sumKontonummern = 0;
		long sumBLZ = 0;
		long sumBetraege = 0;
		while (it.hasNext()) {
			C c = new C();
			PersonDataSet person = it.next();
			System.out.println(person.getName() + ", " + person.getVorname()
					+ ", " + person.getKontonummer() + ", " + person.getBLZ());
			sumKontonummern = sumKontonummern + Long.valueOf(person.getKontonummer());
			sumBLZ = sumBLZ + Long.valueOf(person.getBLZ());
			sumBetraege = sumBetraege + 1000;
			c.setC1satzlaenge("0274");
			c.setC3bankleitzahl("13070024");
			c.setC4bankleitzahlBeguenstigter(person.getBLZ());
			c.setC5kontonummer(person.getKontonummer());
			c.setC7atextschluessel("05");
			c.setC7btextschluesselErgaenzung("000");
			c.setC10bankleitzahlUeberweisender("13070024");
			c.setC11kontonummerUeberweisender("115588600");
			c.setC12betrag("1000");
			c.setC14anameEmpfaenger(person.getName() + ", " + person.getVorname());
			c.setC15name("Opennet Initiative e.V.");
			c.setC16verwendungszwecke("Jahresbeitrag fuer");
			c.setC18erweiterungskennzeichen("03");
			c.setC19kennzeichenerw("02");
			c.setC20daten("ein Kalenderjahr");
			c.setC21kennzeichenerw("02");
			c.setC22daten("Herzlichen Dank");
			c.setC24kennzeichenerw("02");
			c.setC25daten("Opennet Initiative e.V.");
			dta.addC(c);
			System.out.println(c.getAll());
		}
		E e = new E();
		e.setE4anzahlDatensaetze(String.valueOf(dta.getCList().size()));
		e.setE6summeKontonummern(String.valueOf(sumKontonummern));
		e.setE7summeBLZ(String.valueOf(sumBLZ));
		e.setE8summeBetraege(String.valueOf(sumBetraege));
		dta.setE(e);
		System.out.println(e.getAll());
		System.out.println(dta.getAll());
		DTAFile dtaFile = new DTAFile("C:\\DTAUS.027", dta);
	}
}
