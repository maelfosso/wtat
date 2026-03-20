mod models;

use reqwest::blocking::Client;
use reqwest::Error;

use models::{GetPostsResponse};

pub fn get_posts_from_fb_pages(client: &Client, page_id: &String, cursor: Option<String>) -> Result<GetPostsResponse, Error> {
  let mut url = format!(
    "https://facebook-scraper3.p.rapidapi.com/page/posts?page_id={}",
    page_id
  );
  if let Some(c) = cursor {
    url.push_str(&format!("&cursor={}", c));
  }

  let response = client.get(url).send()?;
  let text = response.text()?;
  println!("DEBUG JSON: {}\n\n", text);

  let body = serde_json::from_str(&text).map_err(|e| {
    eprintln!("Parsing error: {}", e);
    panic!("STOP DEBUGGING");
  });
  // Ok(body)
  body
}