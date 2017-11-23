package de.thmundt.dta.controller;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.StringTokenizer;

import de.thmundt.dta.model.DTA;
import de.thmundt.dta.model.PersonDataSet;

public class DTAFile extends File {

	/**
	 * 
	 */
	private static final long serialVersionUID = 5476538605216244912L;

	private FileWriter mFWriter;

	private BufferedWriter mBWriter;

	public DTAFile(String pathname, DTA dta) {
		super(pathname);
		writeFile(dta);
	}

	private void writeFile(DTA dta) {
		try {
			mFWriter = new FileWriter(this);
			mBWriter = new BufferedWriter(mFWriter);
			mBWriter.write(dta.getAll());
			mBWriter.close();
			mFWriter.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
