package de.oni.portal.entities;

import javax.persistence.Entity;
import javax.persistence.Id;

@Entity
public class DummyEntity {

	@Id
	protected long id;
	public void setId(long id) {
		this.id = id;
	}

	protected String payload;

    public String getPayload() {
		return payload;
	}

	public void setPayload(String payload) {
		this.payload = payload;
	}

	public long getId() {
		return id;
	}

}
