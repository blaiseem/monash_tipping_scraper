# monash_tipping_scraper
Scraper to update tips on Monash Tipping Website

To setup, change the function getTipsForSeason() to make a dataframe with columns: roundnumber (numeric), predictedwinner (text), probability (numeric), marginpredict (numeric), stdevMarginPredict (numeric).

The probbaility column should be given as the percentage value. Eg for a match with probability 51% this field should be 51, not 0.51.

The predictedwinner field should be the team you think will win and it should match with one of the values in the dictionary mappingMonashTeamToCode. Feel free to change the values in this dictionary. The keys should remain the same as they match the Monash site.

To use:

```
import scrape

scraper = scrape.MonashWebsiteScraper(username,password,roundNumbers)
scraper.updateTipsForSeason()
print('rounds updated: {}'.format(scraper.roundsUpdated))
```

