package de.opennetinitiative.useradmin.model;

public class AccessPoint {
	private String mName;
	private String mComment;
	private Location mLocation;
	private Person mOwner;
	
	/**
	 * @return Returns the mOwner.
	 */
	public Person getOwner() {
		return mOwner;
	}
	/**
	 * @param owner The mOwner to set.
	 */
	public void setOwner(Person owner) {
		mOwner = owner;
	}
	/**
	 * @return Returns the mComment.
	 */
	public String getComment() {
		return mComment;
	}
	/**
	 * @param comment The mComment to set.
	 */
	public void setComment(String comment) {
		mComment = comment;
	}
	/**
	 * @return Returns the mLocation.
	 */
	public Location getLocation() {
		return mLocation;
	}
	/**
	 * @param location The mLocation to set.
	 */
	public void setLocation(Location location) {
		mLocation = location;
	}
	/**
	 * @return Returns the mName.
	 */
	public String getName() {
		return mName;
	}
	/**
	 * @param name The mName to set.
	 */
	public void setName(String name) {
		mName = name;
	}
}
