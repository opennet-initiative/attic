package de.opennetinitiative.useradmin.model;

public class Address {
	private String mStreet;
	private String mNumber;
	private String mZipCode;
	private String mCity;
	private Location mLoc;
	/**
	 * @return Returns the mLoc.
	 */
	public Location getLoc() {
		return mLoc;
	}
	/**
	 * @param loc The mLoc to set.
	 */
	public void setLoc(Location loc) {
		mLoc = loc;
	}
	/**
	 * @return Returns the mCity.
	 */
	public String getCity() {
		return mCity;
	}
	/**
	 * @param city The mCity to set.
	 */
	public void setCity(String city) {
		mCity = city;
	}
	/**
	 * @return Returns the mNumber.
	 */
	public String getNumber() {
		return mNumber;
	}
	/**
	 * @param number The mNumber to set.
	 */
	public void setNumber(String number) {
		mNumber = number;
	}
	/**
	 * @return Returns the mStreet.
	 */
	public String getStreet() {
		return mStreet;
	}
	/**
	 * @param street The mStreet to set.
	 */
	public void setStreet(String street) {
		mStreet = street;
	}
	/**
	 * @return Returns the mZipCode.
	 */
	public String getZipCode() {
		return mZipCode;
	}
	/**
	 * @param zipCode The mZipCode to set.
	 */
	public void setZipCode(String zipCode) {
		mZipCode = zipCode;
	}
}
