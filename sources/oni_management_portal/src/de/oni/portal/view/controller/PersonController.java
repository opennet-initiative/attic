package de.oni.portal.view.controller;

import java.util.Collection;

import javax.faces.bean.ManagedBean;

import de.oni.portal.entities.Person;
import de.oni.portal.entities.service.PersonRetrievalService;

@ManagedBean
public class PersonController
{
	
	public Collection<Person> getAllPersons()
	{
		return new PersonRetrievalService().getAllPersons();
	}

}
