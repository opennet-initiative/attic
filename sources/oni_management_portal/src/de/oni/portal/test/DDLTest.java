package de.oni.portal.test;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import javax.faces.bean.ManagedBean;
import javax.faces.event.ActionEvent;

import de.oni.portal.persistence.PersistenceProvider;

@ManagedBean
public class DDLTest {

	public void listen(ActionEvent event){
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
