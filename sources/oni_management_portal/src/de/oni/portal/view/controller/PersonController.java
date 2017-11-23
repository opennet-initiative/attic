package de.oni.portal.view.controller;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Collection;

import javax.faces.bean.ManagedBean;
import javax.faces.bean.SessionScoped;
import javax.faces.model.SelectItem;

import de.oni.portal.entities.Person;
import de.oni.portal.entities.service.PersonRetrievalService;
import de.oni.portal.entities.service.PersonStorageService;

@ManagedBean
@SessionScoped
public class PersonController implements Serializable
{
	private static final long serialVersionUID = 4102314825685084980L;

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
	
	public void setEditedPerson(Person editedPerson) {
		this.editedPerson = editedPerson != null ? editedPerson : new Person();
	}

	public Person getEditedPerson() {
		return editedPerson;
	}
	
	public void store()
	{
		new PersonStorageService().storePerson(this.editedPerson);
	}

	public void remove() {
		new PersonStorageService().deletePerson(currentPersonIndex);
	}

	public ArrayList<SelectItem> getStatusList() {
		ArrayList<SelectItem> statusList = new ArrayList<SelectItem>();
		for (Person.PersonStatus personStatus : Person.PersonStatus.values()) {
			statusList.add(new SelectItem(personStatus, personStatus.name()));
		}
		return statusList;
	}

	public ArrayList<SelectItem> getRolesList() {
		ArrayList<SelectItem> rolesList = new ArrayList<SelectItem>();
		for (Person.PersonRole personRoles : Person.PersonRole.values()) {
			rolesList.add(new SelectItem(personRoles, personRoles.name()));
		}
		return rolesList;
	}
}
