import java.io.File;
import edu.uci.ics.crawler4j.crawler.CrawlConfig;
import edu.uci.ics.crawler4j.crawler.CrawlController;
import edu.uci.ics.crawler4j.fetcher.PageFetcher;
import edu.uci.ics.crawler4j.robotstxt.RobotstxtConfig;
import edu.uci.ics.crawler4j.robotstxt.RobotstxtServer;

public class BasicCrawlController 
{
	public static void main(String[] args) throws Exception 
	{
		args = new String[2];
		args[0] = "abc/";
		args[1] = "5";
		String crawlStorageFolder = args[0];
		int numberOfCrawlers = Integer.parseInt(args[1]);
		CrawlConfig config = new CrawlConfig();
		config.setCrawlStorageFolder(crawlStorageFolder);
		config.setPolitenessDelay(0);
		config.setMaxDepthOfCrawling(-1);
		config.setMaxPagesToFetch(-1);
		config.setResumableCrawling(true);
		PageFetcher pageFetcher = new PageFetcher(config);
		RobotstxtConfig robotstxtConfig = new RobotstxtConfig();
		RobotstxtServer robotstxtServer = new RobotstxtServer(robotstxtConfig, pageFetcher);
		CrawlController controller = new CrawlController(config, pageFetcher, robotstxtServer);
		controller.addSeed("http://innemedium.pl/taxonomy/term");
		new File("wynik").mkdirs();
		controller.start(BasicCrawler.class, numberOfCrawlers);
	}
}