library(rvest)

#### Create vector of links for scraper to use

# First page done individually as different address style

first_page <- read_html("https://tribunalsdecisions.service.gov.uk/utiac?utf8=%E2%9C%93&search%5Bquery%5D=&search%5Breported%5D=all&search%5Bcountry%5D=&search%5Bcountry_guideline%5D=0&search%5Bjudge%5D=&search%5Bclaimant%5D=")

case_links <- first_page %>%
  html_nodes("td:nth-child(1) a") %>% 
  html_attr('href')

# Second page onward has page=2 etc, so replicable pattern
# NB - the below takes several minutes - recommend using the case_links.feather file that exists

for (page_num in 2:933) {

  # Link for each new page
  page <- read_html(paste0("https://tribunalsdecisions.service.gov.uk/utiac?page=",
                           page_num,
                           "&search%5Bclaimant%5D=&search%5Bcountry%5D=&search%5Bcountry_guideline%5D=&search%5Bjudge%5D=&search%5Bquery%5D=&search%5Breported%5D=all&utf8=%E2%9C%93"))

  # Get links of cases from page
  new_links <- page %>%
    html_nodes(".unreported a") %>%
    html_attr('href')


  case_links <- c(case_links, new_links)
}

case_links_table <- as.data.table(case_links)

feather::write_feather(case_links_table, "case_links.feather")



