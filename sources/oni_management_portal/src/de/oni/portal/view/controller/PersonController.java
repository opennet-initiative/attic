package de.oni.portal.view.controller;

import java.util.Collection;

import javax.faces.bean.ManagedBean;
import javax.faces.bean.SessionScoped;

import de.oni.portal.entities.Person;
import de.oni.portal.entities.service.PersonRetrievalService;
import de.oni.portal.entities.service.PersonStorageService;

@ManagedBean
@SessionScoped
public class PersonController
{

	private long currentPersonIndex;
	private Person editedPerson;
	
	public Collection<Person> getAllPersons()
	{
		return new PersonRetrievalService().getAllPersons();
	}

	public void setCurrentPersonIndex(long currentPersonIndex) {
		this.currentPersonIndex = currentPersonIndex;
	}

	public long getCurrentPersonIndex() {
		return currentPersonIndex;
	}
	
	public void remove() {
		new PersonStorageService().deletePerson(currentPersonIndex);
	}

	public void setEditedPerson(Person editedPerson) {
		this.editedPerson = editedPerson;
	}

	public Person getEditedPerson() {
		return editedPerson;
	}
}
