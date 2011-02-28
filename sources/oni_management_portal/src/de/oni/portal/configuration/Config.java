package de.oni.portal.configuration;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Map.Entry;
import java.util.Properties;

import org.apache.log4j.Logger;

public class Config
{
	
	private static final Logger log = Logger.getLogger(Config.class);

	protected static Properties props = new Properties();

	public static void readConfig()
	{
		synchronized (props)
		{
			final File dir = new File(System.getProperty("catalina.home"), "conf");
			final File file = new File(dir, "portal.properties");
			props.clear();
			try
			{
				props.load(new FileInputStream(file));
			} catch (FileNotFoundException e)
			{
				System.err.println(String.format("missing config file %s!", file.getAbsolutePath()));
				log.warn(String.format("missing config file %s!", file.getAbsolutePath()));
			} catch (IOException e)
			{
				throw new RuntimeException(e);
			}
		}
	}
	
	public static Properties getLoggingProperties()
	{
		synchronized (props)
		{
			Properties logProps = new Properties();
			for (Entry<Object, Object> pe : props.entrySet())
			{
				if (pe.getKey() != null && pe.getKey().toString().startsWith("log4j."))
				{
					logProps.put(pe.getKey(), pe.getValue());
				}
			}
			return logProps;
		}
	}
	
	public static String getString(String key)
	{
		synchronized (props)
		{
			return props.getProperty(key);
		}
	}

}
