package de.oni.portal.lifecycle;

import java.util.Properties;

import javax.faces.application.Application;
import javax.faces.event.AbortProcessingException;
import javax.faces.event.PostConstructApplicationEvent;
import javax.faces.event.SystemEvent;
import javax.faces.event.SystemEventListener;

import org.apache.log4j.LogManager;
import org.apache.log4j.PropertyConfigurator;

import de.oni.portal.configuration.Config;

public class PortalStartedListener implements SystemEventListener
{

	@Override
	public boolean isListenerForSource(Object source)
	{
		return (source instanceof Application);
	}

	@Override
	public void processEvent(SystemEvent event) throws AbortProcessingException
	{
		if (event instanceof PostConstructApplicationEvent)
		{
			Config.readConfig();
			Properties logProps = Config.getLoggingProperties();
			LogManager.resetConfiguration();
			PropertyConfigurator.configure(logProps);
		}
	}

}
