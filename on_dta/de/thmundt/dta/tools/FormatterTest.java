package de.thmundt.dta.tools;

import junit.framework.TestCase;

public class FormatterTest extends TestCase {

	/*
	 * Test method for
	 * 'de.thmundt.dta.tools.Formatter.addPaddingAndTrim(Feldformat, int,
	 * String)'
	 */
	public void testAddPaddingAndTrim() {
		assertEquals(Formatter.fit("N", 10, "0120"), "0000000120");
		assertEquals(Formatter.fit("N", 3, "0120"), "012");
		assertEquals(Formatter.fit("A", 10, "Test"), "Test      ");
		assertEquals(Formatter.fit("A", 3, "Test Case"), "Tes");

	}

	/*
	 * Test method for
	 * 'de.thmundt.dta.tools.Formatter.isInCorrectFormat(Feldformat, int,
	 * String)'
	 */
	public void testIsInCorrectFormat() {
		assertTrue(Formatter.isInCorrectFormat("N", 10, "0000000120"));
		assertFalse(Formatter.isInCorrectFormat("N", 10, "000000120"));
	}

	/*
	 * Test method for
	 * 'de.thmundt.dta.tools.Formatter.isInCorrectFormat(Feldformat, int,
	 * String)'
	 */
	public void testFitsInField() {
		assertTrue(Formatter.fitsInField("N", 10, "0012012345"));
		assertTrue(Formatter.fitsInField("A", 10, "123451234512345"));
		assertFalse(Formatter.fitsInField("N", 10, "00000000120"));
	}

}
