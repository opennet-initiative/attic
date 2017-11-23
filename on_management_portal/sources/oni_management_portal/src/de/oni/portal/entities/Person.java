package de.oni.portal.entities;

import java.util.ArrayList;
import java.util.Date;
import java.util.EnumSet;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.Temporal;
import javax.persistence.TemporalType;

@Entity
public class Person
{

	public enum PersonStatus { Interested, Normal, Active }
	
	public enum PersonRole
	{
		Admin(1), Crew(2), Csr(4), Executive(8);
	
		private final int internalValue;
		
		PersonRole(int internalValue)
		{
			this.internalValue = internalValue;
		}
		
		public int getInternalValue()
		{
			return this.internalValue;
		}
	}

	@Id
	@GeneratedValue
	protected long id;
	protected String distinguishedName;

	protected String firstName;
	protected String lastName;
	
	@Temporal(TemporalType.DATE)
	protected Date dateOfJoining;

	protected String address;
	protected String zipCode;
	protected String city;
	protected String eMail;
	
	protected String accountNumber;
	protected String bankCode;
	protected String bankName;
	protected String accountHolder;
	
	protected String remark;
	protected String pseudonym;
	
	protected PersonStatus status;
	protected int roles;

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
	
	public Date getDateOfJoining() {
		return dateOfJoining;
	}

	public void setDateOfJoining(Date dateOfJoining) {
		this.dateOfJoining = dateOfJoining;
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

	public String getBankName() {
		return bankName;
	}

	public void setBankName(String bankName) {
		this.bankName = bankName;
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

	public String getPseudonym()
	{
		return pseudonym;
	}

	public void setPseudonym(String pseudonym)
	{
		this.pseudonym = pseudonym;
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

	public void setRoles(EnumSet<PersonRole> roles)
	{
		this.roles = 0;
		for (PersonRole r : roles)
		{
			this.roles |= r.getInternalValue();
		}
	}

	public EnumSet<PersonRole> getRoles()
	{
		EnumSet<PersonRole> r = EnumSet.noneOf(PersonRole.class);
		for (PersonRole pr : PersonRole.values())
		{
			if ((this.roles & pr.getInternalValue()) == pr.getInternalValue())
			{
				r.add(pr);
			}
		}
		return r;
	}

	public void setRolesStrings(String[] roles)
	{
		EnumSet<PersonRole> rolesSet = EnumSet.noneOf(PersonRole.class);
		for (String role : roles)
		{
			rolesSet.add(PersonRole.valueOf(role));
		}
		setRoles(rolesSet);
	}

	public String[] getRolesStrings()
	{
		ArrayList<String> rolesList = new ArrayList<String>();
		for (PersonRole role : getRoles()) {
			rolesList.add(role.name());
		}
		return rolesList.toArray(new String[]{});
	}

	public boolean hasRole(PersonRole role)
	{
		return (this.roles & role.getInternalValue()) == role.getInternalValue();
	}

	public void addRole(PersonRole role)
	{
		EnumSet<PersonRole> roles = getRoles();
		if (!roles.contains(role))
		{
			roles.add(role);
			setRoles(roles);
		}
	}
	
	public void removeRole(PersonRole role)
	{
		EnumSet<PersonRole> roles = getRoles();
		if (roles.contains(role))
		{
			roles.remove(role);
			setRoles(roles);
		}
	}
}
