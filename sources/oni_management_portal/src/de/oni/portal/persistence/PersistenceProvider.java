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

	public static EntityManager getEntityManager()
	{
		return getEntityManager(null);
	}
	
	protected static EntityManager getEntityManager(Map<String, String> params)
	{
		Map<String, String> overrideParams = params != null ? new HashMap<String, String>(params) : new HashMap<String, String>();
		String url = Config.getString("portal.persistence.jdbc.url", null);
		if (url != null) overrideParams.put(PersistenceUnitProperties.JDBC_URL, url);
		String usr = Config.getString("portal.persistence.jdbc.user", null);
		if (usr != null) overrideParams.put(PersistenceUnitProperties.JDBC_USER, usr);
		String drv = Config.getString("portal.persistence.jdbc.driver", null);
		if (drv != null) overrideParams.put(PersistenceUnitProperties.JDBC_DRIVER, drv);
		String pwd = Config.getString("portal.persistence.jdbc.password", null);
		if (pwd != null) overrideParams.put(PersistenceUnitProperties.JDBC_PASSWORD, pwd);
		EntityManagerFactory emf = Persistence.createEntityManagerFactory(PERSISTENCE_UNIT, overrideParams);
		EntityManager em = emf.createEntityManager();
		return em;
	}
	
	protected static void generateSqlScripts()
	{
		final String dir = Config.getString("portal.persistence.sqlscripts.targetfolder", System.getProperty("java.io.tmpdir"));
		Map<String, String> persistProperties = new HashMap<String, String>();
		persistProperties.put(PersistenceUnitProperties.DDL_GENERATION, PersistenceUnitProperties.DROP_AND_CREATE);
		persistProperties.put(PersistenceUnitProperties.DDL_GENERATION_MODE, PersistenceUnitProperties.DDL_SQL_SCRIPT_GENERATION);
		persistProperties.put(PersistenceUnitProperties.APP_LOCATION, dir);
		persistProperties.put(PersistenceUnitProperties.CREATE_JDBC_DDL_FILE, PERSISTENCE_CREATE_DDL);
		persistProperties.put(PersistenceUnitProperties.DROP_JDBC_DDL_FILE, PERSISTENCE_DROP_DDL);
		getEntityManager(persistProperties).close();
		log.info(String.format("sql scripts written to %s", dir));
	}

}
