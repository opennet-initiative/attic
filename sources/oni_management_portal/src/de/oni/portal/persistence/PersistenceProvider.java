package de.oni.portal.persistence;

import java.util.HashMap;
import java.util.Map;

import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.Persistence;

import org.apache.log4j.Logger;
import org.eclipse.persistence.config.PersistenceUnitProperties;

public class PersistenceProvider implements PersistenceConstants
{
	
	private static final Logger log = Logger.getLogger(PersistenceProvider.class);

	public static EntityManager getEntityManager()
	{
		return getEntityManager(null);
	}
	
	protected static EntityManager getEntityManager(Map<String, String> params)
	{
		EntityManagerFactory emf = params != null ? Persistence.createEntityManagerFactory(PERSISTENCE_UNIT, params) : Persistence.createEntityManagerFactory(PERSISTENCE_UNIT);
		EntityManager em = emf.createEntityManager();
		return em;
	}
	
	protected static void generateSqlScripts()
	{
		final String tmpDir = System.getProperty("java.io.tmpdir");
		Map<String, String> persistProperties = new HashMap<String, String>();
		persistProperties.put(PersistenceUnitProperties.DDL_GENERATION, PersistenceUnitProperties.DROP_AND_CREATE);
		persistProperties.put(PersistenceUnitProperties.DDL_GENERATION_MODE, PersistenceUnitProperties.DDL_SQL_SCRIPT_GENERATION);
		persistProperties.put(PersistenceUnitProperties.APP_LOCATION, tmpDir);
		persistProperties.put(PersistenceUnitProperties.CREATE_JDBC_DDL_FILE, PERSISTENCE_CREATE_DDL);
		persistProperties.put(PersistenceUnitProperties.DROP_JDBC_DDL_FILE, PERSISTENCE_DROP_DDL);
		getEntityManager().close();
		log.debug(String.format("sql scripts written to %s", tmpDir));
	}

}
