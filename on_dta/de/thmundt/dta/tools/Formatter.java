package de.thmundt.dta.tools;

public class Formatter {
    public static boolean fitsInField(String feldformat, int feldlaenge,
            String input) {
        if (feldformat.equals("A"))
            return true;
        if (feldformat.equals("N"))
            return (input.length() <= feldlaenge);
        return false;
    }

    public static boolean isInCorrectFormat(String feldformat, int feldlaenge,
            String input) {
        int inputlen = input.length();
        if (inputlen != feldlaenge)
            return false;
        if (feldformat.equals("N")) {
            for (int i = 0; i < inputlen; i++) {
                char curChar = input.charAt(i);
                if ((curChar < '0') || (curChar > '9'))
                    return false;
            }
            return true;
        }
        if (feldformat.equals("A")) {
            return true;
        }
        return false;
    }

    public static String convertMoney(String value) {
        return "";
    }

    public static String fit(String feldformat, int feldlaenge, String input) {
        int inputlen;
        if (input != null)
            inputlen = input.length();
        else
            inputlen = 0;
        if (feldlaenge < inputlen)
            inputlen = feldlaenge;
        char pad = 'x';
        StringBuffer strBuf = new StringBuffer();
        if (feldformat.equals("N")) {
            pad = '0';
            int paddinglength = feldlaenge - inputlen;
            for (int i = 0; i < paddinglength; i++) {
                strBuf.append(pad);
            }
            for (int i = 0; i < inputlen; i++) {
                char curChar = input.charAt(i);
                strBuf.append(curChar);
            }
        }
        if (feldformat.equals("A")) {
            pad = ' ';
            int paddinglength = feldlaenge - inputlen;
            for (int i = 0; i < inputlen; i++) {
                char curChar = input.charAt(i);
                strBuf.append(curChar);
            }
            for (int i = 0; i < paddinglength; i++) {
                strBuf.append(pad);
            }
        }
        if (feldformat.equals("S")) {
            if (inputlen == 0) {
                pad = ' ';
                int paddinglength = feldlaenge - inputlen;
                for (int i = 0; i < inputlen; i++) {
                    char curChar = input.charAt(i);
                    strBuf.append(curChar);
                }
                for (int i = 0; i < paddinglength; i++) {
                    strBuf.append(pad);
                }
            } else {
                pad = '0';
                int paddinglength = feldlaenge - inputlen;
                for (int i = 0; i < paddinglength; i++) {
                    strBuf.append(pad);
                }
                for (int i = 0; i < inputlen; i++) {
                    char curChar = input.charAt(i);
                    strBuf.append(curChar);
                }
            }
        }

        return strBuf.toString().toUpperCase();
    }
}
