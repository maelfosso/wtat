use std::fs;
use serde::{Serialize, Deserialize};
use reqwest::header::{HeaderMap, HeaderValue};

use wtat_ingestion::get_posts_from_fb_pages;

#[derive(Serialize, Deserialize)]
struct  ScrapeState {
  last_cursor: Option<String>
}

fn main() {
  dotenvy::dotenv().ok();
  
  let data_path = std::env::var("DATA_PATH").expect(
    "DATA_PATH is missing"
  );
  let page_id = std::env::var("FB_PAGE_ID").expect("FB_PAGE_ID is missing");
  let rapid_api_key: String = std::env::var("RAPID_API_KEY").expect(
    "RAPID_API_KEY not set"
  );
  let rapid_api_host: String = std::env::var("RAPID_API_HOST").expect(
    "RAPID_API_HOST not set"
  );
  let max_pages: u32 = std::env::var("MAX_PAGES")
    .unwrap_or("0".to_string())
    .parse()
    .expect("MAX_PAGES must be a number");

  let state_path = format!("{}/{}/state.json", data_path, page_id);
  let mut current_cursor = if let Ok(content) = fs::read_to_string(&state_path) {
    let state: ScrapeState = serde_json::from_str(&content).unwrap_or(ScrapeState { last_cursor: None });

    state.last_cursor
  } else {
    None
  };
  //  Option<String> = None;

  let dir_path = format!("{}/{}", data_path, page_id);
  fs::create_dir_all(&dir_path).expect("Impossible to create a directory");

  let mut headers = HeaderMap::new();
  headers.insert("x-rapidapi-key", HeaderValue::from_str(&rapid_api_key).unwrap());
  headers.insert("x-rapidapi-host", HeaderValue::from_str(&rapid_api_host).unwrap());
  headers.insert("Content-Type", HeaderValue::from_static("application/json"));

  let client = reqwest::blocking::Client::builder()
    .default_headers(headers)
    .build().unwrap()
    ;

  let mut current_page = 0;

  loop {
    if max_pages > 0 && current_page >= max_pages {
      println!("Reached the limit: {} pages", max_pages);
      break;
    }

    println!("Collecting with cursor: {:?}", current_cursor);

    match get_posts_from_fb_pages(&client, &page_id, current_cursor.clone()) {
      Ok(response) => {
        let posts = response.results;

        for post in posts {
          let filename = format!("{}/{}.json", dir_path, post.post_id);

          let mut err = format!("Serialization error for post: {}", post.post_id);
          let json_data = serde_json::to_string_pretty(&post)
            .expect(&err);

          err = format!("Error writing file: {}", post.post_id);
          fs::write(filename, json_data).expect(&err);
        }
        
        if response.cursor.is_none() || response.cursor == current_cursor {
          println!("End of pagination.");
          break;
        }

        current_cursor = response.cursor;
        let state = ScrapeState {
          last_cursor: current_cursor.clone()
        };
        let state_json = serde_json::to_string(&state).unwrap();
        fs::write(&state_path, state_json).expect("Failed to save state");

        std::thread::sleep(std::time::Duration::from_secs(1));
        current_page += 1;
      }
      Err(err) => {
        eprintln!("Error: {err}")
      }
    }
  }
  
}
