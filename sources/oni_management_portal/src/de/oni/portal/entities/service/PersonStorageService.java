package de.oni.portal.entities.service;

import javax.persistence.EntityManager;

import org.apache.log4j.Logger;

import de.oni.portal.entities.Person;
import de.oni.portal.persistence.PersistenceProvider;

public class PersonStorageService
{
	
	private static final Logger log = Logger.getLogger(PersonStorageService.class);

	public void storePerson(Person p)
	{
		EntityManager em = PersistenceProvider.getEntityManager();
		try
		{
			em.getTransaction().begin();
			em.persist(p);
			em.getTransaction().commit();
			log.info(String.format("stored person %s", p));
		} finally 
		{
			em.close();
		}
	}

}
