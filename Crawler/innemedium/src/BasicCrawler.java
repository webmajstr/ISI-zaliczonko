import java.awt.Toolkit;
import java.io.BufferedWriter;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.io.Writer;
import edu.uci.ics.crawler4j.crawler.Page;
import edu.uci.ics.crawler4j.crawler.WebCrawler;
import edu.uci.ics.crawler4j.parser.HtmlParseData;
import edu.uci.ics.crawler4j.url.WebURL;

public class BasicCrawler extends WebCrawler 
{
	public boolean isArticle(String url)
	{
		if (!url.startsWith("http://innemedium.pl/wiadomosc/"))
			return false;
		return true;
	}
	
	public boolean isCategory(String url)
	{
		if (!url.startsWith("http://innemedium.pl/kategoria/"))
			return false;
		return true;
	}
	
	public boolean shouldVisit(WebURL url) 
	{
		String href = url.getURL();
		
		if (isArticle(href) || isCategory(href))
			return true;
		return false;
	}

	public void visit(Page page) 
	{
		String url = page.getWebURL().getURL();

		if (page.getParseData() instanceof HtmlParseData) 
		{
			HtmlParseData htmlParseData = (HtmlParseData) page.getParseData();
			String text = htmlParseData.getText();
			
			if (isArticle(url))
			{
				try 
				{
					String title = url.substring(31);
					if (title.contains("\\?"))
						title = title.replaceAll("?"," ");					
					Writer out = new BufferedWriter(new OutputStreamWriter(new FileOutputStream("wynik/" + title + ".txt"),"UTF-8"));
					out.write(text);
					out.close();
				} 
				catch (Exception e) 
				{
					Toolkit.getDefaultToolkit().beep();
					System.out.println("WYJATEK!!! " + e.getMessage() + " " + url);
				}
			}
			
			System.out.println(url);
		}
	}
}
