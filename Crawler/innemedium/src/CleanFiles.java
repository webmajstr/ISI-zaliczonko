import java.awt.Toolkit;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.Vector;

import com.google.common.base.CharMatcher;

public class CleanFiles 
{
	Vector<String> files = new Vector<String>();
	
	public void listFilesForFolder(final File folder) 
	{
	    for (final File fileEntry : folder.listFiles()) 
	    {
	        if (fileEntry.isDirectory()) 
	        {
	            listFilesForFolder(fileEntry);
	        }
	        else 
	        {
	            files.add(fileEntry.getName());
	        }
	    }
	}
	
	public boolean isLetter(char ch)
	{
		if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z'))
			return true;
		return false;
	}
	
	public boolean isDigit(char ch)
	{
		if (ch >= '0' && ch <= '9')
			return true;
		return false;
	}
	
	public boolean isWhitespace(char ch)
	{
		if ((ch == ' ') || (ch =='\n') || (ch == '\t')|| (ch == '\r'))
			return true;
		return false;
	}
	
	public String cleanFromWS(String str)
	{
		return CharMatcher.WHITESPACE.trimFrom(str);
	}
	
	public void saveToFile(String title,String str)
	{
		try 
		{					
			Writer out = new BufferedWriter(new OutputStreamWriter(new FileOutputStream("oczyszczone/" + title),"UTF-8"));
			out.write(str);
			out.close();
			System.out.println("OCZYSZCZONO - " + title);
		} 
		catch (Exception e) 
		{
			Toolkit.getDefaultToolkit().beep();
			System.out.println("WYJATEK!!! " + e.getMessage() + " " + title);
		}
	}
	
	public void cleanFile(String fn)
	{
		InputStream is;
		Vector<String> line = new Vector<String>();
		try 
		{
			is = new FileInputStream("wynik/" + fn);
			BufferedReader in = new BufferedReader(new InputStreamReader(is,"UTF-8"));
			String sCurrentLine;
			while ((sCurrentLine = in.readLine()) != null) 
			{
				line.add(sCurrentLine);
			}
			in.close();
			is.close();
		} 
		catch (Exception e) 
		{
			Toolkit.getDefaultToolkit().beep();
			System.out.println("Exception! - " + e.getMessage() + " - " + fn);
		}
		
		String wynik = "";
		int startLine = -1;
		
		for (int i=0;i<line.size();i++)
		{
			if (line.get(i).contains("                    "))
			{
				startLine = i;
				break;
			}
		}
		
		if (startLine == -1)
		{
			Toolkit.getDefaultToolkit().beep();
			System.out.println("Brak startLine - " + fn);
		}
		
		String endString = "Udostępnij artykuł w sieciach społecznościowych Google Plus One";
		boolean endFlag = false;
		
		for (int i=startLine;i<line.size();i++)
		{
			if (line.get(i).contains(endString))
			{
				line.set(i,line.get(i).replace(endString,""));
				endFlag = true;
			}
			
			if (line.get(i).length()<=5)
				continue;
			if (!isWhitespace(line.get(i).charAt(0)) || (isWhitespace(line.get(i).charAt(0)) && !isWhitespace(line.get(i).charAt(0))))
			{
				String cleanStr = cleanFromWS(line.get(i));
				if (cleanStr.length()>0)
				{
					wynik += cleanStr + '\n';
				}
			}
			
			if (endFlag == true)
			{
				break;
			}
			
			if (i==line.size()-1)
			{
				Toolkit.getDefaultToolkit().beep();
				System.out.println("Brak endString - " + fn);
			}
		}
		
		if (wynik.length()>1)
		{
			wynik = wynik.substring(0,wynik.length()-1);
			saveToFile(fn,wynik);
		}
		else
		{
			Toolkit.getDefaultToolkit().beep();
			System.out.println("Brak wyniku - " + fn);
		}
	}
	
	public void start()
	{
		new File("oczyszczone").mkdirs();
		File folder = new File("wynik");
		listFilesForFolder(folder);
		
		for (int i=0;i<files.size();i++)
		{
			cleanFile(files.get(i));
		}
	}
	
	public static void main(String[] args) 
	{
		new CleanFiles().start();
	}
}
