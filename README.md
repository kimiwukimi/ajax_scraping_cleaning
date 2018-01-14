# Ajax Scraping and cleaning
Disclaimer:  This project is only a demonstration of what are the problems and how to solve them when retrieving data from the web. Please do not violate any website's term of use. Do this at your own risks.
## Example Task
Retrieve all the attributes (about 25, shown in the page below) from top 1000 reviewers' reviews on A website since 8/1/2016. 
> I am just taking A's website as an example. I will never encourage anyone to violate A website's term of use.

![example_reviews](pics/example_reviews.png?raw=true "Title")
	
- Scale: 120,000 pages of reviews (by the time I tested at Oct. 2016)
> The example code in the repository are done at 2016. Since the webpage changes often, they are not working now. But you could still could modify it to finish the example task.

## Steps
1. Retrieval top 1000 reviewers' id 
2. Retrieval all reviews' id of these 1000 reviewers
3. Download these reviews pages
4. Parse fields and store into database

### Step1: Retrieval top reviewers id 
- This is the easiest part. Simply use [Requests](http://docs.python-requests.org/en/master/) and [Regular Expression](https://docs.python.org/2/library/re.html) will do.
- [Example code](get_reviewers_id.py)

![example_top1000_reviewers](pics/example_top1000_reviewers.png?raw=true "Title")

### Step2: Retrieval reviews id 
- **[Ajax](https://en.wikipedia.org/wiki/Ajax_(programming)) rendered webpage** cannot just use requests to scrape ([example](https://www.amazon.com/gp/profile/amzn1.account.AFQ7TVKKSLR6C5MSZDWAYMR2OPCA)).
	- Solution: use **[Selenium](http://www.seleniumhq.org/)** and **[PhantomJS](http://phantomjs.org/)/[Chromium](https://sites.google.com/a/chromium.org/chromedriver/)**.
		- PhantomJS: headless driver (no GUI)
		- Chromium: Chrome driver (like regular chrome)
	- Explanation: use Selenium to simulate human scrolling activity.
- **Change [User-Agent](https://en.wikipedia.org/wiki/User_agent)** to avoid been banned.
	- Use a list of user-agents and changes requests' user-agent could mitigate the probability of been detected scraping. 

![example_review_id](pics/example_review_id.png?raw=true "Title")
- [Example code](get_page.py)

### Step3: Download reviews pages
- This step is the most difficult part due to the scale (120,000 pages) of the example.
1. IP ban
	- use [VPN](https://en.wikipedia.org/wiki/Virtual_private_network), preferably the ones that has a lot of servers and ones that can can change ip automatically.
	- Change User-Agent to avoid been banned.

2. "I'm not a robot" test

![i_am_not_a_robot](pics/i_am_not_a_robot.jpg?raw=true "Title")
	
- Probably not the best way, but you could use chromium to click it manually. Once you clicked it manually, it will not show up possibly in hours.
- Library used: Requests, Regular Expression
- [Example code](download_pages.py)


### Step4: Parse and store into database
- Major problem: unexpected fields might show up when parsing.
	- Consequence: 
		- parsing rules might change when sees new fields that disrupts [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) rules that you previous set. 
	- Suggested solution: 
		1. The better way, in my opinion, would be spend more time browsing reviews pages and gather as much field in advance as possible. The less surprises, the easier to parse with BeautifulSoup. 
		2. Then use absolute path more, instead of relative ones.

- Could use [NoSQL](https://en.wikipedia.org/wiki/NoSQL) or SQLite database to store data (including previous steps).
- [Example code](parse.py)

##  Possible Problems
1. Websites **changes** it's url or html **structure**. Worst case is that you have to do the whole project from ground zero again.
2. Websites **disabled/hide** some **information** from showing **without warning**. Then you have to rethink if the dataset could work if some data are missing.
3. Legal problems since as far as I know, scraping violates a lot of websites term of use. Please consult professional or try this at your own risks.