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

public class ConnectPages 
{
	Vector<String> files = new Vector<String>();
	
	public void print(String str)
	{
		System.out.println(str);
	}
	
	public void sleep(int i)
	{
		try 
		{
			Thread.sleep(i);
		} 
		catch (Exception e) 
		{}
	}
	
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
	
	public String getFullText(String fn)
	{
		InputStream is;
		Vector<String> line = new Vector<String>();
		try 
		{
			is = new FileInputStream("oczyszczone/" + fn + ".txt");
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
		
		String txt = "";
		for (int i=0;i<line.size();i++)
		{
			txt += line.get(i) + '\n';
		}
		
		txt = txt.substring(0,txt.length()-1);
		
		return txt;
	}
	
	public void saveToFile(String title,String str)
	{
		try 
		{					
			Writer out = new BufferedWriter(new OutputStreamWriter(new FileOutputStream("innemedium/" + title),"UTF-8"));
			out.write(str);
			out.close();
		} 
		catch (Exception e) 
		{
			Toolkit.getDefaultToolkit().beep();
			System.out.println("WYJATEK!!! " + e.getMessage() + " " + title);
		}
	}
	
	public void start()
	{
		new File("innemedium").mkdirs();
		File folder = new File("oczyszczone");
		listFilesForFolder(folder);
		
		for (int i=0;i<files.size();i++)
		{
			files.set(i,files.get(i).replace(".txt",""));
			
			if (files.get(i).contains("?page="))
				continue;
			
			int page = 1;
			boolean work = true;
			
			String pg = getFullText(files.get(i));
			
			while (work == true)
			{
				work = false;
				for (int j=0;j<files.size();j++)
				{
					files.set(j,files.get(j).replace(".txt",""));
					
					if (files.get(j).equals(files.get(i) + "?page=" + page))
					{
						work = true;
						page = page + 1;
						pg = pg + '\n' + getFullText(files.get(j));
						System.out.println("CONNECTED - " + files.get(j));
					}
				}
			}
			
			saveToFile(files.get(i),pg);
		}
	}
	
	public static void main(String[] args) 
	{
		new ConnectPages().start();
	}
}
