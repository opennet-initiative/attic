package de.thmundt.dta.model;

import java.util.ArrayList;
import java.util.Iterator;

public class DTA {
	private A mA;
	private E mE;
	private ArrayList<C> mCList = new ArrayList<C>();

	public void setA(A a) {
		mA = a;
	}

	public A getA() {
		return mA;
	}

	public void addC(C c) {
		mCList.add(c);
	}
	
	public ArrayList<C> getCList() {
		return mCList;
	}

	public void setE(E e) {
		mE = e;
	}

	public E getE() {
		return mE;
	}
	
	public String getAll() {
		StringBuffer buf = new StringBuffer();
		Iterator<C> it = mCList.iterator();
		while(it.hasNext()) {
			buf.append(it.next().getAll());
		}
		return mA.getAll() + buf.toString() + mE.getAll();
	}
}
