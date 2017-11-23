package de.oni.portal.entities.service;

import java.util.Collection;

import javax.persistence.EntityManager;
import javax.persistence.Query;

import de.oni.portal.entities.Person;
import de.oni.portal.persistence.PersistenceProvider;

public class PersonRetrievalService
{

	@SuppressWarnings("unchecked")
	public Collection<Person> getAllPersons()
	{
		EntityManager em = PersistenceProvider.getEntityManager();
		try
		{
			em.getTransaction().begin();
			Query q = em.createQuery("select p from Person p");
			em.getTransaction().commit();
			return q.getResultList();
		} finally 
		{
			em.close();
		}
	}
	
}
