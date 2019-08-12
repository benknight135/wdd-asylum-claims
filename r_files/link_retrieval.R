library(rvest)
library(data.table)

#### Create vector of links for scraper to use

case_links <- character(0)

# NB - the below takes several minutes - recommend using the case_links.feather file that exists

for (page_num in 1:938) {

  # Link for each new page
  page <- xml2::read_html(paste0("https://tribunalsdecisions.service.gov.uk/utiac?&page=",
                           page_num))
  # Get links of cases from page
  new_links <- page %>%
    html_nodes("td:nth-child(1) a") %>%
    html_attr('href')


  case_links <- c(case_links, new_links)
}

case_links_table <- as.data.table(case_links)

feather::write_feather(case_links_table, "case_links.feather")



