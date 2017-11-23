package de.thmundt.dta.controller;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.StringTokenizer;

import de.thmundt.dta.model.PersonDataSet;

public class CSVFile extends File {

	/**
	 * 
	 */
	private static final long serialVersionUID = 7158542329887877133L;

	private ArrayList<PersonDataSet> mPersons = new ArrayList<PersonDataSet>();

	private FileReader mFReader;

	private BufferedReader mBReader;

	public CSVFile(String pathname) {
		super(pathname);
		readFile();
	}

	private void readFile() {
		try {
			mFReader = new FileReader(this);
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		mBReader = new BufferedReader(mFReader);
		String line;
		try {
			while ((line = mBReader.readLine()) != null) {
				PersonDataSet person = parseLine(line);
				if (person != null) {
					mPersons.add(person);
				}
			}
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private PersonDataSet parseLine(String line) {
		StringTokenizer tokenizer = new StringTokenizer(line, ";");
		PersonDataSet person = new PersonDataSet();
		if (tokenizer.countTokens() == 4) {
			String name = tokenizer.nextToken();
			String vorname = tokenizer.nextToken();
			String kontonummer = tokenizer.nextToken();
			String blz = tokenizer.nextToken();
			person.setName(name);
			person.setVorname(vorname);
			person.setKontonummer(kontonummer);
			person.setBLZ(blz);
			return person;
		}
		return null;
	}

	public Iterator<PersonDataSet> iterator() {
		return mPersons.iterator();
	}
}
