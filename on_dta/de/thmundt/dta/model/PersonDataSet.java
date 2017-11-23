package de.thmundt.dta.model;

public class PersonDataSet {
	private String mName;

	private String mVorname;

	private String mBLZ;

	private String mKontonummer;

	public String getBLZ() {
		return mBLZ;
	}

	public void setBLZ(String mblz) {
		mBLZ = mblz;
	}

	public String getKontonummer() {
		return mKontonummer;
	}

	public void setKontonummer(String kontonummer) {
		mKontonummer = kontonummer;
	}

	public String getName() {
		return mName;
	}

	public void setName(String name) {
		mName = name;
	}

	public String getVorname() {
		return mVorname;
	}

	public void setVorname(String vorname) {
		mVorname = vorname;
	}
}
