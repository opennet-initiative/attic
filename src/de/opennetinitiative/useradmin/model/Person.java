package de.opennetinitiative.useradmin.model;

public class Person {
	private String mFirstName;
	private String mLastName;
	private String mEmailAddr;
	private String mBankAccount;
	private String mBLZ;
	private int mMemberstatus;
	private String mForumName;
	private String mWikiName;
	private Address mAddr;
	
	/**
	 * @return Returns the mAddr.
	 */
	public Address getAddr() {
		return mAddr;
	}
	/**
	 * @param addr The mAddr to set.
	 */
	public void setAddr(Address addr) {
		mAddr = addr;
	}
	/**
	 * @return Returns the mBankAccount.
	 */
	public String getBankAccount() {
		return mBankAccount;
	}
	/**
	 * @param bankAccount The mBankAccount to set.
	 */
	public void setBankAccount(String bankAccount) {
		mBankAccount = bankAccount;
	}
	/**
	 * @return Returns the mBLZ.
	 */
	public String getBLZ() {
		return mBLZ;
	}
	/**
	 * @param mblz The mBLZ to set.
	 */
	public void setBLZ(String mblz) {
		mBLZ = mblz;
	}
	/**
	 * @return Returns the mEmailAddr.
	 */
	public String getEmailAddr() {
		return mEmailAddr;
	}
	/**
	 * @param emailAddr The mEmailAddr to set.
	 */
	public void setEmailAddr(String emailAddr) {
		mEmailAddr = emailAddr;
	}
	/**
	 * @return Returns the mFirstName.
	 */
	public String getFirstName() {
		return mFirstName;
	}
	/**
	 * @param firstName The mFirstName to set.
	 */
	public void setFirstName(String firstName) {
		mFirstName = firstName;
	}
	/**
	 * @return Returns the mForumName.
	 */
	public String getForumName() {
		return mForumName;
	}
	/**
	 * @param forumName The mForumName to set.
	 */
	public void setForumName(String forumName) {
		mForumName = forumName;
	}
	/**
	 * @return Returns the mLastNamen.
	 */
	public String getLastName() {
		return mLastName;
	}
	/**
	 * @param lastNamen The mLastName to set.
	 */
	public void setLastName(String lastName) {
		mLastName = lastName;
	}
	/**
	 * @return Returns the mMemberstatus.
	 */
	public int getMemberstatus() {
		return mMemberstatus;
	}
	/**
	 * @param memberstatus The mMemberstatus to set.
	 */
	public void setMemberstatus(int memberstatus) {
		mMemberstatus = memberstatus;
	}
	/**
	 * @return Returns the mWikiName.
	 */
	public String getWikiName() {
		return mWikiName;
	}
	/**
	 * @param wikiName The mWikiName to set.
	 */
	public void setWikiName(String wikiName) {
		mWikiName = wikiName;
	}
}
