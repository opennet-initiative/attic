package de.oni.portal.entities;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

@Entity
public class Person
{

	enum PersonStatus { Interested, Normal, Active }
	enum PersonRole { Admin, Crew, Csr, Executive }

	@Id
	@GeneratedValue
	protected long id;
	protected String distinguishedName;

	protected String firstName;
	protected String lastName;
	protected String address;
	protected String zipCode;
	protected String city;
	protected String eMail;
	
	protected String accountNumber;
	protected String bankCode;
	protected String accountHolder;
	
	protected String remark;
	protected String alias;
	
	protected PersonStatus status;

	public String getDistinguishedName()
	{
		return distinguishedName;
	}

	public void setDistinguishedName(String distinguishedName)
	{
		this.distinguishedName = distinguishedName;
	}

	public String getFirstName()
	{
		return firstName;
	}

	public void setFirstName(String firstName)
	{
		this.firstName = firstName;
	}

	public String getLastName()
	{
		return lastName;
	}

	public void setLastName(String lastName)
	{
		this.lastName = lastName;
	}

	public String getAddress()
	{
		return address;
	}

	public void setAddress(String address)
	{
		this.address = address;
	}

	public String getZipCode()
	{
		return zipCode;
	}

	public void setZipCode(String zipCode)
	{
		this.zipCode = zipCode;
	}

	public String getCity()
	{
		return city;
	}

	public void setCity(String city)
	{
		this.city = city;
	}

	public String getEMail()
	{
		return eMail;
	}

	public void setEMail(String eMail)
	{
		this.eMail = eMail;
	}

	public String getAccountNumber()
	{
		return accountNumber;
	}

	public void setAccountNumber(String accountNumber)
	{
		this.accountNumber = accountNumber;
	}

	public String getBankCode()
	{
		return bankCode;
	}

	public void setBankCode(String bankCode)
	{
		this.bankCode = bankCode;
	}

	public String getAccountHolder()
	{
		return accountHolder;
	}

	public void setAccountHolder(String accountHolder)
	{
		this.accountHolder = accountHolder;
	}

	public String getRemark()
	{
		return remark;
	}

	public void setRemark(String remark)
	{
		this.remark = remark;
	}

	public String getAlias()
	{
		return alias;
	}

	public void setAlias(String alias)
	{
		this.alias = alias;
	}

	public long getId()
	{
		return id;
	}

	public PersonStatus getStatus()
	{
		return status;
	}

	public void setStatus(PersonStatus status)
	{
		this.status = status;
	}
}
