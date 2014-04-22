import java.awt.Toolkit;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Vector;
import org.dom4j.Document;
import org.dom4j.DocumentHelper;
import org.dom4j.Element;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.XMLWriter;

/*
 *	IN - POBIERA PLIKI Z FOLDERU "articles" I JEGO PODFOLDERÓW
 *  OUT - ZAPISUJE WYNIKI W PLIKU "wynik.xml"
 */ 

public class ArticlesToXML 
{
	int articleNum = 0;
	
	Vector<String> files = new Vector<String>();
	
	Document document = DocumentHelper.createDocument();
    Element add = document.addElement("add");
	
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
	            files.add(fileEntry.getAbsolutePath());
	        }
	    }
	}
	
	public void addToXML(String fn)
	{
		InputStream is;
		String text = "";
		try 
		{
			is = new FileInputStream(fn);
			BufferedReader in = new BufferedReader(new InputStreamReader(is,"UTF-8"));
			String sCurrentLine;
			while ((sCurrentLine = in.readLine()) != null) 
			{
				text += sCurrentLine + '\n';
			}
			text = text.substring(0,text.length()-1);
			in.close();
			is.close();
		} 
		catch (Exception e) 
		{
			Toolkit.getDefaultToolkit().beep();
			System.out.println("Exception! - " + e.getMessage() + " - " + fn);
		}
		
		fn = fn.replace(".txt","");
		fn = fn.substring(fn.lastIndexOf("/")+1);
		
		Element doc = add.addElement("doc");
		doc.addElement("field").addAttribute("name","id");
		doc.addElement("field").addAttribute("name","title").addText(fn);
		doc.addElement("field").addAttribute("name","datawydarzenia");
		doc.addElement("field").addAttribute("name","miejsce");
		doc.addElement("field").addAttribute("name","description").addText(text);
		
		articleNum = articleNum + 1;
		
		System.out.println("[" + articleNum + "] " + fn);
	}
	
	public void saveXML()
	{
		try
		{
			OutputFormat format = new OutputFormat("  ", true);
	        FileWriter out = new FileWriter("wynik.xml");
	        XMLWriter writer = new XMLWriter(out, format);
	        writer.write(document);
	        out.close();
		}
		catch (Exception e)
		{
			System.out.println(e.getMessage());
		}
	}
	
	public void start()
	{
		File folder = new File("articles");
		listFilesForFolder(folder);
		
		for (int i=0;i<files.size();i++)
		{
			addToXML(files.get(i));
		}
		
		saveXML();
	}
	
	public static void main(String[] args) 
	{
		new ArticlesToXML().start();
	}
}
