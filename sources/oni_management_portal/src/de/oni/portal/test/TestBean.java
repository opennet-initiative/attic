package de.oni.portal.test;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Random;
import java.util.UUID;

import javax.faces.bean.ManagedBean;
import javax.faces.event.ActionEvent;

import org.apache.log4j.Logger;

import de.oni.portal.entities.Person;
import de.oni.portal.entities.Person.PersonRole;
import de.oni.portal.entities.Person.PersonStatus;
import de.oni.portal.entities.service.PersonStorageService;
import de.oni.portal.persistence.PersistenceProvider;

@ManagedBean
public class TestBean {

	@SuppressWarnings("unused")
	private static final Logger log = Logger.getLogger(TestBean.class);

	public void createPerson(ActionEvent event)
	{
		Person p = new Person();
		p.addRole(PersonRole.Crew);
		p.addRole(PersonRole.Admin);
		p.setFirstName("dummy");
		p.setLastName(UUID.randomUUID().toString());
		p.setAccountNumber(Integer.toString(Math.abs(new Random().nextInt())));
		p.setStatus(PersonStatus.Normal);
		p.setBankCode(Integer.toString(Math.abs(new Random().nextInt())));
		p.setCity("Rostock");
		new PersonStorageService().storePerson(p);
	}
	
	public void createScripts(ActionEvent event)
	{
		System.out.println("xxxx");
		try
		{
			Method m = PersistenceProvider.class.getDeclaredMethod("generateSqlScripts", new Class[] {});
			m.setAccessible(true);
			m.invoke(null, new Object[] {});
		} catch (IllegalArgumentException e)
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (SecurityException e)
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IllegalAccessException e)
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (InvocationTargetException e)
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NoSuchMethodException e)
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
