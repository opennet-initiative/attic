package de.oni.portal.persistence;

import java.util.HashMap;
import java.util.Map;

import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.Persistence;

import org.apache.log4j.Logger;
import org.eclipse.persistence.config.PersistenceUnitProperties;

import de.oni.portal.configuration.Config;

public class PersistenceProvider implements PersistenceConstants
{
	
	private static final Logger log = Logger.getLogger(PersistenceProvider.class);
	
	private static EntityManagerFactory emFactory;

	protected static EntityManagerFactory getEntityManagerFactory()
	{
		if (emFactory == null)
		{
			emFactory = Persistence.createEntityManagerFactory(PERSISTENCE_UNIT, getPersistenceOverrides());
		}
		return emFactory;
	}
	
	protected static Map<String, String> getPersistenceOverrides()
	{
		Map<String, String> overrides = new HashMap<String, String>();
		final String url = Config.getString("portal.persistence.jdbc.url", null);
		if (url != null) overrides.put(PersistenceUnitProperties.JDBC_URL, url);
		final String usr = Config.getString("portal.persistence.jdbc.user", null);
		if (usr != null) overrides.put(PersistenceUnitProperties.JDBC_USER, usr);
		final String drv = Config.getString("portal.persistence.jdbc.driver", null);
		if (drv != null) overrides.put(PersistenceUnitProperties.JDBC_DRIVER, drv);
		final String pwd = Config.getString("portal.persistence.jdbc.password", null);
		if (pwd != null) overrides.put(PersistenceUnitProperties.JDBC_PASSWORD, pwd);
		return overrides;
	}

	public static EntityManager getEntityManager()
	{
		return getEntityManagerFactory().createEntityManager();
	}
	
	protected static EntityManager getEntityManager(Map<String, String> params)
	{
		Map<String, String> overrides = getPersistenceOverrides();
		overrides.putAll(params);
		EntityManagerFactory emf = Persistence.createEntityManagerFactory(PERSISTENCE_UNIT, overrides);
		EntityManager em = emf.createEntityManager();
		return em;
	}
	
	protected static void generateSqlScripts()
	{
		final String dir = Config.getString("portal.persistence.sqlscripts.targetfolder", System.getProperty("java.io.tmpdir"));
		Map<String, String> persistenceProperties = new HashMap<String, String>();
		persistenceProperties.put(PersistenceUnitProperties.DDL_GENERATION, PersistenceUnitProperties.DROP_AND_CREATE);
		persistenceProperties.put(PersistenceUnitProperties.DDL_GENERATION_MODE, PersistenceUnitProperties.DDL_SQL_SCRIPT_GENERATION);
		persistenceProperties.put(PersistenceUnitProperties.APP_LOCATION, dir);
		persistenceProperties.put(PersistenceUnitProperties.CREATE_JDBC_DDL_FILE, PERSISTENCE_CREATE_DDL);
		persistenceProperties.put(PersistenceUnitProperties.DROP_JDBC_DDL_FILE, PERSISTENCE_DROP_DDL);
		getEntityManager(persistenceProperties).close();
		log.info(String.format("sql scripts written to %s", dir));
	}

}
